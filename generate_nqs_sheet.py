#!/usr/bin/env python3
"""
generate_nqs_app.py

Reads the full harness results JSON and produces a self-contained HTML
rating application. Open the output file in any browser to rate NQS scores.
Ratings are exported as JSON when complete.

Usage (from repo root, venv active):
  python generate_nqs_app.py results/run_20260318_150753_full.json

Output: results/nqs_rater.html
"""

import json
import sys
from pathlib import Path
from collections import defaultdict


def load_and_group(path: str) -> dict:
    """
    Load full results JSON (condition-keyed dict) and group by case_id.
    Returns: {case_id: {"B": [turns...], "C": [turns...]}}
    Sorted by turn_number within each condition.
    """
    with open(path) as f:
        data = json.load(f)

    cases = defaultdict(lambda: {"B": [], "C": []})

    for condition in ("B", "C"):
        for turn in data.get(condition, []):
            case_id = turn["test_case_id"]
            turn["condition"] = condition
            cases[case_id][condition].append(turn)

    for case_id in cases:
        for cond in ("B", "C"):
            cases[case_id][cond].sort(key=lambda t: t["turn_number"])

    return dict(sorted(cases.items()))


def build_case_data(cases: dict) -> list:
    """
    Convert grouped cases into a JSON-serialisable list for embedding in HTML.
    Each entry holds the full turn data for both conditions.
    """
    result = []
    for case_id, conditions in cases.items():
        entry = {
            "case_id": case_id,
            "conditions": {}
        }
        for cond in ("B", "C"):
            turns = conditions[cond]
            entry["conditions"][cond] = [
                {
                    "turn_number": t["turn_number"],
                    "expects_violation": t.get("expects_violation", False),
                    "narrative": t.get("turn_result", {}).get("narrative", "").strip(),
                    "oracle_violation_detected": t.get("oracle_violation_detected", False),
                    "effectively_committed": t.get("effectively_committed", False),
                    "oracle_violations": t.get("oracle_violations", []),
                }
                for t in turns
            ]
        result.append(entry)
    return result


def generate_html(case_data: list, source_file: str) -> str:
    case_json = json.dumps(case_data, indent=2)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>VeriForge — NQS Rater</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:ital,wght@0,300;0,400;0,600;1,300;1,400&family=JetBrains+Mono:wght@400;500&display=swap');

  :root {{
    --bg:        #0e0c0a;
    --surface:   #181410;
    --border:    #2e2820;
    --accent:    #c8923a;
    --accent-dim:#7a5520;
    --text:      #e8ddd0;
    --text-dim:  #8a7a6a;
    --b-col:     #2a3a4a;
    --c-col:     #2a3a2e;
    --b-accent:  #4a8aaa;
    --c-accent:  #4aaa6a;
    --warn:      #c85a3a;
    --radius:    6px;
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    background: var(--bg);
    color: var(--text);
    font-family: 'Crimson Pro', Georgia, serif;
    font-size: 17px;
    line-height: 1.65;
    min-height: 100vh;
  }}

  /* ── Header ── */
  header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 18px 32px;
    border-bottom: 1px solid var(--border);
    background: var(--surface);
    position: sticky;
    top: 0;
    z-index: 100;
  }}

  .header-title {{
    font-size: 13px;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: var(--accent);
    font-family: 'JetBrains Mono', monospace;
    font-weight: 500;
  }}

  .progress-wrap {{
    display: flex;
    align-items: center;
    gap: 14px;
    flex: 1;
    margin: 0 32px;
  }}

  .progress-bar {{
    flex: 1;
    height: 3px;
    background: var(--border);
    border-radius: 2px;
    overflow: hidden;
  }}

  .progress-fill {{
    height: 100%;
    background: var(--accent);
    transition: width .4s ease;
    border-radius: 2px;
  }}

  .progress-label {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--text-dim);
    white-space: nowrap;
  }}

  /* ── Main layout ── */
  main {{
    max-width: 1400px;
    margin: 0 auto;
    padding: 32px 24px 80px;
  }}

  .case-header {{
    display: flex;
    align-items: baseline;
    gap: 16px;
    margin-bottom: 24px;
    padding-bottom: 14px;
    border-bottom: 1px solid var(--border);
  }}

  .case-id {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 22px;
    font-weight: 500;
    color: var(--accent);
  }}

  .case-type-badge {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    letter-spacing: .1em;
    text-transform: uppercase;
    padding: 3px 8px;
    border-radius: 3px;
    background: var(--border);
    color: var(--text-dim);
  }}

  /* ── Two-column conditions ── */
  .conditions-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 28px;
  }}

  .condition-panel {{
    border-radius: var(--radius);
    border: 1px solid var(--border);
    overflow: hidden;
  }}

  .condition-panel.cond-B {{ border-top: 3px solid var(--b-accent); }}
  .condition-panel.cond-C {{ border-top: 3px solid var(--c-accent); }}

  .cond-label {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 16px;
    background: var(--surface);
    border-bottom: 1px solid var(--border);
  }}

  .cond-dot {{
    width: 8px; height: 8px;
    border-radius: 50%;
  }}

  .cond-B .cond-dot {{ background: var(--b-accent); }}
  .cond-C .cond-dot {{ background: var(--c-accent); }}

  .cond-title {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: var(--text-dim);
  }}

  .cond-B .cond-title {{ color: var(--b-accent); }}
  .cond-C .cond-title {{ color: var(--c-accent); }}

  /* ── Turns ── */
  .turns-list {{
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }}

  .turn-block {{
    padding: 14px;
    background: var(--bg);
    border-radius: calc(var(--radius) - 2px);
    border: 1px solid var(--border);
  }}

  .turn-meta {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
  }}

  .turn-num {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    color: var(--text-dim);
    letter-spacing: .06em;
  }}

  .violation-badge {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    letter-spacing: .08em;
    text-transform: uppercase;
    padding: 2px 6px;
    border-radius: 3px;
    background: rgba(200,90,58,.15);
    color: var(--warn);
    border: 1px solid rgba(200,90,58,.3);
  }}

  .oracle-badge {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    letter-spacing: .08em;
    padding: 2px 6px;
    border-radius: 3px;
  }}

  .oracle-blocked {{
    background: rgba(200,90,58,.1);
    color: var(--warn);
    border: 1px solid rgba(200,90,58,.2);
  }}

  .oracle-clean {{
    background: rgba(74,170,106,.1);
    color: var(--c-accent);
    border: 1px solid rgba(74,170,106,.2);
  }}

  .narrative-text {{
    font-style: italic;
    color: var(--text);
    font-size: 16px;
    line-height: 1.7;
  }}

  /* ── Scoring ── */
  .scoring-row {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 32px;
  }}

  .score-panel {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px;
  }}

  .score-label {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: var(--text-dim);
    margin-bottom: 14px;
  }}

  .star-row {{
    display: flex;
    gap: 8px;
    margin-bottom: 14px;
  }}

  .star-btn {{
    width: 44px; height: 44px;
    border-radius: var(--radius);
    border: 1px solid var(--border);
    background: var(--bg);
    color: var(--text-dim);
    font-family: 'JetBrains Mono', monospace;
    font-size: 16px;
    font-weight: 500;
    cursor: pointer;
    transition: all .15s ease;
    display: flex;
    align-items: center;
    justify-content: center;
  }}

  .star-btn:hover {{
    border-color: var(--accent);
    color: var(--accent);
    background: rgba(200,146,58,.08);
  }}

  .star-btn.selected {{
    background: var(--accent);
    border-color: var(--accent);
    color: var(--bg);
    font-weight: 600;
  }}

  .notes-input {{
    width: 100%;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 10px 12px;
    color: var(--text);
    font-family: 'Crimson Pro', serif;
    font-size: 15px;
    resize: vertical;
    min-height: 60px;
    outline: none;
    transition: border-color .15s;
  }}

  .notes-input:focus {{ border-color: var(--accent-dim); }}
  .notes-input::placeholder {{ color: var(--text-dim); }}

  /* ── Navigation ── */
  .nav-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-top: 16px;
    border-top: 1px solid var(--border);
  }}

  .nav-btn {{
    padding: 10px 24px;
    border-radius: var(--radius);
    border: 1px solid var(--border);
    background: var(--surface);
    color: var(--text);
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    letter-spacing: .06em;
    cursor: pointer;
    transition: all .15s;
  }}

  .nav-btn:hover:not(:disabled) {{
    border-color: var(--accent);
    color: var(--accent);
  }}

  .nav-btn:disabled {{
    opacity: .3;
    cursor: default;
  }}

  .nav-btn.primary {{
    background: var(--accent);
    border-color: var(--accent);
    color: var(--bg);
    font-weight: 600;
  }}

  .nav-btn.primary:hover {{
    background: #d9a04a;
    border-color: #d9a04a;
    color: var(--bg);
  }}

  .completion-incomplete {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--text-dim);
  }}

  /* ── Done screen ── */
  .done-screen {{
    display: none;
    text-align: center;
    padding: 80px 32px;
  }}

  .done-screen.visible {{ display: block; }}

  .done-title {{
    font-size: 32px;
    color: var(--accent);
    margin-bottom: 12px;
  }}

  .done-sub {{
    color: var(--text-dim);
    margin-bottom: 40px;
    font-size: 16px;
  }}

  .export-btn {{
    padding: 14px 40px;
    background: var(--accent);
    border: none;
    border-radius: var(--radius);
    color: var(--bg);
    font-family: 'JetBrains Mono', monospace;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: .08em;
    cursor: pointer;
    margin-bottom: 24px;
    transition: background .15s;
  }}

  .export-btn:hover {{ background: #d9a04a; }}

  .results-preview {{
    text-align: left;
    max-width: 700px;
    margin: 0 auto;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: var(--text-dim);
    white-space: pre-wrap;
    overflow-x: auto;
    max-height: 400px;
    overflow-y: auto;
  }}

  .scale-ref {{
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    margin-bottom: 10px;
  }}

  .scale-chip {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 9px;
    padding: 3px 7px;
    border-radius: 3px;
    background: var(--bg);
    border: 1px solid var(--border);
    color: var(--text-dim);
    white-space: nowrap;
  }}

  .rating-view {{ display: block; }}
  .rating-view.hidden {{ display: none; }}
</style>
</head>
<body>

<header>
  <span class="header-title">VeriForge — NQS Rater</span>
  <div class="progress-wrap">
    <div class="progress-bar"><div class="progress-fill" id="progressFill"></div></div>
    <span class="progress-label" id="progressLabel">0 / 12 rated</span>
  </div>
  <div class="scale-ref">
    <span class="scale-chip">1 Unusable</span>
    <span class="scale-chip">2 Poor</span>
    <span class="scale-chip">3 Adequate</span>
    <span class="scale-chip">4 Good</span>
    <span class="scale-chip">5 Excellent</span>
  </div>
</header>

<main>
  <div class="rating-view" id="ratingView">
    <div class="case-header">
      <span class="case-id" id="caseId"></span>
      <span class="case-type-badge" id="caseType"></span>
    </div>

    <div class="conditions-grid" id="conditionsGrid"></div>

    <div class="scoring-row" id="scoringRow"></div>

    <div class="nav-row">
      <button class="nav-btn" id="prevBtn" onclick="navigate(-1)">← Previous</button>
      <span class="completion-incomplete" id="completionStatus"></span>
      <button class="nav-btn" id="nextBtn" onclick="navigate(1)">Next →</button>
    </div>
  </div>

  <div class="done-screen" id="doneScreen">
    <div class="done-title">All cases rated.</div>
    <div class="done-sub">Save <code>nqs_ratings.json</code> to your results/ directory and bring it to S13.</div>
    <button class="export-btn" onclick="exportResults()">Download nqs_ratings.json</button>
    <div class="results-preview" id="resultsPreview"></div>
  </div>
</main>

<script>
const CASES = {case_json};

// ratings[case_id] = {{B: {{score, notes}}, C: {{score, notes}}}}
const ratings = {{}};
CASES.forEach(c => {{
  ratings[c.case_id] = {{
    B: {{ score: null, notes: "" }},
    C: {{ score: null, notes: "" }}
  }};
}});

let current = 0;

function caseTypeLabel(case_id) {{
  if (case_id.startsWith("tc-a")) return "Type A — State Consistency";
  if (case_id.startsWith("tc-b")) return "Type B — Transition Validity";
  if (case_id.startsWith("tc-m")) return "Compound";
  return "Unknown";
}}

function renderTurns(turns) {{
  return turns.map(t => {{
    const vBadge = t.expects_violation
      ? `<span class="violation-badge">⚠ violation designed</span>` : "";
    const oBadge = t.expects_violation
      ? (t.oracle_violation_detected
          ? `<span class="oracle-badge oracle-blocked">blocked</span>`
          : `<span class="oracle-badge oracle-clean">committed</span>`)
      : "";
    return `
      <div class="turn-block">
        <div class="turn-meta">
          <span class="turn-num">Turn ${{t.turn_number}}</span>
          ${{vBadge}}${{oBadge}}
        </div>
        <div class="narrative-text">${{t.narrative || '<em style="color:var(--text-dim)">[no narrative recorded]</em>'}}</div>
      </div>`;
  }}).join("");
}}

function renderScorePanel(case_id, cond) {{
  const r = ratings[case_id][cond];
  const accentVar = cond === "B" ? "var(--b-accent)" : "var(--c-accent)";
  const stars = [1,2,3,4,5].map(n => {{
    const sel = r.score === n ? "selected" : "";
    return `<button class="star-btn ${{sel}}" onclick="setScore('${{case_id}}','${{cond}}',${{n}})">${{n}}</button>`;
  }}).join("");

  return `
    <div class="score-panel">
      <div class="score-label" style="color:${{accentVar}}">Condition ${{cond}} — NQS Score</div>
      <div class="star-row">${{stars}}</div>
      <textarea class="notes-input" placeholder="Notes (optional)…"
        oninput="setNotes('${{case_id}}','${{cond}}',this.value)">${{r.notes}}</textarea>
    </div>`;
}}

function render() {{
  const c = CASES[current];
  document.getElementById("caseId").textContent = c.case_id;
  document.getElementById("caseType").textContent = caseTypeLabel(c.case_id);

  // Conditions grid
  const grid = document.getElementById("conditionsGrid");
  grid.innerHTML = ["B","C"].map(cond => `
    <div class="condition-panel cond-${{cond}}">
      <div class="cond-label">
        <span class="cond-dot"></span>
        <span class="cond-title">Condition ${{cond}} — ${{cond === "B" ? "Session-start injection" : "Per-turn injection (VeriForge)"}}</span>
      </div>
      <div class="turns-list">${{renderTurns(c.conditions[cond])}}</div>
    </div>`).join("");

  // Scoring row
  document.getElementById("scoringRow").innerHTML =
    renderScorePanel(c.case_id, "B") + renderScorePanel(c.case_id, "C");

  // Nav
  document.getElementById("prevBtn").disabled = current === 0;
  const totalRated = Object.values(ratings).filter(r => r.B.score !== null && r.C.score !== null).length;
  updateProgress(totalRated);

  const allThisRated = ratings[c.case_id].B.score !== null && ratings[c.case_id].C.score !== null;
  const isLast = current === CASES.length - 1;
  const nextBtn = document.getElementById("nextBtn");

  if (isLast && totalRated === CASES.length) {{
    nextBtn.textContent = "Finish →";
    nextBtn.className = "nav-btn primary";
    nextBtn.onclick = showDone;
  }} else {{
    nextBtn.textContent = "Next →";
    nextBtn.className = "nav-btn";
    nextBtn.onclick = () => navigate(1);
    nextBtn.disabled = isLast;
  }}

  const status = document.getElementById("completionStatus");
  const bDone = ratings[c.case_id].B.score !== null;
  const cDone = ratings[c.case_id].C.score !== null;
  if (bDone && cDone) {{
    status.textContent = "✓ Both conditions rated";
    status.style.color = "var(--c-accent)";
  }} else {{
    const missing = (!bDone && !cDone) ? "B and C" : (!bDone ? "B" : "C");
    status.textContent = `Score Condition ${{missing}} to continue`;
    status.style.color = "var(--text-dim)";
  }}
}}

function setScore(case_id, cond, score) {{
  ratings[case_id][cond].score = score;
  render();
}}

function setNotes(case_id, cond, val) {{
  ratings[case_id][cond].notes = val;
}}

function navigate(dir) {{
  current = Math.max(0, Math.min(CASES.length - 1, current + dir));
  render();
  window.scrollTo({{top: 0, behavior: "smooth"}});
}}

function updateProgress(rated) {{
  const total = CASES.length;
  document.getElementById("progressFill").style.width = `${{(rated / total) * 100}}%`;
  document.getElementById("progressLabel").textContent = `${{rated}} / ${{total}} rated`;
}}

function buildExport() {{
  const out = [];
  CASES.forEach(c => {{
    ["B","C"].forEach(cond => {{
      out.push({{
        case_id: c.case_id,
        condition: cond,
        nqs: ratings[c.case_id][cond].score,
        notes: ratings[c.case_id][cond].notes
      }});
    }});
  }});
  return out;
}}

function showDone() {{
  document.getElementById("ratingView").classList.add("hidden");
  document.getElementById("doneScreen").classList.add("visible");
  document.getElementById("resultsPreview").textContent =
    JSON.stringify(buildExport(), null, 2);
}}

function exportResults() {{
  const blob = new Blob([JSON.stringify(buildExport(), null, 2)], {{type: "application/json"}});
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "nqs_ratings.json";
  a.click();
  URL.revokeObjectURL(url);
}}

render();
</script>
</body>
</html>"""


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_nqs_app.py <path_to_full_results.json>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = Path(input_path).parent / "nqs_rater.html"

    cases = load_and_group(input_path)
    case_data = build_case_data(cases)
    html = generate_html(case_data, input_path)

    output_path.write_text(html, encoding="utf-8")
    print(f"Rating app written to: {output_path}")
    print(f"Open in browser: file://{output_path.resolve()}")
    print(f"Cases: {len(case_data)} — {len(case_data) * 2} ratings required (B + C per case)")


if __name__ == "__main__":
    main()