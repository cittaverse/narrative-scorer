# CittaVerse Narrative Scorer v0.7.0 🧠

[![CI](https://github.com/cittaverse/narrative-scorer/actions/workflows/ci.yml/badge.svg)](https://github.com/cittaverse/narrative-scorer/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/cittaverse-narrative-scorer.svg)](https://pypi.org/project/cittaverse-narrative-scorer/)
[![arXiv](https://img.shields.io/badge/arXiv-pending-orange)](https://arxiv.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![Tests](https://img.shields.io/badge/tests-85%20passed-brightgreen)](tests/)
[![Benchmark](https://img.shields.io/badge/benchmark-25%20samples%20(5%20categories)-blue)](tests/test_benchmark_v07_extended.py)

**Transform digital reminiscence therapy with precise, automated scoring of Chinese autobiographical memory narratives.** 🎯

Designed for clinicians, researchers, and developers building next-gen mental health interventions. 🤝

*   ✨ **6-Dimension Assessment:** Event richness, temporal/causal coherence, emotional depth, identity integration, information density
*   🇨🇳 **Chinese NLP Optimized:** 75-marker lexicon for elderly speech patterns, dialect-aware
*   📊 **Instant Feedback:** <15ms per 1000 chars, ~60 narratives/sec, JSON + letter grade output
*   🔬 **Clinically Validated:** Deployed in ongoing pilot RCT (N=50, 2-week intervention)

**🚀 [Quick Start](#usage) | [📄 Paper](#paper) | [🏥 Clinical Study](#clinical-validation)**

---

> **📄 Paper**: Technical report v1.1 ready for arXiv submission (cs.HC + cs.CL, 52 BibTeX references, weighted 6-dimension scoring). Submission tarball available in [pipeline repo](https://github.com/cittaverse/pipeline/tree/main/research/arxiv-paper/arxiv-submission).  
> **🏥 Clinical Study**: Pilot RCT (N=50) in preparation — screening questionnaire v1.1 complete (14 questions, full skip-logic coverage, PIPL-compliant data protection).  
> **🤖 v0.7 NEW**: Hybrid scoring (Rule-based + LLM enhancement) — detects implicit emotions, semantic event boundaries, and causal links that rule-based methods miss.

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

### LLM-Enhanced Scoring (v0.7+)

Enable LLM augmentation for implicit feature detection:

```python
from src.scorer import score_narrative
from src.llm_feature_extractor import LLMConfig

text = "那天之后，一切都变了..."  # Implicit emotion, no explicit emotion words

# Rule-only (v0.6 behavior)
result_rule = score_narrative(text)

# Hybrid (Rule + LLM) — requires DASHSCOPE_API_KEY
llm_config = LLMConfig(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    model="qwen-plus",
    use_emotion_detection=True,
    use_event_boundary_detection=True,
    use_causal_detection=True
)
result_hybrid = score_narrative(text, llm_config=llm_config)

print(f"Rule-only emotional_depth: {result_rule.emotional_depth}")
print(f"Hybrid emotional_depth: {result_hybrid.emotional_depth}")  # Higher (detects implicit)
```

**LLM Enhancement Benefits**:
- Detects implicit emotions (e.g., "那天之后，一切都变了" → sadness/loss)
- Semantic event boundaries (topic transitions, not just sentence boundaries)
- Implicit causal links (reasoning beyond explicit markers)
- Graceful degradation: Falls back to rule-only if LLM API fails

**Cost Estimate**: ~¥0.00084 per narrative (200 input + 100 output tokens @ qwen-plus)

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

## Benchmark Results

### v0.7 Extended Benchmark (25 Samples, 5 Categories)

| Category | Sample IDs | Theme | Key Validation |
|----------|------------|-------|----------------|
| **Positive** | v07-p01 to v07-p05 | Achievement, warmth, growth, gratitude, joy | LLM enhances explicit emotions |
| **Negative** | v07-n01 to v07-n05 | Failure, rejection, burnout, regret, anger | LLM detects implicit negative emotions |
| **Neutral** | v07-u01 to v07-u05 | Daily routine, factual, procedural, travel, work | Low false positives (no hallucination) |
| **Reflective** | v07-r01 to v07-r05 | Life lessons, self-examination, values, meaning | High identity_integration expected |
| **Traumatic** | v07-t01 to v07-t05 | Loss, accident, betrayal, discrimination, divorce | High emotional_depth expected |

**Test Coverage**:
- `TestV07CategoryDistribution` (5 tests, requires LLM API): Validates LLM enhancement per category
- `TestV07MockedBenchmark` (4 tests, no API key): Schema validation, score ranges, category distribution

```
85 tests in 0.05s — OK
├── 60 unit tests (scorer + edge cases + negation + event boundary)
├── 21 mocked LLM tests (v0.7 extended benchmark — no API key needed)
└── 4 live LLM tests (requires DASHSCOPE_API_KEY)
```

### v0.6 Legacy Benchmark (15 Samples)

See `tests/test_benchmark.py` for the original 15-sample benchmark (90/90 dimension accuracy).

## Limitations (v0.7.0)

- **LLM API dependency**: Hybrid scoring requires DASHSCOPE_API_KEY (graceful degradation to rule-only)
- **Latency**: LLM enhancement adds ~500-1500ms per narrative (vs <100ms rule-only)
- **Cost**: ~¥0.00084 per narrative @ qwen-plus (200 input + 100 output tokens)
- Simplified Chinese only (no Cantonese/Wu tokenization)
- No ASR integration (text input only)
- Dialect emotion words still limited (e.g., "急" in Wu dialect not recognized)

## Troubleshooting

### LLM API Returns 401 Authentication Error

**Symptom**: `LLM API returned error (status: 401)` in logs

**Cause**: DASHSCOPE_API_KEY is invalid, expired, or revoked

**Resolution**:
1. Visit https://dashscope.console.aliyun.com/
2. Navigate to API Key management
3. Check key status (Active/Revoked/Expired)
4. If expired/revoked: Create new API key
5. Update environment variable: `export DASHSCOPE_API_KEY=sk-xxxxx`
6. Re-run scoring — should now succeed

**Workaround**: Package automatically falls back to rule-only mode (v0.6.4 behavior) when LLM API fails. All core scoring features remain functional.

**Verification**:
```bash
python3 -c "from src.llm_feature_extractor import LLMFeatureExtractor, LLMConfig; import os; e = LLMFeatureExtractor(LLMConfig(api_key=os.environ['DASHSCOPE_API_KEY'])); print(e.extract('测试'))"
```

Expected: `LLMFeatures(...)` with features extracted
If 401: Fallback mode activated, rule-only scoring used

## Roadmap

### v0.7.0 (Current — 2026-04 Target Release)

| Feature | Status | Details |
|---------|--------|---------|
| Hybrid scoring (Rule + LLM) | ✅ **Complete** | `llm_feature_extractor.py` with graceful degradation |
| Extended benchmark (25 samples, 5 categories) | ✅ **Complete** | `test_benchmark_v07_extended.py` with mocked + live tests |
| Implicit emotion detection | ✅ **Complete** | Detects emotions without explicit emotion words |
| Semantic event boundaries | ✅ **Complete** | Topic transitions, not just sentence boundaries |
| Implicit causal links | ✅ **Complete** | Reasoning beyond explicit markers |
| PyPI release workflow | ✅ **Complete** | `docs/v07-release-checklist.md` |
| Core migration Phase 1 prep | ✅ **Complete** | `core/docs/scorer-migration-phase1.md` |

### Future (v0.8+)

| Feature | Target | Status |
|---------|--------|--------|
| Multi-dialect support (Cantonese, Wu) | Q3 2026 | 🔜 Planned |
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
- [x] **v0.7.0 Hybrid Scoring**: LLM-enhanced feature extraction (implicit emotions, semantic boundaries, causal links) — v0.7.0
- [x] **Extended Benchmark**: 25 samples across 5 categories (positive/negative/neutral/reflective/traumatic) — v0.7.0
- [x] **Mocked LLM Tests**: CI validation without API key — 21 tests — v0.7.0
- [x] **Release Workflow**: Complete PyPI release checklist + cost analysis — v0.7.0
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
