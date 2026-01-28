#!/bin/bash
# Integration Test Script
# Tests all backend API endpoints

echo "🧪 Vypaar-AI Backend API Integration Tests"
echo "=========================================="
echo ""

BACKEND_URL="http://localhost:8000"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

test_endpoint() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    
    echo -n "Testing $name... "
    
    if [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "$BACKEND_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    else
        response=$(curl -s -w "\n%{http_code}" "$BACKEND_URL$endpoint")
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
        echo -e "${GREEN}✓ PASSED${NC} (HTTP $http_code)"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC} (HTTP $http_code)"
        echo "Response: $body"
        ((FAILED++))
        return 1
    fi
}

echo "1. Backend Health Check"
echo "----------------------"
test_endpoint "Health Endpoint" "GET" "/api/v1/health"
echo ""

echo "2. Frontend API Endpoints"
echo "------------------------"
test_endpoint "AI Insights" "GET" "/api/ai/insights"
test_endpoint "Model Accuracy" "GET" "/api/model/accuracy"
test_endpoint "Product Analysis" "GET" "/api/product-analysis"
test_endpoint "Inventory Dashboard" "GET" "/api/inventory/dashboard"
echo ""

echo "3. Forecast API (POST)"
echo "---------------------"
test_endpoint "Forecast Generation" "POST" "/api/forecast" \
    '{"state":"Maharashtra","city":"Mumbai","market":"Vashi","category":"Vegetables","product":"Tomato","forecastRange":7}'
echo ""

echo "=========================================="
echo "📊 Test Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}Failed: $FAILED${NC}"
else
    echo "Failed: 0"
fi
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi
