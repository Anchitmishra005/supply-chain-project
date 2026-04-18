"""
=============================================================================
 Supply Chain Data Generator
=============================================================================
 Generates realistic synthetic datasets for the supply chain pipeline:
   - suppliers.csv   (200 rows)
   - inventory.csv   (1 000 rows)
   - orders.csv      (1 500 rows)
   - shipments.csv   (1 500 rows)

 Each file is written to the  data/  directory alongside this script.
=============================================================================
"""

import os
import random
import csv
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
NUM_SUPPLIERS   = 200
NUM_INVENTORY   = 1000
NUM_ORDERS      = 1500
NUM_SHIPMENTS   = 1500

SEED = 42
random.seed(SEED)

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Helper Data
# ---------------------------------------------------------------------------
PRODUCT_NAMES = [
    "Apple iPhone 15", "Samsung Galaxy S24", "Sony PlayStation 5", "Nintendo Switch OLED", "Dell XPS 15",
    "MacBook Pro 14", "Apple Watch Series 9", "Samsung Odyssey G9", "Logitech MX Master 3S", "Keychron Q1 Pro",
    "NVIDIA RTX 4090", "AMD Ryzen 9 7950X", "Sony WH-1000XM5", "AirPods Pro Gen 2", "iPad Pro 12.9",
    "Google Pixel 8 Pro", "Xbox Series X", "LG C3 OLED TV", "Echo Dot 5th Gen", "Kindle Paperwhite",
    "DJI Mini 4 Pro", "GoPro HERO12 Black", "Bose QuietComfort Ultra", "Asus ROG Zephyrus G14", "Razer DeathAdder V3",
    "Corsair RM850x PSU", "Samsung 990 PRO NVMe", "NZXT Kraken Elite", "Elgato Stream Deck", "Secretlab Titan EVO"
]

PRODUCT_CATEGORIES = [
    "Electronics", "Mechanical", "Electrical", "Sensors", "Assemblies",
    "Raw Materials", "Packaging", "Safety Equipment"
]

CITIES = [
    "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai",
    "Kolkata", "Pune", "Ahmedabad", "Surat", "Jaipur",
    "Shenzhen", "Guangzhou", "Taipei", "Seoul", "Hanoi"
]

COUNTRIES = {
    "Mumbai": "India", "Delhi": "India", "Bangalore": "India",
    "Hyderabad": "India", "Chennai": "India", "Kolkata": "India",
    "Pune": "India", "Ahmedabad": "India", "Surat": "India",
    "Jaipur": "India", "Shenzhen": "China", "Guangzhou": "China",
    "Taipei": "Taiwan", "Seoul": "South Korea", "Hanoi": "Vietnam"
}

COMPANY_PREFIXES = [
    "Tata", "Reliance", "Mahindra", "Adani", "Bajaj",
    "Apex", "Elite", "Alpha", "Omega", "Delta",
    "Nexus", "Quantum", "Stellar", "Pioneer", "Vanguard"
]

COMPANY_SUFFIXES = [
    "Industries", "Pvt Ltd", "Corp", "Manufacturing", "Solutions",
    "Enterprises", "Group", "International", "Partners", "Trading"
]

WAREHOUSE_NAMES = [
    "WH-EAST-01", "WH-EAST-02", "WH-WEST-01", "WH-WEST-02",
    "WH-CENTRAL-01", "WH-CENTRAL-02", "WH-SOUTH-01", "WH-NORTH-01",
    "WH-INTL-01", "WH-INTL-02"
]

DELIVERY_STATUSES = ["Delivered", "In Transit", "Pending", "Delayed", "Cancelled"]
PAYMENT_METHODS   = ["Credit Card", "Wire Transfer", "Purchase Order", "Net 30", "Cash on Delivery"]

# ---------------------------------------------------------------------------
# Date Helpers
# ---------------------------------------------------------------------------
START_DATE = datetime(2024, 1, 1)
END_DATE   = datetime(2025, 12, 31)

def random_date(start: datetime = START_DATE, end: datetime = END_DATE) -> str:
    """Return a random date string between start and end (inclusive)."""
    delta = (end - start).days
    return (start + timedelta(days=random.randint(0, delta))).strftime("%Y-%m-%d")

def random_datetime(start: datetime = START_DATE, end: datetime = END_DATE) -> str:
    """Return a random datetime string between start and end."""
    delta = int((end - start).total_seconds())
    return (start + timedelta(seconds=random.randint(0, delta))).strftime("%Y-%m-%d %H:%M:%S")

# ---------------------------------------------------------------------------
# 1. Suppliers
# ---------------------------------------------------------------------------
def generate_suppliers(n: int = NUM_SUPPLIERS) -> list[dict]:
    """Generate supplier records."""
    rows = []
    used_names = set()
    for i in range(1, n + 1):
        # Unique company name (with numeric fallback when combos are exhausted)
        attempts = 0
        while True:
            base = f"{random.choice(COMPANY_PREFIXES)} {random.choice(COMPANY_SUFFIXES)}"
            name = base if attempts < 200 else f"{base} {i}"
            attempts += 1
            if name not in used_names:
                used_names.add(name)
                break

        city = random.choice(CITIES)
        rows.append({
            "supplier_id":    f"SUP-{i:04d}",
            "supplier_name":  name,
            "contact_email":  f"contact@{name.lower().replace(' ', '')}.com",
            "phone":          f"+91-{random.randint(60000,99999)}{random.randint(10000,99999)}",
            "city":           city,
            "country":        COUNTRIES[city],
            "rating":         round(random.uniform(1.0, 5.0), 1),
            "lead_time_days": random.randint(1, 30),
            "active":         random.choice([1, 1, 1, 1, 0]),  # 80 % active
        })
    return rows


# ---------------------------------------------------------------------------
# 2. Inventory
# ---------------------------------------------------------------------------
def generate_inventory(n: int = NUM_INVENTORY, suppliers: list[dict] = None) -> list[dict]:
    """Generate inventory records across warehouses."""
    rows = []
    supplier_ids = [s["supplier_id"] for s in suppliers] if suppliers else [f"SUP-{i:04d}" for i in range(1, NUM_SUPPLIERS + 1)]

    for i in range(1, n + 1):
        product     = random.choice(PRODUCT_NAMES)
        quantity    = random.randint(0, 5000)
        reorder_pt  = random.randint(50, 500)
        rows.append({
            "inventory_id":      f"INV-{i:05d}",
            "product_id":        product,
            "product_name":      product,
            "category":          random.choice(PRODUCT_CATEGORIES),
            "warehouse_id":      random.choice(WAREHOUSE_NAMES),
            "supplier_id":       random.choice(supplier_ids),
            "quantity_on_hand":  quantity,
            "reorder_point":     reorder_pt,
            "unit_price":        round(random.uniform(5.0, 500.0), 2),
            "last_restock_date": random_date(),
            "stock_status":      "Low Stock" if quantity < reorder_pt else "In Stock",
        })
    return rows


# ---------------------------------------------------------------------------
# 3. Orders
# ---------------------------------------------------------------------------
def generate_orders(n: int = NUM_ORDERS, inventory: list[dict] = None) -> list[dict]:
    """Generate customer order records."""
    rows = []
    product_ids = list({inv["product_id"] for inv in inventory}) if inventory else PRODUCT_NAMES

    for i in range(1, n + 1):
        order_date = random_date()
        quantity   = random.randint(1, 200)
        unit_price = round(random.uniform(10.0, 500.0), 2)
        rows.append({
            "order_id":       f"ORD-{i:05d}",
            "product_id":     random.choice(product_ids),
            "customer_id":    f"CUST-{random.randint(1, 300):04d}",
            "quantity":       quantity,
            "unit_price":     unit_price,
            "total_amount":   round(quantity * unit_price, 2),
            "order_date":     order_date,
            "payment_method": random.choice(PAYMENT_METHODS),
            "warehouse_id":   random.choice(WAREHOUSE_NAMES),
            "priority":       random.choice(["Low", "Medium", "High", "Critical"]),
        })
    return rows


# ---------------------------------------------------------------------------
# 4. Shipments
# ---------------------------------------------------------------------------
def generate_shipments(n: int = NUM_SHIPMENTS, orders: list[dict] = None) -> list[dict]:
    """Generate shipment records linked to orders."""
    rows = []
    order_ids = [o["order_id"] for o in orders] if orders else [f"ORD-{i:05d}" for i in range(1, NUM_ORDERS + 1)]

    for i in range(1, n + 1):
        order_id   = random.choice(order_ids)
        ship_date  = random_date()
        status     = random.choice(DELIVERY_STATUSES)

        # Calculate estimated and actual delivery dates
        est_days  = random.randint(2, 15)
        est_delivery = (datetime.strptime(ship_date, "%Y-%m-%d") + timedelta(days=est_days)).strftime("%Y-%m-%d")

        if status == "Delivered":
            actual_days = est_days + random.randint(-3, 7)   # may be early or late
            actual_delivery = (datetime.strptime(ship_date, "%Y-%m-%d") + timedelta(days=max(1, actual_days))).strftime("%Y-%m-%d")
            delivery_delay  = actual_days - est_days
        elif status == "Cancelled":
            actual_delivery = None
            delivery_delay  = None
        else:
            actual_delivery = None
            delivery_delay  = None

        rows.append({
            "shipment_id":            f"SHP-{i:05d}",
            "order_id":               order_id,
            "supplier_id":            f"SUP-{random.randint(1, NUM_SUPPLIERS):04d}",
            "ship_date":              ship_date,
            "estimated_delivery":     est_delivery,
            "actual_delivery":        actual_delivery if actual_delivery else "",
            "delivery_status":        status,
            "delivery_delay_days":    delivery_delay if delivery_delay is not None else "",
            "carrier":                random.choice(["Delhivery", "BlueDart", "Ecom Express", "Xpressbees", "Shadowfax", "Safexpress", "DTDC"]),
            "shipping_cost":          round(random.uniform(5.0, 250.0), 2),
        })
    return rows


# ---------------------------------------------------------------------------
# CSV Writer
# ---------------------------------------------------------------------------
def write_csv(filename: str, rows: list[dict]) -> None:
    """Write a list of dicts to a CSV file in the data/ directory."""
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"  [OK] {filename:20s}  ->  {len(rows):,} rows  ->  {filepath}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("  Supply Chain Data Generator")
    print("=" * 60)

    suppliers = generate_suppliers()
    write_csv("suppliers.csv", suppliers)

    inventory = generate_inventory(suppliers=suppliers)
    write_csv("inventory.csv", inventory)

    orders = generate_orders(inventory=inventory)
    write_csv("orders.csv", orders)

    shipments = generate_shipments(orders=orders)
    write_csv("shipments.csv", shipments)

    print("=" * 60)
    print("  All datasets generated successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
