import json
import sys
from pathlib import Path

# Add the root directory to path to allow imports from tools
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.finance import run_expenditure_report

def test_run_expenditure_report_happy_path():
    csv_data = """date,amount,category,note
2023-10-01,15.50,Food,Lunch
2023-10-15,50.00,Groceries,Weekly shopping
2023-11-05,100.00,Utilities,Electric bill
2023-10-20,30.00,Groceries,Snacks
"""
    res = run_expenditure_report(csv_data)
    result = json.loads(res.data)

    # Check that report structure is correct
    assert "2023-10" in result["report"]
    assert "2023-11" in result["report"]
    assert result["report"]["2023-10"]["Food"] == 15.50
    assert result["report"]["2023-10"]["Groceries"] == 80.00
    assert result["report"]["2023-11"]["Utilities"] == 100.00

    # Check summary contains total spent
    assert "195.50" in result["summary"]
    assert "Processed 4 expenses" in result["summary"]
    assert "0 errors" in result["summary"]

def test_run_expenditure_report_empty_input():
    res = run_expenditure_report("")
    result = json.loads(res.data)
    assert result["summary"] == "No expenditure data provided."
    assert result["report"] == {}

    res = run_expenditure_report("   \n  ")
    result = json.loads(res.data)
    assert result["summary"] == "No expenditure data provided."
    assert result["report"] == {}

def test_run_expenditure_report_bad_rows():
    csv_data = """date,amount,category,note
2023-10-01,15.50,Food,Lunch
bad_row_no_commas
2023-10-15,not_a_number,Groceries,Shopping
2023-11-05,100.00,Utilities,Electric bill
"""
    res = run_expenditure_report(csv_data)
    result = json.loads(res.data)

    # Should only process 2 valid rows
    assert "Processed 2 expenses" in result["summary"]
    assert "2 errors" in result["summary"]

    # Check values
    assert result["report"]["2023-10"]["Food"] == 15.50
    assert result["report"]["2023-11"]["Utilities"] == 100.00

def test_run_expenditure_report_plain_text():
    text_data = """
2023-01-01, 10, Commute, Bus fare
2023-01-02, 20.5, Commute, Train
2023-01-03, 5, Coffee
"""
    res = run_expenditure_report(text_data)
    result = json.loads(res.data)

    assert "Processed 3 expenses" in result["summary"]
    assert result["report"]["2023-01"]["Commute"] == 30.5
    assert result["report"]["2023-01"]["Coffee"] == 5.0

if __name__ == "__main__":
    # If run directly as a script
    test_run_expenditure_report_happy_path()
    test_run_expenditure_report_empty_input()
    test_run_expenditure_report_bad_rows()
    test_run_expenditure_report_plain_text()
    print("All tests passed!")
