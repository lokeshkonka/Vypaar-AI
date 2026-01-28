#!/usr/bin/env python
"""Quick test of all commodities across endpoints."""

import asyncio
import json
import httpx
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000/api/v1"

async def test_all_endpoints():
    """Test major endpoints with all commodities."""
    
    async with httpx.AsyncClient(timeout=30) as client:
        results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {}
        }
        
        # Test 1: Health Check
        print("\n1️⃣ Health Check...")
        try:
            resp = await client.get(f"{BASE_URL}/health")
            results["tests"]["health"] = {
                "status": "✅ PASS" if resp.status_code == 200 else "❌ FAIL",
                "code": resp.status_code
            }
            print(f"   ✅ Health: {resp.status_code}")
        except Exception as e:
            results["tests"]["health"] = {"status": "❌ FAIL", "error": str(e)}
            print(f"   ❌ Health: {e}")
        
        # Test 2: Get Commodities
        print("\n2️⃣ Get All Commodities...")
        try:
            resp = await client.get(f"{BASE_URL}/market-data/commodities")
            commodities = resp.json()
            count = len(commodities) if isinstance(commodities, list) else len(commodities.get("items", []))
            results["tests"]["commodities_list"] = {
                "status": "✅ PASS" if resp.status_code == 200 else "❌ FAIL",
                "code": resp.status_code,
                "count": count
            }
            print(f"   ✅ Found {count} commodities")
        except Exception as e:
            results["tests"]["commodities_list"] = {"status": "❌ FAIL", "error": str(e)}
            print(f"   ❌ Error: {e}")
        
        # Test 3: Get Markets
        print("\n3️⃣ Get All Markets...")
        try:
            resp = await client.get(f"{BASE_URL}/market-data/markets")
            markets = resp.json()
            count = len(markets) if isinstance(markets, list) else len(markets.get("items", []))
            results["tests"]["markets_list"] = {
                "status": "✅ PASS" if resp.status_code == 200 else "❌ FAIL",
                "code": resp.status_code,
                "count": count
            }
            print(f"   ✅ Found {count} markets")
        except Exception as e:
            results["tests"]["markets_list"] = {"status": "❌ FAIL", "error": str(e)}
            print(f"   ❌ Error: {e}")
        
        # Test 4: Get Prices
        print("\n4️⃣ Get Market Prices...")
        try:
            resp = await client.get(f"{BASE_URL}/market-data/prices?limit=10")
            prices = resp.json()
            count = len(prices) if isinstance(prices, list) else len(prices.get("items", []))
            results["tests"]["prices_list"] = {
                "status": "✅ PASS" if resp.status_code == 200 else "❌ FAIL",
                "code": resp.status_code,
                "count": count
            }
            print(f"   ✅ Found {count} price records")
        except Exception as e:
            results["tests"]["prices_list"] = {"status": "❌ FAIL", "error": str(e)}
            print(f"   ❌ Error: {e}")
        
        # Test 5: Single Prediction
        print("\n5️⃣ Single Commodity Prediction (Wheat at Azadpur)...")
        try:
            resp = await client.post(
                f"{BASE_URL}/predict/",
                json={
                    "commodity_id": 1,
                    "market_id": 1,
                    "prediction_date": "2026-01-26"
                }
            )
            results["tests"]["single_prediction"] = {
                "status": "✅ PASS" if resp.status_code == 200 else "❌ FAIL",
                "code": resp.status_code
            }
            if resp.status_code == 200:
                pred_data = resp.json()
                price = pred_data.get("predicted_price", "N/A")
                confidence = pred_data.get("model_confidence", "N/A")
                print(f"   ✅ Predicted price: ₹{price} (Confidence: {confidence})")
            else:
                error_detail = resp.json().get("detail", "Unknown error")
                print(f"   ❌ Status: {resp.status_code} - {error_detail}")
        except Exception as e:
            results["tests"]["single_prediction"] = {"status": "❌ FAIL", "error": str(e)}
            print(f"   ❌ Error: {e}")
        
        # Test 6: Batch Predictions (Multiple Commodities)
        print("\n6️⃣ Batch Predictions (Wheat, Rice, Potato)...")
        try:
            resp = await client.post(
                f"{BASE_URL}/predict/batch",
                json={
                    "predictions": [
                        {"commodity_id": 1, "market_id": 1, "prediction_date": "2026-01-26"},
                        {"commodity_id": 2, "market_id": 1, "prediction_date": "2026-01-26"},
                        {"commodity_id": 3, "market_id": 1, "prediction_date": "2026-01-26"}
                    ]
                }
            )
            predictions = resp.json()
            count = len(predictions) if isinstance(predictions, list) else len(predictions.get("predictions", []))
            results["tests"]["batch_predictions"] = {
                "status": "✅ PASS" if resp.status_code == 200 else "❌ FAIL",
                "code": resp.status_code,
                "count": count
            }
            print(f"   ✅ Got {count} batch predictions")
        except Exception as e:
            results["tests"]["batch_predictions"] = {"status": "❌ FAIL", "error": str(e)}
            print(f"   ❌ Error: {e}")
        
        # Test 7: Prediction History
        print("\n7️⃣ Prediction History...")
        try:
            resp = await client.get(f"{BASE_URL}/predict/history/1/1")
            history = resp.json()
            count = len(history) if isinstance(history, list) else len(history.get("history", []))
            results["tests"]["prediction_history"] = {
                "status": "✅ PASS" if resp.status_code == 200 else "❌ FAIL",
                "code": resp.status_code,
                "count": count
            }
            print(f"   ✅ Found {count} history records")
        except Exception as e:
            results["tests"]["prediction_history"] = {"status": "❌ FAIL", "error": str(e)}
            print(f"   ❌ Error: {e}")
        
        # Test 8: Model Metrics
        print("\n8️⃣ Model Metrics...")
        try:
            resp = await client.get(f"{BASE_URL}/model/metrics")
            metrics = resp.json()
            results["tests"]["model_metrics"] = {
                "status": "✅ PASS" if resp.status_code == 200 else "❌ FAIL",
                "code": resp.status_code
            }
            if resp.status_code == 200:
                r2 = metrics.get("r2_score", "N/A")
                rmse = metrics.get("rmse", "N/A")
                print(f"   ✅ R² Score: {r2}, RMSE: {rmse}")
            else:
                print(f"   ❌ Status: {resp.status_code}")
        except Exception as e:
            results["tests"]["model_metrics"] = {"status": "❌ FAIL", "error": str(e)}
            print(f"   ❌ Error: {e}")
        
        # Test 9: Inventory List
        print("\n9️⃣ Inventory List...")
        try:
            resp = await client.get(f"{BASE_URL}/inventory/")
            inventory = resp.json()
            count = len(inventory) if isinstance(inventory, list) else len(inventory.get("items", []))
            results["tests"]["inventory_list"] = {
                "status": "✅ PASS" if resp.status_code == 200 else "❌ FAIL",
                "code": resp.status_code,
                "count": count
            }
            print(f"   ✅ Found {count} inventory records")
        except Exception as e:
            results["tests"]["inventory_list"] = {"status": "❌ FAIL", "error": str(e)}
            print(f"   ❌ Error: {e}")
        
        # Test 10: Alerts List
        print("\n🔟 Alerts List...")
        try:
            resp = await client.get(f"{BASE_URL}/alerts/")
            alerts = resp.json()
            count = len(alerts) if isinstance(alerts, list) else len(alerts.get("items", []))
            results["tests"]["alerts_list"] = {
                "status": "✅ PASS" if resp.status_code == 200 else "❌ FAIL",
                "code": resp.status_code,
                "count": count
            }
            print(f"   ✅ Found {count} alerts")
        except Exception as e:
            results["tests"]["alerts_list"] = {"status": "❌ FAIL", "error": str(e)}
            print(f"   ❌ Error: {e}")
        
        # Summary
        passed = sum(1 for t in results["tests"].values() if "✅" in t.get("status", ""))
        total = len(results["tests"])
        
        print("\n" + "="*50)
        print(f"SUMMARY: {passed}/{total} tests passed")
        print("="*50)
        
        for test_name, test_result in results["tests"].items():
            status = test_result.get("status", "UNKNOWN")
            print(f"{status} - {test_name}")
        
        return results

if __name__ == "__main__":
    print("🚀 Starting AgriTech API Commodity Testing...")
    print(f"📍 API: {BASE_URL}\n")
    
    results = asyncio.run(test_all_endpoints())
    
    with open("/tmp/commodity_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\n✅ Results saved to /tmp/commodity_test_results.json")
