import csv
import os
import random
import argparse
from datetime import datetime, timedelta

PAYCHECK_AMOUNT = 3000.00
APARTMENT_AMOUNT = -1500.00
INVESTMENT_AMOUNT = -100.00
EXPENSES = [
    ("AMZN.com Purchase", (10, 200)),
    ("Groceries", (50, 400)),
    ("Seattle Lights", (30, 150)),
    ("Fred Meyer Fuel", (30, 150)),
    ("Etsy", (30, 150)),
    ("Downtown Automotive", (30, 150)),
]


def generate_transactions(year, out_folder):
    rows = []
    for month in range(1, 13):
        # Paycheck (credit)
        payday = datetime(year, month, 1)
        rows.append([
            payday.strftime("%m/%d/%Y"),
            "credit",
            "Paycheck",
            "MEMO",
            PAYCHECK_AMOUNT
        ])
        # My Apartment (debit)
        rent_day = payday + timedelta(days=2)
        rows.append([
            rent_day.strftime("%m/%d/%Y"),
            "debit",
            "My Apartment",
            "MEMO",
            APARTMENT_AMOUNT
        ])
        # Investment (debit)
        investment_day = payday + timedelta(days=10)
        rows.append([
            investment_day.strftime("%m/%d/%Y"),
            "debit",
            "Charles Schwab",
            "MEMO",
            INVESTMENT_AMOUNT
        ])
        # Random expenses (debit)
        for name, (low, high) in EXPENSES:
            if random.random() < 0.8:  # 80% chance each month
                day = random.randint(3, 27)
                amount = round(random.uniform(low, high), 2)
                rows.append([
                    datetime(year, month, day).strftime("%m/%d/%Y"),
                    "debit",
                    name,
                    "MEMO",
                    -amount
                ])
    return rows

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("year", type=int, help="Year for the data")
    parser.add_argument("out_folder", type=str, help="Output folder")
    args = parser.parse_args()

    os.makedirs(args.out_folder, exist_ok=True)
    filename = os.path.join(args.out_folder, f"{args.year}.csv")
    rows = generate_transactions(args.year, args.out_folder)
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Transaction", "Name", "Memo", "Amount"])
        writer.writerows(sorted(rows, key=lambda r: r[0]))
    print(f"Data written to {filename}")

if __name__ == "__main__":
    main()
