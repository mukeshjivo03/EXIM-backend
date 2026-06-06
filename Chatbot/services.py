import re
from django.db import connection
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

class ChatAgent:

    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0,
            groq_api_key =  os.getenv('GROQ_API_KEY')
        )

    def _get_database_schema(self):
        allowed_tables  = ['stock_status' , 'tank_item' , 'tank_item' , 'tank_data' , 'shortage_entries' , 'daily_prices' , 'jivo_rates']
        schema_text = ""

        with connection.cursor() as cursor:
            for table in allowed_tables:
                cursor.execute(f"""
                    SELECT 
                        column_name, 
                        data_type  
                    FROM information_schema.columns 
                    WHERE table_name = '{table}'
                """)

                columns = cursor.fetchall()
                schema_text  += f"Table: {table}\n" 
                for col in columns:
                    schema_text +=  f"  - {col[0]} ({col[1]})\n"  
            
        return schema_text
    

    def _validate_and_sanitize_sql(self, sql_query: str) -> bool:
        clean_query = sql_query.strip()
        if not re.match(r'^\s*SELECT', clean_query, re.IGNORECASE):
            return False

        forbidden_pattern = r'\b(DROP|DELETE|UPDATE|INSERT|ALTER|GRANT|TRUNCATE|CREATE)\b'
        if re.search(forbidden_pattern, clean_query, re.IGNORECASE):
            return False

        return True

    def execute_user_query(self , user_question:str) -> str:
        
        schema = self._get_database_schema()
        sql_prompt = ChatPromptTemplate.from_messages([
                ("system", (
                    "You are an expert PostgreSQL database administrator mapping business requests to queries.\n\n"
                    "Database Schema Context:\n{schema}\n"
                    "Rules:\n"
                    "1. Return ONLY raw SQL inside a single ```sql ... ``` block.\n"
                    "2. Always use case-insensitive partial matching (ILIKE '%value%') for string text lookups.\n"
                    "3. Never guess table joins. Use only the relationships specified in the context.\n\n"

                    "GOLDEN EXAMPLES FOR REFERENCE:\n"
                    "Question: What items do we have outside the factory?\n"
                    "SQL: SELECT rm_name, status, party_name FROM stock_status WHERE status ILIKE '%out%side%factory%';\n\n"

                    "Question: Show me the material item current volume inside tank T-01.\n"
                    "SQL: SELECT ti.item_name, td.volume, td.tank_code FROM tank_data td JOIN tank_item ti ON td.tank_code = ti.tank_code WHERE td.tank_code ILIKE '%T-01%';\n\n"

                    "Question: Check shortages for Jivo Wellness allocations.\n"
                    "SQL: SELECT * FROM shortage_entries WHERE party_name ILIKE '%jivo%';\n"
                )),
                ("human", "{question}")
            ])

        chain = sql_prompt | self.llm
        ai_message = chain.invoke({"schema" : schema , "question"  : user_question})
        raw_content = ai_message.content

        sql_match = re.search(r"```sql\s*(.*?)\s*```", raw_content, re.DOTALL | re.IGNORECASE)
        sql_query = sql_match.group(1) if sql_match else raw_content.strip()

        if not self._validate_and_sanitize_sql(sql_query):
            return "Security violation: The generated query contains disallowed operations."
    
        try:
            with connection.cursor() as cursor:
                # FIX: Change 'execute_query' to 'execute'
                cursor.execute(sql_query) 

                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()

                # Convert results to readable dictionaries
                db_results = [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            return f"Database interaction failed: {str(e)}"
        

        synthesis_prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful procurement dashboard assistant. Review the raw database results and construct a clean, professional, natural language answer for the user."),
            ("human", "User Question: {question}\nDatabase Row Data: {results}")
        ])

        synthesis_chain = synthesis_prompt | self.llm
        final_answer = synthesis_chain.invoke({"question": user_question, "results": str(db_results)})
        
        return final_answer.content
