# Things We've Built — portfolio

The site that lists David's apps and research, live at
**[things-we-have-built.netlify.app](https://things-we-have-built.netlify.app)**.

It has two pages:

- **Apps** (`index.html`) — a card per web app
- **Research Topics** (`topics.html`) — a card per topic, each listing its
  NotebookLM knowledge bases

Pushing to `main` auto-deploys via Netlify (~1 minute). You don't touch
Netlify — just push and it rebuilds.

---

## 🟢 How to add a new project (the short version)

Open Terminal and go to the repo first — **every command below assumes this**:

```bash
cd ~/netlify-portfolio
```

| You want to add… | Run this |
| --- | --- |
| A **web app** (to the Apps page) | `python3 add-app.py` |
| A **NotebookLM or research topic** (to the Topics page) | `python3 add-notebook.py` |

Both scripts ask you a few questions, do everything, and offer to push at the
end. If you say yes to the push, the site updates itself a minute later. If
you say no, they remind you of the one command to push later.

That's it. The rest of this file is detail for when you want it.

---

## 1. Adding a web app — `add-app.py`

```bash
cd ~/netlify-portfolio
python3 add-app.py
```

It asks for:

1. **App name** — e.g. `Diagnostic Teammate`
2. **Live URL** — the address the app is already running at
3. **One-line description** — what it does
4. **Category badge** — e.g. `Clinical · Tool`, `Family · Utility`
5. **Built with** — `streamlit`, `html`, `react`, or `other`

Then it automatically:

- 📸 Screenshots the live app and saves it to `screenshots/` (800×500)
- 🃏 Adds a matching card to `index.html` (picks the next gradient colour)
- 📝 Adds a row to `OVERVIEW.md`
- ✅ Commits, and offers to push
- 🔙 Prints the **"← All projects" back-button snippet** for your app's
  framework — paste that into the app itself so it can link back to the
  portfolio (see ["The back button"](#the-back-button) below)

---

## 2. Adding a NotebookLM or topic — `add-notebook.py`

```bash
cd ~/netlify-portfolio
python3 add-notebook.py
```

It first asks whether you want to:

**a) Add a NotebookLM to an existing topic**
- pick the topic from the numbered list
- give the notebook's **title**, **URL**, **source count**, and whether it's
  **shared**
- it slots the entry in by source count (so the list stays tidy) and adds the
  green **Shared** pill if you said yes

**b) Create a brand-new topic**
- give the **topic name**, a **description**, the **Drive project URL**
  (the gradient colour is chosen for you)
- optionally add a **first NotebookLM** straight away

Then it commits and offers to push.

---

## The back button

Every card link on the portfolio adds `?nav=1` to the address. Each app is set
up to show a small **"← All projects"** link **only when that `?nav=1` is
present** — so when someone opens an app *from the portfolio* they can get
back, but if they're sent the app's URL on its own it stays clean and
standalone.

`add-app.py` prints the right snippet for you to paste into a new app. The
three forms (also stored inside `add-app.py`) are:

- **Streamlit** — `if st.query_params.get("nav") == "1": st.link_button(...)`
- **Static HTML** — a fixed-position `<a>` shown via a `URLSearchParams` check
- **React** — conditional JSX on `window.location.search`

Paste it into the app's own repo, then commit and push **that** repo too.

---

## Pushing (if you said "no" to the auto-push)

```bash
cd ~/netlify-portfolio
git push
```

Your Mac remembers the GitHub login (in Keychain), so this usually goes
through silently. If it ever asks for a password, paste your GitHub
**Personal Access Token** (not your account password).

---

## Files in this repo

| File | What it is |
| --- | --- |
| `index.html` | The Apps page |
| `topics.html` | The Research Topics page |
| `add-app.py` | Tool to add an app card |
| `add-notebook.py` | Tool to add a NotebookLM / topic |
| `screenshots/` | App thumbnails (800×500 JPGs) |
| `OVERVIEW.md` | Plain-language list of everything on the site |
| `README.md` | This file |

---

*Built by David Lloyd with Claude. Hosted on Netlify.*
