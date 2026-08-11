import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.Employee_payroll import (  # adjust import to your filename
    Employees,
    Hourly_employees,
    Salary_employees,
)


def check(label, actual, expected, tol=0.001):
    if isinstance(expected, datetime):
        status = "PASS" if actual == expected else "FAIL"
    else:
        status = "PASS" if abs(actual - expected) < tol else "FAIL"
    print(f"[{status}] {label}: got {actual}, expected {expected}")


# ---- Step 1: boundary math ----
test_date = datetime(2026, 3, 10)
start, end = Employees.current_period_bounds(as_of=test_date)
print(f"period_start={start.date()}, period_end={end.date()}")
check("period_start", start, datetime(2026, 2, 26))
check("period_end", end, datetime(2026, 3, 12))

print()

# ---- Step 2: salary employees ----
cases = [
    ("Hired well before period", "2026-01-15", 1200.0),
    ("Hired exactly on period start", "2026-02-26", 1200.0),
    ("Hired mid-period (half)", "2026-03-05", 600.0),
    ("Hired exactly on period end", "2026-03-12", 0.0),
    ("Hired after period ends", "2026-03-15", 0.0),
]

for label, hired, expected in cases:
    emp = Salary_employees("Test Employee", 1, hired)
    actual = emp.payroll_calc()
    check(label, actual, expected)

print()

# ---- Step 3: hourly employees (should be unaffected by hired_date) ----
hourly_cases = [
    ("Normal week", 40, 800.0),
    ("Zero hours", 0, 0.0),
    ("Partial week", 16, 320.0),
]

for label, hrs, expected in hourly_cases:
    emp = Hourly_employees("Test Employee", 1, "2026-01-01", hrs)
    check(label, emp.payroll_calc(), expected)

print()

# ---- Step 4: type handling ----
try:
    emp = Salary_employees("Test Employee", 1, "2026-01-05")
    result = emp.payroll_calc()
    print(f"[PASS] String hired_date accepted, payroll_calc returned {result}")
except Exception as e:
    print(f"[FAIL] String hired_date raised: {type(e).__name__}: {e}")

try:
    emp = Salary_employees("Test Employee", 1, datetime(2026, 1, 5))
    result = emp.payroll_calc()
    print(f"[PASS] datetime hired_date accepted, payroll_calc returned {result}")
except Exception as e:
    print(f"[FAIL] datetime hired_date raised: {type(e).__name__}: {e}")
