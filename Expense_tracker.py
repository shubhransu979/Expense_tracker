"""
╔══════════════════════════════════════════════════════════╗
║           SMART EXPENSE TRACKER - Python CLI App         ║
║      Track • Analyze • Visualize Your Daily Spending     ║
╚══════════════════════════════════════════════════════════╝

Author  : Smart Expense Tracker
Version : 1.0.0
"""

import csv
import os
import sys
from datetime import datetime, date
from collections import defaultdict

# ─── Optional matplotlib import ───────────────────────────────────────────────
try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# ─── Configuration ─────────────────────────────────────────────────────────────
CSV_FILE = "expenses.csv"
CSV_HEADERS = ["ID", "Date", "Amount", "Category", "Description"]

CATEGORIES = [
    "Food & Dining",
    "Transportation",
    "Shopping",
    "Entertainment",
    "Healthcare",
    "Utilities",
    "Education",
    "Travel",
    "Personal Care",
    "Other",
]

# Color palette for charts
CHART_COLORS = [
    "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7",
    "#DDA0DD", "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E9",
]


# ══════════════════════════════════════════════════════════════════════════════
#  FILE MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════

def initialize_csv():
    """Create CSV file with headers if it doesn't exist."""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()
        print(f"  ✔  Created new expense file: {CSV_FILE}")


def load_expenses():
    """Load all expenses from CSV and return as a list of dicts."""
    expenses = []
    try:
        with open(CSV_FILE, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert stored strings back to proper types
                row["Amount"] = float(row["Amount"])
                row["ID"] = int(row["ID"])
                expenses.append(row)
    except FileNotFoundError:
        initialize_csv()
    except Exception as e:
        print(f"  ✘  Error loading data: {e}")
    return expenses


def save_expense(expense: dict):
    """Append a single expense record to the CSV file."""
    try:
        with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writerow(expense)
        return True
    except Exception as e:
        print(f"  ✘  Error saving expense: {e}")
        return False


def get_next_id(expenses: list) -> int:
    """Return the next available unique ID."""
    if not expenses:
        return 1
    return max(e["ID"] for e in expenses) + 1


# ══════════════════════════════════════════════════════════════════════════════
#  INPUT HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def get_float_input(prompt: str) -> float:
    """Prompt until the user enters a valid positive float."""
    while True:
        raw = input(prompt).strip()
        try:
            value = float(raw)
            if value <= 0:
                print("  ⚠  Amount must be greater than zero. Try again.")
                continue
            return round(value, 2)
        except ValueError:
            print("  ⚠  Invalid number. Please enter a numeric value (e.g. 250.50).")


def get_date_input(prompt: str) -> str:
    """Prompt until the user enters a valid date in YYYY-MM-DD format."""
    while True:
        raw = input(prompt).strip()
        if raw == "":
            # Default to today
            return date.today().isoformat()
        try:
            datetime.strptime(raw, "%Y-%m-%d")
            return raw
        except ValueError:
            print("  ⚠  Invalid date. Use YYYY-MM-DD format (e.g. 2025-07-15).")


def get_category_input() -> str:
    """Display category menu and return the chosen category string."""
    print("\n  Available Categories:")
    for i, cat in enumerate(CATEGORIES, 1):
        print(f"    {i:>2}. {cat}")
    while True:
        raw = input("\n  Enter category number: ").strip()
        try:
            idx = int(raw)
            if 1 <= idx <= len(CATEGORIES):
                return CATEGORIES[idx - 1]
            print(f"  ⚠  Enter a number between 1 and {len(CATEGORIES)}.")
        except ValueError:
            print("  ⚠  Please enter a valid number.")


def get_menu_choice(options: range) -> int:
    """Return a validated integer menu choice within the given range."""
    while True:
        raw = input("\n  ➤  Your choice: ").strip()
        try:
            choice = int(raw)
            if choice in options:
                return choice
            print(f"  ⚠  Please choose between {options.start} and {options.stop - 1}.")
        except ValueError:
            print("  ⚠  Invalid input. Enter a menu number.")


# ══════════════════════════════════════════════════════════════════════════════
#  DISPLAY HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def print_header(title: str):
    """Print a decorated section header."""
    width = 60
    print("\n" + "═" * width)
    print(f"  {title.upper()}")
    print("═" * width)


def print_expense_table(expenses: list):
    """Print expenses in a formatted table."""
    if not expenses:
        print("\n  ⚠  No expenses to display.")
        return

    # Column widths
    col = {"ID": 5, "Date": 12, "Amount": 10, "Category": 20, "Description": 25}
    sep = "  " + "-" * (sum(col.values()) + len(col) * 3)

    # Header row
    print(sep)
    header = (
        f"  {'ID':<{col['ID']}}  "
        f"{'Date':<{col['Date']}}  "
        f"{'Amount':>{col['Amount']}}  "
        f"{'Category':<{col['Category']}}  "
        f"{'Description':<{col['Description']}}"
    )
    print(header)
    print(sep)

    # Data rows
    for e in expenses:
        desc = e["Description"][:col["Description"]]  # truncate long descriptions
        row = (
            f"  {e['ID']:<{col['ID']}}  "
            f"{e['Date']:<{col['Date']}}  "
            f"₹{e['Amount']:>{col['Amount'] - 1},.2f}  "
            f"{e['Category']:<{col['Category']}}  "
            f"{desc:<{col['Description']}}"
        )
        print(row)

    print(sep)
    total = sum(e["Amount"] for e in expenses)
    print(f"  {'TOTAL':>{col['ID'] + col['Date'] + col['Amount'] + 6}}  ₹{total:,.2f}")
    print(sep)


# ══════════════════════════════════════════════════════════════════════════════
#  CORE FEATURES
# ══════════════════════════════════════════════════════════════════════════════

def add_expense():
    """Collect expense details from user and persist to CSV."""
    print_header("Add New Expense")

    expenses = load_expenses()

    amount = get_float_input("  Amount (₹): ")
    category = get_category_input()
    exp_date = get_date_input("  Date [YYYY-MM-DD] (press Enter for today): ")
    description = input("  Description (optional): ").strip() or "—"

    new_expense = {
        "ID": get_next_id(expenses),
        "Date": exp_date,
        "Amount": amount,
        "Category": category,
        "Description": description,
    }

    if save_expense(new_expense):
        print(f"\n  ✔  Expense added successfully! (ID: {new_expense['ID']})")
    else:
        print("\n  ✘  Failed to save expense. Please try again.")


def view_all_expenses():
    """Display all recorded expenses in a table."""
    print_header("All Expenses")
    expenses = load_expenses()

    if not expenses:
        print("\n  ℹ  No expenses recorded yet. Start by adding one!")
        return

    print(f"\n  Total records: {len(expenses)}\n")
    print_expense_table(expenses)


def category_analysis():
    """Show total and percentage spending per category."""
    print_header("Category-wise Analysis")
    expenses = load_expenses()

    if not expenses:
        print("\n  ℹ  No data available for analysis.")
        return

    # Aggregate by category
    totals = defaultdict(float)
    for e in expenses:
        totals[e["Category"]] += e["Amount"]

    grand_total = sum(totals.values())
    sorted_cats = sorted(totals.items(), key=lambda x: x[1], reverse=True)

    print(f"\n  {'Category':<22} {'Amount':>12}  {'Share':>7}  {'Bar'}")
    print("  " + "-" * 60)

    for cat, amt in sorted_cats:
        pct = (amt / grand_total) * 100
        bar = "█" * int(pct / 2.5)  # scale bar to ~40 chars max
        print(f"  {cat:<22} ₹{amt:>10,.2f}  {pct:>6.1f}%  {bar}")

    print("  " + "-" * 60)
    print(f"  {'TOTAL':<22} ₹{grand_total:>10,.2f}  {'100.0%':>7}")


def monthly_report():
    """Generate a monthly spending report for a chosen year-month."""
    print_header("Monthly Expense Report")
    expenses = load_expenses()

    if not expenses:
        print("\n  ℹ  No expenses recorded yet.")
        return

    # Collect unique months from data
    months_available = sorted(set(e["Date"][:7] for e in expenses), reverse=True)
    print("\n  Available months:")
    for i, m in enumerate(months_available, 1):
        print(f"    {i}. {m}")

    while True:
        raw = input("\n  Select month number (or type YYYY-MM directly): ").strip()
        try:
            idx = int(raw)
            if 1 <= idx <= len(months_available):
                chosen_month = months_available[idx - 1]
                break
            print(f"  ⚠  Enter 1–{len(months_available)}.")
        except ValueError:
            # Maybe they typed a month directly
            try:
                datetime.strptime(raw, "%Y-%m")
                chosen_month = raw
                break
            except ValueError:
                print("  ⚠  Invalid input. Enter a number or YYYY-MM.")

    # Filter expenses for chosen month
    month_expenses = [e for e in expenses if e["Date"].startswith(chosen_month)]

    print(f"\n  Report for: {chosen_month}")
    print(f"  Records   : {len(month_expenses)}")
    print_expense_table(month_expenses)

    if month_expenses:
        # Category breakdown for the month
        totals = defaultdict(float)
        for e in month_expenses:
            totals[e["Category"]] += e["Amount"]

        print("\n  Category Breakdown:")
        print("  " + "-" * 38)
        for cat, amt in sorted(totals.items(), key=lambda x: x[1], reverse=True):
            print(f"    {cat:<22} ₹{amt:>10,.2f}")
        print("  " + "-" * 38)
        print(f"    {'Month Total':<22} ₹{sum(totals.values()):>10,.2f}")


# ══════════════════════════════════════════════════════════════════════════════
#  VISUALIZATION
# ══════════════════════════════════════════════════════════════════════════════

def _check_matplotlib():
    """Warn user and return False if matplotlib is missing."""
    if not MATPLOTLIB_AVAILABLE:
        print("\n  ⚠  matplotlib is not installed.")
        print("     Run:  pip install matplotlib")
        return False
    return True


def chart_category_bar():
    """Generate a horizontal bar chart for category-wise spending."""
    if not _check_matplotlib():
        return

    expenses = load_expenses()
    if not expenses:
        print("\n  ℹ  No data available to chart.")
        return

    totals = defaultdict(float)
    for e in expenses:
        totals[e["Category"]] += e["Amount"]

    # Sort descending by amount
    categories = list(totals.keys())
    amounts = [totals[c] for c in categories]
    paired = sorted(zip(amounts, categories), reverse=True)
    amounts, categories = zip(*paired)

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = [CHART_COLORS[i % len(CHART_COLORS)] for i in range(len(categories))]
    bars = ax.barh(categories, amounts, color=colors, edgecolor="white", linewidth=0.8)

    # Value labels inside / outside bars
    for bar, amt in zip(bars, amounts):
        ax.text(
            bar.get_width() + max(amounts) * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"₹{amt:,.0f}",
            va="center", ha="left", fontsize=9, color="#333333",
        )

    ax.set_xlabel("Total Amount (₹)", fontsize=11)
    ax.set_title("Spending by Category", fontsize=14, fontweight="bold", pad=15)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xlim(0, max(amounts) * 1.18)
    plt.tight_layout()
    plt.savefig("chart_categories.png", dpi=150)
    print("\n  ✔  Chart saved as 'chart_categories.png'")
    plt.show()


def chart_monthly_spending():
    """Generate a bar chart showing total spending per month."""
    if not _check_matplotlib():
        return

    expenses = load_expenses()
    if not expenses:
        print("\n  ℹ  No data available to chart.")
        return

    monthly = defaultdict(float)
    for e in expenses:
        month = e["Date"][:7]  # "YYYY-MM"
        monthly[month] += e["Amount"]

    months = sorted(monthly.keys())
    amounts = [monthly[m] for m in months]

    # Pretty labels: "Jan 2025"
    labels = [datetime.strptime(m, "%Y-%m").strftime("%b %Y") for m in months]

    fig, ax = plt.subplots(figsize=(max(8, len(months) * 1.4), 6))
    colors = [CHART_COLORS[i % len(CHART_COLORS)] for i in range(len(months))]
    bars = ax.bar(labels, amounts, color=colors, edgecolor="white", linewidth=0.8, width=0.6)

    # Value labels on top of bars
    for bar, amt in zip(bars, amounts):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(amounts) * 0.01,
            f"₹{amt:,.0f}",
            ha="center", va="bottom", fontsize=9, color="#333333",
        )

    ax.set_ylabel("Total Amount (₹)", fontsize=11)
    ax.set_title("Monthly Spending Overview", fontsize=14, fontweight="bold", pad=15)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_ylim(0, max(amounts) * 1.15)
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig("chart_monthly.png", dpi=150)
    print("\n  ✔  Chart saved as 'chart_monthly.png'")
    plt.show()


def chart_category_pie():
    """Generate a pie chart for category-wise spending distribution."""
    if not _check_matplotlib():
        return

    expenses = load_expenses()
    if not expenses:
        print("\n  ℹ  No data available to chart.")
        return

    totals = defaultdict(float)
    for e in expenses:
        totals[e["Category"]] += e["Amount"]

    # Keep only categories with spending
    labels = list(totals.keys())
    sizes = [totals[l] for l in labels]

    # Explode the biggest slice slightly
    max_idx = sizes.index(max(sizes))
    explode = [0.05 if i == max_idx else 0 for i in range(len(sizes))]

    fig, ax = plt.subplots(figsize=(9, 7))
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=None,
        autopct="%1.1f%%",
        colors=CHART_COLORS[: len(labels)],
        explode=explode,
        startangle=140,
        pctdistance=0.82,
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
    )
    for at in autotexts:
        at.set_fontsize(8)
        at.set_color("white")
        at.set_fontweight("bold")

    ax.legend(
        wedges, labels,
        title="Categories",
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1),
        fontsize=9,
    )
    ax.set_title("Expense Distribution by Category", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig("chart_pie.png", dpi=150)
    print("\n  ✔  Chart saved as 'chart_pie.png'")
    plt.show()


# ══════════════════════════════════════════════════════════════════════════════
#  SEARCH & FILTER
# ══════════════════════════════════════════════════════════════════════════════

def search_expenses():
    """Search expenses by category, date range, or keyword in description."""
    print_header("Search Expenses")

    print("""
  Filter options:
    1. By Category
    2. By Date Range
    3. By Description Keyword
    4. Back to Main Menu
""")
    choice = get_menu_choice(range(1, 5))
    if choice == 4:
        return

    expenses = load_expenses()
    results = []

    if choice == 1:
        category = get_category_input()
        results = [e for e in expenses if e["Category"] == category]
        print(f"\n  Showing expenses for: {category}")

    elif choice == 2:
        print("  Enter date range (YYYY-MM-DD):")
        start = get_date_input("  From: ")
        end = get_date_input("  To  : ")
        results = [e for e in expenses if start <= e["Date"] <= end]
        print(f"\n  Showing expenses from {start} to {end}")

    elif choice == 3:
        keyword = input("  Enter keyword: ").strip().lower()
        results = [e for e in expenses if keyword in e["Description"].lower()]
        print(f"\n  Showing expenses matching: '{keyword}'")

    print_expense_table(results)


# ══════════════════════════════════════════════════════════════════════════════
#  SUMMARY DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

def summary_dashboard():
    """Display a quick snapshot of overall financial health."""
    print_header("Summary Dashboard")

    expenses = load_expenses()
    if not expenses:
        print("\n  ℹ  No expenses recorded yet.")
        return

    total_spent = sum(e["Amount"] for e in expenses)
    this_month = date.today().strftime("%Y-%m")
    this_month_expenses = [e for e in expenses if e["Date"].startswith(this_month)]
    this_month_total = sum(e["Amount"] for e in this_month_expenses)

    # Top category overall
    cat_totals = defaultdict(float)
    for e in expenses:
        cat_totals[e["Category"]] += e["Amount"]
    top_cat = max(cat_totals, key=cat_totals.get)

    # Most recent expense
    latest = max(expenses, key=lambda x: x["Date"])

    print(f"""
  ┌─────────────────────────────────────────────────┐
  │  📊  EXPENSE SNAPSHOT                           │
  ├─────────────────────────────────────────────────┤
  │  Total Records      : {len(expenses):<6}                    │
  │  All-time Spent     : ₹{total_spent:>12,.2f}              │
  │  This Month         : ₹{this_month_total:>12,.2f}              │
  │  Top Category       : {top_cat:<26}│
  │  Latest Entry       : {latest['Date']} — {latest['Category'][:16]:<16}│
  └─────────────────────────────────────────────────┘
""")


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN MENU
# ══════════════════════════════════════════════════════════════════════════════

MENU = """
  ╔══════════════════════════════════════════════════╗
  ║         💰  SMART EXPENSE TRACKER  💰            ║
  ╠══════════════════════════════════════════════════╣
  ║   1.  Add New Expense                            ║
  ║   2.  View All Expenses                          ║
  ║   3.  Category-wise Analysis                     ║
  ║   4.  Monthly Report                             ║
  ║   5.  Search / Filter Expenses                   ║
  ║   6.  Summary Dashboard                          ║
  ║   ──────────────────────────────────────────     ║
  ║   7.  Chart: Category Bar Chart                  ║
  ║   8.  Chart: Monthly Spending Bar Chart          ║
  ║   9.  Chart: Category Pie Chart                  ║
  ║   ──────────────────────────────────────────     ║
  ║   0.  Exit                                       ║
  ╚══════════════════════════════════════════════════╝"""

MENU_ACTIONS = {
    1: add_expense,
    2: view_all_expenses,
    3: category_analysis,
    4: monthly_report,
    5: search_expenses,
    6: summary_dashboard,
    7: chart_category_bar,
    8: chart_monthly_spending,
    9: chart_category_pie,
}


def main():
    """Application entry point — main event loop."""
    initialize_csv()
    print("\n  Welcome to Smart Expense Tracker!")
    if not MATPLOTLIB_AVAILABLE:
        print("  ⚠  Note: matplotlib not found — charts disabled. (pip install matplotlib)")

    while True:
        print(MENU)
        choice = get_menu_choice(range(0, 10))

        if choice == 0:
            print("\n  👋  Thank you for using Smart Expense Tracker. Goodbye!\n")
            sys.exit(0)

        action = MENU_ACTIONS.get(choice)
        if action:
            action()
        else:
            print("\n  ⚠  Invalid option. Please try again.")


# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    main()