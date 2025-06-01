from server.config import *
from llm_calls import *
from sql_calls import *
from utils.rag_utils import sql_rag_call

# --- User Input ---
user_question = "How many facade panels oriented to south?"

# --- Load SQL Database ---
db_path = "sql/building_panels.db"
db_schema = get_dB_schema(db_path)

# --- Retrieve most relevant table ---
# table_descriptions_path = "knowledge/table_descriptions.json" # we use this to help the llm understand which tables are important
# relevant_table, table_description = sql_rag_call(
#     user_question, table_descriptions_path, n_results=1
# )

# if relevant_table:
#     print(f"Most relevant table: {relevant_table}")
# else:
#     print("No relevant table found.")
#     exit()

# --- Filter Schema to relevant table ---

db_context = f"""unit_id	panel_id	room	orientation	is_exterior
187	3B_DOOR0	living room	Unknown	FALSE
187	3B_FLOOR1	living room	Unknown	FALSE
187	3B_ROOF2	living room	Unknown	FALSE
187	3B_WALL10	bathroom	North	TRUE
"""
# --- Generate SQL query from LLM ---
table_description = "This table contains information about panels of the units. Each row records a unique unit ID, their panel ID, the room function, orientation of each panel, and if it's exterior or not."
sql_query = generate_sql_query(db_context, table_description, user_question)
print(f"SQL Query: \n {sql_query}")

# --- LLM says insufficient info ---
if "No information" in sql_query:
    print("I'm sorry, but this database does not contain enough information to answer that question.")
    exit()

# --- Execute SQL with a self-debbuging feature ---
sql_query, query_result = fetch_sql(sql_query, db_context, user_question, db_path)

# -- If self-debugging failed after max_retries we give up
if not query_result:
    print("SQL query failed or returned no data.")
    print("I'm sorry but I was not able to find any relevant information to answer your question. Please, try again.")
    exit()

# --- Build natural language answer to user ---
final_answer = build_answer(sql_query, query_result, user_question)
print(f"Final Answer: \n {final_answer}")
