import json
import os
from datetime import datetime

def load_data():
    if not os.path.exists('erp_inventory.json') or not os.path.exists('ecommerce_sales.json') or not os.path.exists('compliance_rules.json'):
        raise FileNotFoundError("Mock data files not found. Run mock_data_generator.py first.")
        
    with open('erp_inventory.json', 'r') as f:
        inventory = json.load(f)
    with open('ecommerce_sales.json', 'r') as f:
        sales = json.load(f)
    with open('compliance_rules.json', 'r') as f:
        compliance = json.load(f)
        
    return inventory, sales, compliance

def run_reporting_agent():
    print("Running ShelfGuard AI Reporting Agent...")
    
    inventory, sales, compliance = load_data()
    today = datetime.now().date()
    
    # Create lookup map for sales velocities
    sales_map = {item["sku"]: item for item in sales}
    
    processed_batches = []
    
    total_inventory_cost = 0.0
    total_inventory_qty = 0
    
    expired_qty = 0
    expired_cost = 0.0
    
    compliant_qty = 0
    high_risk_cost = 0.0
    total_waste_cost = 0.0
    
    # Loop over all batches in ERP inventory
    for batch in inventory:
        sku = batch["sku"]
        category = batch["category"]
        qty = batch["stock_quantity"]
        cost = batch["unit_cost"]
        batch_num = batch["batch_number"]
        prod_date_str = batch["production_date"]
        exp_date_str = batch["expiry_date"]
        
        prod_date = datetime.strptime(prod_date_str, "%Y-%m-%d").date()
        exp_date = datetime.strptime(exp_date_str, "%Y-%m-%d").date()
        
        # 1. Basic dates calculations
        total_shelf_life = (exp_date - prod_date).days
        remaining_days = (exp_date - today).days
        
        if total_shelf_life <= 0:
            percent_shelf_life = 0.0
        else:
            percent_shelf_life = max(0.0, float(remaining_days) / total_shelf_life)
            
        total_batch_cost = qty * cost
        total_inventory_cost += total_batch_cost
        total_inventory_qty += qty
        
        # 2. Get Sales Velocity & DoC
        sales_info = sales_map.get(sku, {"avg_daily_sales": 1.0})
        avg_daily_sales = sales_info.get("avg_daily_sales", 1.0)
        doc = qty / avg_daily_sales if avg_daily_sales > 0 else 999.0
        
        # 3. Compliance Check
        rules = compliance.get(category, {"min_days_before_expiry": 0, "min_shelf_life_percent": 0.0})
        min_days = rules["min_days_before_expiry"]
        min_percent = rules["min_shelf_life_percent"]
        
        is_expired = remaining_days <= 0
        
        if is_expired:
            compliance_status = "Expired"
            compliance_details = "Product is past its expiry date."
            expired_qty += qty
            expired_cost += total_batch_cost
        elif remaining_days < min_days:
            compliance_status = "Violation"
            compliance_details = f"Days left ({remaining_days}) is below minimum buffer of {min_days} days."
        elif percent_shelf_life < min_percent:
            compliance_status = "Violation"
            compliance_details = f"Remaining shelf life percentage ({percent_shelf_life:.1%}) is below safety threshold of {min_percent:.1%}"
        else:
            compliance_status = "Compliant"
            compliance_details = "Product meets all shelf life safety buffers."
            compliant_qty += qty
            
        # 4. Waste Risk & Cost Calculation
        # How many units are expected to expire before they can be sold?
        if is_expired:
            waste_qty = qty
            waste_cost = total_batch_cost
        elif doc > remaining_days and remaining_days > 0:
            expected_sales = remaining_days * avg_daily_sales
            waste_qty = max(0, qty - int(expected_sales))
            waste_cost = waste_qty * cost
        else:
            waste_qty = 0
            waste_cost = 0.0
            
        total_waste_cost += waste_cost
        
        # 5. Risk Categorization
        # High Risk: Expired, expiring in <= 15 days, or substantial waste cost
        if is_expired:
            risk_level = "High"
            risk_reason = "Product is already expired"
        elif remaining_days <= 15:
            risk_level = "High"
            risk_reason = f"Critical expiration: only {remaining_days} days left"
        elif waste_cost > (0.2 * total_batch_cost) and waste_qty > 0:
            risk_level = "High"
            risk_reason = f"Overstock Expiry: {waste_qty} units ({waste_qty/qty:.0%}) projected to go to waste"
        elif remaining_days <= 45:
            risk_level = "Medium"
            risk_reason = f"Medium expiration window: {remaining_days} days left"
        elif waste_qty > 0:
            risk_level = "Medium"
            risk_reason = f"Minor overstock expiry: {waste_qty} units projected to go to waste"
        else:
            risk_level = "Low"
            risk_reason = "Fresh stock with adequate sales coverage"
            
        if risk_level == "High":
            high_risk_cost += total_batch_cost
            
        processed_batches.append({
            "sku": sku,
            "product_name": batch["product_name"],
            "category": category,
            "stock_quantity": qty,
            "unit_cost": cost,
            "total_cost": total_batch_cost,
            "batch_number": batch_num,
            "production_date": prod_date_str,
            "expiry_date": exp_date_str,
            "remaining_days": remaining_days,
            "percent_shelf_life": percent_shelf_life,
            "avg_daily_sales": avg_daily_sales,
            "days_of_coverage": doc,
            "compliance_status": compliance_status,
            "compliance_details": compliance_details,
            "waste_qty": waste_qty,
            "waste_cost": waste_cost,
            "risk_level": risk_level,
            "risk_reason": risk_reason
        })
        
    # 6. Aggregated Reports Construction
    
    # Report 1: Daily Expiry Summary
    expiry_summary = {
        "expired": {"count": 0, "quantity": 0, "cost": 0.0},
        "expiring_7d": {"count": 0, "quantity": 0, "cost": 0.0},
        "expiring_30d": {"count": 0, "quantity": 0, "cost": 0.0},
        "expiring_90d": {"count": 0, "quantity": 0, "cost": 0.0}
    }
    
    for b in processed_batches:
        r_days = b["remaining_days"]
        qty = b["stock_quantity"]
        cost = b["total_cost"]
        
        if r_days <= 0:
            expiry_summary["expired"]["count"] += 1
            expiry_summary["expired"]["quantity"] += qty
            expiry_summary["expired"]["cost"] += cost
        
        if 0 < r_days <= 7:
            expiry_summary["expiring_7d"]["count"] += 1
            expiry_summary["expiring_7d"]["quantity"] += qty
            expiry_summary["expiring_7d"]["cost"] += cost
            
        if 0 < r_days <= 30:
            expiry_summary["expiring_30d"]["count"] += 1
            expiry_summary["expiring_30d"]["quantity"] += qty
            expiry_summary["expiring_30d"]["cost"] += cost
            
        if 0 < r_days <= 90:
            expiry_summary["expiring_90d"]["count"] += 1
            expiry_summary["expiring_90d"]["quantity"] += qty
            expiry_summary["expiring_90d"]["cost"] += cost

    # Report 2: Weekly Risk Report (High/Medium/Low summaries)
    risk_summary = {
        "High": {"count": 0, "quantity": 0, "cost": 0.0, "waste_cost": 0.0},
        "Medium": {"count": 0, "quantity": 0, "cost": 0.0, "waste_cost": 0.0},
        "Low": {"count": 0, "quantity": 0, "cost": 0.0, "waste_cost": 0.0}
    }
    
    for b in processed_batches:
        rl = b["risk_level"]
        qty = b["stock_quantity"]
        cost = b["total_cost"]
        wc = b["waste_cost"]
        
        risk_summary[rl]["count"] += 1
        risk_summary[rl]["quantity"] += qty
        risk_summary[rl]["cost"] += cost
        risk_summary[rl]["waste_cost"] += wc
        
    # Report 3: Products Near Expiry (<= 30 days remaining, sorted by remaining days)
    near_expiry = [
        b for b in processed_batches 
        if 0 < b["remaining_days"] <= 30
    ]
    near_expiry.sort(key=lambda x: x["remaining_days"])
    
    # Report 4: Compliance Violations (Expired or Safety Buffer Violations)
    violations = [
        b for b in processed_batches 
        if b["compliance_status"] in ("Expired", "Violation")
    ]
    violations.sort(key=lambda x: (x["compliance_status"], x["remaining_days"]))
    
    # Report 5: Inventory Health Score calculation
    # Formula:
    # 40% Expiry Risk Score: 100 * (1.0 - (high_risk_cost / total_inventory_cost))
    # 40% Compliance Score: 100 * (compliant_qty / total_inventory_qty)
    # 20% Overstock Expiry Risk Balance: 100 * (1.0 - (total_waste_cost / total_inventory_cost))
    if total_inventory_cost > 0:
        expiry_risk_factor = 1.0 - (high_risk_cost / total_inventory_cost)
        waste_cost_factor = 1.0 - (total_waste_cost / total_inventory_cost)
    else:
        expiry_risk_factor = 1.0
        waste_cost_factor = 1.0
        
    if total_inventory_qty > 0:
        compliance_factor = compliant_qty / total_inventory_qty
    else:
        compliance_factor = 1.0
        
    expiry_risk_score = round(100 * expiry_risk_factor, 1)
    compliance_score = round(100 * compliance_factor, 1)
    waste_risk_score = round(100 * waste_cost_factor, 1)
    
    health_score = round((0.4 * expiry_risk_score) + (0.4 * compliance_score) + (0.2 * waste_risk_score), 1)
    
    health_metrics = {
        "overall_score": health_score,
        "expiry_risk_score": expiry_risk_score,
        "compliance_score": compliance_score,
        "waste_risk_score": waste_risk_score,
        "total_inventory_cost": total_inventory_cost,
        "total_inventory_qty": total_inventory_qty,
        "total_waste_cost": total_waste_cost,
        "total_violations_count": len(violations)
    }
    
    # Save the consolidated reports payload
    report_payload = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "health_metrics": health_metrics,
        "expiry_summary": expiry_summary,
        "risk_summary": risk_summary,
        "near_expiry": near_expiry,
        "violations": violations,
        "batches": processed_batches
    }
    
    with open('report_data.json', 'w') as f:
        json.dump(report_payload, f, indent=4)
        
    print(f"Generated report_data.json successfully! Health Score: {health_score}")

if __name__ == "__main__":
    run_reporting_agent()
