#!/usr/bin/env python3
"""
Generate an HTML report from a saved eval JSON file.

Usage:
  python scripts/generate_report.py results/eval_20260314_120000.json
  python scripts/generate_report.py            # uses most recent result file
"""

import json
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
RESULTS_DIR = ROOT / "results"


def score_color(score) -> str:
    if not score:
        return "#888"
    if score >= 4:
        return "#22c55e"
    if score >= 3:
        return "#f59e0b"
    return "#ef4444"


def pct_color(pct: int) -> str:
    if pct >= 80:
        return "#22c55e"
    if pct >= 50:
        return "#f59e0b"
    return "#ef4444"


def pips_html(score) -> str:
    s = int(score) if score else 0
    parts = []
    for i in range(1, 6):
        bg = score_color(s) if i <= s else "#2a2a2a"
        parts.append('<div class="pip" style="background:' + bg + '"></div>')
    return "".join(parts)


def dim_row(label: str, score) -> str:
    return (
        '<div class="dim">'
        '<span>' + label + '</span>'
        '<div class="pips">' + pips_html(score) + '</div>'
        '<strong style="color:' + score_color(score) + '">' + str(score) + '</strong>'
        '</div>'
    )


def generate_report(data: dict) -> str:
    summary = data["summary"]
    results = data["results"]
    model = data.get("model", "Unknown")

    pass_rate_num = int(summary["pass_rate"].replace("%", ""))
    judge_score = summary.get("avg_judge_score")

    # Category rows
    cat_rows = ""
    for cat, stats in summary["by_category"].items():
        pct = round(stats["passed"] / stats["total"] * 100)
        cat_rows += (
            "<tr>"
            "<td>" + cat.replace("_", " ").title() + "</td>"
            "<td>" + str(stats["passed"]) + "/" + str(stats["total"]) + "</td>"
            '<td><div class="bar-wrap"><div class="bar" style="width:' + str(pct) + '%;background:' + pct_color(pct) + '"></div></div>'
            '<span style="color:' + pct_color(pct) + ';font-weight:600">' + str(pct) + '%</span></td>'
            "</tr>"
        )

    # Task detail cards
    task_cards = ""
    for r in results:
        js = r.get("judge_scores") or {}
        pass_badge = '<span class="badge pass">PASS</span>' if r["test_passed"] else '<span class="badge fail">FAIL</span>'

        error_section = ""
        if r.get("test_error") and not r["test_passed"]:
            error_section = '<div class="error-box"><strong>Error:</strong> ' + r["test_error"][:300] + "</div>"

        judge_section = ""
        if js and js.get("overall", 0) > 0:
            dims_html = (
                dim_row("Correctness", js.get("correctness", 0)) +
                dim_row("Code Quality", js.get("code_quality", 0)) +
                dim_row("Completeness", js.get("completeness", 0)) +
                dim_row("Explanation", js.get("explanation", 0))
            )
            overall_score = js.get("overall", 0)
            reasoning = js.get("reasoning", "")
            judge_section = (
                '<div class="judge-box">'
                '<div class="judge-header">'
                '<span>&#129302; Judge Score</span>'
                '<strong style="color:' + score_color(overall_score) + ';font-size:1.4em">' + str(overall_score) + '/5</strong>'
                "</div>"
                '<div class="dims">' + dims_html + "</div>"
                '<p class="reasoning">&ldquo;' + reasoning + "&rdquo;</p>"
                "</div>"
            )

        code_preview = r.get("solution_code", "")[:600].replace("<", "&lt;").replace(">", "&gt;")
        has_more = "..." if len(r.get("solution_code", "")) > 600 else ""

        task_cards += (
            '<div class="task-card" id="' + r["task_id"] + '">'
            '<div class="task-header">'
            "<div>"
            '<span class="task-id">' + r["task_id"] + "</span>"
            '<span class="category-tag">' + r["category"].replace("_", " ") + "</span>"
            '<span class="diff-tag diff-' + r["difficulty"] + '">' + r["difficulty"] + "</span>"
            "</div>"
            '<div style="display:flex;align-items:center;gap:12px">'
            '<span class="latency">' + (str(r["latency_ms"]) + "ms" if r.get("latency_ms") is not None else "N/A") + "</span>"
            + pass_badge +
            "</div>"
            "</div>"
            "<h3>" + r["title"] + "</h3>"
            + error_section +
            "<details>"
            "<summary>View solution code</summary>"
            "<pre><code>" + code_preview + has_more + "</code></pre>"
            "</details>"
            + judge_section +
            "</div>"
        )

    judge_card = ""
    if judge_score:
        judge_card = (
            '<div class="stat-card">'
            '<div class="stat-label">Avg Judge Score</div>'
            '<div class="stat-value" style="color:' + score_color(judge_score) + '">' +
            str(judge_score) + '<span style="font-size:.5em">/5</span></div>'
            "</div>"
        )

    avg_latency = summary.get("avg_latency_ms", "?")

    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Qwencode Eval Report</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'SF Mono', 'Fira Code', monospace; background: #0d1117; color: #c9d1d9; min-height: 100vh; }
    .header { background: linear-gradient(135deg, #161b22 0%, #0d1117 100%); border-bottom: 1px solid #30363d; padding: 32px 48px; }
    .header h1 { font-size: 1.6em; font-weight: 700; color: #f0f6fc; letter-spacing: -0.5px; }
    .header h1 span { color: #58a6ff; }
    .meta { color: #8b949e; font-size: .85em; margin-top: 6px; }
    .content { max-width: 1100px; margin: 0 auto; padding: 32px 24px; }
    .stats-row { display: flex; gap: 16px; margin-bottom: 32px; flex-wrap: wrap; }
    .stat-card { background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 20px 24px; flex: 1; min-width: 140px; }
    .stat-label { color: #8b949e; font-size: .75em; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px; }
    .stat-value { font-size: 2.2em; font-weight: 700; color: #f0f6fc; line-height: 1; }
    .section-title { font-size: 1em; font-weight: 600; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 16px; }
    table { width: 100%; border-collapse: collapse; background: #161b22; border: 1px solid #30363d; border-radius: 10px; overflow: hidden; margin-bottom: 32px; }
    th { background: #21262d; color: #8b949e; font-size: .75em; text-transform: uppercase; letter-spacing: 1px; padding: 12px 16px; text-align: left; }
    td { padding: 12px 16px; border-top: 1px solid #21262d; color: #c9d1d9; }
    .bar-wrap { display: inline-block; width: 100px; height: 6px; background: #30363d; border-radius: 3px; margin-right: 8px; vertical-align: middle; }
    .bar { height: 100%; border-radius: 3px; }
    .task-card { background: #161b22; border: 1px solid #30363d; border-radius: 10px; padding: 20px 24px; margin-bottom: 16px; }
    .task-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
    .task-id { font-size: .8em; font-weight: 700; color: #58a6ff; background: #0d1f3c; padding: 3px 8px; border-radius: 4px; margin-right: 8px; }
    .category-tag { font-size: .75em; color: #8b949e; background: #21262d; padding: 3px 8px; border-radius: 4px; margin-right: 6px; }
    .diff-tag { font-size: .7em; padding: 2px 7px; border-radius: 4px; text-transform: uppercase; letter-spacing: .5px; }
    .diff-easy { color: #22c55e; background: #0f2a1a; }
    .diff-medium { color: #f59e0b; background: #2a1f0a; }
    .diff-hard { color: #ef4444; background: #2a0f0f; }
    .latency { font-size: .8em; color: #8b949e; }
    .badge { font-size: .75em; font-weight: 700; padding: 4px 10px; border-radius: 4px; }
    .badge.pass { color: #22c55e; background: #0f2a1a; }
    .badge.fail { color: #ef4444; background: #2a0f0f; }
    h3 { color: #e6edf3; font-size: .95em; font-weight: 500; margin-bottom: 12px; }
    .error-box { background: #2a0f0f; border: 1px solid #ef444440; border-radius: 6px; padding: 10px 14px; font-size: .82em; color: #ef4444; margin-bottom: 12px; }
    details { margin-bottom: 12px; }
    summary { cursor: pointer; color: #58a6ff; font-size: .82em; padding: 4px 0; user-select: none; }
    pre { background: #0d1117; border: 1px solid #30363d; border-radius: 6px; padding: 14px; overflow-x: auto; margin-top: 8px; }
    code { font-size: .8em; color: #c9d1d9; line-height: 1.5; white-space: pre; }
    .judge-box { background: #0d1117; border: 1px solid #30363d; border-radius: 8px; padding: 14px; margin-top: 4px; }
    .judge-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; font-size: .85em; color: #8b949e; }
    .dims { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; margin-bottom: 10px; }
    .dim { display: flex; align-items: center; gap: 8px; font-size: .8em; }
    .dim span { color: #8b949e; width: 90px; flex-shrink: 0; }
    .pips { display: flex; gap: 3px; }
    .pip { width: 10px; height: 10px; border-radius: 2px; }
    .reasoning { font-size: .8em; color: #8b949e; font-style: italic; border-top: 1px solid #21262d; padding-top: 8px; }
  </style>
</head>
<body>
  <div class="header">
    <h1>Qwencode Eval &mdash; <span>""" + model + """</span></h1>
    <div class="meta">Generated """ + datetime.now().strftime("%Y-%m-%d %H:%M") + " &middot; " + str(summary["total_tasks"]) + " tasks &middot; " + str(avg_latency) + """ms avg latency</div>
  </div>
  <div class="content">
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-label">Pass Rate</div>
        <div class="stat-value" style="color:""" + pct_color(pass_rate_num) + '">' + summary["pass_rate"] + """</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Passed</div>
        <div class="stat-value" style="color:#22c55e">""" + str(summary["passed"]) + """</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Failed</div>
        <div class="stat-value" style="color:#ef4444">""" + str(summary["failed"]) + """</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Avg Latency</div>
        <div class="stat-value">""" + str(avg_latency) + """<span style="font-size:.4em">ms</span></div>
      </div>
      """ + judge_card + """
    </div>

    <div class="section-title">By Category</div>
    <table>
      <thead><tr><th>Category</th><th>Score</th><th>Pass Rate</th></tr></thead>
      <tbody>""" + cat_rows + """</tbody>
    </table>

    <div class="section-title">Task Results</div>
    """ + task_cards + """
  </div>
</body>
</html>"""
    return html


def main():
    if len(sys.argv) > 1:
        result_file = Path(sys.argv[1])
    else:
        files = sorted(RESULTS_DIR.glob("eval_*.json"), reverse=True)
        if not files:
            print("No result files found. Run grade.py first.")
            sys.exit(1)
        result_file = files[0]
        print(f"Using most recent: {result_file.name}")

    data = json.loads(result_file.read_text())
    html = generate_report(data)

    out = result_file.with_suffix(".html")
    out.write_text(html)
    print(f"Report saved -> {out}")
    print(f"Open with:   open {out}")


if __name__ == "__main__":
    main()
