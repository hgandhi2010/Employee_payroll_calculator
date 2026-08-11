# Employee_payroll_calculator
Employee Payroll Calculator

# 💼 Employee Payroll Engine

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Build Status](https://img.shields.io/badge/tests-passing-brightgreen.svg)

An object-oriented Python payroll system designed to calculate gross pay for both hourly and salaried workforce members. The engine uses a deterministic anchor-date model to manage 14-day pay periods, handling edge cases such as mid-period hires through automatic proration.
✨ Key Technical Features
Deterministic Bi-Weekly Pay Engine: Calculates pay windows using a fixed anchor date (2026-01-01), eliminating calendar drift across 14-day intervals.

Smart Proration Logic: Automatically prorates salaried employee compensation when hire dates fall inside an active pay period (returns $0.0 for future hires).

Data Encapsulation: Employs private attributes (__hrs_worked) to prevent accidental modification of recorded hourly data.

Flexible Type Normalization: Robust parsing converts string dates (YYYY-MM-DD) or native datetime instances seamlessly.
---

## 📐 System Architecture

```mermaid
classDiagram
    direction TB

    class Exception {
        <<Built-in>>
    }

    class EmployeeExistError {
        +Custom Exception
    }

    class Employees {
        +int PAY_PERIOD_DAYS = 14
        +str empl_name
        +str|int empl_id
        +datetime hired_date
        +__init__(empl_name, empl_id, hired_date)
        +payroll_calc()
        +pay_period_anchor()$ datetime
        +days_since_anchor(as_of)$ int
        +current_period_bounds(as_of)$ tuple
        #_to_datetime(value)$ datetime
    }

    class Hourly_employees {
        +float hrly_wage = 20.0
        -float __hrs_worked
        +__init__(empl_name, empl_id, hired_date, hrs_worked)
        +payroll_calc() float
        +__str__() str
    }

    class Salary_employees {
        +float hrs_worked = 37.5
        +float salary_wage = 32.0
        +__init__(empl_name, empl_id, hired_date)
        +payroll_calc(as_of) float
        +__str__() str
    }

    Exception <|-- EmployeeExistError
    Employees <|-- Hourly_employees : Inherits
    Employees <|-- Salary_employees : Inherits
