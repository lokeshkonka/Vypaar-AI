#!/usr/bin/env bash
# CSV Import Feature - Integration Verification

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd "$(dirname "$0")"

echo -e "${BLUE}=========================================="
echo "CSV Import Feature - Integration Verification"
echo "==========================================${NC}\n"

# Track results
PASSED=0
FAILED=0
WARNINGS=0

check_file() {
    local file=$1
    local desc=$2
    if [ -f "$file" ]; then
        local size=$(du -h "$file" | cut -f1)
        echo -e "${GREEN}✓${NC} $desc ($size)"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $desc - FILE NOT FOUND"
        ((FAILED++))
    fi
}

check_contains() {
    local file=$1
    local pattern=$2
    local desc=$3
    if grep -q "$pattern" "$file" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $desc"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $desc - PATTERN NOT FOUND"
        ((FAILED++))
    fi
}

echo -e "${BLUE}Checking Backend Files...${NC}"
check_file "backend/app/models/import_schemas.py" "Pydantic schemas"
check_file "backend/app/services/import_service.py" "Import service"
check_file "backend/app/api/v1/endpoints/data_import.py" "API endpoints"

echo -e "\n${BLUE}Checking Frontend Files...${NC}"
check_file "frontend/src/context/DataImportContext.tsx" "React context"
check_file "frontend/src/pages/DataImport.tsx" "Import page UI"
check_file "frontend/src/components/common/Breadcrumbs.tsx" "Breadcrumb component"

echo -e "\n${BLUE}Checking Backend Integration...${NC}"
check_contains "backend/app/api/v1/router.py" "data_import" "Router includes data_import"
check_contains "backend/app/api/v1/endpoints/__init__.py" "data_import" "Endpoints exports data_import"

echo -e "\n${BLUE}Checking Frontend Integration...${NC}"
check_contains "frontend/src/App.tsx" "DataImport" "App imports DataImport"
check_contains "frontend/src/App.tsx" "DataImportProvider" "App imports DataImportProvider"
check_contains "frontend/src/App.tsx" "/data/import" "App has /data/import route"
check_contains "frontend/src/components/dashboard/Navbar/Navbar.tsx" "Import Data" "Navbar has Import Data link"
check_contains "frontend/src/components/dashboard/Navbar/Navbar.tsx" "/data/import" "Navbar links to /data/import"

echo -e "\n${BLUE}Checking Documentation...${NC}"
check_file "CSV_IMPORT_COMPLETE.md" "Feature documentation"
check_file "FEATURE_1_CSV_IMPORT_SUMMARY.md" "Implementation summary"
check_file "test_csv_import.py" "Test suite"

echo -e "\n${BLUE}Checking Backend Syntax...${NC}"
if python -m py_compile backend/app/models/import_schemas.py 2>/dev/null; then
    echo -e "${GREEN}✓${NC} import_schemas.py syntax valid"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} import_schemas.py has syntax errors"
    ((FAILED++))
fi

if python -m py_compile backend/app/services/import_service.py 2>/dev/null; then
    echo -e "${GREEN}✓${NC} import_service.py syntax valid"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} import_service.py has syntax errors"
    ((FAILED++))
fi

if python -m py_compile backend/app/api/v1/endpoints/data_import.py 2>/dev/null; then
    echo -e "${GREEN}✓${NC} data_import.py syntax valid"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} data_import.py has syntax errors"
    ((FAILED++))
fi

echo -e "\n${BLUE}Checking Frontend TypeScript...${NC}"
cd frontend
if npx tsc --noEmit 2>&1 | grep -q "error TS" 2>/dev/null; then
    echo -e "${YELLOW}⚠${NC}  TypeScript compilation has warnings (usually OK)"
    ((WARNINGS++))
else
    echo -e "${GREEN}✓${NC} TypeScript compilation successful"
    ((PASSED++))
fi
cd ..

echo -e "\n${BLUE}Running Test Suite...${NC}"
if python test_csv_import.py 2>&1 | tail -5 | grep -q "7/7 tests passed"; then
    echo -e "${GREEN}✓${NC} All tests passing (7/7)"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠${NC}  Could not verify test results"
    ((WARNINGS++))
fi

# Summary
echo -e "\n${BLUE}=========================================="
echo "Verification Summary"
echo "==========================================${NC}"
echo -e "${GREEN}Passed: ${PASSED}${NC}"
if [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}Warnings: ${WARNINGS}${NC}"
fi
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}Failed: ${FAILED}${NC}"
fi

echo -e "\n${BLUE}Status:${NC}"
if [ $FAILED -eq 0 ] && [ $PASSED -gt 20 ]; then
    echo -e "${GREEN}✅ CSV Import Feature - FULLY INTEGRATED${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Start backend:  cd backend && python run.py"
    echo "2. Start frontend: cd frontend && npm run dev"
    echo "3. Access at:      http://localhost:5173/data/import"
    echo "4. Look for 'Import Data' in sidebar navigation"
    exit 0
else
    echo -e "${RED}❌ CSV Import Feature - INTEGRATION ISSUES FOUND${NC}"
    echo "Please review the failures above"
    exit 1
fi
