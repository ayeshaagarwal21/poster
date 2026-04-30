from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import google.generativeai as genai
import psycopg2

# ---------------- API CONFIG ----------------
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Use stable model
model = genai.GenerativeModel("gemini-pro")

# ---------------- DB CONNECTION ----------------
def connect_db():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT")
        )
        return conn
    except:
        return None

def create_table():
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS query_logs (
            id SERIAL PRIMARY KEY,
            user_input TEXT,
            bot_response TEXT
        );
        """)
        conn.commit()
        cur.close()
        conn.close()

def log_query(user_input, bot_response):
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO query_logs (user_input, bot_response) VALUES (%s, %s);",
            (user_input, bot_response)
        )
        conn.commit()
        cur.close()
        conn.close()

# ---------------- SAFE AI FUNCTION ----------------
def my_output(query):
    try:
        response = model.generate_content(query)
        return response.text
    except Exception:
        return "⚠️ AI service is currently unavailable due to API limits."

# ---------------- UI ----------------
st.set_page_config(page_title="CHAT_BOT")
st.header("CHAT_BOT")

user_input = st.text_input("Input", key="input")
submit = st.button("Ask your query")

# DB warning
if not connect_db():
    st.warning("⚠️ Database not connected. Running without logging.")

create_table()

if submit and user_input:
    response = my_output(user_input)

    # log safely
    log_query(user_input, response)

    st.subheader("Response:")
    st.write(response)