"""
Employee Payroll System

This module provides a payroll calculation system supporting:
- Hourly employees (paid based on hours worked × hourly wage)
- Salaried employees (paid based on fixed weekly hours × salary wage,
  prorated if hired mid-period)

Classes:
    Employees: Base class representing a generic employee.
    Hourly_employees: Subclass for employees paid by the hour.
    Salary_employees: Subclass for employees on a fixed salary.
    EmployeeExistError: Custom exception for duplicate employee errors.
"""

from datetime import datetime, timedelta


class EmployeeExistError(Exception):
    """Raised when attempting to add a duplicate employee (e.g. duplicate empl_id)."""

    pass


class Employees:
    """Base class representing a generic employee in the payroll system.

    Serves as a parent for specific employee types (hourly/salary).
    Provides shared attributes (name, ID, hire date) and a static anchor
    date for pay period calculations.

    Class Attributes:
        PAY_PERIOD_DAYS (int): Length of a standard pay period (14 days).
    """

    PAY_PERIOD_DAYS = 14  # Standard bi-weekly pay period length

    def __init__(self, empl_name, empl_id, hired_date):
        """Initialize an employee with basic personal and employment info.

        Args:
            empl_name (str): Full name of the employee.
            empl_id (str or int): Unique employee identifier.
            hired_date (str or datetime): Date of hire. If a string is
                passed, it must be in "YYYY-MM-DD" format and will be
                converted to a datetime object automatically.
        """
        self.empl_name = empl_name
        self.empl_id = empl_id
        self.hired_date = self._to_datetime(hired_date)

    @staticmethod
    def _to_datetime(value):
        """Normalize a hire date to a datetime object.

        Accepts either a datetime object (returned as-is) or a
        "YYYY-MM-DD" formatted string (parsed into a datetime).

        Raises:
            TypeError: If value is neither a datetime nor a string.
            ValueError: If value is a string but not in "YYYY-MM-DD" format.
        """
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            return datetime.strptime(value, "%Y-%m-%d")
        raise TypeError(
            f"hired_date must be a str ('YYYY-MM-DD') or datetime, "
            f"got {type(value).__name__}"
        )

    def payroll_calc(self):
        """Calculate the employee's pay for the current period.

        Placeholder method — intended to be overridden by subclasses
        (Hourly_employees, Salary_employees) with specific pay logic.

        Returns:
            None by default; subclasses should return a float.
        """
        pass

    @staticmethod
    def pay_period_anchor():
        """Get the fixed anchor (start) date for the first pay period.

        Returns:
            datetime: The fixed start date ("2026-01-01") from which all
                      pay periods are calculated.
        """
        start_day = "2026-01-01"
        return datetime.strptime(start_day, "%Y-%m-%d")

    @classmethod
    def days_since_anchor(cls, as_of=None):
        """Calculate total whole days elapsed since the anchor date.

        Args:
            as_of (datetime, optional): The date to measure from.
                Defaults to today if not provided.

        Returns:
            int: Number of days elapsed since the anchor date.
        """
        as_of = as_of or datetime.today()
        return (as_of - cls.pay_period_anchor()).days

    @classmethod
    def current_period_bounds(cls, as_of=None):
        """Get the start and end dates of whichever pay period 'as_of' falls in.

        Args:
            as_of (datetime, optional): The date to check. Defaults to
                today if not provided.

        Returns:
            tuple(datetime, datetime): (period_start, period_end)
        """
        as_of = as_of or datetime.today()
        elapsed = cls.days_since_anchor(as_of)
        periods_completed = elapsed // cls.PAY_PERIOD_DAYS
        period_start = cls.pay_period_anchor() + timedelta(
            days=periods_completed * cls.PAY_PERIOD_DAYS
        )
        period_end = period_start + timedelta(days=cls.PAY_PERIOD_DAYS)
        return period_start, period_end


class Hourly_employees(Employees):
    """Represents an employee paid on an hourly wage basis.

    Calculates pay based on the number of hours worked multiplied by a
    fixed hourly wage rate. hired_date does not affect pay for hourly
    employees — hrs_worked already reflects actual time worked.

    Class Attributes:
        hrly_wage (float): Standard hourly wage rate ($20.00/hr).
    """

    hrly_wage = 20.0

    def __init__(self, empl_name, empl_id, hired_date, hrs_worked):
        """Initialize an hourly employee with their worked hours.

        Args:
            empl_name (str): Full name of the employee.
            empl_id (str or int): Unique employee identifier.
            hired_date (str or datetime): Date of hire.
            hrs_worked (float): Total hours worked in the current pay period.
        """
        super().__init__(empl_name, empl_id, hired_date)
        self.__hrs_worked = hrs_worked

    def payroll_calc(self):
        """Calculate pay for an hourly employee.

        Formula: hours worked × hourly wage rate.

        Returns:
            float: Gross pay for the current pay period.
        """
        return self.__hrs_worked * Hourly_employees.hrly_wage

    def __str__(self):
        return (
            f"Employee: {self.empl_name}, Employee_ID: {self.empl_id}, "
            f"Current_Pay: {self.payroll_calc()}, "
            f"for hours worked: {self.__hrs_worked}"
        )


class Salary_employees(Employees):
    """Represents an employee paid on a fixed salary basis.

    Calculates pay based on a fixed number of weekly hours (37.5) multiplied
    by a salary wage rate, prorated if hired_date falls partway through the
    current pay period.

    Class Attributes:
        hrs_worked (float): Standard weekly hours for salaried employees (37.5).
        salary_wage (float): Fixed salary wage rate ($32/hr).
    """

    hrs_worked = 37.5
    salary_wage = 32.0

    def __init__(self, empl_name, empl_id, hired_date):
        """Initialize a salaried employee.

        Args:
            empl_name (str): Full name of the employee.
            empl_id (str or int): Unique employee identifier.
            hired_date (str or datetime): Date of hire.
        """
        super().__init__(empl_name, empl_id, hired_date)

    def payroll_calc(self, as_of=None):
        """Calculate pay for a salaried employee, prorated if hired mid-period.

        Args:
            as_of (datetime, optional): The date to calculate pay against.
                Defaults to today if not provided. Primarily useful for
                testing specific pay periods deterministically.

        Returns:
            float: Gross pay for the current pay period. Full pay if hired
                before the period started, prorated if hired during it,
                0 if not yet employed as of the period's start.
        """
        period_start, period_end = Employees.current_period_bounds(as_of=as_of)
        full_period_pay = self.hrs_worked * self.salary_wage

        if self.hired_date <= period_start:
            return full_period_pay
        elif self.hired_date >= period_end:
            return 0.0
        else:
            days_present = (period_end - self.hired_date).days
            fraction = days_present / Employees.PAY_PERIOD_DAYS
            return full_period_pay * fraction

    def __str__(self):
        return (
            f"Employee: {self.empl_name}, Employee_ID: {self.empl_id}, "
            f"Current_Pay: {self.payroll_calc()}, "
            f"for hours worked: {Salary_employees.hrs_worked}"
        )
