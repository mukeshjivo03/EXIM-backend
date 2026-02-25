import pymssql
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class SAPConnection:
    def __init__(self):
        self.host = getattr(settings, 'SAP_DB_HOST', '103.89.45.75')
        self.database = getattr(settings, 'SAP_DB_NAME', 'Jivo_All_Branches_Live')
        self.username = getattr(settings, 'SAP_DB_USER', 'ab')
        self.password = getattr(settings, 'SAP_DB_PASSWORD', 'Jivo@!@#$')
        self.connection = None
        self.cursor = None
    
    def connect(self):
        try:
            self.connection = pymssql.connect(
                server=self.host,
                user=self.username,
                password=self.password,
                database=self.database,
                timeout=60,
                login_timeout=30
            )
            # This is crucial: it ensures execute_query returns dictionaries!
            self.cursor = self.connection.cursor(as_dict=True) 
            return True
        except Exception as e:
            raise ConnectionError(f"SAP connection failed: {str(e)}")
        
        
    def disconnect(self):
        if self.cursor:
            self.cursor.close()
            
        if self.connection:
            self.connection.close()
            
    def execute_query(self, query):
        try:
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            return result
        except Exception as e:
            raise Exception(f"Query execution failed: {str(e)}")
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
            
        
class Queries:
    
    @staticmethod
    def get_all_product():
        return """
            SELECT ItemCode, ItemName, Category, SalFactor2, U_Tax_Rate, Deleted, U_Variety, SalPackUn, U_Brand, U_Unit, U_Sub_Group
            FROM OPENQUERY(HANADB112, 'SELECT "ItemCode", "ItemName", ''OIL'' AS "Category", "SalFactor2", "U_Tax_Rate", "Deleted", "U_Variety", "SalPackUn", "U_Brand", "U_Unit", "U_Sub_Group" 
            FROM "JIVO_OIL_HANADB"."OITM" 
            WHERE "ItemCode" LIKE ''FG%'' OR "ItemCode" LIKE ''SCH%'' OR "ItemCode" LIKE ''RM%'' OR "ItemCode" LIKE ''PM%'' ')
        """
    
    @staticmethod
    def get_single_product(itemCode):
        return f"""
            SELECT ItemCode, ItemName, Category, SalFactor2, U_Tax_Rate, Deleted, U_Variety, SalPackUn, U_Brand, U_Unit, U_Sub_Group
            FROM OPENQUERY(HANADB112, 'SELECT "ItemCode", "ItemName", ''OIL'' AS "Category", "SalFactor2", "U_Tax_Rate", "Deleted", "U_Variety", "SalPackUn", "U_Brand", "U_Unit", "U_Sub_Group" 
            FROM "JIVO_OIL_HANADB"."OITM" 
            WHERE "ItemCode" = ''{itemCode}'' ')
        """     
    @staticmethod
    def get_single_party(cardCode):
        return f"""
            SELECT CardCode, CardName, State1, U_Main_Group, Country 
            FROM OPENQUERY(HANADB112, 
            'SELECT "CardCode", "CardName", "State1", "U_Main_Group", "Country" 
             FROM "JIVO_OIL_HANADB"."OCRD" 
             WHERE "CardCode" = ''{cardCode}'' AND "CardType"=''S'' ')
        """