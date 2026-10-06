# FINISH – releases the AI lock (refunds unused requests), sends the daily fit digest (no AI) and writes the public front page.
from common import *
S = state_load()
L = S.get("lease")
if L:
    for job in S["queue"]:
        if job.get("status") in ("stopped", "failed", "ready") and job.get("src") == "auto":
            L["packs"][job["hk"]] = {"s": "", "tries": job.get("tries", 0) + 1, "next": T if job["status"] != "failed" else (TODAY + timedelta(days=1)).isoformat(), "day": T}
st0 = release(S)
if st0 is None: _, st0 = ledger_read(); st0 = roll(st0) if st0 else None
file = Path("jobs.json")
try: data = json.loads(file.read_text(encoding="utf-8"))
except Exception: data = None
if data is None: print("Agent 1 did not finish – nothing to publish."); sys.exit(0)
jobs, meta = data["jobs"], data["meta"]
ORDER = {"High": 0, "Medium": 1, "Low": 2, "": 1}

# ---- daily FIT DIGEST (private email, no AI) ----
if (st0 is not None and PROFILE.ok and S.get("mail_ok") and STATE_KEY and (WANT_DIGEST or (NOW.hour >= DIGEST_HOUR and st0.get("digest_day") != T))
        and time.time() - S["start"] < 14 * 60):
    pool = sorted([j for j in jobs if is_open(j)], key=lambda j: (ORDER[j["fit"]], days(j) if days(j) is not None else 999))[:15]
    rows = []
    for j in pool:
        txt = details(j["link"]) if time.time() - S["start"] < 15 * 60 else None
        f = evaluate(j["title"], txt or "")
        s_ = pstate(st0, j)[0]
        rows.append((f["score"], j, f, {"email": "pack emailed", "gmail-folder": "pack in Gmail folder V18-packs", "backup": "pack waiting (backup)",
                                       "lowfit": "below your pack threshold", "skip": "page not readable"}.get(s_, "pack queued" if f["score"] >= PACK_MIN_FIT else "no pack")))
    rows.sort(key=lambda r: -r[0])
    lines = [f"YOUR FIT DIGEST – {T}", f"{len([j for j in jobs if is_open(j)])} open jobs · top {len(rows)} ranked against your CV · packs are made for fit ≥ {PACK_MIN_FIT}", ""]
    for i, (sc, j, f, st_) in enumerate(rows, 1):
        dl = f"deadline {j['deadline']} ({days(j)} days)" if j["deadline"] else "deadline: check posting"
        lines += [f"{i}. {j['title']} – {j['info'].replace('via ', '')}", f"   {dl} · {st_}", f"   {j['link']}", "   " + fit_text(f).replace("\n", "\n   ").rstrip(), ""]
    lines += ["How to read this: skills = how many of the job's key terms appear in your CV; ✗ missing = terms to add ONLY if true; ⚠ = knock-out risks.",
              "Get a full pack for any job: Actions → V18 → Run workflow → paste the link, or email yourself a 'JOB' message."]
    try:
        msg = make_msg(f"Your fit digest – {T} – {len(rows)} jobs ranked", "\n".join(lines), [])
        try: smtp_send(msg)
        except Exception: imap_put("V18-packs", msg)
        ledger_update(lambda st: st.__setitem__("digest_day", T), "digest"); say(S, "Finish", f"📊 fit digest emailed ({len(rows)} jobs ranked)")
    except Exception as e: S["log"].append(f"DIGEST  not delivered ({type(e).__name__}) – tried again next run")

# ---- PUBLIC front page: job list only ----
warn = list(dict.fromkeys(S["warn"]))
open_ = sorted([j for j in jobs if is_open(j)], key=lambda j: (ORDER[j["fit"]], days(j) is None, days(j) or 0))
closed = [j for j in jobs if not is_open(j)]
u = st0["used"] if (st0 and st0["day"] == T) else {"high": 0, "low": 0}
FIT = {"High": "🟢 High", "Medium": "🟡 Medium", "Low": "⚪ Low", "": "–"}
def row(j):
    d = days(j); left = "check" if d is None else ("🔴 " if 0 <= d <= 7 else "") + f"{d} days"
    new_ = " 🆕" if (TODAY - date.fromisoformat(j["found"])).days <= 2 else ""
    return f"| [{md(j['title'])}]({j['link'].replace(' ', '%20').replace(')', '%29')}){new_} | {md(j['info'])} | {j['deadline'] or '–'} | {left} |" + (f" {FIT[j['fit']]} |" if PUBLIC_FIT else "")
H = "| Job | Found via | Deadline | Left |" + (" Fit |" if PUBLIC_FIT else "") + "\n|---|---|---|---|" + ("---|" if PUBLIC_FIT else "") + "\n"
out = [f"# {md((ENV('PAGE_TITLE', '') or 'Job tracker').strip()[:60])}\n"] + [f"> ⚠️ **{md(w)}**\n" for w in warn]
out += [f"**{len(open_)} open jobs** · updated {T} · six agents check every 5 minutes · sources working today: "
        f"{sum(1 for v in meta['sources'].values() if v.get('last_ok') == T)} of {len(SOURCES)} · AI today: {u['high'] + u['low']} of {CAP['high'] + CAP['low']} requests\n",
        "🆕 = found in the last 2 days · 🔴 = 7 days or less left · always confirm the deadline on the official posting. "
        "Fit scores, application packs and employer emails are delivered privately to your Gmail and are not shown here.\n",
        H + "\n".join(row(j) for j in open_) + "\n"]
if closed: out.append(f"<details><summary>Closed ({len(closed)})</summary>\n\n" + H + "\n".join(row(j) for j in closed) + "\n\n</details>\n")
Path("README.md").write_text("\n".join(out), encoding="utf-8")
S["log"].append(f"{len(open_)} open jobs · AI today: {u['high'] + u['low']} requests")
text = "\n".join(["### Finish"] + [f"- {s[8:]}" for s in S["summary"] if s.startswith("Finish:")] + [f"- ⚠️ {w}" for w in warn]
                 + [f"- Issue: {a}" for a in S["alerts"]] + ["", "```", *S["log"], "```"])
print(text)
if ENV("GITHUB_STEP_SUMMARY"):
    with open(ENV("GITHUB_STEP_SUMMARY"), "a", encoding="utf-8") as f: f.write(text + "\n")
state_save(S)
