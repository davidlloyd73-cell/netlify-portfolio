#!/usr/bin/env python3
"""
add-app.py  —  add a new project to the "Things We've Built" portfolio.

Run it from inside this repo:

    python3 add-app.py

It will, in order:
  1. Ask for the app's name, live URL, one-line description, category, and
     what it's built with (Streamlit / static HTML / React / other).
  2. Screenshot the live URL with headless Chrome and save it 800x500 to
     screenshots/<slug>.jpg  (falls back to a coloured tile if that fails).
  3. Insert a matching card into index.html and a row into OVERVIEW.md.
  4. Commit, and offer to push  (pushing auto-deploys via Netlify).
  5. Print the exact "← All projects" back-button snippet to paste into the
     new app, so it links back here when opened from the portfolio.

You can also run it non-interactively, e.g.:

    python3 add-app.py --name "My App" --url "https://my-app.netlify.app" \
        --desc "Does a useful thing." --category "Business · Tool" \
        --framework html --push

Anything you don't pass as a flag, it will ask for.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(REPO, "index.html")
OVERVIEW = os.path.join(REPO, "OVERVIEW.md")
SHOTS = os.path.join(REPO, "screenshots")
PORTFOLIO_URL = "https://things-we-have-built.netlify.app/"

# Gradient pairs the cards rotate through (matches the existing palette).
PALETTE = [
    ("#7c5cff", "#22d3ee"), ("#22d3ee", "#34d399"), ("#f472b6", "#7c5cff"),
    ("#34d399", "#fbbf24"), ("#fbbf24", "#f472b6"), ("#f472b6", "#22d3ee"),
    ("#7c5cff", "#f472b6"), ("#38bdf8", "#34d399"), ("#ef4444", "#f472b6"),
]

CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
]

# Back-button snippets, one per framework. The portfolio appends ?nav=1 to
# every card link, so each snippet shows the link only when nav=1 is present.
BACK_SNIPPETS = {
    "streamlit": '''# --- Back to portfolio: only when opened from the projects site (?nav=1) ---
# Put this near the top of your main page body, before st.title(...).
if st.query_params.get("nav") == "1":
    st.link_button("← All projects", "%s")''' % PORTFOLIO_URL,

    "html": '''<!-- Back-to-portfolio pill: shows only when opened from the portfolio (?nav=1). -->
<!-- Paste just inside <body>. -->
<a id="all-projects-link" href="%s"
   style="display:none;position:fixed;top:14px;left:14px;z-index:99999;
          font:600 14px/1 'Segoe UI',system-ui,sans-serif;color:#fff;
          background:rgba(0,0,0,0.6);padding:10px 16px;border-radius:999px;
          text-decoration:none;backdrop-filter:blur(6px);">← All projects</a>
<script>
  if (new URLSearchParams(location.search).get('nav') === '1') {
    document.getElementById('all-projects-link').style.display = 'inline-block';
  }
</script>''' % PORTFOLIO_URL,

    "react": '''{/* Back to portfolio: only when opened from the projects site (?nav=1). */}
{new URLSearchParams(window.location.search).get("nav") === "1" && (
  <a href="%s"
     style={{ position: "fixed", top: 14, left: 14, zIndex: 99999, color: "#fff",
              background: "rgba(0,0,0,0.6)", padding: "10px 16px", borderRadius: 999,
              textDecoration: "none", fontWeight: 600, fontFamily: "system-ui, sans-serif" }}>
    ← All projects
  </a>
)}''' % PORTFOLIO_URL,
}

ICON_SVG = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M7 17L17 7M9 7h8v8"/></svg>')


def ask(label: str, default: str | None = None, required: bool = True) -> str:
    suffix = f" [{default}]" if default else ""
    while True:
        try:
            val = input(f"{label}{suffix}: ").strip()
        except EOFError:
            # Non-interactive (piped) and nothing supplied: take the default,
            # or empty if optional, rather than crashing.
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


def slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s or "app"


def host_of(url: str) -> str:
    return re.sub(r"^https?://", "", url).rstrip("/")


def find_chrome() -> str | None:
    for path in CHROME_CANDIDATES:
        if os.path.exists(path):
            return path
    return None


def screenshot(url: str, dest: str) -> bool:
    """Headless-Chrome screenshot of url, resized to 800x500. True on success."""
    chrome = find_chrome()
    if not chrome:
        print("  ! No Chrome/Chromium found — using a coloured tile instead.")
        return False
    tmp = "/tmp/_addapp_shot.png"
    print("  * Waking the app and capturing a screenshot (up to ~30s)...")
    try:
        subprocess.run(
            [chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars",
             f"--screenshot={tmp}", "--window-size=1440,900",
             "--virtual-time-budget=25000", url],
            check=True, capture_output=True, timeout=90,
        )
    except Exception as e:  # noqa: BLE001
        print(f"  ! Screenshot failed ({e}); using a coloured tile instead.")
        return False
    if not os.path.exists(tmp):
        return False
    # Resize to 800 wide (1440x900 -> 800x500) with macOS sips if available.
    if _which("sips"):
        subprocess.run(["sips", "--resampleWidth", "800", "-s", "format", "jpeg",
                        "-s", "formatOptions", "82", tmp, "--out", dest],
                       check=False, capture_output=True)
    else:
        # No sips: just move the PNG to the .jpg name (browsers don't care).
        os.replace(tmp, dest)
    return os.path.exists(dest)


def _which(cmd: str) -> bool:
    return subprocess.run(["which", cmd], capture_output=True).returncode == 0


def pick_gradient() -> tuple[str, str]:
    try:
        html = open(INDEX, encoding="utf-8").read()
        n = html.count('class="card"')
    except OSError:
        n = 0
    return PALETTE[n % len(PALETTE)]


def build_card(name, url, desc, category, slug, has_shot, ga, gb) -> str:
    link = url if "?" in url else url + "?nav=1"
    if has_shot:
        media = (f'        <img class="shot" src="screenshots/{slug}.jpg" '
                 f'alt="{name}" loading="lazy">')
    else:
        media = (f'        <div class="shot" style="display:flex;align-items:center;'
                 f'justify-content:center;background:linear-gradient(135deg,{ga},{gb});'
                 f'font-size:48px;">\U0001fa84</div>')
    return f'''
      <a class="card" href="{link}" target="_blank" rel="noopener" style="--g-a:{ga}; --g-b:{gb};">
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
    html = open(INDEX, encoding="utf-8").read()
    if "</main>" not in html:
        sys.exit("! Could not find </main> in index.html — aborting.")
    html = html.replace("    </main>", card_html + "\n    </main>", 1)
    open(INDEX, "w", encoding="utf-8").write(html)


def insert_overview_row(name: str, desc: str) -> None:
    if not os.path.exists(OVERVIEW):
        return
    text = open(OVERVIEW, encoding="utf-8").read()
    marker = "\n\n## How it's made"
    row = f"| **{name}** | {desc} |"
    if marker in text:
        before, sep, after = text.partition(marker)
        text = before.rstrip() + "\n" + row + sep + after
    else:
        text = text.rstrip() + "\n" + row + "\n"
    open(OVERVIEW, "w", encoding="utf-8").write(text)


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", REPO, *args], capture_output=True, text=True)


def main() -> None:
    ap = argparse.ArgumentParser(description="Add a project card to the portfolio.")
    ap.add_argument("--name")
    ap.add_argument("--url")
    ap.add_argument("--desc")
    ap.add_argument("--category", help='e.g. "Clinical · Tool"')
    ap.add_argument("--framework", choices=["streamlit", "html", "react", "other"])
    ap.add_argument("--no-screenshot", action="store_true")
    ap.add_argument("--push", action="store_true", help="push without asking")
    a = ap.parse_args()

    print("\n\U0001f9f1  Add a new app to the portfolio\n" + "-" * 36)
    name = a.name or ask("App name")
    url = a.url or ask("Live URL (https://...)")
    if not url.startswith("http"):
        url = "https://" + url
    desc = a.desc or ask("One-line description")
    category = a.category or ask("Category badge", default="Clinical · Tool")
    framework = a.framework or ask(
        "Built with? (streamlit/html/react/other)", default="other").lower()

    slug = slugify(name)
    ga, gb = pick_gradient()

    os.makedirs(SHOTS, exist_ok=True)
    has_shot = False
    if not a.no_screenshot:
        # Screenshot the bare URL (clean shot, no nav pill in the thumbnail).
        has_shot = screenshot(url, os.path.join(SHOTS, f"{slug}.jpg"))

    insert_card(build_card(name, url, desc, category, slug, has_shot, ga, gb))
    insert_overview_row(name, desc)
    print(f"\n✓ Card added to index.html and OVERVIEW.md (gradient {ga}→{gb}).")

    # Stage + commit
    paths = ["index.html", "OVERVIEW.md"]
    if has_shot:
        paths.append(f"screenshots/{slug}.jpg")
    git("add", *paths)
    msg = f"Add {name} to portfolio"
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

    # Back-button reminder
    snippet = BACK_SNIPPETS.get(framework)
    print("\n" + "=" * 60)
    if snippet:
        print(f"NEXT: add the ← All projects button to your {framework} app.")
        print("Paste this into the app, commit & push that repo too:\n")
        print(snippet)
    else:
        print("NEXT: add a link back to the portfolio in your app:")
        print(f"  {PORTFOLIO_URL}")
        print("Show it only when the URL contains ?nav=1 so the app stays")
        print("standalone when shared on its own.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
