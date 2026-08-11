# Naturalize AI Text

`naturalize-ai-text` is a quality-first Codex skill for revising AI-generated or heavily AI-assisted prose without sacrificing facts, citations, narrative continuity, genre conventions, disclosure duties, or the writer's supported voice.

Version: **2.0.0**

The skill treats AI-detector output as a volatile observation from a named instrument—not as proof of authorship and not as the definition of good writing. It explicitly rejects typo injection, hidden characters, fabricated experiences, fake citations, translation-loop damage, and other integrity-breaking shortcuts.

## What it does

- Routes work by revision mode, provenance, publication context, and disclosure requirements.
- Freezes the original text and its SHA-256 before editing.
- Diagnoses reader-facing problems such as redundant summaries, paragraph-role symmetry, over-explained morals, generic framing, and uniform cadence.
- Revises in content-led passes covering scene or information, structure, voice, sentence form, and surface correctness.
- Protects facts, quotations, citations, chronology, viewpoint, character knowledge, terminology, and causal direction.
- Provides deterministic tools for text validation, texture analysis, and detector-experiment records.
- Requires matched controls, exact-input hashes, complete run reporting, and quality gates when detector experiments are explicitly authorized.

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

### Windows PowerShell

```powershell
git clone https://github.com/zhaoyuxiangyyds-lab/naturalize-ai-text.git
New-Item -ItemType Directory -Force "$HOME\.agents\skills" | Out-Null
Copy-Item -Recurse -Force ".\naturalize-ai-text\naturalize-ai-text" "$HOME\.agents\skills\naturalize-ai-text"
```

### macOS or Linux

```bash
git clone https://github.com/zhaoyuxiangyyds-lab/naturalize-ai-text.git
mkdir -p "$HOME/.agents/skills"
cp -R ./naturalize-ai-text/naturalize-ai-text "$HOME/.agents/skills/naturalize-ai-text"
```

Restart Codex if the skill does not appear immediately.

## Example prompt

```text
Use $naturalize-ai-text to improve this text while preserving facts, voice,
genre, and disclosure. Run detector experiments only when I explicitly request
them, and report every validation result.
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

### Experiment records

Creates and validates exact-input records for explicitly authorized detector experiments.

```bash
python naturalize-ai-text/scripts/experiment_record.py init final.txt \
  --sample-id sample-01 \
  --stage final \
  --mode revision \
  --provenance unknown \
  --language zh \
  --genre fiction \
  -o sample-01.json

python naturalize-ai-text/scripts/experiment_record.py validate sample-01.json --text final.txt
```

## Run the tests

The test suite uses Python's standard library and requires no third-party packages.

```bash
python -m unittest discover -s naturalize-ai-text/tests -p "test_*.py" -v
```

Version 2.0.0 currently includes 22 deterministic unit tests.

## Integrity and limitations

This project improves writing; it does not certify authorship or promise a detector bypass. Detector output depends on language, genre, length, generator, detector version, threshold, and exact input construction. A score belongs only to the exact tested bytes and cannot prove that a person or a model wrote the text.

Users are responsible for following the disclosure, attribution, assessment, publication, privacy, copyright, and platform rules that apply to their work.

## 中文简介

`naturalize-ai-text` 是一个面向 Codex 的文本自然化 skill。它优先改善文章质量，同时保护事实、引用、逻辑、叙事连续性、体裁、作者已有声音和必要的 AI 使用披露。

它不会通过故意加入错别字、隐藏字符、虚构经历、伪造引用或破坏语法来追求检测分数。只有用户明确授权时，才按照可复现的实验流程记录检测结果；任何检测结果都不能证明文本由人类创作。

安装时，请将仓库中的 `naturalize-ai-text` 子目录复制到：

```text
$HOME/.agents/skills/naturalize-ai-text
```

## License

Released under the [MIT License](LICENSE).
