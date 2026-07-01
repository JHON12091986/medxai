"""
Finance Management Module
=========================

This module provides tools for managing personal finances, including expense tracking,
budget setting, and expenditure reporting. It supports:

- Adding and deleting expenses
- Setting and tracking monthly budgets
- Generating summaries and reports for specific months
- Listing recent expenses
- Legacy CSV-based expenditure reporting for backward compatibility

The module uses a JSON file (`data/finance_log.json`) for persistent storage of expenses and budgets.

Example Usage:
    >>> from tools.finance import add_expense, set_budget, get_summary
    >>> set_budget(50000, "BDT")
    >>> add_expense(500, "Food", "Lunch at office")
    >>> print(get_summary())

Note:
    All monetary values are stored as floats and should be handled with appropriate precision.
    The default currency is BDT (Bangladeshi Taka).
"""
import os
import json
import fcntl
from datetime import datetime
import uuid
import csv
import io
from collections import defaultdict
import logging
from tools.retry import ToolResult

logger = logging.getLogger("nina.tools.finance")

# --- LEGACY REPORT GENERATION FOR TESTS ---
def run_expenditure_report(expenses_data: str) -> ToolResult:
    """
    Parses expenses from CSV or text, categorizes and sums them by month and category.
    Returns a JSON string containing a compact text summary and a structured report.
    """
    try:
        logger.info("TAG:finance action=run_expenditure_report msg=starting_report_generation")

        if not expenses_data or not expenses_data.strip():
            logger.warning("TAG:finance action=run_expenditure_report msg=empty_input")
            return ToolResult.success(json.dumps({
                "summary": "No expenditure data provided.",
                "report": {}
            }))

        report = defaultdict(lambda: defaultdict(float))
        total_spent = 0.0
        valid_entries = 0
        errors = 0
        reader = csv.reader(io.StringIO(expenses_data.strip()))
        for row_num, row in enumerate(reader):
            if not row:
                continue

            if row_num == 0 and any(h.strip().lower() in ['date', 'amount', 'category'] for h in row):
                continue

            if len(row) < 3:
                logger.warning(f"TAG:finance action=parse_row msg=invalid_row_format row_num={row_num}")
                errors += 1
                continue

            date_str = row[0].strip()
            amount_str = row[1].strip()
            category = row[2].strip()

            try:
                if len(date_str) >= 7:
                    month = date_str[:7]
                else:
                    month = "Unknown"

                amount = float(amount_str)

                report[month][category] += amount
                total_spent += amount
                valid_entries += 1
            except ValueError:
                logger.warning(f"TAG:finance action=parse_row msg=value_error row_num={row_num} amount={amount_str}")
                errors += 1
                continue

        text_summary = f"Processed {valid_entries} expenses with {errors} errors. Total spent: {total_spent:.2f}."
        for month, categories in sorted(report.items()):
            text_summary += f"\nMonth: {month}"
            month_total = 0.0
            for cat, amt in sorted(categories.items()):
                text_summary += f"\n  - {cat}: {amt:.2f}"
                month_total += amt
            text_summary += f"\n  Total for {month}: {month_total:.2f}"

        logger.info(f"TAG:finance action=run_expenditure_report msg=success valid_entries={valid_entries} errors={errors} total={total_spent}")

        return ToolResult.success(json.dumps({
            "summary": text_summary,
            "report": {month: dict(cats) for month, cats in report.items()}
        }))

    except Exception as e:
        logger.error(f"TAG:finance action=run_expenditure_report msg=unexpected_error error={str(e)}")
        return ToolResult.failure(str(e))

# --- NEW EXPENSE TRACKER (F-04) ---
DATA_FILE = "data/finance_log.json"

def _load_expenses():
    """
    Loads expense data from the persistent JSON storage file.

    This function reads the finance log file (`data/finance_log.json`) and returns its contents.
    If the file does not exist or cannot be read, it returns a default structure with an empty budget
    and no entries.

    The function uses file locking (shared lock) to ensure thread-safe read operations.

    Returns:
        dict: A dictionary containing:
            - "budget" (dict): The monthly budget, with keys:
                - "monthly" (float): The budget amount
                - "currency" (str): The currency code (default: "BDT")
            - "entries" (list): A list of expense entries, where each entry is a dict with keys:
                - "id" (str): A unique identifier for the expense
                - "amount" (float): The expense amount
                - "category" (str): The expense category
                - "note" (str): Optional note for the expense
                - "date" (str): The date of the expense in "YYYY-MM-DD" format

    Note:
        If the file is corrupted or cannot be read, the function logs the error and returns a default
        structure to ensure the system remains operational.
    """
    if not os.path.exists(DATA_FILE):
        return {"budget": {"monthly": 0.0, "currency": "BDT"}, "entries": []}
    try:
        with open(DATA_FILE, 'r') as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            data = json.load(f)
            return data
    except Exception:
        return {"budget": {"monthly": 0.0, "currency": "BDT"}, "entries": []}

def _save_expenses(data):
    """
    Saves expense data to the persistent JSON storage file.

    This function writes the provided data to the finance log file (`data/finance_log.json`).
    It creates the directory if it does not exist and uses file locking (exclusive lock) to ensure
    thread-safe write operations.

    Args:
        data (dict): A dictionary containing the finance data to save. Expected structure:
            - "budget" (dict): The monthly budget, with keys:
                - "monthly" (float): The budget amount
                - "currency" (str): The currency code (default: "BDT")
            - "entries" (list): A list of expense entries, where each entry is a dict with keys:
                - "id" (str): A unique identifier for the expense
                - "amount" (float): The expense amount
                - "category" (str): The expense category
                - "note" (str): Optional note for the expense
                - "date" (str): The date of the expense in "YYYY-MM-DD" format

    Note:
        The function handles file creation, truncation, and locking automatically. If the file
        already exists, it is overwritten with the new data.
    """
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'r+' if os.path.exists(DATA_FILE) else 'w+') as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        if f.readable():
            try:
                f.seek(0)
                f.read(1)
            except Exception:
                pass
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()

def add_expense(amount: float, category: str, note: str = "") -> str:
    """
    Adds an expense entry for the current date.

    This function creates a new expense entry with the provided amount, category, and optional note.
    The entry is saved to the persistent storage and a summary string is returned.

    Args:
        amount (float): The amount spent. Must be a positive number.
        category (str): The category of the expense (e.g., "Food", "Transport", "Entertainment").
        note (str, optional): An optional note or description for the expense. Defaults to "".

    Returns:
        str: A summary string confirming the expense was logged, including the amount, category,
             and the total spent in the current month.

    Example:
        >>> add_expense(500, "Food", "Lunch at office")
        "✅ Logged: 500 BDT for 'Food'. Total spent this month: 12500.00 BDT."

    Note:
        The expense is recorded with the current date. The currency used is taken from the budget settings.
    """
    data = _load_expenses()
    entry = {
        "id": str(uuid.uuid4())[:8],
        "amount": float(amount),
        "category": category,
        "note": note,
        "date": datetime.today().strftime('%Y-%m-%d')
    }
    data["entries"].append(entry)
    _save_expenses(data)
    
    current_month = datetime.today().strftime('%Y-%m')
    sum_spent = sum(e["amount"] for e in data["entries"] if e["date"].startswith(current_month))
    currency = data.get("budget", {}).get("currency", "BDT")
    return f"✅ Logged: {amount} {currency} for '{category}'. Total spent this month: {sum_spent:.2f} {currency}."

def set_budget(amount: float, currency: str = "BDT") -> str:
    """
    Sets the monthly budget for expense tracking.

    This function updates the monthly budget amount and currency in the persistent storage.
    The budget is used to calculate remaining funds and track overspending.

    Args:
        amount (float): The monthly budget amount. Must be a positive number.
        currency (str, optional): The currency code for the budget (e.g., "BDT", "USD", "EUR").
                                Defaults to "BDT".

    Returns:
        str: A confirmation string indicating the budget was set successfully.

    Example:
        >>> set_budget(50000, "BDT")
        "✅ Monthly budget set: 50,000.00 BDT"
    """
    data = _load_expenses()
    data["budget"] = {"monthly": float(amount), "currency": currency}
    _save_expenses(data)
    return f"✅ Monthly budget set: {amount:,.2f} {currency}"

def get_summary(month: str = None) -> str:
    """
    Generates a detailed spending summary for the specified month or the current month.

    This function calculates the total expenses for the specified month, compares them against the
    set budget, and provides a breakdown of expenses by category. If no budget is set or no expenses
    are recorded, appropriate messages are returned.

    Args:
        month (str, optional): The month for which to generate the summary, in "YYYY-MM" format.
                              If not provided, the current month is used.

    Returns:
        str: A formatted string containing the spending summary for the specified month. The summary
             includes:
             - Total spent
             - Budget
             - Remaining budget or overspending
             - Breakdown of expenses by category

    Example:
        >>> set_budget(50000, "BDT")
        >>> add_expense(500, "Food", "Lunch at office")
        >>> print(get_summary())
        📊 Expenses — 2026-06
        Total spent: 500.00 BDT
        Budget: 50000.00 BDT
        Remaining: 49500.00 BDT
        
        By category:
        • Food: 500.00 BDT  (1 entries)
    """
    if not month:
        month = datetime.today().strftime('%Y-%m')
    
    data = _load_expenses()
    budget_data = data.get("budget", {"monthly": 0.0, "currency": "BDT"})
    budget = budget_data.get("monthly", 0.0)
    currency = budget_data.get("currency", "BDT")
    
    month_entries = [e for e in data["entries"] if e["date"].startswith(month)]
    
    if not month_entries and budget == 0.0:
        return f"No expenses recorded for {month}"
    
    total_spent = sum(e["amount"] for e in month_entries)
    remaining = budget - total_spent
    
    lines = [
        f"📊 Expenses — {month}",
        f"Total spent: {total_spent:.2f} {currency}",
        f"Budget: {budget:.2f} {currency}"
    ]
    
    if remaining >= 0:
        lines.append(f"Remaining: {remaining:.2f} {currency}")
    else:
        lines.append(f"⚠️ OVER BUDGET by {abs(remaining):.2f} {currency}")
        
    lines.append("")
    lines.append("By category:")
    
    cat_spent = defaultdict(float)
    cat_count = defaultdict(int)
    for e in month_entries:
        cat_spent[e["category"]] += e["amount"]
        cat_count[e["category"]] += 1
        
    for cat, amt in sorted(cat_spent.items()):
        lines.append(f"• {cat}: {amt:.2f} {currency}  ({cat_count[cat]} entries)")
        
    return "\n".join(lines)

def list_expenses(limit: int = 10) -> str:
    """
    Retrieves and formats the most recent expense entries.

    This function fetches the most recent expense entries from the persistent storage and formats them
    into a human-readable string. The number of entries returned is limited by the `limit` parameter.

    Args:
        limit (int, optional): The maximum number of recent expense entries to retrieve. Defaults to 10.

    Returns:
        str: A formatted string listing the most recent expense entries. Each entry includes:
            - A unique identifier
            - The date of the expense
            - The amount spent
            - The category of the expense
            - An optional note (if provided)

    Example:
        >>> list_expenses(3)
        'Last 3 expenses:\n        - [a1b2c3d4] 2026-06-23 - 500.00 BDT on Food (Lunch at office)\n        - [e5f6g7h8] 2026-06-22 - 200.00 BDT on Transport\n        - [i9j0k1l2] 2026-06-22 - 1000.00 BDT on Entertainment'

    Note:
        If no expenses are recorded, the function returns "No expenses recorded."
    """
    data = _load_expenses()
    currency = data.get("budget", {}).get("currency", "BDT")
    entries = data["entries"][-limit:]
    if not entries:
        return "No expenses recorded."
    
    lines = [f"Last {len(entries)} expenses:"]
    for e in entries:
        note_str = f" ({e['note']})" if e["note"] else ""
        lines.append(f"• [{e['id']}] {e['date']} - {e['amount']:.2f} {currency} on {e['category']}{note_str}")
    return "\n".join(lines)


def get_expenses(limit: int = 10) -> str:
    """
    Retrieves and formats the most recent expense entries (alias for `list_expenses`).

    This function is an alias for `list_expenses` and provides the same functionality.
    It fetches the most recent expense entries from the persistent storage and formats them
    into a human-readable string. The number of entries returned is limited by the `limit` parameter.

    Args:
        limit (int, optional): The maximum number of recent expense entries to retrieve. Defaults to 10.

    Returns:
        str: A formatted string listing the most recent expense entries. Each entry includes:
            - A unique identifier
            - The date of the expense
            - The amount spent
            - The category of the expense
            - An optional note (if provided)

    Example:
        >>> get_expenses(3)
        'Last 3 expenses:\n        • [a1b2c3d4] 2026-06-23 - 500.00 BDT on Food (Lunch at office)\n        • [e5f6g7h8] 2026-06-22 - 200.00 BDT on Transport\n        • [i9j0k1l2] 2026-06-22 - 1000.00 BDT on Entertainment'

    Note:
        If no expenses are recorded, the function returns "No expenses recorded."
        This function is identical to `list_expenses`.
    """
    return list_expenses(limit)

def get_total(month: str = None) -> float:
    """
    Calculates the total amount spent in a specified month.

    This function calculates the sum of all expenses recorded for a given month. If no month is specified,
    it defaults to the current month.

    Args:
        month (str, optional): The month for which to calculate the total expenses, in "YYYY-MM" format.
                              If not provided, the current month is used.

    Returns:
        float: The total amount spent in the specified month.

    Example:
        >>> get_total("2026-06")
        12500.00

    Note:
        If no expenses are recorded for the specified month, the function returns 0.0.
    """
    if not month:
        month = datetime.today().strftime('%Y-%m')
    data = _load_expenses()
    month_entries = [e for e in data["entries"] if e["date"].startswith(month)]
    return sum(e["amount"] for e in month_entries)

def delete_last_expense() -> str:
    """
    Deletes the most recently added expense entry.

    This function removes the most recent expense entry from the persistent storage and returns
    a confirmation message. If no expenses are recorded, it returns a message indicating that
    there are no expenses to delete.

    Returns:
        str: A confirmation string indicating the result of the deletion. The string includes:
            - The amount of the deleted expense
            - The category of the deleted expense
            - The date of the deleted expense

    Raises:
        ValueError: If the expense log is corrupted or cannot be read.

    Example:
        >>> delete_last_expense()
        "🗑️ Deleted last expense: 500.00 BDT for 'Food' on 2026-06-23."

    Note:
        If no expenses are recorded, the function returns "No expenses to delete."
    """
    data = _load_expenses()
    if not data["entries"]:
        return "No expenses to delete."

    last_entry = data["entries"].pop()
    _save_expenses(data)

    currency = data.get("budget", {}).get("currency", "BDT")
    return f"🗑️ Deleted last expense: {last_entry['amount']:.2f} {currency} for '{last_entry['category']}' on {last_entry['date']}."
