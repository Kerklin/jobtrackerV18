# V18 – six agents for your job search (setup guide)

V18 runs a **team of six agents** on GitHub every 5 minutes:

| # | Agent | What it does | AI |
|---|---|---|---|
| 1 | **Job Scout** | Searches the job sources, scores every job against your CV, picks the best match and reads its job description | no |
| 2 | **Fit & HR Screener** | Checks every requirement against your CV, gives a fit score, an HR prescreening, ATS keywords and an **Apply / Apply with caution / Skip** decision. If it says Skip, the team stops and no more AI is used. | 1 request |
| 3 | **CV Writer** | Writes your tailored, ATS-safe CV, following Agent 2's instructions | 1 request |
| 4 | **Cover Letter Writer** | Writes the tailored cover letter, matching Agent 3's CV | 1 request |
| 5 | **Salary Analyst** | Reads pay figures in the posting, searches the web (optional) and recommends your number | 1 request |
| 6 | **Employer Email Writer** | Writes the email to the employer and puts it in your **Gmail Drafts** with the CV and letter attached (never sent automatically). Then it emails you the complete pack. | 1 request |

The six agents run one after another on **one private GitHub computer**. They pass work to each other through that computer's
temporary folder, which is deleted after every run. This repository is **public**, but your CV, scores, CVs, letters, salary
figures and emails never enter it.

---

## Before you start
- A **GitHub** account.
- A **Gmail** account with **2-Step Verification** turned on.
- Your **CV as plain text**. Line 1 is your name; line 2 is your city/country and contact details. Keep it under 7,000 characters, with no tables.

> **Using an older version (V15, V16 or V17)?** Open each old repository → **Actions** → the workflow → **⋯** → **Disable workflow**.
> Otherwise two agent teams use your one AI allowance.

## Step 1 – Create the repository (2 minutes)
**+** → **New repository** → name **`V18`** → **Public** → tick **Add a README file** → **Create repository**.

## Step 2 – Upload the files (3 minutes)
1. Unzip `V18.zip`.
2. **Add file** → **Upload files** → drag in the **`agents`** folder and **`SETUP.md`** → **Commit changes**.
   Use Chrome or Edge, which keep the folder when you drag it.
3. **Add file** → **Create new file** → type exactly `.github/workflows/v18.yml` → paste the contents of `v18.yml` → **Commit changes**.

✅ **Check:** the repository shows a folder `agents` with **9 files** (`common.py`, `a1_scout.py` … `a6_email.py`, `finish.py`, `save.py`), plus `SETUP.md` and a `.github` folder.

## Step 3 – Gmail app password (3 minutes)
Open **myaccount.google.com/apppasswords** → name it `V18` → **Create** → copy the 16 characters.

## Step 4 – Secrets (5 minutes)
**V18** → **Settings** → **Secrets and variables** → **Actions** → **Secrets** tab → **New repository secret**:

| Name (exactly) | Value | |
|---|---|---|
| `MASTER_CV` | Your full CV as plain text | required |
| `MAIL_USER` | Your Gmail address | required |
| `MAIL_PASS` | The 16-character app password | required |
| `BACKUP_KEY` | 40 random characters (see below) | recommended |
| `MAIL_TO` | Another address for the packs | optional |
| `SEARCH_API_KEY` | Brave Search API key, so Agent 5 finds salary evidence on the web | optional |

**BACKUP_KEY.** Run this in Windows PowerShell, copy the result, and **never change it later**:
```powershell
-join ((48..57)+(65..90)+(97..122) | Get-Random -Count 40 | % {[char]$_})
```
⚠️ Use **Repository secrets**, not Environment or Dependabot secrets. Use exact names in capitals. Secrets don't carry over from older repositories, so add them again.

## Step 5 – One setting (1 minute)
**Settings** → **Actions** → **General** → **Workflow permissions** → **Read and write permissions** → **Save**.

## Step 6 – First run (3 minutes)
**Actions** → **V18** → **Run workflow** → paste one job's own link → tick **Send the fit digest now** → **Run workflow**.

✅ **Check after 3–5 minutes:**
- **In the run:** nine green steps (Agent 1 … Agent 6, Finish, Save), each with its own short report.
- **In Gmail:**
  - "V18 pack · fit … · Apply: …" with the CV, cover letter and full report
  - a new **draft** to the employer in **Drafts**
  - "Your fit digest"
- **On the Code tab:** the job table, with no ⚠️ lines at the top.
- **Branches:** `agent-lock` (and later `agent-backup`) appear. Don't delete them.

---

## Daily use
| What | How |
|---|---|
| **Fit digest** | Every morning: open jobs ranked by fit, with ✓ matches, ✗ missing and ⚠ risks |
| **Automatic packs** | The team works on jobs with fit ≥ `PACK_MIN_FIT` (65), most urgent first, up to `PACKS_PER_DAY` |
| **One job now** | **Actions** → **V18** → **Run workflow** → paste the link (plus language and focus if you want) |
| **Job behind a login (LinkedIn, Workday)** | In Gmail, **send an email to yourself** with a subject starting **`JOB`**, and the job link **and the full job text** in the body |
| **Sending the application** | Open Gmail **Drafts**. Check the recipient and the attachments, read everything, then press Send yourself. |
| **Emergency stop** | **Settings** → **Secrets and variables** → **Actions** → **Variables** → new variable `AI_ENABLED` = `no`. Delete it to resume. |

### What is in each pack email
- **Fit:** Agent 2's score and decision.
- **⚠️ Check before sending:** years or certifications not in your CV, `[ADD …]` gaps, foreign links, letter and email length, and the recipient address.
- **Attachments:** CV (Word) and cover letter (Word).
- **Full report:**
  - **A.** Fit, HR prescreening and ATS
  - **B.** CV
  - **C.** Cover letter
  - **D.** Salary
  - **E.** Employer email
  - **F.** Sending notes, including a follow-up email to send after 7–10 days

### How to read a fit score (0–100)
| Part | Points | What it checks |
|---|---|---|
| Skills | 55 | How many of the job's key terms appear in your CV (terms in the job title count double) |
| Experience | 15 | Years asked for vs. years in your CV (approximate) |
| Education | 10 | Degree level asked for vs. yours |
| Languages | 15 | Required languages vs. yours. A missing required language caps the score at 55. |
| Eligibility | 5 | "Nationals of …", local-hire or internal-only posts → score capped at 25, and the job is not listed |

**High** = 70+, **Medium** = 50–69, **Low** = under 50. **UNCONFIRMED** means the job description couldn't be read, so the score is capped at 60.
The quick score comes from Agent 1. Agent 2's AI analysis confirms or corrects it.

---

## AI budget (free GitHub Models)
- **Per pack:** 5 requests (3 on the stronger model, 2 on the smaller one).
- **Daily limits:** 30 + 100 requests a day by default, which can't be raised above 35 + 110. At most 15 an hour by default (20 maximum).
- **Before starting:** Agent 2 reserves all 5 requests.
- **If the team stops early** (Skip decision or an error), Finish refunds the unused requests.
- **If a run is killed:** its reservation stays counted until the lock expires (25 minutes), so the budget is never exceeded.
- **One team at a time:** only one run uses AI. A second run waits (manual runs wait up to 4 minutes) or tries again later.

## When something fails
| Situation | What happens |
|---|---|
| Sending the pack fails | Saved straight into your Gmail folder **V18-packs** |
| Gmail unreachable and `BACKUP_KEY` set | Encrypted copy on branch `agent-backup` (one copy, no history), emailed later with no new AI, then deleted |
| Gmail unreachable, no `BACKUP_KEY` | Nothing is stored. The pack is made again the next day. |
| Gmail login refused | No AI is used. A warning appears and an Issue is opened. |
| An agent's AI request fails | The team stops for that job. Unused requests are refunded and the job is tried again (up to 5 times). |
| AI fails in 3 runs in a row | AI pauses for 6 hours and an Issue is opened |
| Gmail draft can't be created | The pack still arrives. Copy the email from section E. |

## Warnings on the front page
| Warning | Fix |
|---|---|
| Setup not finished – add these secrets: … | Add the listed secrets (step 4) |
| MASTER_CV looks too short | Paste your **full** CV as plain text |
| Email not usable: Gmail refused the app password | Make a new app password → update `MAIL_PASS`. Changing your Google password revokes app passwords. |
| BACKUP_KEY is shorter than 32 characters | Make a 40-character key (step 4) |
| AI is switched off | Delete the `AI_ENABLED` variable |
| Red ✗ on "Save" | Step 5 |
| Red ✗ on "Get the code" or "Agent 1" | Run it again. If it repeats, check that the files are in the `agents` folder and the branch is `main`. |

## Settings (top of `.github/workflows/v18.yml`)
`PACK_MIN_FIT` (40–100) · `PACKS_PER_DAY` (max 20) · `DIGEST_HOUR_UTC` · `PUBLIC_FIT` · `AI_HIGH_PER_DAY` (max 35) ·
`AI_LOW_PER_DAY` (max 110) · `AI_PER_HOUR` (max 20) · `SEARCH_WORDS` · `FEEDS`. Values above a maximum are ignored.

## Where your data is
| Public (anyone can see) | Private (only you) |
|---|---|
| Job titles, links, deadlines, a coarse High/Medium/Low label (`PUBLIC_FIT: "no"` hides it) | Your CV (secret) |
| The code | Fit scores, reasons, CVs, letters, salary figures, employer emails (Gmail only) |
| AI counters and unreadable job codes (branch `agent-lock`) | Gmail Drafts to employers |
| Run logs: status and references like `#1def75` | Jobs you send yourself (link or `JOB` email) |

**Keep the repository to yourself.** Don't add collaborators: anyone with write access could read your secrets.
**Always read every pack and draft before sending.** Fill in or delete each `[ADD ONLY IF TRUE: …]` placeholder.
