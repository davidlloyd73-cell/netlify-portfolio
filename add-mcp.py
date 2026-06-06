#!/usr/bin/env python3
"""
add-mcp.py  —  add a tool / MCP server to the "Things We've Built" portfolio.

Run it from inside this repo:

    python3 add-mcp.py

It will, in order:
  1. Ask for the tool's name, link (usually a GitHub repo), one-line
     description, and category badge (e.g. "Clinical · MCP Server").
  2. Insert a matching card into tools.html and a row into OVERVIEW.md.
     There is no screenshot step — MCPs/tools have no live web URL, so the
     card uses a gradient/icon tile instead of a thumbnail.
  3. Commit, and offer to push  (pushing auto-deploys via Netlify).

You can also run it non-interactively, e.g.:

    python3 add-mcp.py --name "my-mcp" --url "https://github.com/me/my-mcp" \
        --desc "Does a useful thing." --category "Clinical · MCP Server" \
        --icon "🔌" --push

Anything you don't pass as a flag, it will ask for.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.join(REPO, "tools.html")
OVERVIEW = os.path.join(REPO, "OVERVIEW.md")

# Gradient pairs the cards rotate through (matches the existing palette).
PALETTE = [
    ("#7c5cff", "#22d3ee"), ("#22d3ee", "#34d399"), ("#f472b6", "#7c5cff"),
    ("#34d399", "#fbbf24"), ("#fbbf24", "#f472b6"), ("#f472b6", "#22d3ee"),
    ("#7c5cff", "#f472b6"), ("#38bdf8", "#34d399"), ("#ef4444", "#f472b6"),
]

ICON_SVG = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M7 17L17 7M9 7h8v8"/></svg>')


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
            sys.exit(f"! '{label}' is required but no input is available. "
                     f"Pass it as a flag, e.g. --{label.split()[0].lower()}.")
        if not val and default is not None:
            return default
        if val or not required:
            return val
        print("  (required)")


def host_of(url: str) -> str:
    return re.sub(r"^https?://", "", url).rstrip("/")


def pick_gradient() -> tuple[str, str]:
    try:
        html = open(TOOLS, encoding="utf-8").read()
        n = html.count('class="card"')
    except OSError:
        n = 0
    return PALETTE[n % len(PALETTE)]


def build_card(name, url, desc, category, icon, ga, gb) -> str:
    media = (f'        <div class="shot" style="display:flex;align-items:center;'
             f'justify-content:center;background:linear-gradient(135deg,{ga},{gb});'
             f'font-size:48px;">{icon}</div>')
    return f'''
      <a class="card" href="{url}" target="_blank" rel="noopener" style="--g-a:{ga}; --g-b:{gb};">
{media}
        <span class="badge"><span class="dot"></span>{category}</span>
        <h2>{name}</h2>
        <p>{desc}</p>
        <div class="footer">
          <span class="url">{host_of(url)}</span>
          <span class="visit">Open {ICON_SVG}</span>
        </div>
      </a>
'''


def insert_card(card_html: str) -> None:
    html = open(TOOLS, encoding="utf-8").read()
    if "</main>" not in html:
        sys.exit("! Could not find </main> in tools.html — aborting.")
    html = html.replace("    </main>", card_html + "\n    </main>", 1)
    open(TOOLS, "w", encoding="utf-8").write(html)


def insert_overview_row(name: str, desc: str) -> None:
    if not os.path.exists(OVERVIEW):
        return
    text = open(OVERVIEW, encoding="utf-8").read()
    row = f"| **{name}** | {desc} |"
    # Slot the row into the "Tools & MCPs" table, just before the next section.
    marker = "\n\n## Adding to the site"
    if "## Tools & MCPs" in text and marker in text:
        before, sep, after = text.partition(marker)
        text = before.rstrip() + "\n" + row + sep + after
    else:
        text = text.rstrip() + "\n" + row + "\n"
    open(OVERVIEW, "w", encoding="utf-8").write(text)


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", REPO, *args], capture_output=True, text=True)


def main() -> None:
    ap = argparse.ArgumentParser(description="Add a tool / MCP card to the portfolio.")
    ap.add_argument("--name")
    ap.add_argument("--url", help="usually a GitHub repo URL")
    ap.add_argument("--desc")
    ap.add_argument("--category", help='e.g. "Clinical · MCP Server"')
    ap.add_argument("--icon", help="emoji for the gradient tile", default="🔌")
    ap.add_argument("--push", action="store_true", help="push without asking")
    a = ap.parse_args()

    print("\n\U0001f9f1  Add a tool / MCP to the portfolio\n" + "-" * 36)
    name = a.name or ask("Tool / MCP name")
    url = a.url or ask("Link (https://... — usually a GitHub repo)")
    if not url.startswith("http"):
        url = "https://" + url
    desc = a.desc or ask("One-line description")
    category = a.category or ask("Category badge", default="Clinical · MCP Server")
    icon = a.icon or ask("Tile emoji", default="🔌")

    ga, gb = pick_gradient()

    insert_card(build_card(name, url, desc, category, icon, ga, gb))
    insert_overview_row(name, desc)
    print(f"\n✓ Card added to tools.html and OVERVIEW.md (gradient {ga}→{gb}).")

    # Stage + commit
    git("add", "tools.html", "OVERVIEW.md")
    msg = f"Add {name} to portfolio (Tools & MCPs)"
    res = git("commit", "-m", msg)
    if res.returncode != 0:
        print(res.stdout + res.stderr)
        sys.exit("! Commit failed — nothing changed?")
    print(f"✓ Committed: {git('rev-parse', '--short', 'HEAD').stdout.strip()}")

    # Push
    do_push = a.push
    if not do_push:
        do_push = ask("Push now to deploy via Netlify? (y/n)", default="y").lower().startswith("y")
    if do_push:
        res = git("push")
        print(res.stdout + res.stderr)
        if res.returncode == 0:
            print("✓ Pushed. Netlify will rebuild in ~1 minute.")
        else:
            print("! Push failed. Run it yourself:  cd '%s' && git push" % REPO)
    else:
        print("Skipped push. When ready:  cd '%s' && git push" % REPO)


if __name__ == "__main__":
    main()
