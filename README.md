# Naturalize AI Text

`naturalize-ai-text` is a Codex skill designed to help AI generate text with a lower AI-detection rate and to reduce the AI-detection rate of existing AI-generated or heavily AI-assisted text. It keeps writing quality first while preserving facts, citations, narrative continuity, genre conventions, disclosure duties, and the writer's supported voice.

Version: **2.0.0**

The skill works by improving content selection, structure, voice, sentence rhythm, and surface quality. It explicitly rejects typo injection, hidden characters, fabricated experiences, fake citations, translation-loop damage, and other shortcuts that make a document less trustworthy or less readable.

## What it does

- Helps AI produce new text with a lower AI-detection rate from the first draft.
- Revises AI-generated or AI-assisted text to reduce its AI-detection rate.
- Routes work by revision mode, provenance, publication context, and disclosure requirements.
- Freezes the original text and its SHA-256 before editing.
- Diagnoses reader-facing problems such as redundant summaries, paragraph-role symmetry, over-explained morals, generic framing, and uniform cadence.
- Revises in content-led passes covering scene or information, structure, voice, sentence form, and surface correctness.
- Protects facts, quotations, citations, chronology, viewpoint, character knowledge, terminology, and causal direction.
- Provides deterministic tools for text validation and texture analysis.

## Repository layout

```text
.
├── README.md
├── LICENSE
└── naturalize-ai-text/
    ├── SKILL.md
    ├── agents/
    │   └── openai.yaml
    ├── references/
    ├── scripts/
    └── tests/
```

The repository documentation stays outside the skill directory so the installed skill contains only runtime instructions and resources.

## Installation

Codex Desktop and Codex CLI use the same user-level skill location:

```text
$HOME/.agents/skills/naturalize-ai-text
```

The commands below back up an existing installation before copying the current version.

### Codex Desktop on Windows

Open PowerShell and run:

```powershell
$download = Join-Path $env:TEMP ("naturalize-ai-text-" + [guid]::NewGuid())
$skills = Join-Path $HOME ".agents\skills"
$target = Join-Path $skills "naturalize-ai-text"
git clone --depth 1 https://github.com/zhaoyuxiangyyds-lab/naturalize-ai-text.git $download
New-Item -ItemType Directory -Force $skills | Out-Null
if (Test-Path $target) { Rename-Item -LiteralPath $target -NewName ("naturalize-ai-text.backup-" + (Get-Date -Format "yyyyMMdd-HHmmss")) }
Copy-Item -Recurse -Force (Join-Path $download "naturalize-ai-text") $skills
```

Restart Codex Desktop, then open **Skills** in the sidebar and select **Naturalize AI Text**.

### Codex CLI on Windows

Open PowerShell and run:

```powershell
$download = Join-Path $env:TEMP ("naturalize-ai-text-" + [guid]::NewGuid())
$skills = Join-Path $HOME ".agents\skills"
$target = Join-Path $skills "naturalize-ai-text"
git clone --depth 1 https://github.com/zhaoyuxiangyyds-lab/naturalize-ai-text.git $download
New-Item -ItemType Directory -Force $skills | Out-Null
if (Test-Path $target) { Rename-Item -LiteralPath $target -NewName ("naturalize-ai-text.backup-" + (Get-Date -Format "yyyyMMdd-HHmmss")) }
Copy-Item -Recurse -Force (Join-Path $download "naturalize-ai-text") $skills
codex
```

In Codex CLI, run `/skills` to confirm the installation, then invoke it with `$naturalize-ai-text`.

### Codex Desktop on macOS

Open Terminal and run:

```bash
download="$(mktemp -d)/repo"
skills="$HOME/.agents/skills"
target="$skills/naturalize-ai-text"
git clone --depth 1 https://github.com/zhaoyuxiangyyds-lab/naturalize-ai-text.git "$download"
mkdir -p "$skills"
if [ -d "$target" ]; then mv "$target" "$skills/naturalize-ai-text.backup-$(date +%Y%m%d-%H%M%S)"; fi
cp -R "$download/naturalize-ai-text" "$target"
```

Restart Codex Desktop, then open **Skills** in the sidebar and select **Naturalize AI Text**.

### Codex CLI on macOS

Open Terminal and run:

```bash
download="$(mktemp -d)/repo"
skills="$HOME/.agents/skills"
target="$skills/naturalize-ai-text"
git clone --depth 1 https://github.com/zhaoyuxiangyyds-lab/naturalize-ai-text.git "$download"
mkdir -p "$skills"
if [ -d "$target" ]; then mv "$target" "$skills/naturalize-ai-text.backup-$(date +%Y%m%d-%H%M%S)"; fi
cp -R "$download/naturalize-ai-text" "$target"
codex
```

In Codex CLI, run `/skills` to confirm the installation, then invoke it with `$naturalize-ai-text`.

Codex detects skill changes automatically. If the skill does not appear, fully restart Codex and check that `SKILL.md` is directly inside the installed `naturalize-ai-text` directory.

## Example prompt

```text
Use $naturalize-ai-text to generate or revise this text for a lower AI-detection
rate while preserving facts, citations, voice, genre, and disclosure. Report
every validation result.
```

## Included tools

### Texture analysis

Describes repetition, rhythm, transitions, punctuation, and document structure. It is not an AI detector.

```bash
python naturalize-ai-text/scripts/analyze_texture.py input.txt --language auto --genre fiction
```

### Deterministic validation

Checks exact bytes, SHA-256, Unicode hazards, punctuation pairs, duplicated text, and formatting risks. It cannot prove facts, spelling, continuity, or authorship.

```bash
python naturalize-ai-text/scripts/validate_text.py input.txt --format json --pretty
```

## Run the tests

The test suite uses Python's standard library and requires no third-party packages.

```bash
python -m unittest discover -s naturalize-ai-text/tests -p "test_*.py" -v
```

Version 2.0.0 currently includes 22 deterministic unit tests.

## Integrity and limitations

This project aims to reduce AI-detection rates without sacrificing writing quality, but it cannot promise a fixed score or universal result. Detector output depends on language, genre, length, generator, detector version, threshold, and exact input construction. A score cannot prove that a person or a model wrote the text.

Users are responsible for following the disclosure, attribution, assessment, publication, privacy, copyright, and platform rules that apply to their work.

## 中文简介

`naturalize-ai-text` 是一个面向 Codex 的文本自然化 skill，主要作用是帮助 AI 生成 AI 率更低的文本，以及降低现有 AI 生成或 AI 辅助文本的 AI 率。它在降低 AI 检测率的同时，尽量保护事实、引用、逻辑、叙事连续性、体裁、作者已有声音和必要的 AI 使用披露。

它主要从内容取舍、结构、语气、句式节奏和表层质量入手，不会通过故意加入错别字、隐藏字符、虚构经历、伪造引用或破坏语法来追求检测分数。不同检测工具的结果可能不同，因此不能保证固定分数，也不能用检测结果证明文本由人类创作。

Codex Desktop 和 Codex CLI 使用相同的用户级安装目录：

```text
$HOME/.agents/skills/naturalize-ai-text
```

## License

Released under the [MIT License](LICENSE).
