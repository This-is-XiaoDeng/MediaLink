from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from medialink.models import Series, MappingEntry, LinkMode

console = Console(force_terminal=True, legacy_windows=False)


def print_banner() -> None:
    title = Text("MediaLink", style="bold bright_cyan")
    console.print(Panel(title, subtitle="media library linker", border_style="cyan"))


def print_series_summary(series_list: list[Series]) -> None:
    if not series_list:
        console.print("[yellow]No recognizable media files found.[/]")
        return

    table = Table(title="Scan Results", border_style="dim blue")
    table.add_column("Title", style="bright_white")
    table.add_column("Seasons", style="cyan")
    table.add_column("Episodes", style="green")
    table.add_column("Movies", style="magenta")
    table.add_column("Files", style="yellow")

    for series in sorted(series_list, key=lambda s: s.title.lower()):
        total_eps = sum(len(s.episodes) for s in series.seasons.values())
        total_movies = len(series.movies)
        total_files = sum(
            sum(1 + len(ep.subtitles) for ep in season.episodes.values())
            for season in series.seasons.values()
        ) + sum(
            1 + len(ep.subtitles) for ep in series.movies.values()
        )
        seasons_str = ", ".join(f"S{s:02d}" for s in sorted(series.seasons.keys())) if series.seasons else "-"
        table.add_row(series.title, seasons_str, str(total_eps), str(total_movies), str(total_files))

    console.print(table)


def print_dry_run(entries: list[MappingEntry]) -> None:
    console.print("\n[bold yellow]--dry-run mode: the following operations would be performed[/]")

    table = Table(title="Planned Operations", border_style="dim yellow")
    table.add_column("#", style="dim", width=4)
    table.add_column("Action", style="cyan", width=8)
    table.add_column("Source", style="dim white")
    table.add_column("=>", style="bright_white", width=3)
    table.add_column("Target", style="green")

    for i, entry in enumerate(entries, 1):
        action = _mode_label(entry.mode)
        table.add_row(str(i), action, str(entry.source), "=>", str(entry.target))

    console.print(table)
    console.print(f"\n[dim]Total: {len(entries)} file operations[/]")


def print_result(entries: list[MappingEntry], created: int, skipped: int, errors: int, dry_run: bool) -> None:
    if dry_run:
        return

    console.print(f"\n[bold green]Done![/] Created: {created}, Skipped: {skipped}, Errors: {errors}")


def print_errors(errors: list[tuple[Path, Path, str]]) -> None:
    if not errors:
        return
    console.print("\n[bold red]Errors:[/]")
    for src, dst, msg in errors:
        console.print(f"  [red]X[/] {src} -> {dst}: {msg}")


def _mode_label(mode: LinkMode) -> str:
    labels = {
        LinkMode.SOFT: "symlink",
        LinkMode.HARD: "hardlink",
        LinkMode.COPY: "copy",
        LinkMode.MOVE: "move",
    }
    return labels.get(mode, mode.value)
