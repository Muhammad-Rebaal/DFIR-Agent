import os
import logging
from groq import Groq
from db import execute_query, get_schema
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.FileHandler("log.txt", mode="w"),
        logging.StreamHandler()
    ]
)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM = f"""You are an autonomous DFIR (Digital Forensics and Incident Response) AI Investigator.
Your objective is to investigate security incidents by hunting through raw telemetry data. You are not given the answers upfront; you must discover the attack chain organically.

You have access to a telemetry database via the `execute_sql` tool. Here is the current schema:
{get_schema()}

You have two tools at your disposal:
1. execute_sql[<SQL query>] - Runs a SQL query against the evidence database and returns the results. 
2. submit[<final answer>] - Submits your final investigative findings once the entire attack chain is verified.

Investigation Methodology:
- Formulate a clear hypothesis before running any query.
- Break complex problems down. Do not write massive nested subqueries. If you find a compromised user in Turn 1, just use that literal string in your Turn 2 query.
- Do not make blind assumptions about specific data values. Use exploratory queries (e.g., LIMIT 1, DISTINCT, or LIKE) to understand the data shape first.
- SELF-CRITIQUE: If a query returns 0 rows or an error, pause. Analyze WHY it failed. Did you assume a column name? Did you filter on a string that doesn't exist? Criticize your previous decision, correct your logic, and try a different pivot.
- Build a solid chain of evidence. Every IP, SID, or Email is a pivot point to the next stage of the attack.

Each turn, you MUST respond in the following exact format:
Thought: <your hypothesis, self-critique, and reasoning>
Action: execute_sql[<SQL query>]   OR   Action: submit[<final answer>]
"""

def run_agent(question, max_turns=8):
    logging.info(f"Starting investigation. Question: {question}")
    
    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": f"Question: {question}"}
    ]
    transcript = []
    
    for turn in range(max_turns):
        logging.info(f"Turn {turn + 1}")
        
        resp = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.0,
            max_tokens=1000
        )
        text = resp.choices[0].message.content
        transcript.append(text)
        messages.append({"role": "assistant", "content": text})
        
        logging.info(f"Agent Output:\n{text}")

        if "submit[" in text:
            answer = text.split("submit[")[1].split("]")[0]
            logging.info(f"Agent submitted final answer: {answer}")
            return answer, transcript
            
        if "execute_sql[" in text:
            query = text.split("execute_sql[")[1].split("]")[0]
            logging.info(f"Executing Query: {query}")
            
            obs = execute_query(query)
            logging.info(f"Observation returned {len(obs.splitlines()) - 1} rows of data.")
            logging.debug(f"Full Observation:\n{obs}")
            
            messages.append({"role": "user", "content": f"Observation: {obs}"})
            
    logging.warning("Agent reached maximum turns without submitting an answer.")
    return None, transcript

def generate_report(question, answer, transcript, filename="report.txt"):
    if not answer:
        answer = "Investigation timed out before a final conclusion was reached."
        
    logging.info(f"Generating final DFIR report -> {filename}")
    transcript_text = "\n".join(transcript)
    
    prompt = f"""You are a Senior Security Analyst. Based on the following AI agent investigation transcript, generate a professional DFIR Incident Response Report.
    
    Initial Trigger/Question: {question}
    Final Answer Discovered: {answer}
    
    Investigation Transcript:
    {transcript_text}
    
    Please write a concise, professional report including:
    - Executive Summary
    - Attack Timeline & Chain of Events
    - Compromised Entities (Accounts, IPs, SIDs)
    - Exfiltrated/Accessed Data
    
    Output ONLY the report text."""
    
    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1500
    )
    report_content = resp.choices[0].message.content
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    logging.info(f"Report successfully saved to {filename}")
    return report_content