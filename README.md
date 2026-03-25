# CittaVerse Narrative Scorer v0.6.3

[![CI](https://github.com/cittaverse/narrative-scorer/actions/workflows/ci.yml/badge.svg)](https://github.com/cittaverse/narrative-scorer/actions/workflows/ci.yml)
[![arXiv](https://img.shields.io/badge/arXiv-pending-orange)](https://arxiv.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-72%20passed-brightgreen)](tests/)
[![Benchmark](https://img.shields.io/badge/benchmark-90%2F90%20✓-blue)](tests/test_benchmark.py)

Automated narrative quality assessment for Chinese autobiographical memories in reminiscence therapy.

> **📄 Paper**: Technical report v1.1 ready for arXiv submission (cs.HC + cs.CL, 52 BibTeX references, weighted 6-dimension scoring). Submission tarball available in [pipeline repo](https://github.com/cittaverse/pipeline/tree/main/research/arxiv-paper/arxiv-submission).  
> **🏥 Clinical Study**: Pilot RCT (N=50) in preparation — screening questionnaire v1.1 complete (14 questions, full skip-logic coverage, PIPL-compliant data protection).

## Overview

This tool scores narrative quality across **six dimensions**:

1. **Event Richness** (事件丰富度) - Internal/external detail count — weight: 0.15
2. **Temporal Coherence** (时间连贯性) - Time markers and sequence clarity — weight: 0.15
3. **Causal Coherence** (因果连贯性) - Cause-effect reasoning — weight: 0.15
4. **Emotional Depth** (情感深度) - Emotion word density — weight: **0.20**
5. **Identity Integration** (自我认同整合) - Self-reference frequency — weight: 0.15
6. **Information Density Distribution** (信息密度分布) - Central vs. peripheral balance — weight: **0.20**

> Emotional Depth and Information Density receive higher weights based on their stronger association with therapeutic outcomes in reminiscence therapy (Westerhof & Bohlmeijer, 2024; Kensinger & Gutchess, 2026).

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Command Line

```bash
# Score a text directly
python src/scorer.py "我记得那是一个春天的下午，阳光明媚..."

# Run demo with sample text
python src/scorer.py --demo
```

### Python API

```python
from src.scorer import score_narrative

text = "我记得那是一个春天的下午，阳光明媚..."
result = score_narrative(text)

print(f"Composite Score: {result.composite_score}")
print(f"Letter Grade: {result.letter_grade}")
print(f"Feedback: {result.feedback}")

# Access individual dimensions
print(f"Event Richness: {result.event_richness}")
print(f"Temporal Coherence: {result.temporal_coherence}")
# ... etc
```

### Web UI (Gradio)

Launch the interactive web interface:

```bash
# Install Gradio (one-time)
pip install gradio

# Start the web server
python src/gradio_ui.py
```

Then open http://localhost:7860 in your browser.

**Features**:
- 📝 Text input with example loading
- 🚀 One-click scoring
- 📊 Visual score breakdown with letter grades
- 💬 Natural language feedback in Chinese
- 📄 JSON output for programmatic use

### JSON Output

```json
{
  "event_richness": 75.5,
  "temporal_coherence": 82.3,
  "causal_coherence": 68.0,
  "emotional_depth": 71.2,
  "identity_integration": 85.0,
  "information_density": 90.0,
  "central_count": 6,
  "peripheral_count": 4,
  "central_ratio": 0.6,
  "total_events": 10,
  "time_markers_count": 5,
  "causal_markers_count": 3,
  "self_references_count": 8,
  "emotion_words_count": 4,
  "composite_score": 78.5,
  "letter_grade": "B",
  "feedback": "这是一段不错的叙事，有一些亮点可以继续加强。特别突出的是信息密度分布（90 分）。建议加强因果连贯性（68 分）。"
}
```

## Example

See `examples/` directory for sample inputs and outputs.

```bash
# Run with example file
python src/scorer.py "$(cat examples/sample_input.txt)"
```

## Scoring Algorithm

### Event Extraction
- Splits text by Chinese sentence boundaries (。！？)
- Classifies sentences as central (specific details) or peripheral (reflections)
- Extracts time markers from temporal vocabulary list

### Dimension Scoring
Each dimension is scored 0-100 based on:
- **Event Richness**: Weighted events per 100 chars (central=1.0, peripheral=0.4) + count bonus + central bonus — *v0.6.2: prevents all-reflective narratives from scoring high*
- **Temporal Coherence**: Log-scaled marker density + time coverage — *v0.6.2: single-event cap at 25, prevents short-text inflation*
- **Causal Coherence**: Causal marker density (negation-aware since v0.5.1)
- **Emotional Depth**: Log-scaled emotion density + count bonus — *v0.6.2: text length floor at 60 chars*
- **Identity Integration**: Log-scaled self-reference density — *v0.6.1: prevents universal saturation*
- **Information Density**: Distance from optimal 60/40 central-peripheral ratio

### Composite Score
Weighted average with default weights:
- Event Richness: 15%
- Temporal Coherence: 15%
- Causal Coherence: 15%
- Emotional Depth: 20%
- Identity Integration: 15%
- Information Density: 20%

### Letter Grades
- **S**: ≥90 (Excellent)
- **A**: ≥80 (Very Good)
- **B**: ≥70 (Good)
- **C**: ≥60 (Fair)
- **D**: ≥50 (Poor)
- **F**: <50 (Needs Improvement)

## Customization

### Custom Weights

```python
custom_weights = {
    "event_richness": 0.20,
    "temporal_coherence": 0.20,
    "causal_coherence": 0.20,
    "emotional_depth": 0.15,
    "identity_integration": 0.15,
    "information_density": 0.10
}

result = score_narrative(text, weights=custom_weights)
```

### Extend Vocabulary

Edit `src/scorer.py` to add more markers:
- `TIME_MARKERS`: Temporal connectives
- `CAUSAL_MARKERS`: Causal connectives
- `SELF_MARKERS`: Self-reference words
- `EMOTION_WORDS`: Emotion vocabulary

## Integrations

- **[nlg-metricverse](https://github.com/disi-unibo-nlp/nlg-metricverse)**: Available as a plug-in metric — [PR #11](https://github.com/disi-unibo-nlp/nlg-metricverse/pull/11)
- **[awesome-dementia-detection](https://github.com/billzyx/awesome-dementia-detection)**: Listed as a narrative evaluation tool ✅ Merged

## Community Recognition

| List | Stars | Status |
|------|-------|--------|
| [awesome-dementia-detection](https://github.com/billzyx/awesome-dementia-detection) | 42+ | ✅ **Merged** |
| [Awesome-LLM-Eval](https://github.com/onejune2018/Awesome-LLM-Eval) | 548+ | ⏳ PR #23 Open |
| [awesome-ai-eval](https://github.com/Vvkmnn/awesome-ai-eval) | 69+ | ⏳ PR #6 Open |
| [nlg-metricverse](https://github.com/disi-unibo-nlp/nlg-metricverse) | 94+ | ⏳ PR #11 Open |

## Applications

- **Reminiscence Therapy**: Assess narrative quality in older adults
- **MCI Screening**: Detect cognitive decline through narrative patterns
- **Research**: Quantify narrative changes over time
- **Clinical Practice**: Track therapy progress

## Benchmark Results (v0.6.3)

15 gold-standard samples covering diverse narrative types:

| Category | Samples | Coverage |
|----------|---------|----------|
| Rich childhood memory | bench-001 | Specific events, temporal flow |
| Sparse reflective | bench-002, bench-014 | Low-detail, all-peripheral |
| Emotional family | bench-003 | Causal + emotional markers |
| Minimal single-sentence | bench-004 | Edge case: 1 event |
| Multi-scene journey | bench-005 | Geographic progression |
| Dialect-flavored (方言) | bench-006 | Wu dialect vocabulary |
| Multi-generational (多代际) | bench-007 | Cross-generation events |
| Trauma narrative | bench-008 | Physiological + emotional |
| Festival memory | bench-009 | Routine/habitual events |
| Work/career | bench-010 | Numeric specifics, time spans |
| Childhood friendship | bench-011 | Temporal markers, reunion |
| Food/cooking memory | bench-012 | Process-heavy, low self-ref |
| Migration story | bench-013 | Causal markers, identity shift |
| Long multi-topic | bench-015 | 12 sentences, 3 life events |

**Results**: 90/90 dimension checks within gold-annotated ranges (100% accuracy)

```
72 tests in 0.03s — OK
├── 60 unit tests (scorer + edge cases + negation + event boundary)
└── 12 benchmark tests (dimension accuracy + behavioral invariants)
```

## Limitations (v0.6.3)

- Rule-based event extraction (no LLM yet — v0.6 uses topic-transition markers)
- Simplified Chinese only (no Cantonese/Wu tokenization)
- No ASR integration (text input only)
- Dialect emotion words still limited (e.g., "急" in Wu dialect not recognized)
- Short-text identity_integration inflation (single "我" in ≤12 chars → high score)
- Lunar calendar terms partially covered (腊月/正月 yes, specific regional variants may miss)

## Roadmap → v0.7

See **[ROADMAP-v0.6.md](ROADMAP-v0.6.md)** for the full plan. Key highlights:

| Feature | Target | Status |
|---------|--------|--------|
| LLM-as-Judge scoring (hybrid rule+LLM) | Q2 2026 | 🔜 [Architecture designed](../pipeline/docs/llm_as_judge_architecture.md) |
| ~~Negation & context awareness~~ | ~~Q2 2026~~ | ✅ **v0.5.1** |
| ~~Event boundary detection v2~~ | ~~Q2 2026~~ | ✅ **v0.6.0** |
| ~~CI/CD (GitHub Actions)~~ | ~~Q2 2026~~ | ✅ **v0.6.0** |
| ~~Test suite expansion (8 → 50+)~~ | ~~Q2 2026~~ | ✅ **72 tests** |
| ~~Dimension calibration~~ | ~~Q2 2026~~ | ✅ **v0.6.2** |
| ~~15-sample benchmark~~ | ~~Q2 2026~~ | ✅ **v0.6.2** |
| ~~Year/date temporal recognition~~ | ~~Q2 2026~~ | ✅ **v0.6.3** |
| ~~Expanded emotion vocabulary~~ | ~~Q2 2026~~ | ✅ **v0.6.3** |
| Multi-dialect support (Cantonese, Wu) | Q3 2026 | 🔜 Planned |
| Human-AI agreement validation (ICC) | Q4 2026 | ⏳ Blocked on RCT |
| FastAPI production server | Q3 2026 | 🔜 Planned |

### Completed
- [x] Emotion vocabulary expansion (30 → 78 words: trauma, social, dialect) — v0.6.3
- [x] Year/date temporal recognition (\d{4}年，\d+ 月，lunar calendar, ages) — v0.6.3
- [x] 15-sample benchmark suite (90/90 dimension accuracy) — v0.6.2
- [x] Dimension calibration: event_richness, temporal_coherence, emotional_depth — v0.6.2
- [x] LLM-as-Judge architecture research (3 options evaluated, Option C recommended) — v0.6.2
- [x] nlg-metricverse plugin integration — PR #11 submitted — v0.6.0
- [x] First external list merge: awesome-dementia-detection — v0.6.0
- [x] Event boundary detection v2 — topic-transition-aware splitting, short-clause merging, enhanced classification — v0.6.0
- [x] GitHub Actions CI (Python 3.9-3.12 matrix) — v0.6.0
- [x] Test expansion: 11 → 36 → 46 → 60 → 72 test cases — v0.6.2
- [x] Negation detection (不/没有/未/并不/从不 etc.) — v0.5.1
- [x] Negation-aware causal & emotion counting — v0.5.1
- [x] Web UI (Gradio) — v0.5
- [x] Weighted scoring rationale — v0.5
- [x] arXiv technical report — v1.1 ready

## Citation

If you use this tool in your research, please cite:

```bibtex
@software{cittaverse_narrative_scorer,
  title = {CittaVerse Narrative Scorer: Automated Assessment of Chinese Autobiographical Memory Quality},
  author = {Hulk and CittaVerse Team},
  year = {2026},
  url = {https://github.com/cittaverse/narrative-scorer}
}
```

## License

MIT License - see LICENSE file

## Contact

- GitHub: https://github.com/cittaverse/narrative-scorer
- Issues: https://github.com/cittaverse/narrative-scorer/issues

---

*Part of CittaVerse - AI-Assisted Reminiscence Therapy for Older Adults*
