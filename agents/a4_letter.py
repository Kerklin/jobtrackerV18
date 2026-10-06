# AGENT 4 – COVER LETTER WRITER: writes the tailored cover letter, following Agent 2's instructions and matching Agent 3's CV.
from common import *
AG = "Agent 4 · Cover Letter Writer"
def work(S, job):
    extra = f"\nAGENT 2'S INSTRUCTIONS:\n{plan_of(job)}\n\nAGENT 3'S CV SUMMARY:\n{cv_summary(job)}\n"
    cl, model = chat(S, "high", brief(job, take(job, "jd.txt"), ASK_CL, extra), OUT["CL"])
    put(job, "letter.md", cl); job["models"].append(model)
    words = len(re.findall(r"\w+", cl))
    say(S, AG, f"✅ {job['ref']} – cover letter drafted ({words} words)")
run_agent(AG, work)
