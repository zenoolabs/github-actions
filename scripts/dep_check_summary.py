#!/usr/bin/env python3
"""Summarize an OWASP dependency-check JSON report into a GitHub job summary.

Writes a Markdown findings table (dependency, CVE, severity, CVSS) to the file named
by $GITHUB_STEP_SUMMARY, so the results show up on the Actions run page and no one has
to download and unzip the HTML report. The full HTML report stays available as an
artifact for detail.

Usage:
    dep_check_summary.py <path-to-dependency-check-report.json> [max_rows]

If the report is missing or has no findings, a short "no vulnerabilities" note is
written instead. Never fails the build: reporting problems must not break CI.
"""

import json
import os
import sys

# Order used to sort findings (most severe first) and to render a small badge.
SEVERITY_RANK = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "MODERATE": 2, "LOW": 3}
DEFAULT_MAX_ROWS = 50


def cvss_score(vulnerability: dict) -> str:
    """Return the best available CVSS score for a vulnerability as a string.

    Prefers CVSS v3 base score, falls back to v2, then to a dash.

    Args:
        vulnerability: A single entry from a dependency's `vulnerabilities` list.

    Returns:
        The score as a string, or "-" when none is present.
    """
    v3 = vulnerability.get("cvssv3") or {}
    if v3.get("baseScore") is not None:
        return str(v3["baseScore"])
    v2 = vulnerability.get("cvssv2") or {}
    if v2.get("score") is not None:
        return str(v2["score"])
    return "-"


def collect_findings(report: dict) -> list:
    """Flatten a dependency-check report into a list of finding rows.

    Args:
        report: The parsed dependency-check JSON report.

    Returns:
        A list of dicts with keys: dependency, cve, severity, cvss, rank.
    """
    findings = []
    for dependency in report.get("dependencies", []):
        name = dependency.get("fileName", "unknown")
        for vulnerability in dependency.get("vulnerabilities", []):
            severity = (vulnerability.get("severity") or "UNKNOWN").upper()
            findings.append(
                {
                    "dependency": name,
                    "cve": vulnerability.get("name", "-"),
                    "severity": severity,
                    "cvss": cvss_score(vulnerability),
                    "rank": SEVERITY_RANK.get(severity, 99),
                }
            )
    findings.sort(key=lambda f: (f["rank"], f["dependency"]))
    return findings


def render(findings: list, max_rows: int) -> str:
    """Render findings as a Markdown job-summary section.

    Args:
        findings: The sorted finding rows from `collect_findings`.
        max_rows: Maximum number of rows to show before truncating.

    Returns:
        A Markdown string.
    """
    if not findings:
        return "## Dependency-Check\n\n✅ No known vulnerabilities found.\n"

    counts = {}
    for f in findings:
        counts[f["severity"]] = counts.get(f["severity"], 0) + 1
    badge = " · ".join(
        f"{sev.title()}: {counts[sev]}"
        for sev in ("CRITICAL", "HIGH", "MEDIUM", "MODERATE", "LOW")
        if sev in counts
    )

    lines = [
        f"## Dependency-Check: {len(findings)} finding(s)",
        "",
        f"**{badge}**",
        "",
        "| Dependency | CVE | Severity | CVSS |",
        "|---|---|---|---|",
    ]
    for f in findings[:max_rows]:
        lines.append(
            f"| {f['dependency']} | {f['cve']} | {f['severity'].title()} | {f['cvss']} |"
        )
    if len(findings) > max_rows:
        lines.append("")
        lines.append(
            f"_…and {len(findings) - max_rows} more. See the "
            f"`dependency-check-report` artifact for the full HTML report._"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    """Parse the report path from argv and write the summary."""
    if len(sys.argv) < 2:
        print("usage: dep_check_summary.py <report.json> [max_rows]", file=sys.stderr)
        # Not a build failure — just nothing to summarize.
        return

    report_path = sys.argv[1]
    max_rows = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_MAX_ROWS

    if not os.path.isfile(report_path):
        summary = "## Dependency-Check\n\n_No JSON report was produced._\n"
    else:
        try:
            with open(report_path, encoding="utf-8") as handle:
                report = json.load(handle)
            summary = render(collect_findings(report), max_rows)
        except (ValueError, KeyError) as error:
            summary = f"## Dependency-Check\n\n_Could not parse report: {error}._\n"

    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_file:
        with open(summary_file, "a", encoding="utf-8") as handle:
            handle.write(summary)
    else:
        print(summary)


if __name__ == "__main__":
    main()
