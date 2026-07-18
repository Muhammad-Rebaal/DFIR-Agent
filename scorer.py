def score(transcript, final_answer, ground_truth, solution_path, gamma=0.4):
    full_text = " ".join(transcript).lower()
    if final_answer and ground_truth.lower() in final_answer.lower():
        return 1.0
    reward, d = 0.0, 1.0
    for step in reversed(solution_path):
        d *= gamma
        key_terms = [w for w in step.replace(".", "").split() if len(w) > 4]
        if any(t.lower() in full_text for t in key_terms):
            reward += d
    return reward

question = "A password spray attack was detected at 08:36 on 2024-07-17 from IP 192.168.1.73. One account was successfully compromised and later used from an anonymized IP in Amsterdam to exfiltrate sensitive data. Identify the compromised account, determine what sensitive files were downloaded, and find the SID of the compromised account."
ground_truth_answer = "S-1-5-21-1874151667-3554330288-105586563-1715"
solution_path = [
    "Identify password spray from signin_logs where multiple accounts failed from IP 192.168.1.73",
    "Find amandap@vnevado.alpineskihouse.co as the only successful login ResultType 0 from that IP",
    "Correlate anonymized IP 170.54.121.63 sign-in from Amsterdam for amandap in signin_logs",
    "Check file_access_log for downloads by amandap from 170.54.121.63",
    "Discover Customer_PII_Export_Q2.csv and AWS_Root_Credentials.txt were downloaded",
    "Look up alert_evidence for AccountSid S-1-5-21-1874151667-3554330288-105586563-1715",
]