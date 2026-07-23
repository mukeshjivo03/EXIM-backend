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
