import sqlite3
import pandas as pd
from data import signin_logs, alert_evidence, email_events, inbox_rules, calendar_events, user_emails_and_files, file_access_log, contacts_list, lunary_users, lunary_projects

con = sqlite3.connect("simulated_db.db", check_same_thread=False)

signin_logs.to_sql("signin_logs", con, if_exists="replace", index=False)
alert_evidence.to_sql("alert_evidence", con, if_exists="replace", index=False)
email_events.to_sql("email_events", con, if_exists="replace", index=False)
inbox_rules.to_sql("inbox_rules", con, if_exists="replace", index=False)
calendar_events.to_sql("calendar_events", con, if_exists="replace", index=False)
user_emails_and_files.to_sql("user_emails_and_files", con, if_exists="replace", index=False)
file_access_log.to_sql("file_access_log", con, if_exists="replace", index=False)
contacts_list.to_sql("contacts_list", con, if_exists="replace", index=False)
lunary_users.to_sql("lunary_users", con, if_exists="replace", index=False)
lunary_projects.to_sql("lunary_projects", con, if_exists="replace", index=False)

def execute_query(query: str) -> str:
    try:
        df = pd.read_sql_query(query, con)
        return df.to_string(index=False)
    except Exception as e:
        return f"Error: {e}"

def get_schema() -> str:
    """Dynamically generates the schema for all tables in the database."""
    tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", con)['name'].tolist()
    schema_str = "Available tables and columns:\n"
    for table in tables:
        columns = pd.read_sql_query(f"PRAGMA table_info({table})", con)['name'].tolist()
        schema_str += f"- {table}({', '.join(columns)})\n"
    return schema_str