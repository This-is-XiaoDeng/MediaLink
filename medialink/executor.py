from __future__ import annotations

import shutil
from pathlib import Path

from medialink.models import MappingEntry, LinkMode


class ExecutorResult:
    def __init__(self) -> None:
        self.created: list[tuple[Path, Path]] = []
        self.skipped: list[tuple[Path, Path, str]] = []
        self.errors: list[tuple[Path, Path, str]] = []
        self.dry_run: bool = False


def execute_mappings(entries: list[MappingEntry], dry_run: bool = False) -> ExecutorResult:
    result = ExecutorResult()
    result.dry_run = dry_run

    for entry in entries:
        if dry_run:
            result.created.append((entry.source, entry.target))
            continue

        try:
            entry.target.parent.mkdir(parents=True, exist_ok=True)

            if entry.target.exists() or entry.target.is_symlink():
                result.skipped.append((entry.source, entry.target, "target already exists"))
                continue

            _perform_action(entry)
            result.created.append((entry.source, entry.target))
        except OSError as e:
            result.errors.append((entry.source, entry.target, str(e)))

    return result


def _perform_action(entry: MappingEntry) -> None:
    if entry.mode == LinkMode.SOFT:
        entry.target.symlink_to(entry.source)
    elif entry.mode == LinkMode.HARD:
        entry.target.hardlink_to(entry.source)
    elif entry.mode == LinkMode.COPY:
        shutil.copy2(entry.source, entry.target)
    elif entry.mode == LinkMode.MOVE:
        shutil.move(str(entry.source), str(entry.target))
