from langchain.tools import tool


@tool
def calculate_progress(total_tasks: int, completed_tasks: int) -> str:
    """Calculate project completion percentage from total tasks and completed tasks."""
    if total_tasks <= 0:
        return "Total tasks must be greater than zero."

    if completed_tasks < 0:
        return "Completed tasks cannot be negative."

    if completed_tasks > total_tasks:
        return "Completed tasks cannot be greater than total tasks."

    percentage = (completed_tasks / total_tasks) * 100
    return f"Progress: {percentage:.2f}% completed."


@tool
def calculate_budget(total_budget: float, spent_amount: float) -> str:
    """Calculate spent percentage and remaining budget from total budget and spent amount."""
    if total_budget <= 0:
        return "Total budget must be greater than zero."

    if spent_amount < 0:
        return "Spent amount cannot be negative."

    if spent_amount > total_budget:
        return "Spent amount cannot be greater than total budget."

    spent_percentage = (spent_amount / total_budget) * 100
    remaining_budget = total_budget - spent_amount

    return (
        f"Spent: {spent_percentage:.2f}% of the budget. "
        f"Remaining budget: {remaining_budget:.2f}."
    )


@tool
def financial_report(company_name: str, revenue: float, expenses: float) -> str:
    """Generate a simple financial report using company name, revenue, and expenses."""
    if revenue < 0:
        return "Revenue cannot be negative."

    if expenses < 0:
        return "Expenses cannot be negative."

    profit = revenue - expenses

    if revenue == 0:
        profit_margin = 0
    else:
        profit_margin = (profit / revenue) * 100

    return (
        f"Financial report for {company_name}: "
        f"Revenue = {revenue:.2f}, "
        f"Expenses = {expenses:.2f}, "
        f"Profit = {profit:.2f}, "
        f"Profit margin = {profit_margin:.2f}%."
    )


def get_tools():
    """Return all tools used by the ThreadMind AI agent."""
    return [calculate_progress, calculate_budget, financial_report]
