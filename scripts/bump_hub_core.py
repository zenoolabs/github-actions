#!/usr/bin/env python3
"""Bump the `hubBackendVersion` literal in a hub instance's build.gradle.

Used by the reusable `hub-core-bump` workflow, which runs when hub core publishes
a new release. Kept as a script (rather than inline shell) so the parse/validate/
rewrite logic is readable and testable on its own.

Usage:
    bump_hub_core.py --version 3.176.0 [--file build.gradle]

Writes `current`, `previous` and `changed` to $GITHUB_OUTPUT when that env var is
set, so the calling workflow can branch on whether anything actually changed.

Exit codes:
    0  success (changed=true, or changed=false when already at the target version)
    1  refused: bad version, missing file, or no hubBackendVersion found
"""

import argparse
import os
import re
import sys

# `version` reaches the workflow through a repository_dispatch client_payload, which
# any actor able to dispatch on the instance repo controls, and it is substituted into
# build.gradle, a branch name and a commit message. Constrain it to a bare X.Y.Z.
VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")

# Matches:  hubBackendVersion = '3.173.1'
# Captures the surrounding text so indentation and quoting are preserved on rewrite.
ASSIGNMENT_PATTERN = re.compile(r"(hubBackendVersion\s*=\s*')([^']+)(')")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Namespace with `version` (target hub core version) and `file` (build.gradle path).
    """
    parser = argparse.ArgumentParser(description="Bump hubBackendVersion in build.gradle")
    parser.add_argument("--version", required=True, help="Target hub core version, e.g. 3.176.0")
    parser.add_argument("--file", default="build.gradle", help="Path to build.gradle")
    return parser.parse_args()


def fail(message: str) -> None:
    """Emit a GitHub Actions error annotation and exit non-zero.

    Args:
        message: Human-readable reason the bump was refused.
    """
    print(f"::error::{message}", file=sys.stderr)
    sys.exit(1)


def write_outputs(**outputs: str) -> None:
    """Append key=value pairs to the GitHub Actions step output file.

    No-ops when GITHUB_OUTPUT is unset, so the script stays runnable locally.

    Args:
        **outputs: Output names mapped to their values.
    """
    path = os.environ.get("GITHUB_OUTPUT")
    if not path:
        return
    with open(path, "a", encoding="utf-8") as handle:
        for key, value in outputs.items():
            handle.write(f"{key}={value}\n")


def bump(source: str, target_version: str) -> tuple[str, str]:
    """Rewrite the hubBackendVersion literal in build.gradle contents.

    Args:
        source: Full text of build.gradle.
        target_version: Version to pin hub core to.

    Returns:
        Tuple of (new contents, previous version).

    Raises:
        ValueError: If no hubBackendVersion assignment is present.
    """
    match = ASSIGNMENT_PATTERN.search(source)
    if not match:
        raise ValueError("no hubBackendVersion assignment found in build.gradle")

    previous = match.group(2)
    updated = ASSIGNMENT_PATTERN.sub(
        lambda m: f"{m.group(1)}{target_version}{m.group(3)}", source, count=1
    )
    return updated, previous


def main() -> None:
    """Validate inputs, rewrite build.gradle, and report what changed."""
    args = parse_args()

    if not VERSION_PATTERN.match(args.version):
        fail(f"refusing to bump: '{args.version}' is not a bare X.Y.Z version")

    if not os.path.isfile(args.file):
        fail(f"{args.file} not found")

    with open(args.file, encoding="utf-8") as handle:
        source = handle.read()

    try:
        updated, previous = bump(source, args.version)
    except ValueError as error:
        fail(str(error))
        return  # unreachable; keeps type checkers happy

    if previous == args.version:
        print(f"Already on {args.version}; nothing to do.")
        write_outputs(changed="false")
        return

    with open(args.file, "w", encoding="utf-8") as handle:
        handle.write(updated)

    print(f"Bumped hubBackendVersion: {previous} -> {args.version}")
    write_outputs(changed="true", previous=previous, current=args.version)


if __name__ == "__main__":
    main()
