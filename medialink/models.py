from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class FileKind(Enum):
    VIDEO = "video"
    SUBTITLE = "subtitle"
    OTHER = "other"


class LinkMode(Enum):
    SOFT = "soft"
    HARD = "hard"
    COPY = "copy"
    MOVE = "move"


class MediaType(Enum):
    MOVIE = "movie"
    EPISODE = "episode"


@dataclass
class MediaFile:
    source_path: Path
    file_kind: FileKind
    ext: str

    title: str = ""
    season: int = 0
    episode: int = 0
    media_type: MediaType = MediaType.EPISODE
    year: int | None = None

    parent_dir_name: str = ""

    guessit_raw: dict = field(default_factory=dict)


@dataclass
class MappingEntry:
    source: Path
    target: Path
    file_kind: FileKind
    mode: LinkMode


@dataclass
class Episode:
    number: int
    video: MediaFile | None = None
    subtitles: list[MediaFile] = field(default_factory=list)

    @property
    def all_files(self) -> list[MediaFile]:
        files: list[MediaFile] = []
        if self.video:
            files.append(self.video)
        files.extend(self.subtitles)
        return files


@dataclass
class Season:
    number: int
    episodes: dict[int, Episode] = field(default_factory=dict)


@dataclass
class Series:
    title: str
    seasons: dict[int, Season] = field(default_factory=dict)
    movies: dict[int, Episode] = field(default_factory=dict)
    media_type: MediaType = MediaType.EPISODE
    year: int | None = None


@dataclass
class Override:
    title: str | None = None
    season: int | None = None
    episode_offset: int = 0
