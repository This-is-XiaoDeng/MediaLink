from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

from guessit import guessit

from medialink.models import MediaFile, FileKind, Series, Season, Episode, MediaType, Override


_SEASON_0_DIRS = frozenset({"sps", "specials", "sp", "ova", "ovas", "extras", "special"})


def identify_and_group(files: list[MediaFile], overrides: list[Override] | None = None) -> list[Series]:
    for mf in files:
        result = guessit(mf.source_path.name)
        mf.guessit_raw = dict(result)

        mf.title = str(result.get("title") or mf.parent_dir_name)
        mf.media_type = MediaType.EPISODE
        mf.year = result.get("year")

        etype = result.get("type")
        if etype == "movie":
            mf.media_type = MediaType.MOVIE
            mf.episode = 0
            mf.season = 0
        else:
            if mf.parent_dir_name.lower() in _SEASON_0_DIRS:
                mf.season = 0
            else:
                mf.season = int(result.get("season", 1))
            episode = result.get("episode")
            if episode is not None:
                mf.episode = int(episode)
            else:
                absolute_ep = result.get("absolute_episode")
                if absolute_ep is not None:
                    mf.episode = int(absolute_ep)
                else:
                    mf.episode = 0

    _match_subtitles(files)

    overrides = overrides or []
    _apply_overrides(files, overrides)

    return _group_into_series(files)


def _match_subtitles(files: list[MediaFile]) -> None:
    """Match subtitle files to their video files by proximity (same directory) and episode number."""
    videos_by_dir: dict[Path, dict[int, MediaFile]] = {}
    for mf in files:
        if mf.file_kind == FileKind.VIDEO and mf.episode > 0:
            parent = mf.source_path.parent
            videos_by_dir.setdefault(parent, {})[mf.episode] = mf

    for mf in files:
        if mf.file_kind != FileKind.SUBTITLE:
            continue
        parent = mf.source_path.parent
        result = guessit(mf.source_path.name)
        sub_ep = result.get("episode")
        sub_season = result.get("season", 1)
        sub_title = str(result.get("title", ""))

        if parent in videos_by_dir and sub_ep:
            ep = int(sub_ep)
            if ep in videos_by_dir[parent]:
                video = videos_by_dir[parent][ep]
                mf.title = video.title
                mf.season = video.season
                mf.episode = video.episode
                mf.media_type = video.media_type
                mf.year = video.year
                continue

        if sub_ep:
            mf.title = sub_title or mf.parent_dir_name
            mf.season = int(sub_season)
            mf.episode = int(sub_ep)
        else:
            mf.title = sub_title or mf.parent_dir_name
            mf.season = 0
            mf.episode = 0


def _apply_overrides(files: list[MediaFile], overrides: list[Override]) -> None:
    for mf in files:
        for ov in overrides:
            if ov.title is not None:
                mf.title = ov.title
            if ov.season is not None:
                mf.season = ov.season
            if ov.episode_offset != 0:
                mf.episode += ov.episode_offset


def _sanitize_title(title: str) -> str:
    return title.strip()


def _group_into_series(files: list[MediaFile]) -> list[Series]:
    series_map: dict[str, Series] = {}

    for mf in files:
        if mf.file_kind == FileKind.OTHER:
            continue
        if not mf.title:
            continue

        key = _sanitize_title(mf.title).lower()
        if key not in series_map:
            series_map[key] = Series(title=_sanitize_title(mf.title), media_type=mf.media_type, year=mf.year)

        series = series_map[key]
        season_num = mf.season if mf.media_type == MediaType.EPISODE else 0

        if season_num not in series.seasons:
            series.seasons[season_num] = Season(number=season_num)
        season = series.seasons[season_num]

        ep_num = mf.episode
        if ep_num not in season.episodes:
            season.episodes[ep_num] = Episode(number=ep_num)
        episode = season.episodes[ep_num]

        if mf.file_kind == FileKind.VIDEO:
            if episode.video is None:
                episode.video = mf
        elif mf.file_kind == FileKind.SUBTITLE:
            if mf not in episode.subtitles:
                episode.subtitles.append(mf)

    return list(series_map.values())
