from __future__ import annotations

import argparse
import sys
from pathlib import Path

from medialink.models import LinkMode, Override
from medialink.scanner import scan_directory
from medialink.identifier import identify_and_group
from medialink.planner import plan_mappings
from medialink.executor import execute_mappings
from medialink.output import (
    console,
    print_banner,
    print_series_summary,
    print_dry_run,
    print_result,
    print_errors,
)

VERSION = "0.1.0"

COPYRIGHT_TEXT = """MediaLink
Copyright (C) 2026  This-is-XiaoDeng

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>."""


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="medialink",
        description="Scan and organize media files by creating links (symlinks) into a structured library.",
    )
    parser.add_argument("source", type=Path, help="Source media directory to scan")
    parser.add_argument("target", type=Path, help="Target media library root directory")
    parser.add_argument(
        "--mode",
        choices=["soft", "hard", "copy", "move"],
        default="soft",
        help="Link mode: soft (symlink, default), hard (hardlink), copy, move",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview operations without executing them",
    )
    parser.add_argument(
        "--override",
        "-o",
        action="append",
        metavar="KEY=VALUE",
        help="Override metadata. e.g. --override title='New Title' --override season=2",
    )
    parser.add_argument(
        "--include-other",
        action="store_true",
        help="Include non-media files (by default .txt, .nfo etc are skipped)",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Reduce output verbosity",
    )
    parser.add_argument(
        "--auto-number",
        action="store_true",
        help="Auto-assign sequential episode numbers to files whose episode cannot be detected",
    )
    parser.add_argument(
        "--skip-specials",
        action="store_true",
        help="Skip files in SPs, Specials, OVA and similar directories",
    )
    parser.add_argument(
        "--movie-dir",
        type=Path,
        default=None,
        help="Target directory for movies/OVAs (default: TARGET/movies/)",
    )
    parser.add_argument(
        "--version",
        "-V",
        action="version",
        version=VERSION,
    )
    parser.add_argument(
        "--copyright",
        action="store_true",
        help="Display copyright and license information and exit",
    )

    args = parser.parse_args()

    if args.copyright:
        print(COPYRIGHT_TEXT)
        return

    print_banner()

    source_dir = args.source.expanduser().resolve()
    target_dir = args.target.expanduser().resolve()

    if not source_dir.is_dir():
        console.print(f"[red]Error: source directory not found: {source_dir}[/]")
        sys.exit(1)

    mode = LinkMode(args.mode)
    overrides = _parse_overrides(args.override or [])

    files = scan_directory(source_dir, include_other=args.include_other)
    series_list = identify_and_group(files, overrides, auto_number=args.auto_number, skip_specials=args.skip_specials)

    print_series_summary(series_list)

    mappings = plan_mappings(series_list, target_dir, mode, movie_dir=args.movie_dir)

    if not mappings:
        console.print("[yellow]No files to process.[/]")
        return

    if args.dry_run:
        print_dry_run(mappings)
        return

    result = execute_mappings(mappings, dry_run=False)

    if not args.quiet:
        _print_created(result)

    print_result(
        mappings,
        created=len(result.created),
        skipped=len(result.skipped),
        errors=len(result.errors),
        dry_run=False,
    )
    print_errors(result.errors)


def _parse_overrides(raw: list[str]) -> list[Override]:
    ov = Override()
    has_custom = False
    for item in raw:
        if "=" not in item:
            continue
        key, _, value = item.partition("=")
        key = key.strip().lower()
        value = value.strip().strip("'\"")
        if key == "title":
            ov.title = value
            has_custom = True
        elif key == "season":
            ov.season = int(value)
            has_custom = True
        elif key == "episode_offset":
            ov.episode_offset = int(value)
            has_custom = True
    return [ov] if has_custom else []


def _print_created(result) -> None:
    for src, dst in result.created:
        console.print(f"  [green]+[/] {dst}")
