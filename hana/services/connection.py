from hdbcli import dbapi
from django.conf import settings

class HANAConnection:
    def __init__(self):
        self.connection = None
        self.cursor = None
        
    def connect(self):
        cfg =  settings.DATABASES['hana']
        try :
            self.connection = dbapi.connect(
                address=cfg['HOST'],
                port=int(cfg['PORT']),
                user=cfg['USER'],
                password=cfg['PASSWORD'],
            )
            self.cursor =  self.connection.cursor()
            print("Connected to HANA successfully")
            return True
              
        except Exception as e:
            print(e)
            raise ConnectionError(f"SAP connection failed: {str(e)}")
        
    def disconnect(self):
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        
    def execute(self, sql: str, params=None):
        try:
            self.cursor.execute(sql, params or [])
            if self.cursor.description is None:
                self.connection.commit()
                return []

            columns = [col[0] for col in self.cursor.description]
            return [dict(zip(columns, row)) for row in self.cursor.fetchall()]

        except Exception as e:
            self.connection.rollback()
            
            raise RuntimeError(f"HANA query failed: {str(e)}")




class Queries():
    OIL_SCHEMA = settings.DATABASES['hana']['OIL_SCHEMA']
    BEVERAGE_SCHEMA = settings.DATABASES['hana']['BEVERAGE_SCHEMA']

    @staticmethod
    def resolve_branch(branch):
        if branch == 'OIL':
            return Queries.OIL_SCHEMA
        elif branch == 'BEVERAGES':
            return Queries.BEVERAGE_SCHEMA
        raise ValueError(f"Unknown branch: {branch!r}")
        
    @staticmethod
    def get_all_accounts(branch):
        s = Queries.resolve_branch(branch)
        return F"""
        SELECT 
            "AcctCode", "AcctName", "FatherNum", "GroupMask",
            "U_Bank_Name", "U_Account_Number", "U_IFSC", "CurrTotal", "ActCurr",
            CASE 
            WHEN "FatherNum" IN ('1104100','1104200') THEN 'Bank'
            WHEN "FatherNum" = '1106100' THEN 'FD'
            WHEN "FatherNum" IN ('2201100','2201200','2201300','2201400','2202100','2202300') THEN 'Loan'
    END AS "Category"
        FROM {s}."OACT"
        WHERE "Postable" = 'Y' 
        AND "Frozen" = 'N' 
        AND "ActType" = 'N'
        AND "FatherNum" IN (
            '1104100', '1104200',   -- Bank accounts
            '1106100',               -- FDs
            '2201100', '2201200', '2201300', '2201400',  -- Bank OD/CC, Term Loans, Credit Card, Vehicle Loans
            '2202100', '2202300'     -- Unsecured loans (individual + corporate)
        )
        ORDER BY "FatherNum", "AcctCode"
        """

    @staticmethod
    def get_account_closing_balances(branch):
        s = Queries.resolve_branch(branch)
        return F"""
        SELECT
            a."AcctCode",
            a."AcctName",
            a."FatherNum",
            SUM(j."Debit" - j."Credit") AS "ClosingBalance"
        FROM {s}."OACT" a
        LEFT JOIN {s}."JDT1" j
            ON j."Account" = a."AcctCode"
            AND j."RefDate" >= ?
            AND j."RefDate" <= ?
        WHERE a."AcctCode" = ?
        AND a."Postable" = 'Y'
        AND a."Frozen" = 'N'
        AND a."ActType" = 'N'
        GROUP BY a."AcctCode", a."AcctName", a."FatherNum"
        ORDER BY a."FatherNum", a."AcctCode"
        """