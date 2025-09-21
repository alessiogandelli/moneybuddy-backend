import sqlite3
import json
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd

# Carica le variabili d'ambiente
load_dotenv()

# In .env anche OPENAI_API_KEY
HF_API_KEY = os.getenv("HF_API_KEY")
DB_PATH = os.getenv("DB_PATH")

def get_database_schema(db_path: str) -> str:
    with open("/home/dema/Downloads/transactions_schema_summary.md", "r", encoding="utf-8") as f:
        return f.readlines()

def call_llm(prompt: str) -> str:
    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
        api_key=os.environ["HF_API_KEY"],
    )

    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b:novita",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
    )
    response = dict(completion.choices[0].message)
    return response["content"]

def execute_database_query(sql_query: str) -> Dict[str, Any]:
    """
    Esegue una query SQL sul database delle transazioni
    
    Args:
        sql_query: Query SQL da eseguire
        is_final_answer: True se il risultato è la risposta finale, False se serve per ulteriore elaborazione
    
    Returns:
        Risultati della query formattati
    """
    try:
        # Get DB_PATH from environment
        DB_PATH = os.getenv("DB_PATH")
        
        # More detailed error checking
        if not DB_PATH:
            return {"error": "DB_PATH environment variable not set"}
        if not os.path.exists(DB_PATH):
            return {"error": f"Database file not found at path: {DB_PATH}"}
        
        # Clean and validate SQL query
        sql_query = sql_query.strip()
        if not sql_query:
            return {"error": "Empty SQL query provided"}
        
        # Security checks - be more specific about what we're checking
        sql_upper = sql_query.upper()
        dangerous_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE', 'REPLACE']
        
        for keyword in dangerous_keywords:
            if keyword in sql_upper:
                return {"error": f"Dangerous keyword '{keyword}' not allowed. Only SELECT queries are permitted."}
        
        # Check if it starts with SELECT (after removing whitespace and comments)
        cleaned_query = sql_upper.lstrip()
        if not cleaned_query.startswith('SELECT'):
            return {"error": "Only SELECT queries are allowed"}
        
        """Using pandas - returns DataFrame directly"""
        try:
            # This automatically handles connection, execution, and conversion to DataFrame
            df = pd.read_sql_query(sql_query, sqlite3.connect(DB_PATH))
                        
        except sqlite3.Error as e:
            return {"error": f"SQL execution error: {str(e)}", "dataframe": None}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}", "dataframe": None}

        conn = None
        try:
            conn = sqlite3.connect(DB_PATH)                
            df = pd.read_sql_query(sql_query, conn)
                        
            return {
                "success": True,
                "dataframe": df,
                "query_info": {
                    "rows": len(df),
                    "columns": list(df.columns),
                    "dtypes": df.dtypes.to_dict()
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "dataframe": None,
                "error": str(e)
            }
        finally:
            if conn:
                conn.close()
        
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

def parse_llm_response(response: str) -> tuple[Optional[str], Optional[bool], Optional[str]]:
    """
    Estrae informazioni dalla risposta dell'LLM
    
    Returns:
        (sql_query, is_final_answer, direct_response)
    """
    try:
        # Cerca un blocco JSON nella risposta
        start = response.find('{')
        end = response.rfind('}') + 1
        
        if start != -1 and end > start:
            json_str = response[start:end]
            data = json.loads(json_str)
            
            return data
        
        # Se non c'è JSON, è una risposta diretta
        return None
        
    except:
        # Se fallisce il parsing, tratta come risposta diretta
        return None

class FinanceManager:
    def __init__(self):
        self.schema = get_database_schema(DB_PATH) if DB_PATH else "Schema non disponibile"
        
    def get_system_prompt(self, user_query: str="", task: str="", db_result = None) -> str:
        """Genera il system prompt per l'LLM"""
        if task == "SQL_query":
            return f"""You are Moneyca, an AI Finance Manager specialized in analyzing financial transactions and acting as a reliable assistant.  
Your task is to provide a conversational interface and support to the user who is interacting with their banking/money management application.  
You know the user and you have access to the following database, which contains all of the user’s past transactions along with their details and metadata.

Here is the Database schema summary for the database:
{self.schema}

INSTRUCTIONS:
1. If you can answer the user’s question without requiring additional information/data from the database, respond directly in a polite and friendly manner.  
2. If you need data from the database, generate a JSON response in the following SQL query format:  
{{"query": "SELECT ... FROM transactions WHERE ...", "stop": true/false}}

- "stop": true → Use this when the query result itself is the final answer that can be directly shown to the user, without needing additional reasoning or processing.

- "stop": false → Use this when the query result is only intermediate data that you (the AI) still need to analyze, process, or combine with other information before providing the final answer to the user. (Example: retrieving the average spent on transport to later suggest saving tips.)

EXAMPLES:
- Question: "How much did I spend on groceries this month?"  
  Answer: {{"query": "SELECT SUM(ABS(amount)) FROM transactions WHERE amount < 0 AND val_date >= date('now', 'start of month') AND text_creditor LIKE '%groceries%'", "stop": true}}
- Question: "How can I save money on transport?"  
  Answer: {{"query": "SELECT AVG(ABS(amount)) as avg_transport FROM transactions WHERE amount < 0 AND text_creditor LIKE '%transport%'", "stop": false}}

Question: {user_query}  
Answer:"""
        elif task == "SQL_conclusion":
            return f"""You are Moneyca, an AI Finance Manager specialized in analyzing financial transactions and acting as a reliable assistant.
Your task is to provide a conversational interface and support to the user who is interacting with their banking / money-management application.
You know the user and you have access to the following database, which contains all of the user's past transactions along with their details and metadata.

Please respond to the following user request: {user_query}

The following data, extracted from the user's database, are relevant to the request:
{db_result["dataframe"]}

Provide a detailed, helpful response:"""
        elif task == "categorization_definition":
            return f"""You are Moneyca, an AI Finance Manager specialized in analyzing financial transactions and acting as a reliable assistant.
Your task is to provide a conversational interface and support to the user who is interacting with their banking / money-management application.
You know the user and you have access to the following database, which contains all of the user's past transactions along with their details and metadata.

I have a list of merchant names from the user's transactions database.
Your task is to analyze these merchant names and find a list of categories that best describe the type of business or service each merchant provides.

Provide as output a json array with just all the categorie names, without assigning them to merchants. The categories should be concise and relevant to the types of merchants provided. Examples of categories could include "Groceries", "Dining", "Transport", "Utilities", "Entertainment", etc. If a merchant name is ambiguous or does not clearly fit into a specific category, assign it to a general category "Other".

Example output:
{{"categories": ["Groceries", "Dining", "Transport", "Utilities", "Entertainment"]}}

Here are the merchant names:
{user_query}"""
        elif task =="categorization_assignment":
            return f"""You are Moneyca, an AI Finance Manager specialized in analyzing financial transactions and acting as a reliable assistant.
Your task is to provide a conversational interface and support to the user who is interacting with their banking / money-management application.
You know the user and you have access to the following database, which contains all of the user's past transactions along with their details and metadata.

I have a list of merchant names from the user's transactions database and a list of categories.
Your task is to analyze these merchant names and assign each merchant to the most appropriate category from the provided list.
Here are the merchant names:
{', '.join(user_query)}

Here are the categories:
{', '.join(db_result)}

Provide as output a json list of couples with just the categories assigned to each merchant, in the same order as the merchant names provided. If a merchant name is ambiguous or does not clearly fit into a specific category, assign it to a general category "Other".

Example output:
{{"merchant_categories": [("marchant_name_x", "category_n"), ("merchant_name_y", "category_n2"), ("merchant_name_z", "category_n3"),..]}}"""

    def categorization(self):
        """Add categories to transactions table"""
        conn = sqlite3.connect(DB_PATH)
        
        # Check if category column exists
        columns = pd.read_sql_query("PRAGMA table_info(transactions)", conn)['name'].tolist()
        if 'category' in columns:
            # just for testing
            other_cols = ', '.join([col for col in columns if col != 'category'])
            conn.executescript(f"CREATE TABLE temp_transactions AS SELECT {other_cols} FROM transactions; DROP TABLE transactions; ALTER TABLE temp_transactions RENAME TO transactions;")
            conn.close()
            return "Category column already exists"
        
        # Get unique merchants and categorize them
        merchants = pd.read_sql_query("SELECT DISTINCT merchant_name FROM transactions WHERE merchant_name IS NOT NULL", conn)['merchant_name'].tolist()
        unique_merchants = list(set(merchants))

        system_prompt = self.get_system_prompt(user_query = unique_merchants, task= "categorization_definition")
        print(f" First prompt: {system_prompt}")
        response = call_llm(system_prompt)
        print(f"LLM SQL response: {response}")
        data = parse_llm_response(response)
        if not data:
            return "Failed to get categories from LLM"
        categories = data.get("categories")
        merchant_map = {"merchant_categories": []}
        if not isinstance(categories, list):
            print("No categories found")
        else:
            print("\n\n")
            print(merchants)
            input("Press Enter to continue...")
            i = 0
            for i in range(0, len(merchants), 10):
                group = merchants[i:i+20]
                # process group of 20 merchants
                print(group)
                system_prompt = self.get_system_prompt(user_query = group, task= "categorization_assignment", db_result = categories)
                print(f" First prompt: {system_prompt}")
                response = call_llm(system_prompt)
                data = parse_llm_response(response)
                if data:
                    merchant_map["merchant_categories"].extend(data["merchant_categories"])
                print("\n\n\n\n________________________________")
                print(f"LLM so far: {merchant_map}")
                print("\n\n\n")
        
        # Add column and update rows
        conn.execute("ALTER TABLE transactions ADD COLUMN category VARCHAR(50)")
        for merchant, category in dict(merchant_map).items():
            conn.execute("UPDATE transactions SET category = ? WHERE merchant_name = ?", (category, merchant))
        conn.execute("UPDATE transactions SET category = 'Unknown' WHERE merchant_name IS NULL")
        
        conn.commit()
        conn.close()
        return f"Added categories for {len(merchants)} merchants"

    def process_query(self, user_query: str) -> str:
        
        # Chiedi all'LLM se serve estrarre dal database SQL
        system_prompt = self.get_system_prompt(user_query, task= "SQL_query")
        print(f" First prompt: {system_prompt}")
        response = call_llm(system_prompt)
        print(f"LLM SQL response: {response}")

        
        # Parsing
        data = parse_llm_response(response)

        sql_query = data.get("query")
        is_final = data.get("stop", True)
        
        if not sql_query:
            return "Non sono riuscito a generare una query SQL appropriata."
        
        # STEP 3: Esegui la query
        db_result = execute_database_query(sql_query)
        print(f"From database: {db_result['dataframe']}")
        
        if "error" in db_result:
            return f"Errore nel database: {db_result['error']}"
        
        # STEP 4: Se è risposta finale, formatta e restituisci
        if is_final and not db_result['success']:
            return "Non ho trovato dati per la tua richiesta."
        
        # STEP 5: Se serve elaborazione, chiama di nuovo l'LLM con i dati
        context_prompt = self.get_system_prompt(user_query, "SQL_conclusion", db_result)
        return call_llm(context_prompt)

def main():
    """Funzione principale per testare il sistema"""
    if not HF_API_KEY:
        print("ERRORE: HF_TOKEN non trovato nelle variabili d'ambiente")
        return
    
    if not DB_PATH:
        print("ERRORE: DB_PATH non trovato nelle variabili d'ambiente")
        return
    
    manager = FinanceManager()
    
    while True:
        user_input = input("\nQuery: ").strip()
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
        if user_input.lower() == "categorization":
            result = manager.categorization()
            print(result)
        elif user_input:
            response = manager.process_query(user_input)
            print(f"LLM: {response}")

if __name__ == "__main__":
    main()