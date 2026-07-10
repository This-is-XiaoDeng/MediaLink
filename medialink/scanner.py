from __future__ import annotations

from pathlib import Path

from medialink.models import MediaFile, FileKind

VIDEO_EXTS = {".mkv", ".mp4", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".ts", ".m2ts", ".rmvb", ".rm", ".ogm", ".divx"}
SUBTITLE_EXTS = {".ass", ".ssa", ".srt", ".sub", ".idx", ".vtt", ".pgs", ".sup"}
SKIP_EXTS = {".txt", ".nfo", ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico", ".sfv", ".md5", ".torrent", ".url", ".lnk"}


def scan_directory(root: Path, include_other: bool = False) -> list[MediaFile]:
    files: list[MediaFile] = []

    for entry in sorted(root.rglob("*")):
        if not entry.is_file():
            continue
        ext = entry.suffix.lower()
        kind = _classify(ext)
        if not include_other and kind == FileKind.OTHER:
            continue

        parent_dir = entry.parent.name

        mf = MediaFile(
            source_path=entry,
            file_kind=kind,
            ext=ext,
            parent_dir_name=parent_dir,
        )
        files.append(mf)

    return files


def _classify(ext: str) -> FileKind:
    if ext in VIDEO_EXTS:
        return FileKind.VIDEO
    if ext in SUBTITLE_EXTS:
        return FileKind.SUBTITLE
    if ext in SKIP_EXTS:
        return FileKind.OTHER
    return FileKind.OTHER
