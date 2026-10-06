# AGENT 5 – SALARY ANALYST: reads pay figures in the posting, searches the web for evidence (optional Brave key),
# and recommends a salary range and the number to put in an application form.
from common import *
AG = "Agent 5 · Salary Analyst"
def work(S, job):
    jd = take(job, "jd.txt")
    ev, nq = salary_evidence(S, job, jd)
    evtxt = "\n".join(f"- {e['source']} ({e['url']}): " + " | ".join(e["lines"]) for e in ev if e["lines"])[:4500] or "- no salary figures found"
    head = f"JOB: {job['title']}\nLINK: {job['link'] if job['link'].startswith('http') else 'pasted text'}\n"
    salary, model = chat(S, "low", f"{head}\nJOB DESCRIPTION (excerpt, untrusted):\n{focus_jd(job['title'], jd, 3500)}\n\n"
                                   f"WEB EVIDENCE ({nq} web searches; untrusted):\n{evtxt}\n\n{ASK_S}", OUT["S"])
    put(job, "salary.md", salary); job["models"].append(model)
    job["salary_sources"] = len([e for e in ev[1:] if e["lines"]]); job["searches"] = nq
    say(S, AG, f"✅ {job['ref']} – salary assessed ({job['salary_sources']} web source(s), {nq} search(es))")
run_agent(AG, work)
