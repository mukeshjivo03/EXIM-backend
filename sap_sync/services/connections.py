import pymssql
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class SAPConnection:
    def __init__(self):
        self.host = getattr(settings, 'SAP_DB_HOST')
        self.database = getattr(settings, 'SAP_DB_NAME')
        self.username = getattr(settings, 'SAP_DB_USER')
        self.password = getattr(settings, 'SAP_DB_PASSWORD')
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
    def get_all_rm_product():
        return """
SELECT *
FROM OPENQUERY(HANADB112, '
    SELECT 
        T1."ItemCode",
        T1."ItemName",
        ''OIL'' AS "Category",
        T1."SalFactor2",
        T1."U_Tax_Rate",
        T1."Deleted",
        T1."U_Variety",
        T1."SalPackUn",
        T1."U_Brand",
        T1."U_Unit",
        T1."U_Sub_Group",

        SUM(T0."TransValue") AS "TotalTransValue",
        SUM(T0."InQty")      AS "TotalInQty",
        SUM(T0."OutQty")     AS "TotalOutQty",

        (SUM(T0."InQty") - SUM(T0."OutQty")) AS "TotalQty",

        CASE 
            WHEN (SUM(T0."InQty") - SUM(T0."OutQty")) <> 0 
            THEN SUM(T0."TransValue") / (SUM(T0."InQty") - SUM(T0."OutQty"))
            ELSE 0
        END AS "Rate"

    FROM "JIVO_OIL_HANADB"."OITM" T1

    LEFT JOIN "JIVO_OIL_HANADB"."OINM" T0
        ON T1."ItemCode" = T0."ItemCode"
        AND T0."Warehouse" = ''BH-LO''

    WHERE T1."ItemCode" LIKE ''RM%''
    AND T1."U_Unit" = ''OIL''

    GROUP BY
        T1."ItemCode",
        T1."ItemName",
        T1."SalFactor2",
        T1."U_Tax_Rate",
        T1."Deleted",
        T1."U_Variety",
        T1."SalPackUn",
        T1."U_Brand",
        T1."U_Unit",
        T1."U_Sub_Group"

    ORDER BY T1."ItemCode"
')
"""
        
    @staticmethod
    def get_all_fg_product():
        return """
            SELECT ItemCode, ItemName, Category, SalFactor2, U_Tax_Rate, Deleted, U_Variety, SalPackUn, U_Brand, U_Unit, U_Sub_Group
            FROM OPENQUERY(HANADB112, 'SELECT "ItemCode", "ItemName", ''OIL'' AS "Category", "SalFactor2", "U_Tax_Rate", "Deleted", "U_Variety", "SalPackUn", "U_Brand", "U_Unit", "U_Sub_Group" 
            FROM "JIVO_OIL_HANADB"."OITM" 
            WHERE "ItemCode" LIKE ''FG%'' AND "U_Unit" = ''OIL'' ')
        """
    
    @staticmethod
    def get_single_fg_product(itemCode):
        return f"""
            SELECT ItemCode, ItemName, Category, SalFactor2, U_Tax_Rate, Deleted, U_Variety, SalPackUn, U_Brand, U_Unit, U_Sub_Group
            FROM OPENQUERY(HANADB112, 'SELECT "ItemCode", "ItemName", ''OIL'' AS "Category", "SalFactor2", "U_Tax_Rate", "Deleted", "U_Variety", "SalPackUn", "U_Brand", "U_Unit", "U_Sub_Group" 
            FROM "JIVO_OIL_HANADB"."OITM" 
            WHERE "ItemCode" = ''{itemCode}'' AND "ItemCode" LIKE ''FG%'' AND "U_Unit" = ''OIL'' ')
        """  
        
    @staticmethod
    def get_single_rm_product(itemCode):
        return f"""
            SELECT ItemCode, ItemName, Category, SalFactor2, U_Tax_Rate, Deleted, U_Variety, SalPackUn, U_Brand, U_Unit, U_Sub_Group
            FROM OPENQUERY(HANADB112, 'SELECT "ItemCode", "ItemName", ''OIL'' AS "Category", "SalFactor2", "U_Tax_Rate", "Deleted", "U_Variety", "SalPackUn", "U_Brand", "U_Unit", "U_Sub_Group" 
            FROM "JIVO_OIL_HANADB"."OITM" 
            WHERE "ItemCode" = ''{itemCode}'' AND "ItemCode" LIKE ''RM%'' AND "U_Unit" = ''OIL'' ')
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
        
    @staticmethod
    def get_all_pos():
        return """
            SELECT * FROM OPENQUERY(HANADB112, '
            SELECT 
                -- ===== Contract Information (PO details From OPOR and POR1) =====
                T3."DocNum" AS "PO Number",
                T3."DocDate" AS "PO Date",
                T0."DocStatus" AS "Status",
                T2."ItemCode" AS "Product Code",
                T2."Dscription" AS "Product",
                T0."CardName" AS "Vendor",
                T2."Quantity" AS "Contract Qty",
                T2."Price" AS "Contract Rate",
                T2."LineTotal" AS "Contract Value",

                -- ===== Loading Details (UDFs from PDN1) =====
                T1."Quantity" AS "Load Qty",
                T1."U_UNE_CUNT" AS "Unload Qty",
                T1."U_UNE_LTS" AS "Allowance",

                -- ===== Transport & Freight Details (UDFs from OPDN) =====
                T0."U_TransporterName" AS "Transporter",
                T0."U_VehicleNoM" AS "Vehicle No",
                T0."U_BilltyNumber" AS "Bilty No",
                T0."U_BiltyDate" AS "Bilty Date",

                -- ===== GRPO & Invoice Details =====
                T0."DocNum" AS "GRPO Number",
                T0."DocDate" AS "GRPO Date",
                T4."NumAtCard" AS "Invoice Number",

                -- ===== Summary & Landed Costs =====
                T1."LineTotal" AS "Basic Amount",

                -- FIX applied here: Changed CostSum to TtlExpndLC
                IFNULL(T7."TtlExpndLC", 0) AS "Landed Cost", 

                T4."DocTotal" AS "Net Amount"

            FROM "JIVO_OIL_HANADB"."OPDN" T0                                     -- GRPO Header
            INNER JOIN "JIVO_OIL_HANADB"."PDN1" T1 ON T0."DocEntry" = T1."DocEntry" -- GRPO Lines

            -- Join back to the Purchase Order Lines
            LEFT JOIN "JIVO_OIL_HANADB"."POR1" T2 ON T1."BaseEntry" = T2."DocEntry" 
                             AND T1."BaseLine" = T2."LineNum" 
                             AND T1."BaseType" = 22          -- 22 ensures it only links to POs

            -- Join back to Purchase Order Header
            LEFT JOIN "JIVO_OIL_HANADB"."OPOR" T3 ON T2."DocEntry" = T3."DocEntry"

            -- Join to AP Invoice Lines & Header
            LEFT JOIN "JIVO_OIL_HANADB"."PCH1" T5 ON T5."BaseEntry" = T0."DocEntry" 
                             AND T5."BaseLine" = T1."LineNum"
                             AND T5."BaseType" = 20          -- 20 ensures it only links to GRPOs
            LEFT JOIN "JIVO_OIL_HANADB"."OPCH" T4 ON T5."DocEntry" = T4."DocEntry"

            -- Landed Cost Link (IPF1 uses OrigLine for the base line reference)
            LEFT JOIN "JIVO_OIL_HANADB"."IPF1" T7 ON T7."BaseEntry" = T0."DocEntry" 
                             AND T7."OrigLine" = T1."LineNum" 
                             AND T7."BaseType" = 20
            LEFT JOIN "JIVO_OIL_HANADB"."OIPF" T6 ON T7."DocEntry" = T6."DocEntry"

            -- Add a WHERE clause to filter for a specific document or date range
            WHERE T3."DocDate" > ''2025-03-31 00:00:00.000'' AND T2."ItemCode" LIKE ''RM%'' ')
        """


    @staticmethod
    def get_single_po(grpo_no):
        return f"""
            SELECT * FROM OPENQUERY(HANADB112, '
            SELECT 
                -- ===== Contract Information (PO details From OPOR and POR1) =====
                T3."DocNum" AS "PO Number",
                T3."DocDate" AS "PO Date",
                T0."DocStatus" AS "Status",
                T2."ItemCode" AS "Product Code",
                T2."Dscription" AS "Product",
                T0."CardName" AS "Vendor",
                T2."Quantity" AS "Contract Qty",
                T2."Price" AS "Contract Rate",
                T2."LineTotal" AS "Contract Value",

                -- ===== Loading Details (UDFs from PDN1) =====
                T1."Quantity" AS "Load Qty",
                T1."U_UNE_CUNT" AS "Unload Qty",
                T1."U_UNE_LTS" AS "Allowance",

                -- ===== Transport & Freight Details (UDFs from OPDN) =====
                T0."U_TransporterName" AS "Transporter",
                T0."U_VehicleNoM" AS "Vehicle No",
                T0."U_BilltyNumber" AS "Bilty No",
                T0."U_BiltyDate" AS "Bilty Date",

                -- ===== GRPO & Invoice Details =====
                T0."DocNum" AS "GRPO Number",
                T0."DocDate" AS "GRPO Date",
                T4."NumAtCard" AS "Invoice Number",

                -- ===== Summary & Landed Costs =====
                T1."LineTotal" AS "Basic Amount",

                -- FIX applied here: Changed CostSum to TtlExpndLC
                IFNULL(T7."TtlExpndLC", 0) AS "Landed Cost", 

                T4."DocTotal" AS "Net Amount"

            FROM "JIVO_OIL_HANADB"."OPDN" T0                                     -- GRPO Header
            INNER JOIN "JIVO_OIL_HANADB"."PDN1" T1 ON T0."DocEntry" = T1."DocEntry" -- GRPO Lines

            -- Join back to the Purchase Order Lines
            LEFT JOIN "JIVO_OIL_HANADB"."POR1" T2 ON T1."BaseEntry" = T2."DocEntry" 
                             AND T1."BaseLine" = T2."LineNum" 
                             AND T1."BaseType" = 22          -- 22 ensures it only links to POs

            -- Join back to Purchase Order Header
            LEFT JOIN "JIVO_OIL_HANADB"."OPOR" T3 ON T2."DocEntry" = T3."DocEntry"

            -- Join to AP Invoice Lines & Header
            LEFT JOIN "JIVO_OIL_HANADB"."PCH1" T5 ON T5."BaseEntry" = T0."DocEntry" 
                             AND T5."BaseLine" = T1."LineNum"
                             AND T5."BaseType" = 20          -- 20 ensures it only links to GRPOs
            LEFT JOIN "JIVO_OIL_HANADB"."OPCH" T4 ON T5."DocEntry" = T4."DocEntry"

            -- Landed Cost Link (IPF1 uses OrigLine for the base line reference)
            LEFT JOIN "JIVO_OIL_HANADB"."IPF1" T7 ON T7."BaseEntry" = T0."DocEntry" 
                             AND T7."OrigLine" = T1."LineNum" 
                             AND T7."BaseType" = 20
            LEFT JOIN "JIVO_OIL_HANADB"."OIPF" T6 ON T7."DocEntry" = T6."DocEntry"

            -- Add a WHERE clause to filter for a specific document or date range
            WHERE T0."DocNum" = ''{grpo_no}''')
        """
    @staticmethod
    def get_balance_sheet():
        return """
        SELECT * FROM OPENQUERY(HANADB112, '
                WITH "VendorLatestTransaction" AS (
                    SELECT
                        a."CardCode",
                        a."CardName",
                        CAST(a."Balance" AS DECIMAL(18,2)) AS "Balance",
                        b."RefDate" AS "Last Transaction Date",
                        CAST(b."Debit" AS DECIMAL(18,2)) AS "Last Transanction Amount",
                        ROW_NUMBER() OVER (PARTITION BY a."CardCode" ORDER BY b."RefDate" DESC) AS "RowNum"
                    FROM "JIVO_OIL_HANADB"."OCRD" a
                    INNER JOIN "JIVO_OIL_HANADB"."JDT1" b ON a."CardCode" = b."ShortName"
                    WHERE b."RefDate" >= ''2024-10-01'' AND b."Debit" > 0 AND
                    a."CardCode" IN (
                        ''CUSTA000908'', ''CUSTA000887'', ''CUSTA000907'', ''VENDA000005'', ''VENDA000038'',
                        ''VENDA000102'', ''VENDA000149'', ''VENDA000316'', ''VENDA000509'', ''VENDA000724'',
                        ''VENDA001035'', ''VENDA001048'', ''VENDA001203'', ''CUSTA000341'', ''VENDA000103'',
                        ''VENDA000178'', ''VENDA000205'', ''VENDA000224'', ''VENDA000083'', ''VENDA000245'',
                        ''VENDA000255'', ''VENDA000265'', ''VENDA000342'', ''VENDA000496'', ''VENDA000693'',
                        ''VENDA000698'', ''VENDA000714'', ''VENDA001442'', ''VENDA001450'', ''VENDA000784'',
                        ''VENDA000804'', ''VENDA000916'', ''VENDA000950'', ''VENDA000966'', ''VENDA000967'',
                        ''VENDA001028'', ''VENDA001030'', ''VENDA001175'', ''VENDA001424'', ''VENDA001240'',
                        ''VENDA001276'', ''VENDA001287'', ''VENDA001288'', ''VENDA001403'', ''VENDA001390'',
                        ''VENDA001423'', ''VENDA001559'', ''VENDA000671'', ''VENDA000616'', ''VENDA001304'',
                        ''VENDA001315'', ''VENDA001339'', ''VENDA001347'', ''VENDA001358'', ''VENDA001375'',
                        ''VENDA000498'', ''VENDA001494'', ''VENDA001386'', ''VENDA001272'', ''VENDA000596'',
                        ''VENDA001028'', ''VENDA001303'', ''VENDA000614'', ''VENDA000279'', ''VENDA000599'',
                        ''VENDA000953'', ''VENDA001132'', ''VENDA001565'', ''VENDA000212'', ''VENDA000043'',
                        ''VENDA000580'', ''VENDA000493'', ''VENDA001421'', ''VENDA001353'', ''VENDA000220'',
                        ''VENDA001543'', ''VENDA001331'', ''VENDA000966'', ''VENDA001022'', ''VENDA000994'',
                        ''VENDA001472'', ''VENDA001329'', ''VENDA001291'', ''VENDA001138'', ''VENDA001295'',
                        ''VENDA000593'', ''VENDA000731'', ''VENDA000947'', ''VENDA001287'', ''VENDA001278'',
                        ''VENDA001490'', ''VENDA000256'', ''VENDA000556'', ''VENDA001107'', ''VENDA001239'',
                        ''VENDA000482'', ''VENDA000967'', ''VENDA001373'', ''VENDA001174'', ''VENDA000104'',
                        ''VENDA001555'', ''VENDA001293'', ''VENDA000750'', ''VENDA000325'', ''VENDA000931'',
                        ''VENDA000399'', ''VENDA001521'', ''VENDA000503'', ''VENDA000327'', ''VENDA000775'',
                        ''VENDA000020'', ''VENDA001334'', ''VENDA001335'', ''VENDA000208'', ''VENDA000676'',
                        ''VENDA001170'', ''VENDA000150'', ''VENDA001556'', ''VENDA000703'', ''VENDA001030'',
                        ''VENDA000387'', ''VENDA000629'', ''VENDA000940'', ''VENDA001541'', ''VENDA001052'',
                        ''VENDA001207'', ''VENDA001242'', ''VENDA000382'', ''VENDA001531'', ''CUSTA001092'',
                        ''VENDA000930'', ''VENDA000252'', ''VENDA000633'', ''VENDA000052'', ''VENDA001326'',
                        ''VENDA000597'', ''VENDA000388'', ''VENDA001240'', ''VENDA000558'', ''VENDA000161'',
                        ''VENDA001199'', ''VENDA000006'', ''VENDA001233'', ''VENDA001296'', ''VENDA000934'',
                        ''VENDA000202'', ''VENDA001263'', ''VENDA000527'', ''VENDA000134''
                    )
                )
                SELECT "CardCode", "CardName", "Balance", "Last Transaction Date", "Last Transanction Amount"
                FROM "VendorLatestTransaction"
                WHERE "RowNum" = 1 AND "Balance" <> 0
                ORDER BY "Balance"
            ')
        """
        
    def get_open_grpos(self):
        return """
        SELECT * FROM OPENQUERY(HANADB112, '
        SELECT 
            T0."DocNum" AS "GRPO Number",
            T0."NumAtCard" AS "Vendor Ref No",
            T2."U_NAME" AS "User Name",
            T0."CardName" AS "Vendor Name",
            T1."WhsCode" AS "Warehouse",
            DAYS_BETWEEN(T0."DocDate", CURRENT_DATE) AS "Pending Days"
        FROM "JIVO_OIL_HANADB"."OPDN" T0
        INNER JOIN "JIVO_OIL_HANADB"."PDN1" T1 ON T0."DocEntry" = T1."DocEntry"
        
        -- Join for User Name
        LEFT JOIN "JIVO_OIL_HANADB"."OUSR" T2 ON T0."UserSign" = T2."USERID"
    
        WHERE T0."DocDate" >= ''2026-01-01'' 
          AND T1."ItemCode" LIKE ''RM%'' 
          AND T0."DocStatus" = ''O'' 
          AND T1."WhsCode" IN (''BH-GJ'', ''BH-CRUDE'', ''BH-VA'')
        ORDER BY "Pending Days" DESC
    ')
    """
    
    
    def get_unique_warehouse(self):
        return """
            SELECT DISTINCT Warehouse
            FROM (
            
                -- ===== OLD SAP DATA =====
                SELECT 
                    'Old' AS SAP,
                    A.Warehouse COLLATE SQL_Latin1_General_CP1_CI_AS AS Warehouse,
                    CAST(A.TransType AS NVARCHAR(MAX)) AS TransTypeId,
                    CASE 
                        WHEN A.TransType IN (13,14,15,16)        THEN 'Sales'
                        WHEN A.TransType IN (18,19,20,21)        THEN 'Purchase'
                        WHEN A.TransType IN (59,60,10000071,202) THEN 'Production'
                        WHEN A.TransType IN (67)                 THEN 'Stocks Transfer'
                        WHEN A.TransType IN (69)                 THEN 'Landed Cost'
                        WHEN A.TransType IN (162)                THEN 'Inventory Revaluation'
                        ELSE 'Check' 
                    END AS TransType,
                    CASE 
                        WHEN B.U_Type = 'Cotton Seed Oil' THEN 'Cotton Seed'
                        WHEN B.U_Type = 'Gold'            THEN 'Blended'
                        ELSE B.U_Type 
                    END COLLATE SQL_Latin1_General_CP1_CI_AS AS U_Sub_Group,   -- ⚠️ named U_Sub_Group to match other UNIONs
                    T2.ChapterID COLLATE SQL_Latin1_General_CP1_CI_AS AS ChapterID,
                    CASE 
                        WHEN B.Series = 1353 THEN 'Finished'
                        WHEN B.Series = 1356 THEN 'Loose Oil'
                    END AS [Stock Type],
                    A.ItemCode COLLATE SQL_Latin1_General_CP1_CI_AS AS IteCode,
                    B.ItemName COLLATE SQL_Latin1_General_CP1_CI_AS AS ItemName,
                    B.U_IsLiter COLLATE SQL_Latin1_General_CP1_CI_AS AS IsLiter,
                    (A.InQty - A.OutQty)               AS Quantity,
                    (A.InQty - A.OutQty) * B.SalPackUn AS Liter
                FROM OINM A
                INNER JOIN OITM B  ON A.ItemCode  = B.ItemCode
                INNER JOIN OCHP T2 ON T2.AbsEntry = B.ChapterId
                WHERE A.DocDate BETWEEN '2025-04-01' AND '2024-09-30'
                  AND B.U_IsLiter = 'Y'

                UNION ALL

                -- ===== NEW SAP DATA (HANA - Transactions) =====
                SELECT * FROM OPENQUERY(HANADB112, '
                    SELECT ''New'' SAP, T0."Warehouse", CAST(T0."TransType" AS VARCHAR(20)) TransType,
                    CASE 
                        WHEN T0."TransType" IN (13,14,15,16)        THEN ''Sales''
                        WHEN T0."TransNum" = 14223                  THEN ''Purchase''
                        WHEN T0."TransType" IN (18,19,20,21)        THEN ''Purchase''
                        WHEN T0."TransType" IN (59,60,10000071,202) THEN ''Production''
                        WHEN T0."TransType" IN (67)                 THEN ''Stocks Transfer''
                        WHEN T0."TransType" IN (69)                 THEN ''Landed Cost''
                        WHEN T0."TransType" IN (162)                THEN ''Inventory Revaluation''
                        ELSE ''Check'' 
                    END "VoucherType",
                    CASE 
                        WHEN T1."ItemCode" IN (''RM0000012'',''RM0000013'',''RM0000014'') THEN ''OLIVE IMPORTED''
                        WHEN T1."ItemCode" IN (''RM0000019'')                             THEN ''SUNFLOWER IMPORTED''
                        WHEN T1."ItemName" LIKE ''GIFT%''                                 THEN ''BLENDED''
                        ELSE T1."U_Sub_Group" 
                    END "U_Sub_Group",
                    T2."ChapterID" "HSN",
                    CASE WHEN T1."Series"=389 THEN ''Finished'' WHEN T1."Series"=392 THEN ''Loose Oil'' END "Stock Type",
                    T0."ItemCode", T1."ItemName", T1."U_IsLitre",
                    SUM(T0."InQty" - T0."OutQty") Quantity,
                    SUM((T0."InQty" - T0."OutQty") * T1."SalPackUn") Liter
                    FROM "JIVO_OIL_HANADB"."OINM" T0
                    INNER JOIN "JIVO_OIL_HANADB"."OITM" T1 ON T0."ItemCode" = T1."ItemCode"
                    INNER JOIN "JIVO_OIL_HANADB"."OCHP" T2 ON T2."AbsEntry" = T1."ChapterID"
                    WHERE T0."DocDate" BETWEEN ''2025-04-01'' AND CURRENT_DATE
                      AND T1."U_IsLitre" = ''Y''
                    GROUP BY T1."ItemCode", T0."TransType", T0."TransNum",
                    CASE WHEN T1."Series"=389 THEN ''Finished'' WHEN T1."Series"=392 THEN ''Loose Oil'' END,
                    T1."U_Sub_Group", T0."ItemCode", T1."ItemName", T1."U_IsLitre", T0."Warehouse", T2."ChapterID"
                ')

                UNION ALL

                -- ===== NEW SAP DATA (HANA - Closing Balance) =====
                SELECT * FROM OPENQUERY(HANADB112, '
                    SELECT ''New'' SAP, T0."Warehouse", ''CB'', ''Closing'',
                    CASE 
                        WHEN T1."ItemCode" IN (''RM0000012'',''RM0000013'',''RM0000014'') THEN ''OLIVE IMPORTED''
                        WHEN T1."ItemCode" IN (''RM0000019'')                             THEN ''SUNFLOWER IMPORTED''
                        WHEN T1."ItemName" LIKE ''GIFT%''                                 THEN ''BLENDED''
                        ELSE T1."U_Sub_Group" 
                    END "U_Sub_Group",
                    T2."ChapterID",
                    CASE WHEN T1."Series"=389 THEN ''Finished'' WHEN T1."Series"=392 THEN ''Loose Oil'' END "Stock Type",
                    T0."ItemCode", T1."ItemName", T1."U_IsLitre",
                    SUM(T0."InQty" - T0."OutQty") Quantity,
                    SUM((T0."InQty" - T0."OutQty") * T1."SalPackUn") Liter
                    FROM "JIVO_OIL_HANADB"."OINM" T0
                    INNER JOIN "JIVO_OIL_HANADB"."OITM" T1 ON T0."ItemCode" = T1."ItemCode"
                    INNER JOIN "JIVO_OIL_HANADB"."OCHP" T2 ON T2."AbsEntry" = T1."ChapterID"
                    WHERE T0."DocDate" <= CURRENT_DATE
                      AND T1."U_IsLitre" = ''Y''
                    GROUP BY T1."ItemCode", T0."Warehouse", T1."U_Sub_Group",
                    T0."ItemCode", T1."ItemName", T1."U_IsLitre", T1."Series", T2."ChapterID"
                ')

                UNION ALL

                -- ===== NEW SAP DATA (HANA - Opening Balance) =====
                SELECT * FROM OPENQUERY(HANADB112, '
                    SELECT ''New'' SAP, T0."Warehouse", ''OB'', ''Opening'',
                    CASE 
                        WHEN T1."ItemCode" IN (''RM0000012'',''RM0000013'',''RM0000014'') THEN ''OLIVE IMPORTED''
                        WHEN T1."ItemCode" IN (''RM0000019'')                             THEN ''SUNFLOWER IMPORTED''
                        WHEN T1."ItemName" LIKE ''GIFT%''                                 THEN ''BLENDED''
                        ELSE T1."U_Sub_Group" 
                    END "U_Sub_Group",
                    T2."ChapterID",
                    CASE WHEN T1."Series"=389 THEN ''Finished'' WHEN T1."Series"=392 THEN ''Loose Oil'' END "Stock Type",
                    T0."ItemCode", T1."ItemName", T1."U_IsLitre",
                    SUM(T0."InQty" - T0."OutQty") Quantity,
                    SUM((T0."InQty" - T0."OutQty") * T1."SalPackUn") Liter
                    FROM "JIVO_OIL_HANADB"."OINM" T0
                    INNER JOIN "JIVO_OIL_HANADB"."OITM" T1 ON T0."ItemCode" = T1."ItemCode"
                    INNER JOIN "JIVO_OIL_HANADB"."OCHP" T2 ON T2."AbsEntry" = T1."ChapterID"
                    WHERE T0."DocDate" < ''2025-04-01''
                      AND T1."U_IsLitre" = ''Y''
                    GROUP BY T1."ItemCode", T0."Warehouse", T1."U_Sub_Group",
                    T0."ItemCode", T1."ItemName", T1."U_IsLitre", T1."Series", T2."ChapterID"
                ')

            ) AS FullResult

        
        """
    def get_inventory(self):
        return f"""
            SELECT Warehouse as Warehouse ,U_Sub_Group as Category, SUM(ABS(LITER)) AS Total 
            FROM   
            (
                SELECT * FROM OPENQUERY(HANADB112, '
                    SELECT ''New'' SAP, T0."Warehouse", ''CB'', ''Closing'',
                    CASE 
                        WHEN T1."ItemCode" IN (''RM0000012'',''RM0000013'',''RM0000014'') THEN ''OLIVE IMPORTED''
                        WHEN T1."ItemCode" IN (''RM0000019'')                             THEN ''SUNFLOWER IMPORTED''
                        WHEN T1."ItemName" LIKE ''GIFT%''                                 THEN ''BLENDED''
                        ELSE T1."U_Sub_Group" 
                    END "U_Sub_Group",
                    T2."ChapterID",
                    CASE WHEN T1."Series"=389 THEN ''Finished'' WHEN T1."Series"=392 THEN ''Loose Oil'' END "Stock Type",
                    T0."ItemCode", T1."ItemName", T1."U_IsLitre",
                    SUM(T0."InQty" - T0."OutQty") Quantity,
                    SUM((T0."InQty" - T0."OutQty") * T1."SalPackUn") Liter
                    FROM "JIVO_OIL_HANADB"."OINM" T0
                    INNER JOIN "JIVO_OIL_HANADB"."OITM" T1 ON T0."ItemCode" = T1."ItemCode"
                    INNER JOIN "JIVO_OIL_HANADB"."OCHP" T2 ON T2."AbsEntry" = T1."ChapterID"
                    WHERE T0."DocDate" <= CURRENT_DATE
                      AND T1."U_IsLitre" = ''Y''
                      AND T1."ItemCode" LIKE ''RM%''
                    GROUP BY T1."ItemCode", T0."Warehouse", T1."U_Sub_Group",
                    T0."ItemCode", T1."ItemName", T1."U_IsLitre", T1."Series", T2."ChapterID"
                ')
            ) AS Result
            WHERE U_Sub_Group NOT IN ('GHEE')
            GROUP BY U_Sub_Group , Warehouse
            ORDER BY Warehouse
        """