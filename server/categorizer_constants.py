from itertools import chain

default_categories = {
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
    ],
    "Groceries": [
        "Groceries",
    ],
    "Car": [
        "Gas",
        "Oil Change",
        "Renewal"
    ],
}

categories = {
    "Bank": [
        'Cash Back Rewards',
        'Fee'
    ],
    "Car": [
        'Gas',
        'Oil Change',
        'Renewal'
    ],
    "Groceries": [
        'District-H',
        "Fred Myers",
        "Instacart",
        "Joe Farm",
        "London Drugs",
        "Mayuri",
        "Metropolitan",
        "Other",
        "Pride India Grocery Store",
        "Safeway",
        "Shoppers Drug Mart",
        "T&T",
        "Target",
        "Walmart",
        "Wholefoods"
    ],
    "Home": [
        "Internet",
        "Rent",
        "Seattle City Lights"
    ],
    "Ignore": [
        "Bank Transfer",
        "Credit Card Payment",
        "Transfer"
    ],
    "Insurance": [
        "State Farm"
    ],
    "Investing": [
        "Charles Schwab",
        "Coinbase",
        "Morgan Stanley Cash",
        "Saving Interest"
    ],
    "Medical": [
        "Bartell Drug",
        "CVS",
        "Dermatologist",
        "Drug Mart",
        "ER",
        "Providence",
        "Quest Diagnostic",
        "Urgent Care"
    ],
    "Miscellaneous": [
        "Amazon",
        "Baseball Game",
        "Car Record",
        "Car Wash",
        "Clothes",
        "Gifts",
        "Golf",
        "Haircut",
        "Mail",
        "Movies",
        "Museum",
        "Photons App",
        "Printing",
        "Restaurant",
        "Spotify",
        "Tax Guy",
        "Udemy",
        "Unknown",
        "Walgreens"
    ],
    "Taxes": [
        "Income Tax",
    ],
    "Travel": [
        "Amtrak",
        "I-94",
        "Parking",
        "Tolls",
        "Transit Card",
        "Uber",
    ],
    "Vacation": [
        "Cash",
        "Ferry",
        "Flights",
        "Hotel",
        "Rent a Car"
    ],
    "Work": ["Paycheck"]
}

all_categories = list(chain.from_iterable(
    [category_types for _category, category_types in categories.items()]))

type_to_category = {
    value: key for key, values in categories.items() for value in values
}


label_to_id = { label: i for i, label in enumerate(all_categories)}
id_to_label = {i: label for i, label in enumerate(all_categories)}