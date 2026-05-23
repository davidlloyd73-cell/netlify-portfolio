#!/usr/bin/env python3
"""
add-notebook.py  —  add a NotebookLM (or a whole new topic) to the
Research Topics page (topics.html) of the "Things We've Built" portfolio.

Run it from inside this repo:

    python3 add-notebook.py

Two modes:
  1. Add a NotebookLM to an existing topic
     - pick a topic from the list
     - give the notebook's title, URL, source count, and whether it's shared
     - it inserts a new entry, kept in descending source-count order to match
       the existing layout
  2. Create a new topic
     - give the topic name, description, Drive project URL (auto-rotates the
       gradient), and optionally a first NotebookLM

Then it commits and offers to push (push auto-deploys via Netlify).

Flag-driven examples (anything omitted is asked for):

    # add a notebook to an existing topic
    python3 add-notebook.py --topic "Post-EMIS" \
        --nb-title "Local Inference Benchmarks" \
        --nb-url "https://notebooklm.google.com/notebook/XXedit" \
        --sources 12 --shared --push

    # create a new topic with a first notebook
    python3 add-notebook.py --new-topic --topic "Diabetes Remission" \
        --desc "A primary-care pathway for type-2 remission." \
        --drive-url "https://drive.google.com/drive/project/XXedit" \
        --nb-title "Remission Evidence Base" \
        --nb-url "https://notebooklm.google.com/notebook/XXedit" --sources 30
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.abspath(__file__))
TOPICS = os.path.join(REPO, "topics.html")

PALETTE = [
    ("#7c5cff", "#22d3ee"), ("#ef4444", "#f472b6"), ("#22d3ee", "#7c5cff"),
    ("#f472b6", "#fbbf24"), ("#34d399", "#22d3ee"), ("#fbbf24", "#34d399"),
    ("#38bdf8", "#7c5cff"), ("#f472b6", "#22d3ee"),
]

DRIVE_SVG = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
             'stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
             '<path d="M7 17L17 7M9 7h8v8"/></svg>')


# ─── small helpers ──────────────────────────────────────────────────────────
def ask(label: str, default: str | None = None, required: bool = True) -> str:
    suffix = f" [{default}]" if default else ""
    while True:
        try:
            val = input(f"{label}{suffix}: ").strip()
        except EOFError:
            if default is not None:
                return default
            if not required:
                return ""
            sys.exit(f"! '{label}' is required but no input is available.")
        if not val and default is not None:
            return default
        if val or not required:
            return val
        print("  (required)")


def ask_yes(label: str, default_yes: bool = False) -> bool:
    d = "y" if default_yes else "n"
    return ask(f"{label} (y/n)", default=d).lower().startswith("y")


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", REPO, *args], capture_output=True, text=True)


def read_html() -> str:
    return open(TOPICS, encoding="utf-8").read()


def write_html(html: str) -> None:
    open(TOPICS, "w", encoding="utf-8").write(html)


def norm(text: str) -> str:
    """Strip tags + entities for comparing/printing topic names."""
    text = re.sub(r"<[^>]+>", "", text)
    return text.replace("&nbsp;", " ").replace("\xa0", " ").strip()


def find_topics(html: str) -> list[tuple[str, str]]:
    """Return [(display_name, full_article_html), ...] in document order."""
    out = []
    for art in re.findall(r"<article class=\"topic\".*?</article>", html, re.S):
        m = re.search(r'<div class="thumb"><h2>(.*?)</h2></div>', art, re.S)
        name = norm(m.group(1)) if m else "(unnamed)"
        out.append((name, art))
    return out


def count_of(li: str) -> int:
    m = re.search(r">(\d+)\s+sources?<", li)
    return int(m.group(1)) if m else 0


def build_li(title: str, url: str, sources: int, shared: bool) -> str:
    pill = '<span class="shared-pill">Shared</span>' if shared else ""
    unit = "source" if sources == 1 else "sources"
    return (f'<li><a href="{url}" target="_blank" rel="noopener">'
            f'<span class="title">{title}{pill}</span>'
            f'<span class="meta">{sources} {unit}</span></a></li>')


def pick_gradient(html: str) -> tuple[str, str]:
    n = html.count('class="topic"')
    return PALETTE[n % len(PALETTE)]


# ─── add a notebook into an existing topic ──────────────────────────────────
def add_to_topic(html: str, topic_name: str, new_li: str, new_count: int) -> str:
    topics = find_topics(html)
    target = None
    for name, art in topics:
        if name.lower() == topic_name.lower():
            target = art
            break
    if target is None:
        names = ", ".join(n for n, _ in topics)
        sys.exit(f"! Topic '{topic_name}' not found. Available: {names}")

    ul = re.search(r'(<ul class="notebooks">)(.*?)(</ul>)', target, re.S)
    if not ul:
        sys.exit(f"! Couldn't find the notebooks list inside '{topic_name}'.")
    items = re.findall(r"<li>.*?</li>", ul.group(2), re.S)

    # insert in descending source-count order (matches existing layout)
    idx = len(items)
    for i, li in enumerate(items):
        if count_of(li) < new_count:
            idx = i
            break
    items.insert(idx, new_li)

    rebuilt = (ul.group(1) + "\n"
               + "\n".join("            " + li for li in items)
               + "\n          " + ul.group(3))
    new_art = target[:ul.start()] + rebuilt + target[ul.end():]
    return html.replace(target, new_art, 1)


# ─── create a new topic ─────────────────────────────────────────────────────
def add_new_topic(html, name, desc, drive_url, ga, gb, first_li):
    nb_block = first_li if first_li else (
        '<li style="opacity:.6;list-style:none;padding:10px 14px;">'
        '<span class="title">No notebooks yet</span></li>')
    article = f'''
      <article class="topic" style="--g-a:{ga}; --g-b:{gb};">
        <div class="thumb"><h2>{name}</h2></div>
        <div class="body">
          <p>{desc}</p>
          <h3>NotebookLM knowledge bases</h3>
          <ul class="notebooks">
            {nb_block}
          </ul>
          <a class="drive-link" href="{drive_url}" target="_blank" rel="noopener">Open in Drive {DRIVE_SVG}</a>
        </div>
      </article>
'''
    if "</main>" not in html:
        sys.exit("! Could not find </main> in topics.html — aborting.")
    return html.replace("    </main>", article + "\n    </main>", 1)


# ─── main ───────────────────────────────────────────────────────────────────
def main() -> None:
    ap = argparse.ArgumentParser(description="Add a NotebookLM or topic to topics.html")
    ap.add_argument("--new-topic", action="store_true", help="create a new topic")
    ap.add_argument("--topic", help="topic name (existing, or the new one's name)")
    ap.add_argument("--desc", help="description (new topic only)")
    ap.add_argument("--drive-url", help="Drive project URL (new topic only)")
    ap.add_argument("--nb-title")
    ap.add_argument("--nb-url")
    ap.add_argument("--sources", type=int)
    ap.add_argument("--shared", action="store_true")
    ap.add_argument("--push", action="store_true")
    a = ap.parse_args()

    if not os.path.exists(TOPICS):
        sys.exit("! topics.html not found — run this from the portfolio repo.")
    html = read_html()
    topics = find_topics(html)

    print("\n\U0001f4d3  Add to the Research Topics page\n" + "-" * 34)

    new_topic = a.new_topic
    if not a.topic and not new_topic:
        print("\nWhat do you want to do?")
        print("  1) Add a NotebookLM to an existing topic")
        print("  2) Create a new topic")
        new_topic = ask("Choose 1 or 2", default="1") == "2"

    # ----- gather the notebook (optional for a brand-new empty topic) -----
    def gather_notebook(optional: bool):
        if a.nb_title or a.nb_url:
            title, url = a.nb_title, a.nb_url
        else:
            if optional and not ask_yes("Add a NotebookLM now?", default_yes=True):
                return None
            title = ask("NotebookLM title")
            url = ask("NotebookLM URL (https://notebooklm.google.com/...)")
        sources = a.sources if a.sources is not None else int(ask("Source count", default="1") or "1")
        shared = a.shared or ask_yes("Is it a shared notebook?", default_yes=False)
        return build_li(title, url, sources, shared), sources

    if new_topic:
        name = a.topic or ask("New topic name")
        desc = a.desc or ask("One-paragraph description")
        drive_url = a.drive_url or ask("Drive project URL")
        ga, gb = pick_gradient(html)
        nb = gather_notebook(optional=True)
        first_li = nb[0] if nb else ""
        html = add_new_topic(html, name, desc, drive_url, ga, gb, first_li)
        summary = f'new topic "{name}" (gradient {ga}→{gb})'
        commit_msg = f"Add research topic: {name}"
    else:
        if a.topic:
            name = a.topic
        else:
            print("\nExisting topics:")
            for i, (tn, _) in enumerate(topics, 1):
                print(f"  {i}) {tn}")
            choice = ask("Pick a topic by number or name")
            if choice.isdigit() and 1 <= int(choice) <= len(topics):
                name = topics[int(choice) - 1][0]
            else:
                name = choice
        nb = gather_notebook(optional=False)
        html = add_to_topic(html, name, nb[0], nb[1])
        summary = f'NotebookLM added to "{name}"'
        commit_msg = f"Add NotebookLM to {name} on topics page"

    write_html(html)
    print(f"\n✓ {summary}.")

    git("add", "topics.html")
    res = git("commit", "-m", commit_msg)
    if res.returncode != 0:
        print(res.stdout + res.stderr)
        sys.exit("! Commit failed — nothing changed?")
    print(f"✓ Committed: {git('rev-parse', '--short', 'HEAD').stdout.strip()}")

    do_push = a.push or ask_yes("Push now to deploy via Netlify?", default_yes=True)
    if do_push:
        res = git("push")
        print(res.stdout + res.stderr)
        print("✓ Pushed. Netlify will rebuild in ~1 minute."
              if res.returncode == 0
              else f"! Push failed. Run:  cd '{REPO}' && git push")
    else:
        print(f"Skipped push. When ready:  cd '{REPO}' && git push")


if __name__ == "__main__":
    main()
