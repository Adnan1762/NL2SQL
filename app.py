from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import sqlite3
import google.generativeai as genai

# ✅ Set up your API key properly
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# ✅ Use a supported model like 'gemini-pro'
def get_genai_response(question, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt + "\n\nQuestion: " + question)
    return response.text.strip()

# ✅ Execute SQL query
def read_sql_query(sql, db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    try:
        cur.execute(sql)
        rows = cur.fetchall()
        conn.commit()
    except Exception as e:
        rows = [("Error", str(e))]
    conn.close()
    return rows

# ✅ Define Prompt
prompt = """
You are an expert in converting English questions to SQL queries.
The SQL database is called STUDENT and has the following columns: NAME, CLASS, SECTION, MARKS.

Examples:
Q: How many entries are there?
A: SELECT COUNT(*) FROM STUDENT;

Q: Show all students in Data Science.
A: SELECT * FROM STUDENT WHERE CLASS = "Data Science";

Q: Tell me all students
A: SELECT * FROM STUDENT;

Q: Show students with marks greater than 80
A: SELECT * FROM STUDENT WHERE MARKS > 80;

Important: Return only the SQL query without any markdown formatting, explanations, or the word 'SQL'.
"""

# ✅ Streamlit UI
st.set_page_config(page_title="NL2SQL with Google Generative AI")
st.header("Natural Language to SQL using GenAI")

question = st.text_input("Enter your question in English:", key="input")
submit = st.button("Submit")

if submit and question:
    try:
        sql_query = get_genai_response(question, prompt)
        
        # Clean up the response to extract only SQL
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        
        st.subheader("Generated SQL Query")
        st.code(sql_query, language="sql")

        result = read_sql_query(sql_query, "student.db")
        st.subheader("SQL Query Result")
        
        if result:
            for row in result:
                st.write(row)
        else:
            st.write("No results found.")
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.write("Please check your API key and try again.")