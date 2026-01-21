from fastapi import Header, HTTPException
from jose import jwt
import requests
from app.config.settings import settings

JWKS_URL = f"{settings.CLERK_ISSUER}/.well-known/jwks.json"
JWKS = requests.get(JWKS_URL).json()

def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    token = authorization.split(" ")[1]

    try:
        payload = jwt.decode(
            token,
            JWKS,
            algorithms=["RS256"],
            issuer=settings.CLERK_ISSUER,
            options={"verify_aud": False},
        )
        return payload["sub"]  # clerk_user_id
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
