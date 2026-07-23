# services.py
from .connection import HANAConnection, Queries


def get_all_accounts(branch):
    sql = Queries.get_all_accounts(branch)
    with HANAConnection() as conn:
        return conn.execute(sql)


def get_account_closing_balances(branch, acct_code, from_date, to_date):
    """Balance for a single account over the [from_date, to_date] range."""
    sql = Queries.get_account_closing_balances(branch)
    with HANAConnection() as conn:
        return conn.execute(sql, [from_date, to_date, acct_code])


def get_account_ledger(branch, acct_code, from_date, to_date):
    """Journal lines for a single account over the [from_date, to_date] range."""
    sql = Queries.get_account_ledger(branch)
    with HANAConnection() as conn:
        return conn.execute(sql, [acct_code, from_date, to_date])


def get_accounts_summary(branch):
    """KPI totals (count + balance) grouped by category for the branch."""
    sql = Queries.get_accounts_summary(branch)
    with HANAConnection() as conn:
        return conn.execute(sql)


def get_account_monthly_trend(branch, acct_code, from_date, to_date):
    """Monthly debit/credit/net series for a single account over a range."""
    sql = Queries.get_account_monthly_trend(branch)
    with HANAConnection() as conn:
        return conn.execute(sql, [acct_code, from_date, to_date])
