#!/bin/bash
# Feature #2: User Settings & Profile - Integration Validation Script
# This script validates that all components are properly integrated

echo "================================"
echo "Feature #2: Integration Validation"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counter
CHECKS=0
PASSED=0

# Test function
test_file() {
    CHECKS=$((CHECKS + 1))
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} File exists: $1"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}✗${NC} File missing: $1"
    fi
}

test_content() {
    CHECKS=$((CHECKS + 1))
    if grep -q "$2" "$1"; then
        echo -e "${GREEN}✓${NC} Found in $1: $2"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}✗${NC} Not found in $1: $2"
    fi
}

echo "Backend Files:"
test_file "backend/app/models/user_schemas.py"
test_file "backend/app/services/user_settings_service.py"
test_file "backend/app/api/v1/endpoints/user_settings.py"

echo ""
echo "Frontend Files:"
test_file "frontend/src/context/UserSettingsContext.tsx"
test_file "frontend/src/pages/UserSettings.tsx"

echo ""
echo "Backend Integration:"
test_content "backend/app/api/v1/endpoints/__init__.py" "user_settings"
test_content "backend/app/api/v1/router.py" "user_settings.router"

echo ""
echo "Frontend Integration:"
test_content "frontend/src/App.tsx" "import UserSettings from"
test_content "frontend/src/App.tsx" "import { UserSettingsProvider }"
test_content "frontend/src/App.tsx" "path=\"/dashboard/settings\""
test_content "frontend/src/App.tsx" "UserSettingsProvider"
test_content "frontend/src/components/dashboard/Navbar/Navbar.tsx" "FiSettings"
test_content "frontend/src/components/dashboard/Navbar/Navbar.tsx" "Settings"
test_content "frontend/src/components/dashboard/Navbar/Navbar.tsx" "/dashboard/settings"

echo ""
echo "================================"
echo "Integration Validation Results"
echo "================================"
echo "Checks Passed: $PASSED / $CHECKS"

if [ $PASSED -eq $CHECKS ]; then
    echo -e "${GREEN}✓ All integration checks passed!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠ Some checks failed. Review above.${NC}"
    exit 1
fi
