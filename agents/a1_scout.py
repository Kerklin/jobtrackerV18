# AGENT 1 – JOB SCOUT: searches the job sources, scores every job against your profile (no AI),
# picks the jobs that deserve an application pack, reads their job descriptions and hands them to Agent 2.
from common import *
AG = "Agent 1 · Job Scout"
S = {"start": time.time(), "queue": [], "lease": None, "summary": [], "log": [], "warn": [], "alerts": [], "manual": False, "mail_ok": False}
if (bad := selfcheck()): sys.exit(f"STOP: self-check failed (checks {bad}). Nothing was changed.")

# ---- 1. public job list (title, link, deadline, coarse fit label – nothing else) ----
file = Path("jobs.json")
try: data = json.loads(file.read_text(encoding="utf-8")) if file.exists() else {}
except Exception: data = {}; S["warn"].append("jobs.json was damaged – the list was rebuilt")
if isinstance(data, list): data = {"jobs": data}
meta = {"sources": data.get("meta", {}).get("sources", {})}
KEEP = ("title", "info", "link", "deadline", "fit", "found", "status")
jobs = [{k: j.get(k, "") for k in KEEP} for j in data.get("jobs", []) if j.get("title") and str(j.get("link", "")).startswith("http")]
for j in jobs:
    j["status"] = j["status"] or "open"; j["found"] = j["found"] or T
    if not PUBLIC_FIT: j["fit"] = ""

# ---- 2. search + quick profile match ----
slot, block = (NOW.hour * 60 + NOW.minute) // 5, f"{T}T{NOW.hour // 6}"
seen_k = {key(j) for j in jobs}; links = {same(j["link"]) for j in jobs}; new, opened = [], 0
rotate = SCHEDULED and len(SOURCES) > 6 and bool(data)
for idx, (name, kind, url, pat) in enumerate(SOURCES):
    s = meta["sources"].setdefault(name, {"last_ok": "", "muted": ""})
    if JOB_URL or s.get("muted") == block or (rotate and idx % 6 != slot % 6): continue
    try: items = read(kind, url, pat)
    except Exception as e: s["muted"] = block; S["log"].append(f"FAILED  {name} ({type(e).__name__}) – paused for 6 h"); continue
    s["last_ok"], s["muted"], n = T, "", 0
    for ti, link, tx in items:
        j = dict(title=ti, link=link)
        if not ti or key(j) in seen_k or same(link) in links or not link.startswith("http"): continue
        seen_k.add(key(j)); links.add(same(link))
        if not is_role(ti) or any(has(w, ti.lower()) for w in SKIP_TITLE): continue
        text = tx
        if opened < 8 and not generic(link):
            page = details(link); opened += 1
            if page: text = page
        d = deadline(text) or deadline(tx)
        if d and d < T: continue
        f = evaluate(ti, text) if PROFILE.ok else {"label": "", "score": 0}
        if PROFILE.ok and f["score"] <= 25: continue                 # not eligible / outside your field: not listed
        new.append(dict(title=ti, info="via " + name, link=link, deadline=d, fit=f["label"] if PUBLIC_FIT else "", found=T, status="open")); n += 1
    S["log"].append(f"OK      {name} ({len(items)} read, {n} new)")
jobs[:0] = new
jobs[:] = [j for j in jobs if not (j["deadline"] and j["deadline"] < (TODAY - timedelta(days=30)).isoformat())]
file.write_text(json.dumps({"meta": meta, "jobs": jobs}, ensure_ascii=False, indent=1), encoding="utf-8")
say(S, AG, f"{len(new)} new matching job(s) · {len([j for j in jobs if is_open(j)])} open")

# ---- 3. setup checks ----
missing = [n for n, v in (("MASTER_CV", MASTER_CV), ("MAIL_USER", MAIL_USER), ("MAIL_PASS", MAIL_PASS)) if not v]
if missing: S["warn"].append("Setup not finished – add these secrets (Settings → Secrets and variables → Actions → Secrets): " + ", ".join(missing))
elif not PROFILE.ok: S["warn"].append("MASTER_CV looks too short – paste your FULL CV as plain text")
if not AI_ON: S["warn"].append("AI is switched off (repository variable AI_ENABLED = no) – no application packs are made")
if BACKUP_KEY and not BACKUP_ON: S["warn"].append("BACKUP_KEY is shorter than 32 characters and is not used – see SETUP.md, step 4")
if MAIL_USER and MAIL_PASS:
    ok, why = mail_check(); S["mail_ok"] = ok
    if not ok: S["warn"].append(f"Email not usable: {why} – see SETUP.md, 'Email problems'")
    else: retry_backup(S)

# ---- 4. what gets an application pack ----
_, st0 = ledger_read(); st0 = roll(st0) if st0 else None
FINAL = ("email", "gmail-folder", "backup", "skip", "lowfit")
reqs = []
if JOB_URL: reqs.append({"link": JOB_URL, "text": None, "title": "", "src": "link"})
if st0 is not None and STATE_KEY and S["mail_ok"]:
    for it in sent_jobs(S, st0["seen"]):
        b = body_text(it["msg"])[:60000]; m = re.search(r"https?://[^\s<>\"]+", b)
        reqs.append({"link": m[0].rstrip(").,>") if m else "", "text": b, "src": "inbox", "mid": it["mid"],
                     "title": re.sub(r"(?i)^\s*(fwd?:\s*)?job\s*[:\-–]?\s*", "", subject_of(it["msg"]))[:140]})
ORDER = {"High": 0, "Medium": 1, "Low": 2, "": 1}
if not reqs and st0 is not None and STATE_KEY and PROFILE.ok:
    room = max(0, PACKS_PER_DAY - st0["packs_today"])
    def wanted(j):
        s_, tries, nxt = pstate(st0, j)
        return is_open(j) and j["fit"] in ("High", "Medium", "") and not generic(j["link"]) and s_ not in FINAL and tries < 5 and nxt <= T
    cand = sorted([j for j in jobs if wanted(j)], key=lambda j: (0 if (days(j) is not None and days(j) <= 7) else 1, ORDER[j["fit"]], days(j) if days(j) is not None else 999))
    reqs = [{"link": j["link"], "text": None, "title": j["title"], "src": "auto"} for j in cand[: min(room, 3)]]
    if not room: say(S, AG, f"daily limit of {PACKS_PER_DAY} application packs reached")
S["manual"] = any(r["src"] != "auto" for r in reqs)
blocked = (missing or not PROFILE.ok or not AI_ON or not S["mail_ok"] or not TOKEN or not STATE_KEY)
if reqs and blocked:
    say(S, AG, "application packs not started – see the warnings above. No AI was used.")
    if MAIL_USER and MAIL_PASS and not S["mail_ok"]:
        issue(S, "V18: email is not working", "No packs are made while email fails. No AI was used. See SETUP.md → 'Email problems'.")
    reqs = []

# ---- 5. read each job description, check fit, hand the good ones to Agent 2 ----
def private_note(subject, text):
    try: smtp_send(make_msg(subject, text, []))
    except Exception: pass
for r in reqs:
    if len(S["queue"]) >= (2 if S["manual"] else 1) or time.time() - S["start"] > 200: break
    raw, text = None, r["text"]; pasted = bool(text and len(text) > 400)
    if r["link"] and not generic(r["link"]) and not (pasted and jd_ok(text, True)):
        try: raw = get(r["link"], 20); text = page_text(raw); pasted = False
        except Exception: text = r["text"] if pasted else None
    job = {**r, "title": r["title"] or title_of(raw, text)}
    job["text"] = None
    if not job["link"]: job["link"] = "inbox:" + sha_hex(r.get("text") or "")[:12]
    job["hk"], job["ref"] = hkey(job), ref(job)
    if not jd_ok(text, pasted):
        why = "could not be opened" if text is None else "does not show this job's own description (login page or job list)"
        say(S, AG, f"❌ {job['ref']} – the page {why}. No AI was used.")
        if r["src"] == "auto":
            _, tries, _n = pstate(st0, job)
            mark(job["hk"], {"s": "skip" if (text is not None or tries >= 2) else "", "tries": tries + 1, "next": (TODAY + timedelta(days=1)).isoformat(), "day": T})
        else:
            private_note(f"V18: could not read {job['title'][:60]}", f"Agent 1 could not read the job description at:\n{r['link'] or '(no link)'}\n\n"
                         f"Reason: the page {why}.\n\nFix: send yourself an email with a subject starting JOB and paste the job link "
                         "AND the full job text into the body. No AI budget was used.")
            if r["src"] == "inbox": mark_seen(r["mid"])
        continue
    fit = evaluate(job["title"], text)
    if r["src"] == "auto" and fit["score"] < PACK_MIN_FIT:
        mark(job["hk"], {"s": "lowfit", "day": T}); say(S, AG, f"↷ {job['ref']} – fit {fit['score']}/100 is below {PACK_MIN_FIT}; no pack, no AI used"); continue
    job.update(fit=fit, status="ready", tries=pstate(st0, job)[1] if r["src"] == "auto" else 0)
    put(job, "jd.txt", text); S["queue"].append(job)
    say(S, AG, f"→ {job['ref']} handed to Agent 2 (quick fit {fit['score']}/100)")
if not reqs and not any("limit" in s for s in S["summary"]):
    say(S, AG, "no application pack due now" if SCHEDULED else "nothing to do: paste a job link in Run workflow, or email yourself a JOB message")
finish_step(S, AG)
