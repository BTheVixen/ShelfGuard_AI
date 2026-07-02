import json
import os
from datetime import datetime, timedelta
import random

def generate_mock_data():
    # Set seed for reproducibility
    random.seed(42)
    
    today = datetime.now().date()
    
    # 1. Define compliance configurations by category
    compliance_rules = {
        "Dairy": {
            "min_days_before_expiry": 7,
            "min_shelf_life_percent": 0.15,
            "required_temp_range": "2°C - 4°C"
        },
        "Produce": {
            "min_days_before_expiry": 3,
            "min_shelf_life_percent": 0.10,
            "required_temp_range": "8°C - 12°C"
        },
        "Bakery": {
            "min_days_before_expiry": 2,
            "min_shelf_life_percent": 0.20,
            "required_temp_range": "Ambient"
        },
        "Pharmacy": {
            "min_days_before_expiry": 30,
            "min_shelf_life_percent": 0.25,
            "required_temp_range": "15°C - 25°C"
        },
        "Meat": {
            "min_days_before_expiry": 4,
            "min_shelf_life_percent": 0.15,
            "required_temp_range": "0°C - 2°C"
        }
    }
    
    # Write compliance rules
    with open('compliance_rules.json', 'w') as f:
        json.dump(compliance_rules, f, indent=4)
    print("Generated compliance_rules.json")

    # 2. Product definitions to generate realistic inventory
    product_catalog = [
        # Dairy
        {"sku": "DAI-001", "name": "Organic Whole Milk 1L", "category": "Dairy", "unit_cost": 2.50, "total_shelf_life_days": 14},
        {"sku": "DAI-002", "name": "Greek Yogurt Plain 500g", "category": "Dairy", "unit_cost": 3.80, "total_shelf_life_days": 21},
        {"sku": "DAI-003", "name": "Cheddar Cheese Block 250g", "category": "Dairy", "unit_cost": 4.20, "total_shelf_life_days": 60},
        {"sku": "DAI-004", "name": "Salted Butter 250g", "category": "Dairy", "unit_cost": 3.00, "total_shelf_life_days": 90},
        
        # Produce
        {"sku": "PRD-001", "name": "Baby Spinach Salad Bag 200g", "category": "Produce", "unit_cost": 1.90, "total_shelf_life_days": 7},
        {"sku": "PRD-002", "name": "Organic Strawberries 400g", "category": "Produce", "unit_cost": 4.50, "total_shelf_life_days": 6},
        {"sku": "PRD-003", "name": "Yellow Bananas 1kg", "category": "Produce", "unit_cost": 1.80, "total_shelf_life_days": 8},
        
        # Bakery
        {"sku": "BAK-001", "name": "Sourdough Bread Loaf 500g", "category": "Bakery", "unit_cost": 3.20, "total_shelf_life_days": 4},
        {"sku": "BAK-002", "name": "Butter Croissants (4 Pack)", "category": "Bakery", "unit_cost": 3.50, "total_shelf_life_days": 3},
        {"sku": "BAK-003", "name": "Chocolate Chip Muffins", "category": "Bakery", "unit_cost": 2.80, "total_shelf_life_days": 5},
        
        # Pharmacy
        {"sku": "PHA-001", "name": "Daily Multivitamin Tabs 90s", "category": "Pharmacy", "unit_cost": 12.50, "total_shelf_life_days": 365},
        {"sku": "PHA-002", "name": "Allergy Relief Tablets 30s", "category": "Pharmacy", "unit_cost": 8.90, "total_shelf_life_days": 730},
        {"sku": "PHA-003", "name": "Children's Cough Syrup 150ml", "category": "Pharmacy", "unit_cost": 6.50, "total_shelf_life_days": 540},
        
        # Meat
        {"sku": "MET-001", "name": "Premium Beef Minced 500g", "category": "Meat", "unit_cost": 6.90, "total_shelf_life_days": 5},
        {"sku": "MET-002", "name": "Free Range Chicken Breast 600g", "category": "Meat", "unit_cost": 8.50, "total_shelf_life_days": 6},
        {"sku": "MET-003", "name": "Pork Chops 400g", "category": "Meat", "unit_cost": 5.80, "total_shelf_life_days": 7}
    ]

    erp_inventory = []
    ecommerce_sales = []
    
    # Seed specific statuses relative to today for dynamic reports
    # Batch offsets dictate when the product expires relative to today
    inventory_batches = [
        # (sku, qty, batch_number, age_days_offset_from_expiry)
        # Category: Dairy
        ("DAI-001", 120, "B-DAI01-A", -2),  # Expired 2 days ago
        ("DAI-001", 350, "B-DAI01-B", 3),   # Expires in 3 days (Near Expiry, Compliance Violation)
        ("DAI-001", 600, "B-DAI01-C", 11),  # Expires in 11 days (Fresh)
        ("DAI-002", 90, "B-DAI02-A", 1),    # Expires tomorrow (Critical Expiry, Compliance Violation)
        ("DAI-002", 240, "B-DAI02-B", 14),  # Expires in 14 days (Ok)
        ("DAI-003", 50, "B-DAI03-A", 5),    # Expires in 5 days (Near Expiry, Compliance Violation)
        ("DAI-003", 300, "B-DAI03-B", 45),  # Expires in 45 days (Fresh)
        ("DAI-004", 400, "B-DAI04-A", 65),  # Expires in 65 days (Fresh)
        
        # Category: Produce
        ("PRD-001", 80, "B-PRD01-A", -1),   # Expired yesterday
        ("PRD-001", 150, "B-PRD01-B", 2),   # Expires in 2 days (Near Expiry, Compliance Violation)
        ("PRD-001", 300, "B-PRD01-C", 5),   # Expires in 5 days (Fresh)
        ("PRD-002", 200, "B-PRD02-A", 1),   # Expires in 1 day (Critical, Violation)
        ("PRD-002", 150, "B-PRD02-B", 4),   # Expires in 4 days (Fresh)
        ("PRD-003", 500, "B-PRD03-A", 2),   # Expires in 2 days (Near Expiry, Violation)
        ("PRD-003", 800, "B-PRD03-B", 7),   # Expires in 7 days (Fresh)
        
        # Category: Bakery
        ("BAK-001", 45, "B-BAK01-A", -1),   # Expired yesterday
        ("BAK-001", 120, "B-BAK01-B", 1),   # Expires tomorrow (Critical, Violation)
        ("BAK-001", 200, "B-BAK01-C", 3),   # Expires in 3 days (Fresh)
        ("BAK-002", 110, "B-BAK02-A", 1),   # Expires tomorrow (Critical, Violation)
        ("BAK-003", 90, "B-BAK03-A", 2),    # Expires in 2 days (Near Expiry, Violation)
        ("BAK-003", 180, "B-BAK03-B", 4),   # Expires in 4 days (Fresh)
        
        # Category: Pharmacy
        ("PHA-001", 60, "B-PHA01-A", -15),  # Expired 15 days ago
        ("PHA-001", 120, "B-PHA01-B", 20),  # Expires in 20 days (Compliance Violation for pharmacy)
        ("PHA-001", 450, "B-PHA01-C", 180), # Expires in 180 days (Fresh)
        ("PHA-002", 300, "B-PHA02-A", 250), # Fresh
        ("PHA-003", 80, "B-PHA03-A", 15),   # Expires in 15 days (Compliance Violation for pharmacy)
        ("PHA-003", 200, "B-PHA03-B", 240), # Fresh
        
        # Category: Meat
        ("MET-001", 30, "B-MET01-A", -2),   # Expired 2 days ago
        ("MET-001", 140, "B-MET01-B", 2),   # Expires in 2 days (Near Expiry, Violation)
        ("MET-001", 220, "B-MET01-C", 4),   # Expires in 4 days (Fresh)
        ("MET-002", 95, "B-MET02-A", 1),    # Expires in 1 day (Critical, Violation)
        ("MET-002", 210, "B-MET02-B", 5),   # Fresh
        ("MET-003", 160, "B-MET03-A", 3),   # Expires in 3 days (Near Expiry, Violation)
        ("MET-003", 240, "B-MET03-B", 6)    # Fresh
    ]
    
    # We will compute production and expiry dates based on these relative offsets
    for sku, qty, batch_num, days_offset in inventory_batches:
        prod_info = next(item for item in product_catalog if item["sku"] == sku)
        
        expiry_date = today + timedelta(days=days_offset)
        production_date = expiry_date - timedelta(days=prod_info["total_shelf_life_days"])
        
        erp_inventory.append({
            "sku": sku,
            "product_name": prod_info["name"],
            "category": prod_info["category"],
            "stock_quantity": qty,
            "unit_cost": prod_info["unit_cost"],
            "batch_number": batch_num,
            "production_date": production_date.strftime("%Y-%m-%d"),
            "expiry_date": expiry_date.strftime("%Y-%m-%d")
        })

    # 3. Generate Sales Velocity Data
    # We want to create scenarios where:
    # - Some short-dated items have SLOW sales (high waste risk!)
    # - Some short-dated items have FAST sales (low waste risk)
    # Average daily sales by SKU
    sales_velocities = {
        "DAI-001": {"avg_daily_sales": 120.0, "growth_rate": 0.05},  # Fast selling (350 qty will sell in ~3 days!)
        "DAI-002": {"avg_daily_sales": 25.0,  "growth_rate": 0.02},  # Moderate (90 qty will sell in ~3.6 days, risk since expires in 1 day!)
        "DAI-003": {"avg_daily_sales": 5.0,   "growth_rate": -0.01}, # Very slow (50 qty will take 10 days to sell, expires in 5 days! 25 units waste risk!)
        "DAI-004": {"avg_daily_sales": 15.0,  "growth_rate": 0.01},  # Normal
        "PRD-001": {"avg_daily_sales": 85.0,  "growth_rate": 0.08},  # Fast
        "PRD-002": {"avg_daily_sales": 120.0, "growth_rate": 0.04},  # Very Fast (200 qty expires in 1 day, daily sales is 120. Risk of wasting ~80 units!)
        "PRD-003": {"avg_daily_sales": 150.0, "growth_rate": 0.02},  # Fast (500 qty expires in 2 days, daily sales is 150. Will waste ~200 units!)
        "BAK-001": {"avg_daily_sales": 65.0,  "growth_rate": 0.03},  # Fast
        "BAK-002": {"avg_daily_sales": 80.0,  "growth_rate": 0.02},  # Fast (110 qty expires tomorrow, sales is 80. Risk of wasting ~30 units!)
        "BAK-003": {"avg_daily_sales": 40.0,  "growth_rate": 0.01},  # Moderate
        "PHA-001": {"avg_daily_sales": 2.5,   "growth_rate": 0.00},  # Very slow (120 qty expires in 20 days, sales is 2.5. Will sell 50 units, 70 units waste!)
        "PHA-002": {"avg_daily_sales": 1.8,   "growth_rate": 0.01},  # Slow
        "PHA-003": {"avg_daily_sales": 3.0,   "growth_rate": -0.02}, # Slow (80 qty expires in 15 days, sales is 3.0. Will sell 45 units, 35 units waste!)
        "MET-001": {"avg_daily_sales": 85.0,  "growth_rate": 0.05},  # Fast (140 qty expires in 2 days, sales is 85. Will sell all 140 before expiry since 2 * 85 = 170!)
        "MET-002": {"avg_daily_sales": 60.0,  "growth_rate": 0.02},  # Moderate (95 qty expires in 1 day, sales is 60. Will waste ~35 units!)
        "MET-003": {"avg_daily_sales": 45.0,  "growth_rate": 0.01}   # Moderate
    }
    
    for sku, data in sales_velocities.items():
        prod_info = next(item for item in product_catalog if item["sku"] == sku)
        
        # Calculate recent volume (last 7 days)
        last_7_days_sales = round(data["avg_daily_sales"] * 7 * random.uniform(0.9, 1.1))
        
        ecommerce_sales.append({
            "sku": sku,
            "product_name": prod_info["name"],
            "avg_daily_sales": data["avg_daily_sales"],
            "growth_rate": data["growth_rate"],
            "last_7_days_sales_volume": last_7_days_sales
        })

    # Write ERP Inventory
    with open('erp_inventory.json', 'w') as f:
        json.dump(erp_inventory, f, indent=4)
    print("Generated erp_inventory.json")

    # Write Ecommerce Sales
    with open('ecommerce_sales.json', 'w') as f:
        json.dump(ecommerce_sales, f, indent=4)
    print("Generated ecommerce_sales.json")

if __name__ == "__main__":
    generate_mock_data()
