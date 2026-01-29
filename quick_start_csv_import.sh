#!/usr/bin/env bash
# Quick Start Guide for CSV Import Feature

set -e

echo "=========================================="
echo "CSV Import Feature - Quick Start"
echo "=========================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "\n${BLUE}Step 1: Running verification tests...${NC}"
cd "$(dirname "$0")"
python test_csv_import.py

echo -e "\n${BLUE}Step 2: Building frontend...${NC}"
cd frontend
npm run build > /dev/null 2>&1
echo -e "${GREEN}✓ Frontend build successful${NC}"

echo -e "\n${BLUE}Step 3: Checking backend syntax...${NC}"
cd ../backend
python -m py_compile app/models/import_schemas.py
python -m py_compile app/services/import_service.py
python -m py_compile app/api/v1/endpoints/data_import.py
echo -e "${GREEN}✓ Backend syntax check passed${NC}"

echo -e "\n${YELLOW}Step 4: Starting services (optional)...${NC}"
echo "To start the backend, run:"
echo "  cd backend && python run.py"
echo ""
echo "To start the frontend, run:"
echo "  cd frontend && npm run dev"
echo ""

echo -e "\n${GREEN}=========================================="
echo "✓ CSV Import feature is ready!"
echo "==========================================${NC}"
echo ""
echo "Access the feature at: http://localhost:5173/data/import"
echo "Look for 'Import Data' in the sidebar navigation"
echo ""
echo "Test with sample CSV files:"
echo "- Sales data: date, market_name, commodity_name, price, quantity"
echo "- Market prices: date, market_name, commodity_name, price"
echo "- Inventory: date, market_name, commodity_name, quantity_available"
echo ""
