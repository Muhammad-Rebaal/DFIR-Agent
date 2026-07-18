import logging
from data import signin_logs, alert_evidence, email_events, inbox_rules, calendar_events, user_emails_and_files, file_access_log, contacts_list, lunary_users, lunary_projects
from agent import run_agent, generate_report
from scorer import score, question, ground_truth_answer, solution_path
from regenerate import anonymize
import db

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s | %(levelname)s | %(message)s', 
    datefmt='%H:%M:%S',
    handlers=[
        logging.FileHandler("log.txt", mode="a"),
        logging.StreamHandler()
    ]
)

logging.info("Running Baseline Environment Test...")
answer1, transcript1 = run_agent(question, max_turns=12)
generate_report(question, answer1, transcript1, filename="report.txt")
reward1 = score(transcript1, answer1, ground_truth_answer, solution_path)
logging.info(f"Original Environment Target Answer Match Reward: {reward1}")
logging.info("="*50)

logging.info("Regenerating Structure-Preserving Environment (Anonymization)...")
s_logs, a_ev, e_ev, i_rl, c_ev, f_txt, fa_log, c_ls, l_us, l_pr, val_map = anonymize(
    signin_logs, alert_evidence, email_events, inbox_rules, calendar_events, user_emails_and_files, file_access_log, contacts_list, lunary_users, lunary_projects
)

s_logs.to_sql("signin_logs", db.con, if_exists="replace", index=False)
a_ev.to_sql("alert_evidence", db.con, if_exists="replace", index=False)
e_ev.to_sql("email_events", db.con, if_exists="replace", index=False)
i_rl.to_sql("inbox_rules", db.con, if_exists="replace", index=False)
c_ev.to_sql("calendar_events", db.con, if_exists="replace", index=False)
f_txt.to_sql("user_emails_and_files", db.con, if_exists="replace", index=False)
fa_log.to_sql("file_access_log", db.con, if_exists="replace", index=False)
c_ls.to_sql("contacts_list", db.con, if_exists="replace", index=False)
l_us.to_sql("lunary_users", db.con, if_exists="replace", index=False)
l_pr.to_sql("lunary_projects", db.con, if_exists="replace", index=False)

anon_question = question
anon_ground_truth = ground_truth_answer
for raw, anon in val_map.items():
    anon_question = anon_question.replace(raw, anon)
    anon_ground_truth = anon_ground_truth.replace(raw, anon)

anon_solution_path = [step for step in solution_path]
for i in range(len(anon_solution_path)):
    for raw, anon in val_map.items():
        anon_solution_path[i] = anon_solution_path[i].replace(raw, anon)

logging.info("Running Regenerated Environment Test...")
answer2, transcript2 = run_agent(anon_question, max_turns=12)
generate_report(anon_question, answer2, transcript2, filename="report_anonymized.txt")
reward2 = score(transcript2, answer2, anon_ground_truth, anon_solution_path)
logging.info(f"Regenerated Environment Target Answer Match Reward: {reward2}")