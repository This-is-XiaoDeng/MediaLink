from __future__ import annotations

import re
from pathlib import Path

from medialink.models import Series, Season, Episode, MediaFile, MediaType, FileKind, LinkMode, MappingEntry


def plan_mappings(
    series_list: list[Series],
    target_root: Path,
    mode: LinkMode = LinkMode.SOFT,
) -> list[MappingEntry]:
    entries: list[MappingEntry] = []

    for series in series_list:
        category = "anime" if series.media_type == MediaType.EPISODE else "movies"

        for season_num in sorted(series.seasons.keys()):
            season = series.seasons[season_num]
            for ep_num in sorted(season.episodes.keys()):
                episode = season.episodes[ep_num]
                entries.extend(_plan_episode(series, season, episode, target_root, category, mode))

    return entries


def _plan_episode(
    series: Series,
    season: Season,
    episode: Episode,
    target_root: Path,
    category: str,
    mode: LinkMode,
) -> list[MappingEntry]:
    entries: list[MappingEntry] = []
    safe_title = _safe_filename(series.title)

    if series.media_type == MediaType.MOVIE:
        season_dir = target_root / category / safe_title
    else:
        season_dir = target_root / category / safe_title / f"Season {season.number:02d}"

    if episode.video:
        video = episode.video
        target_path = _build_filename(series, season, episode, video, season_dir)
        entries.append(MappingEntry(source=video.source_path, target=target_path, file_kind=video.file_kind, mode=mode))

    for sub in episode.subtitles:
        target_path = _build_filename(series, season, episode, sub, season_dir)
        entries.append(MappingEntry(source=sub.source_path, target=target_path, file_kind=sub.file_kind, mode=mode))

    return entries


def _build_filename(
    series: Series,
    season: Season,
    episode: Episode,
    media_file: MediaFile,
    season_dir: Path,
) -> Path:
    safe_title = _safe_filename(series.title)
    ext = media_file.ext

    if series.media_type == MediaType.MOVIE:
        year_part = f" ({series.year})" if series.year else ""
        return season_dir / f"{safe_title}{year_part}{ext}"
    else:
        base = f"{safe_title} S{season.number:02d}E{episode.number:02d}"
        if media_file.file_kind == FileKind.SUBTITLE:
            return _build_subtitle_path(media_file, base, season_dir)
        return season_dir / f"{base}{ext}"


def _build_subtitle_path(media_file: MediaFile, base: str, season_dir: Path) -> Path:
    source_stem = media_file.source_path.stem

    sub_tags = _extract_subtitle_tags(source_stem)
    if sub_tags:
        return season_dir / f"{base}.{sub_tags}{media_file.ext}"
    return season_dir / f"{base}{media_file.ext}"


_SUBTITLE_TAG_RE = re.compile(r"\.(sc|tc|chs|cht|en|ja|jp|ko|fr|de|es|pt|ru|ar|hi|th|vi|id|default|forced|sdh|cc)(?:\.|$)")


def _extract_subtitle_tags(stem: str) -> str:
    tags: list[str] = []
    parts = stem.split(".")
    in_tags = False
    for i, part in enumerate(parts):
        if part.lower() in {
            "sc", "tc", "chs", "cht", "en", "ja", "jp", "ko", "fr", "de",
            "es", "pt", "ru", "ar", "hi", "th", "vi", "id", "default",
            "forced", "sdh", "cc",
        }:
            in_tags = True
            tags.append(part)
        elif in_tags and part.isdigit():
            tags.append(part)
        else:
            if in_tags:
                break

    return ".".join(tags) if tags else ""


def _safe_filename(name: str) -> str:
    unsafe = '<>:"/\\|?*'
    result = name
    for ch in unsafe:
        result = result.replace(ch, "")
    while result.endswith(".") or result.endswith(" "):
        result = result[:-1]
    return result.strip()
