from itertools import chain

CategoriesDict = dict[str, list[str]]

default_categories: CategoriesDict = {
    "Income": [
        "Work",
        "Cash Back Rewards",
        "Savings Interest",
        "Investment"
    ],
    "Investment": [
        "Charles Schwab",
        "Coinbase",
    ],
    "Home": [
        "Rent",
        "Internet",
    ],
    "Insurance": [
        "State Farm",
        "American Family Insurance",
    ],
    "Medical": [
        "Urgent Care",
        "Pharmacy",
        "Dermatologist",
        "ER",
        "Checkups"
    ],
    "Miscellaneous": [
        "Amazon",
        "Gifts",
        "Restaurant",
        "Movies",
        "Taxes",
        "Uber"
    ],
    "Groceries": [
        "Groceries",
    ],
    "Car": [
        "Gas",
        "Oil Change",
        "Renewal"
    ],
    "Ignore": [
        "Bank Transfer",
        "Credit Card Payment",
    ]
}