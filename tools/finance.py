import csv
import io
import json
import logging
from collections import defaultdict

logger = logging.getLogger("nina.tools.finance")
# Using a file handler for tools.log
file_handler = logging.FileHandler("tools.log")
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

def run_expenditure_report(expenses_data: str) -> str:
    """
    Parses expenses from CSV or text, categorizes and sums them by month and category.
    Returns a JSON string containing a compact text summary and a structured report.

    Expected CSV columns (or text lines comma-separated): date, amount, category, note
    Example line: 2023-10-15, 50.00, Groceries, Weekly shopping
    """
    logger.info("TAG:finance action=run_expenditure_report msg=starting_report_generation")

    if not expenses_data or not expenses_data.strip():
        logger.warning("TAG:finance action=run_expenditure_report msg=empty_input")
        return json.dumps({
            "summary": "No expenditure data provided.",
            "report": {}
        })

    report = defaultdict(lambda: defaultdict(float))
    total_spent = 0.0
    valid_entries = 0
    errors = 0

    try:
        # Simple heuristic to detect if it's text/csv.
        # We process line by line, trying to split by comma
        reader = csv.reader(io.StringIO(expenses_data.strip()))
        for row_num, row in enumerate(reader):
            # Skip empty lines
            if not row:
                continue

            # If header row, skip
            if row_num == 0 and any(h.strip().lower() in ['date', 'amount', 'category'] for h in row):
                continue

            if len(row) < 3:
                logger.warning(f"TAG:finance action=parse_row msg=invalid_row_format row_num={row_num}")
                errors += 1
                continue

            date_str = row[0].strip()
            amount_str = row[1].strip()
            category = row[2].strip()
            # Note is optional, but if present it's row[3]

            try:
                # Extract month (YYYY-MM format ideally, but try to handle parts)
                # If date is YYYY-MM-DD, taking first 7 chars is fine.
                # If it's something else, fallback to "Unknown" if it's too short
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

        # Format the output
        text_summary = f"Processed {valid_entries} expenses with {errors} errors. Total spent: {total_spent:.2f}."
        for month, categories in sorted(report.items()):
            text_summary += f"\nMonth: {month}"
            month_total = 0.0
            for cat, amt in sorted(categories.items()):
                text_summary += f"\n  - {cat}: {amt:.2f}"
                month_total += amt
            text_summary += f"\n  Total for {month}: {month_total:.2f}"

        logger.info(f"TAG:finance action=run_expenditure_report msg=success valid_entries={valid_entries} errors={errors} total={total_spent}")

        return json.dumps({
            "summary": text_summary,
            "report": {month: dict(cats) for month, cats in report.items()}
        })

    except Exception as e:
        logger.error(f"TAG:finance action=run_expenditure_report msg=unexpected_error error={str(e)}")
        return json.dumps({
            "summary": "Failed to process expenditure report due to an internal error.",
            "report": {}
        })
