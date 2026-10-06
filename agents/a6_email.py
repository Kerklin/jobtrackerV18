# AGENT 6 – EMPLOYER EMAIL WRITER: drafts the email to the employer, puts it with the CV and cover letter as a
# DRAFT in your Gmail (never sent automatically), runs the final fact checks and emails you the complete pack.
from common import *
AG = "Agent 6 · Employer Email Writer"
_top = [l.strip() for l in MASTER_CV.splitlines() if l.strip()][:2]
LETTERHEAD = ("**" + _top[0].lstrip("# ") + "**\n" + (_top[1] + "\n" if len(_top) > 1 else "") + TODAY.strftime("%d %B %Y") + "\n\n") if _top else ""
def work(S, job):
    jd = take(job, "jd.txt")
    extra = f"\nAGENT 2'S INSTRUCTIONS:\n{plan_of(job)}\n\nAGENT 3'S CV SUMMARY:\n{cv_summary(job)}\n"
    mail, model = chat(S, "low", brief(job, jd, ASK_E, extra), OUT["E"])
    put(job, "email.md", mail); job["models"].append(model)
    analysis, cv, cl, salary = take(job, "analysis.md"), take(job, "cv.md"), take(job, "letter.md"), take(job, "salary.md")
    flags = checks(cv, cl, mail, jd, salary)
    # --- the email to the employer, as a Gmail DRAFT with the CV and letter attached ---
    em = re.split(r"(?i)##\s*sending notes", re.sub(r"(?i)^\s*##\s*email to employer\s*", "", mail.strip()))
    em_body, notes = em[0].strip(), (em[1].strip() if len(em) > 1 else "")
    sm = re.search(r"(?im)^\**subject\**:\s*(.+)$", em_body)
    em_subject = (sm[1].strip() if sm else f"Application – {job['title']} – {CAND}")[:180]
    em_text = re.sub(r"(?im)^\**subject\**:.*\n?", "", em_body, count=1).strip()
    to = employer_address(jd)
    base = f"{ascii_(CAND).replace(' ', '_')}_{slug(job['title'])[:40]}"
    cv_doc = (f"{base}_CV.docx", docx_bytes(cv, "cv", f"CV – {job['title']}"))
    cl_doc = (f"{base}_Cover_Letter.docx", docx_bytes(LETTERHEAD + re.sub(r"(?i)##\s*cover letter", "", cl), "cl", f"Cover letter – {job['title']}"))
    try:
        gmail_draft(to, em_subject, em_text, [cv_doc, cl_doc])
        draft = f"ready in your Gmail **Drafts**{' to ' + to if to else ' – add the recipient'} with the CV and cover letter attached (NOT sent)"
    except Exception as e:
        draft = "could not be created in Gmail – copy it from section F"; S["log"].append(f"DRAFT   not created ({type(e).__name__})")
    if not to: flags.append("no application e-mail address found in the posting – check how to apply (portal?) before sending")
    else: flags.append(f"recipient {to} was taken from the posting – confirm it before sending")
    # --- the complete pack for YOU ---
    link_txt = job["link"] if job["link"].startswith("http") else "pasted text"
    sal = re.sub(r"(?im)^##\s*salary expectations\s*$", "", salary).strip()
    letter_txt = re.sub(r"(?i)##\s*cover letter", "", cl).strip()
    report = (f"# Application pack – {job['title']}\n\n**Posting:** {link_txt}  \n**Prepared:** {T} by six agents using {', '.join(sorted(set(job['models'])))} "
              f"(GitHub Models) · web searches: {job.get('searches', 0)} · salary sources: {job.get('salary_sources', 0)}"
              f"{'  · language: ' + LANG if LANG != 'auto' else ''}\n\n"
              f"**Fit: {job['ai_fit']}/100 · Decision: {job['decision']}** · Employer email: {draft}\n\n"
              f"## Quick fit check (Agent 1)\n```\n{fit_text(job['fit'])}```\n\n"
              + ("## ⚠️ Check before sending\n" + "\n".join(f"- {x}" for x in flags) + "\n\n" if flags else "")
              + f"---\n\n# A. Fit evaluation, HR prescreening and ATS (Agent 2)\n\n{analysis}\n\n"
              f"---\n\n# B. Tailored CV (Agent 3) – copy-paste ready\n\n{cv}\n\n"
              f"---\n\n# C. Cover letter (Agent 4) – copy-paste ready\n\n{letter_txt}\n\n"
              f"---\n\n# D. Salary expectations (Agent 5)\n\n{sal}\n\n"
              f"---\n\n# E. Email to the employer (Agent 6) – copy-paste ready\n\nSubject: {em_subject}\n\n{em_text}\n\n"
              f"---\n\n# F. Sending notes (Agent 6)\n\n{notes}\n")
    body = (f"Application pack for: {job['title']}\n{link_txt}\n\nFIT {job['ai_fit']}/100 · DECISION: {job['decision']}\n"
            f"Email to the employer: {draft.replace('**', '')}\n\n"
            + ("CHECK BEFORE SENDING:\n" + "\n".join(f"- {x}" for x in flags) + "\n\n" if flags else "")
            + "Attached: CV (Word), cover letter (Word), full report. The full report follows below.\n\n" + report)
    files = [(f"{base}_Report.md", report.encode("utf-8")), cv_doc, cl_doc]
    subject = f"V18 pack · fit {job['ai_fit']} · {job['decision']}: {job['title'][:80]}"
    status = deliver(S, job["hk"], subject, body, files)
    L = S["lease"]
    if status != "email": L["mail_fail"] += 1
    if status == "none":
        job["status"] = "failed"; say(S, AG, f"❌ {job['ref']} – could not be delivered or kept; it will be made again tomorrow"); return
    L["made"] += 1; job["status"] = "done"
    checkpoint(S, job["hk"], {"s": status, "day": T})
    state_save(S)
    if ENV("TEST_CRASH_AFTER_DELIVERY"): os._exit(9)
    if job["src"] == "inbox": mark_seen(job["mid"])
    where = {"email": "pack emailed to you", "gmail-folder": "email failed – pack saved in your Gmail folder V18-packs",
             "backup": "email failed – pack kept encrypted, sent automatically later"}[status]
    say(S, AG, f"✅ {job['ref']} – employer email drafted · {where} · {len(flags)} item(s) to check")
run_agent(AG, work)
