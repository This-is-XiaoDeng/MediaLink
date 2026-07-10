# MediaLink

递归扫描下载目录，通过创建链接（软链接/硬链接/复制/移动）将媒体文件按标题/季/集整理到目标目录的 CLI 工具。

适用于整理番剧、电影、电视剧，方便接入飞牛影视、Plex、Jellyfin、Emby 等媒体库。

## 安装

```bash
git clone https://github.com/This-is-XiaoDeng/MediaLink
cd MediaLink
poetry install
```

依赖 [guessit](https://github.com/guessit-io/guessit) 解析文件名，[rich](https://github.com/Textualize/rich) 美化终端输出。

## 用法

```bash
poetry run medialink <源目录> <目标目录> [选项]
```

### 选项

| 参数 | 说明 |
|------|------|
| `--mode soft\|hard\|copy\|move` | 链接模式，默认 `soft`（软链接） |
| `--dry-run` | 预览操作，不实际执行 |
| `--override KEY=VALUE`, `-o` | 覆写元数据，可多次指定 |
| `--include-other` | 包含非媒体文件（默认跳过 .txt .nfo .jpg 等） |
| `--quiet`, `-q` | 减少输出 |

### 覆写参数

```bash
--override title="Chuunibyou demo Koi ga Shitai!"  # 覆写标题
--override season=2                                  # 覆写季号
--override episode_offset=5                          # 集数偏移量
```

## 示例

### 预览变更

```bash
poetry run medialink /vol1/1000/Media/种子下载 /vol1/1000/Media/anime --dry-run
```

输入文件：
```
种子下载/
  [Airota&VCB-Studio] Chuunibyou demo Koi ga Shitai!/
    [Airota&VCB-Studio] Chuunibyou demo Koi ga Shitai! [Hi10p_1080p]/
      [Airota&VCB-Studio] Chuunibyou demo Koi ga Shitai! [01][Hi10p_1080p][x264_flac].mkv
      [Airota&VCB-Studio] Chuunibyou demo Koi ga Shitai! [01][Hi10p_1080p][x264_flac].sc.ass
      [Airota&VCB-Studio] Chuunibyou demo Koi ga Shitai! [02][Hi10p_1080p][x264_flac].mkv
      [Airota&VCB-Studio] Chuunibyou demo Koi ga Shitai! [02][Hi10p_1080p][x264_flac].sc.ass
```

计划输出：
```
anime/
  Chuunibyou demo Koi ga Shitai!/
    Season 01/
      Chuunibyou demo Koi ga Shitai! S01E01.mkv
      Chuunibyou demo Koi ga Shitai! S01E01.sc.ass
      Chuunibyou demo Koi ga Shitai! S01E02.mkv
      Chuunibyou demo Koi ga Shitai! S01E02.sc.ass
```

### 覆写标题 + 季号

```bash
poetry run medialink download/ library/ -o "title=Chuunibyou demo Koi ga Shitai! Ren" -o season=2
```

### 复制模式（Windows 环境无软链接权限时）

```bash
poetry run medialink download/ library/ --mode copy
```

## 支持的文件类型

**视频：** `.mkv` `.mp4` `.avi` `.mov` `.wmv` `.flv` `.webm` `.m4v` `.ts` `.m2ts` `.rmvb` `.rm` `.ogm` `.divx`

**字幕：** `.ass` `.ssa` `.srt` `.sub` `.idx` `.vtt` `.pgs` `.sup`

字幕语言标签（如 `.sc` `.tc` `.en` `.sc.ass`）会被自动识别并保留在目标文件名中。

## 目标路径规则

| 类型 | 路径格式 |
|------|----------|
| 剧集 (TV) | `{target}/anime/{Title}/Season {NN}/{Title} S{NN}E{NN}.{ext}` |
| 电影 | `{target}/movies/{Title}/{Title} ({Year}).{ext}` |

## 链接模式说明

| 模式 | 说明 |
|------|------|
| `soft` | 软链接（符号链接），Windows 需要开发者模式或管理员权限 |
| `hard` | 硬链接，同一文件系统内有效，不占额外空间 |
| `copy` | 复制文件，适用于跨文件系统或 Windows 无 symlink 权限 |
| `move` | 移动文件，源文件会被移走 |

## [许可证](LICENSE)

```
MediaLink
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
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```
