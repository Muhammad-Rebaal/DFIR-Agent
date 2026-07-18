import re

def anonymize_value(val, mapping, prefix, counter):
    if not isinstance(val, str):
        return val
    if val in mapping:
        return mapping[val]
    mapping[val] = f"{prefix}_{counter[0]}"
    counter[0] += 1
    return mapping[val]

def anonymize_ip(val, mapping, counter):
    if not isinstance(val, str):
        return val
    if val in mapping:
        return mapping[val]
    mapping[val] = f"10.99.99.{counter[0]}"
    counter[0] += 1
    return mapping[val]

def anonymize(signin, evidence, emails, rules, calendar, files, access_log, contacts, users, projects):
    mapping = {}
    counters = {"user": [1], "ip": [1], "sid": [1], "msg": [1], "org": [1], "proj": [1], "alert": [1]}
    
    df_signin = signin.copy()
    df_evidence = evidence.copy()
    df_emails = emails.copy()
    df_rules = rules.copy()
    df_calendar = calendar.copy()
    df_files = files.copy()
    df_access = access_log.copy()
    df_contacts = contacts.copy()
    df_users = users.copy()
    df_projects = projects.copy()

    df_signin["UserPrincipalName"] = df_signin["UserPrincipalName"].apply(lambda x: anonymize_value(x, mapping, "anon_user", counters["user"]))
    df_signin["IPAddress"] = df_signin["IPAddress"].apply(lambda x: anonymize_ip(x, mapping, counters["ip"]))
    
    df_evidence["AccountUpn"] = df_evidence["AccountUpn"].apply(lambda x: anonymize_value(x, mapping, "anon_user", counters["user"]))
    df_evidence["AccountSid"] = df_evidence["AccountSid"].apply(lambda x: anonymize_value(x, mapping, "anon_sid", counters["sid"]))
    df_evidence["AttackerIP"] = df_evidence["AttackerIP"].apply(lambda x: anonymize_ip(x, mapping, counters["ip"]))
    df_evidence["NetworkMessageId"] = df_evidence["NetworkMessageId"].apply(lambda x: anonymize_value(x, mapping, "anon_msg", counters["msg"]) if x else x)

    df_emails["SenderAddress"] = df_emails["SenderAddress"].apply(lambda x: anonymize_value(x, mapping, "anon_user", counters["user"]))
    df_emails["RecipientAddress"] = df_emails["RecipientAddress"].apply(lambda x: anonymize_value(x, mapping, "anon_user", counters["user"]))
    df_emails["NetworkMessageId"] = df_emails["NetworkMessageId"].apply(lambda x: anonymize_value(x, mapping, "anon_msg", counters["msg"]))

    df_rules["UserPrincipalName"] = df_rules["UserPrincipalName"].apply(lambda x: anonymize_value(x, mapping, "anon_user", counters["user"]))
    df_rules["ClientIP"] = df_rules["ClientIP"].apply(lambda x: anonymize_ip(x, mapping, counters["ip"]))

    df_access["UserPrincipalName"] = df_access["UserPrincipalName"].apply(lambda x: anonymize_value(x, mapping, "anon_user", counters["user"]))
    df_access["ClientIP"] = df_access["ClientIP"].apply(lambda x: anonymize_ip(x, mapping, counters["ip"]))

    df_users["email"] = df_users["email"].apply(lambda x: anonymize_value(x, mapping, "anon_user", counters["user"]))
    df_users["org_id"] = df_users["org_id"].apply(lambda x: anonymize_value(x, mapping, "anon_org", counters["org"]))
    
    df_projects["org_id"] = df_projects["org_id"].apply(lambda x: anonymize_value(x, mapping, "anon_org", counters["org"]))
    df_projects["project_id"] = df_projects["project_id"].apply(lambda x: anonymize_value(x, mapping, "anon_proj", counters["proj"]))

    def clean_text(text):
        if not isinstance(text, str):
            return text
        for raw, anon in mapping.items():
            text = text.replace(raw, anon)
        return text

    df_calendar["participants"] = df_calendar["participants"].apply(clean_text)
    df_files["Content"] = df_files["Content"].apply(clean_text)
    df_contacts["Email"] = df_contacts["Email"].apply(clean_text)
    df_emails["Subject"] = df_emails["Subject"].apply(clean_text)

    return df_signin, df_evidence, df_emails, df_rules, df_calendar, df_files, df_access, df_contacts, df_users, df_projects, mapping