import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

products = {
    "Laptop": ("Electronics", 55000),
    "Phone": ("Electronics", 25000),
    "Tablet": ("Electronics", 18000),
    "Headphones": ("Accessories", 3000),
    "Keyboard": ("Accessories", 1500),
    "Monitor": ("Electronics", 14000),
}
regions = ["North", "South", "East", "West"]

rows = []
order_id = 1000
dates = pd.date_range("2024-01-01", "2024-12-31", freq="D")

for d in dates:
    n_orders = rng.poisson(5.5)
    for _ in range(n_orders):
        product = rng.choice(list(products.keys()))
        region = rng.choice(regions)

        # Planted story: Laptop sales in the West collapse in Q3
        if product == "Laptop" and region == "West" and d.month in (7, 8, 9):
            if rng.random() < 0.75:
                continue  # order never happens

        category, base_price = products[product]
        unit_price = round(base_price * rng.uniform(0.95, 1.05))
        units = int(rng.integers(1, 5))
        order_id += 1
        rows.append(
            {
                "order_id": order_id,
                "date": d.date(),
                "product": product,
                "category": category,
                "region": region,
                "customer_id": f"C{rng.integers(1, 301):04d}",
                "units": units,
                "unit_price": unit_price,
                "revenue": units * unit_price,
            }
        )

df = pd.DataFrame(rows)
df.to_csv("data/sales_2024.csv", index=False)
print(f"Saved data/sales_2024.csv with {len(df)} rows")