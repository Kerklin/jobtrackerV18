# AGENT 2 – FIT & HR SCREENER: reserves the AI budget for the whole team, evaluates your fit requirement by requirement,
# runs the HR prescreening and the ATS keyword analysis, and decides Apply / Apply with caution / Skip.
# Its instructions guide Agents 3, 4 and 6.
from common import *
AG = "Agent 2 · Fit & HR Screener"
S = state_load(); jobs = active(S)
if not jobs: say(S, AG, "nothing to do"); finish_step(S, AG); sys.exit(0)
err = acquire(S, len(jobs), LOCK_WAIT if S["manual"] else 0)
if err:
    for j in jobs: j["status"] = "waiting"
    say(S, AG, f"⏳ not started: {err}." + (" Your request is kept – run it again later." if S["manual"] else "")); finish_step(S, AG); sys.exit(0)
L = S["lease"]
for i, job in enumerate(jobs):
    if i >= L["jobs"]: job["status"] = "waiting"; say(S, AG, f"⏳ {job['ref']} – not enough AI budget in this run"); continue
    _, st = ledger_read()
    if job["src"] == "auto" and st and pstate(st, job)[0] in ("email", "gmail-folder", "backup"):
        job["status"] = "done-elsewhere"; say(S, AG, f"↷ {job['ref']} – already done by another run"); continue
    if time.time() - S["start"] > RUN_GUARD: job["status"] = "waiting"; say(S, AG, f"⏳ {job['ref']} – run time limit; stays queued"); continue
    jd = take(job, "jd.txt")
    try:
        analysis, model = chat(S, "high", brief(job, jd, ASK_FIT, "\nAUTOMATIC FIT CHECK (keyword-based, may be wrong):\n" + fit_text(job["fit"]), floor=2500), OUT["A"])
    except NoAccess as e:
        L["failed"] = True
        for j in jobs[i:]: j["status"] = "stopped"
        say(S, AG, f"❌ AI refused access ({e}) – check that GitHub Models is enabled")
        issue(S, "V18: AI (GitHub Models) is not available", f"The AI service refused access ({e})."); break
    except Stop as e:
        L["failed"] = L["errors"] > 0; job["status"] = "stopped"; say(S, AG, f"⏳ {job['ref']} – stopped ({e}); it will be tried again"); continue
    m = re.search(r"FIT_SCORE:\s*(\d{1,3})", analysis); ai_fit = min(100, int(m[1])) if m else job["fit"]["score"]
    d = re.search(r"DECISION:\s*(Apply with caution|Apply|Skip)", analysis, re.I)
    decision = d[1].capitalize() if d else ("Apply" if ai_fit >= 70 else "Apply with caution" if ai_fit >= 50 else "Skip")
    job.update(ai_fit=ai_fit, decision=decision, models=[model])
    put(job, "analysis.md", re.sub(r"(?m)^(FIT_SCORE|DECISION):.*$", "", analysis).strip())
    if job["src"] == "auto" and (decision == "Skip" or ai_fit < PACK_MIN_FIT - 10):
        job["status"] = "skipped-fit"; L["packs"][job["hk"]] = {"s": "lowfit", "day": T}
        say(S, AG, f"↷ {job['ref']} – fit {ai_fit}/100, decision {decision}: the team stops here (CV, letter, salary and email are not made)")
    else:
        say(S, AG, f"✅ {job['ref']} – fit {ai_fit}/100 (quick check {job['fit']['score']}) · decision: {decision} → Agents 3-6")
    state_save(S)
finish_step(S, AG)
