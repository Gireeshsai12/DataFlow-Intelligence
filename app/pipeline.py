"""Generate and publish the NovaCart demo as a single PostgreSQL transaction."""
import argparse
import logging
import random
from datetime import date, timedelta

from app.db import connect, migrate

LOG = logging.getLogger(__name__)
FIRST = date(2024, 1, 1)
CHANNELS = ("Search", "Social", "Email", "Referral")
CATEGORIES = ("Home", "Electronics", "Outdoors", "Kitchen", "Apparel")


def generate(scale):
    rng = random.Random(42)
    customers = [(i, FIRST + timedelta(days=rng.randrange(550)),
                  rng.choice(("Northeast", "South", "West", "Midwest")),
                  rng.choice(CHANNELS), rng.choice(("Consumer", "Business")))
                 for i in range(1, 500 * scale + 1)]
    products = []
    for i in range(1, 100 * scale + 1):
        category = rng.choice(CATEGORIES)
        price = rng.randrange(12, 240) * 100 + 99
        products.append((i, f"{category} {i:04}", category, price,
                         price * rng.randint(35, 67) // 100, rng.randrange(450)))
    campaigns = []
    for i in range(1, 17):
        impressions = rng.randrange(10_000, 100_000)
        campaigns.append((i, CHANNELS[i % 4], rng.randrange(50_000, 400_000),
                          impressions, impressions * rng.randint(2, 9) // 100))
    orders, items, refunds = [], [], []
    for i in range(1, 2500 * scale + 1):
        customer = rng.choice(customers)
        max_age = (date(2025, 12, 24) - customer[1]).days
        ordered = customer[1] + timedelta(days=int(max_age * rng.random() ** 0.65))
        orders.append((i, customer[0], ordered, rng.choice([None, *range(1, 17)]),
                       rng.choice(("Card", "Wallet", "PayPal"))))
        total = 0
        for product in rng.sample(products, rng.randint(1, 4)):
            quantity = rng.randint(1, 3)
            discount = product[3] * rng.choice((0, 0, 5, 10, 15)) // 100
            items.append((i, product[0], quantity, product[3], product[4], discount))
            total += quantity * (product[3] - discount)
        if rng.random() < 0.07:
            refunds.append((i, total // 3, ordered + timedelta(days=rng.randint(1, 7))))
    sessions = []
    for i in range(1, 6000 * scale + 1):
        variant = rng.choice(("Control", "Treatment"))
        visited = date(2025, 7, 1) + timedelta(days=rng.randrange(184))
        customer = rng.choice(customers)
        cart = rng.random() < 0.33
        converted = cart and rng.random() < (0.34 if variant == "Treatment" else 0.29)
        sessions.append((i, customer[0] if customer[1] <= visited and rng.random() < .6 else None,
                         visited, variant, rng.choice(("Desktop", "Mobile", "Tablet")), cart, converted))
    return dict(customers=customers, products=products, campaigns=campaigns, orders=orders,
                items=items, refunds=refunds, sessions=sessions)


def refresh(scale=1, only_if_empty=False):
    if not 1 <= scale <= 100:
        raise ValueError("Scale must be between 1 and 100")
    with connect() as db:
        acquired = db.execute("SELECT pg_try_advisory_lock(423810) AS ok").fetchone()["ok"]
        if not acquired:
            return False
        if only_if_empty and db.execute("SELECT EXISTS(SELECT 1 FROM orders) AS ok").fetchone()["ok"]:
            return True
        run = db.execute("INSERT INTO pipeline_runs(status) VALUES('running') RETURNING id").fetchone()["id"]
        db.commit()
        try:
            data = generate(scale)
            with db.transaction():
                for table in reversed(data):
                    db.execute(f"DELETE FROM {table}")
                for table, rows in data.items():
                    with db.cursor().copy(f"COPY {table} FROM STDIN") as writer:
                        for row in rows:
                            writer.write_row(row)
                invalid = db.execute("""
                    SELECT count(*) AS n FROM order_facts f
                    JOIN orders o ON o.id=f.id JOIN customers c ON c.id=o.customer_id
                    LEFT JOIN refunds r ON r.order_id=f.id
                    WHERE f.sales<f.refund OR o.ordered<c.signup OR r.refunded<o.ordered
                """).fetchone()["n"]
                if invalid:
                    raise ValueError(f"{invalid} invalid order totals or dates")
                db.execute("UPDATE pipeline_runs SET status='succeeded',finished=now(),detail=%s WHERE id=%s",
                           (f"{len(data['orders']):,} orders published", run))
        except Exception:
            LOG.exception("Refresh %s failed", run)
            db.execute("UPDATE pipeline_runs SET status='failed',finished=now(),detail=%s WHERE id=%s",
                       ("Publication failed. See server logs.", run))
            db.commit()
            raise
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scale", type=int, default=1)
    parser.add_argument("--if-empty", action="store_true")
    args = parser.parse_args()
    migrate()
    if not refresh(args.scale, args.if_empty):
        parser.exit(1, "A refresh is already running. Retry after it finishes.\n")


if __name__ == "__main__":
    main()
