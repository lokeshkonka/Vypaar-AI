"""Discussions endpoint for community discussions."""

from typing import Optional, List
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from loguru import logger

from app.api.dependencies import get_db
from app.models.schemas import (
    DiscussionCreate,
    DiscussionUpdate,
    DiscussionResponse,
    DiscussionListResponse,
    CommentCreate,
    CommentResponse,
    CommentListResponse,
)
from app.database.repositories import DiscussionRepository, CommentRepository
from app.database.models import Discussion
from app.core.utils import get_current_timestamp


router = APIRouter(prefix="/discussions", tags=["Discussions"])


def get_discussion_repo(db=Depends(get_db)) -> DiscussionRepository:
    """Get discussion repository."""
    return DiscussionRepository(db)


def get_comment_repo(db=Depends(get_db)) -> CommentRepository:
    """Get comment repository."""
    return CommentRepository(db)


@router.get("/", response_model=DiscussionListResponse)
async def get_discussions(
    commodity: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: str = Query("recent", pattern="^(recent|popular|views)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    repo: DiscussionRepository = Depends(get_discussion_repo),
) -> DiscussionListResponse:
    """Get discussions with optional filtering and search."""
    try:
        if search:
            discussions = await repo.search(search, skip, limit)
        elif commodity:
            discussions = await repo.get_by_commodity(commodity, skip, limit)
        else:
            discussions = await repo.get_recent(skip, limit)

        # Sort discussions
        if sort_by == "popular":
            discussions.sort(key=lambda x: x.likes_count, reverse=True)
        elif sort_by == "views":
            discussions.sort(key=lambda x: x.views_count, reverse=True)

        responses = [
            DiscussionResponse(
                id=d.id,
                title=d.title,
                content=d.content,
                commodity=d.commodity,
                market=d.market,
                author=d.author,
                avatar_url=d.avatar_url,
                likes_count=d.likes_count,
                replies_count=d.replies_count,
                views_count=d.views_count,
                is_pinned=d.is_pinned,
                tags=d.tags or [],
                status=d.status,
                created_at=d.created_at,
                updated_at=d.updated_at,
            )
            for d in discussions
        ]

        return DiscussionListResponse(
            discussions=responses,
            total=len(responses),
            page=skip // limit + 1,
            page_size=limit,
        )
    except Exception as e:
        logger.error(f"Error fetching discussions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch discussions")


@router.get("/pinned", response_model=List[DiscussionResponse])
async def get_pinned_discussions(
    limit: int = Query(10, ge=1, le=20),
    repo: DiscussionRepository = Depends(get_discussion_repo),
) -> List[DiscussionResponse]:
    """Get pinned discussions."""
    try:
        discussions = await repo.get_pinned(limit)
        return [
            DiscussionResponse(
                id=d.id,
                title=d.title,
                content=d.content,
                commodity=d.commodity,
                market=d.market,
                author=d.author,
                avatar_url=d.avatar_url,
                likes_count=d.likes_count,
                replies_count=d.replies_count,
                views_count=d.views_count,
                is_pinned=d.is_pinned,
                tags=d.tags or [],
                status=d.status,
                created_at=d.created_at,
                updated_at=d.updated_at,
            )
            for d in discussions
        ]
    except Exception as e:
        logger.error(f"Error fetching pinned discussions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch pinned discussions")


@router.get("/{discussion_id}", response_model=DiscussionResponse)
async def get_discussion(
    discussion_id: int,
    repo: DiscussionRepository = Depends(get_discussion_repo),
) -> DiscussionResponse:
    """Get a specific discussion by ID."""
    try:
        discussion = await repo.get_by_id(discussion_id)
        if not discussion:
            raise HTTPException(status_code=404, detail="Discussion not found")

        # Increment views
        await repo.increment_views(discussion_id)

        return DiscussionResponse(
            id=discussion.id,
            title=discussion.title,
            content=discussion.content,
            commodity=discussion.commodity,
            author=discussion.author,
            avatar_url=discussion.avatar_url,
            likes_count=discussion.likes_count,
            replies_count=discussion.replies_count,
            views_count=discussion.views_count + 1,
            is_pinned=discussion.is_pinned,
            tags=discussion.tags or [],
            status=discussion.status,
            created_at=discussion.created_at,
            updated_at=discussion.updated_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching discussion {discussion_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch discussion")


@router.post("/", response_model=DiscussionResponse, status_code=status.HTTP_201_CREATED)
async def create_discussion(
    request: DiscussionCreate,
    repo: DiscussionRepository = Depends(get_discussion_repo),
) -> DiscussionResponse:
    """Create a new discussion."""
    try:
        # Generate default avatar if not provided
        avatar_url = request.avatar_url or f"https://api.dicebear.com/7.x/avataaars/svg?seed={request.author}"

        discussion = await repo.create(
            title=request.title,
            content=request.content,
            commodity=request.commodity,
            market=request.market,
            author=request.author,
            avatar_url=avatar_url,
            tags=request.tags or [],
            status="PUBLISHED",
            likes_count=0,
            replies_count=0,
            views_count=0,
            is_pinned=False,
        )

        await repo.db.commit()

        logger.info(f"Discussion created: {discussion.id} by {request.author}")

        return DiscussionResponse(
            id=discussion.id,
            title=discussion.title,
            content=discussion.content,
            commodity=discussion.commodity,
            author=discussion.author,
            avatar_url=discussion.avatar_url,
            likes_count=discussion.likes_count,
            replies_count=discussion.replies_count,
            views_count=discussion.views_count,
            is_pinned=discussion.is_pinned,
            tags=discussion.tags or [],
            status=discussion.status,
            created_at=discussion.created_at,
            updated_at=discussion.updated_at,
        )
    except Exception as e:
        logger.error(f"Error creating discussion: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create discussion")


@router.put("/{discussion_id}", response_model=DiscussionResponse)
async def update_discussion(
    discussion_id: int,
    request: DiscussionUpdate,
    repo: DiscussionRepository = Depends(get_discussion_repo),
) -> DiscussionResponse:
    """Update a discussion."""
    try:
        discussion = await repo.get_by_id(discussion_id)
        if not discussion:
            raise HTTPException(status_code=404, detail="Discussion not found")

        if request.title:
            discussion.title = request.title
        if request.content:
            discussion.content = request.content
        if request.tags is not None:
            discussion.tags = request.tags

        discussion.updated_at = get_current_timestamp()
        await repo.db.flush()
        await repo.db.commit()

        logger.info(f"Discussion {discussion_id} updated")

        return DiscussionResponse(
            id=discussion.id,
            title=discussion.title,
            content=discussion.content,
            commodity=discussion.commodity,
            author=discussion.author,
            avatar_url=discussion.avatar_url,
            likes_count=discussion.likes_count,
            replies_count=discussion.replies_count,
            views_count=discussion.views_count,
            is_pinned=discussion.is_pinned,
            tags=discussion.tags or [],
            status=discussion.status,
            created_at=discussion.created_at,
            updated_at=discussion.updated_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating discussion {discussion_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update discussion")


@router.delete("/{discussion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_discussion(
    discussion_id: int,
    repo: DiscussionRepository = Depends(get_discussion_repo),
):
    """Delete a discussion (soft delete - mark as archived)."""
    try:
        discussion = await repo.get_by_id(discussion_id)
        if not discussion:
            raise HTTPException(status_code=404, detail="Discussion not found")

        discussion.status = "ARCHIVED"
        await repo.db.flush()
        await repo.db.commit()

        logger.info(f"Discussion {discussion_id} archived")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting discussion {discussion_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete discussion")


@router.post("/{discussion_id}/like", response_model=DiscussionResponse)
async def like_discussion(
    discussion_id: int,
    repo: DiscussionRepository = Depends(get_discussion_repo),
) -> DiscussionResponse:
    """Like a discussion."""
    try:
        discussion = await repo.increment_likes(discussion_id)
        if not discussion:
            raise HTTPException(status_code=404, detail="Discussion not found")

        await repo.db.commit()

        logger.info(f"Discussion {discussion_id} liked")

        return DiscussionResponse(
            id=discussion.id,
            title=discussion.title,
            content=discussion.content,
            commodity=discussion.commodity,
            author=discussion.author,
            avatar_url=discussion.avatar_url,
            likes_count=discussion.likes_count,
            replies_count=discussion.replies_count,
            views_count=discussion.views_count,
            is_pinned=discussion.is_pinned,
            tags=discussion.tags or [],
            status=discussion.status,
            created_at=discussion.created_at,
            updated_at=discussion.updated_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error liking discussion {discussion_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to like discussion")


@router.get("/commodity/{commodity}", response_model=DiscussionListResponse)
async def get_discussions_by_commodity(
    commodity: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    repo: DiscussionRepository = Depends(get_discussion_repo),
) -> DiscussionListResponse:
    """Get discussions for a specific commodity."""
    try:
        discussions = await repo.get_by_commodity(commodity, skip, limit)

        responses = [
            DiscussionResponse(
                id=d.id,
                title=d.title,
                content=d.content,
                commodity=d.commodity,
                market=d.market,
                author=d.author,
                avatar_url=d.avatar_url,
                likes_count=d.likes_count,
                replies_count=d.replies_count,
                views_count=d.views_count,
                is_pinned=d.is_pinned,
                tags=d.tags or [],
                status=d.status,
                created_at=d.created_at,
                updated_at=d.updated_at,
            )
            for d in discussions
        ]

        return DiscussionListResponse(
            discussions=responses,
            total=len(responses),
            page=skip // limit + 1,
            page_size=limit,
        )
    except Exception as e:
        logger.error(f"Error fetching discussions for commodity {commodity}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch discussions")


# Comment endpoints
@router.get("/{discussion_id}/comments", response_model=CommentListResponse)
async def get_comments(
    discussion_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    repo: CommentRepository = Depends(get_comment_repo),
) -> CommentListResponse:
    """Get comments for a discussion."""
    try:
        comments = await repo.get_by_discussion(discussion_id, skip, limit)

        responses = [
            CommentResponse(
                id=c.id,
                discussion_id=c.discussion_id,
                author=c.author,
                avatar_url=c.avatar_url or f"https://api.dicebear.com/7.x/avataaars/svg?seed={c.author}",
                content=c.content,
                likes_count=c.likes_count,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
            for c in comments
        ]

        return CommentListResponse(
            comments=responses,
            total=len(responses),
            page=skip // limit + 1,
            page_size=limit,
        )
    except Exception as e:
        logger.error(f"Error fetching comments for discussion {discussion_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch comments")


@router.post("/{discussion_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    discussion_id: int,
    request: CommentCreate,
    comment_repo: CommentRepository = Depends(get_comment_repo),
    discussion_repo: DiscussionRepository = Depends(get_discussion_repo),
) -> CommentResponse:
    """Create a new comment on a discussion."""
    try:
        avatar_url = request.avatar_url or f"https://api.dicebear.com/7.x/avataaars/svg?seed={request.author}"

        comment = await comment_repo.create(
            discussion_id=discussion_id,
            author=request.author,
            avatar_url=avatar_url,
            content=request.content,
            likes_count=0,
        )

        # Update discussion reply count
        await discussion_repo.increment_replies(discussion_id)

        logger.info(f"Comment created on discussion {discussion_id} by {request.author}")

        return CommentResponse(
            id=comment.id,
            discussion_id=comment.discussion_id,
            author=comment.author,
            avatar_url=comment.avatar_url,
            content=comment.content,
            likes_count=comment.likes_count,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
        )
    except Exception as e:
        logger.error(f"Error creating comment: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create comment")


@router.post("/{discussion_id}/comments/{comment_id}/like", response_model=CommentResponse)
async def like_comment(
    discussion_id: int,
    comment_id: int,
    repo: CommentRepository = Depends(get_comment_repo),
) -> CommentResponse:
    """Like a comment."""
    try:
        comment = await repo.increment_likes(comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")

        logger.info(f"Comment {comment_id} liked")

        return CommentResponse(
            id=comment.id,
            discussion_id=comment.discussion_id,
            author=comment.author,
            avatar_url=comment.avatar_url,
            content=comment.content,
            likes_count=comment.likes_count,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error liking comment {comment_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to like comment")


@router.delete("/{discussion_id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    discussion_id: int,
    comment_id: int,
    comment_repo: CommentRepository = Depends(get_comment_repo),
    discussion_repo: DiscussionRepository = Depends(get_discussion_repo),
):
    """Delete a comment."""
    try:
        success = await comment_repo.delete(comment_id)
        if not success:
            raise HTTPException(status_code=404, detail="Comment not found")

        # Update discussion reply count
        await discussion_repo.decrement_replies(discussion_id)

        logger.info(f"Comment {comment_id} deleted")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting comment {comment_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete comment")
