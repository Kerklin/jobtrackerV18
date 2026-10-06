# AGENT 3 – CV WRITER: writes the complete ATS-safe tailored CV, following Agent 2's instructions.
from common import *
AG = "Agent 3 · CV Writer"
def work(S, job):
    cv, model = chat(S, "high", brief(job, take(job, "jd.txt"), ASK_CV, f"\nAGENT 2'S INSTRUCTIONS:\n{plan_of(job)}\n"), OUT["CV"])
    put(job, "cv.md", cv); job["models"].append(model)
    say(S, AG, f"✅ {job['ref']} – tailored CV drafted ({len(cv.split())} words)")
run_agent(AG, work)
