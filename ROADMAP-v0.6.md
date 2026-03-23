# Narrative Scorer v0.6 Roadmap

> CittaVerse Narrative Scorer 从 v0.5 (rule-based) → v0.6 (LLM-enhanced hybrid) 的演进规划
> 
> Created: 2026-03-23 | GEO #59

---

## v0.5 Current State (Baseline)

| Aspect | Status |
|--------|--------|
| Architecture | Pure rule-based (regex + vocabulary lists + heuristic scoring) |
| Dimensions | 6 (event richness, temporal/causal coherence, emotional depth, identity integration, info density) |
| Language | Chinese only (Mandarin) |
| Dependencies | Zero external API (fully offline) |
| Lines of code | ~462 (scorer.py) |
| Test coverage | Basic (119 lines, ~8 test cases) |
| UI | Gradio web interface |
| Clinical deployment | Pilot RCT N=50 (screening ready) |

### v0.5 Known Limitations

1. **Vocabulary ceiling**: Emotion/temporal/causal word lists are finite; unseen expressions score 0
2. **No context understanding**: "我很开心" and "我并不开心" score the same for emotional depth
3. **No event boundary detection**: Uses simple sentence splitting, misses complex event structures
4. **Single dialect**: Only standard Mandarin; Cantonese/Hokkien/Wu dialect speakers are excluded
5. **No LLM validation**: Can't cross-check rule scores against semantic understanding
6. **Fixed thresholds**: Scoring bands don't adapt to individual cognitive baselines

---

## v0.6 Target Architecture

### Core Principle: Hybrid Scoring

```
Input text
    │
    ├─── Rule Engine (v0.5) ──→ Rule Scores (6 dim)
    │                                  │
    ├─── LLM Module ──────────→ LLM Scores (6 dim)
    │                                  │
    └─── Fusion Layer ────────→ Final Scores (weighted ensemble)
                                       │
                                  Confidence + Explanation
```

**Key design constraint**: LLM module is **optional**. When offline or API-unavailable, system degrades gracefully to v0.5 rule-only mode.

---

## Feature Plan

### Phase A: LLM Integration (Priority: High)

#### A1. LLM-as-Judge Scoring Module
- **Goal**: Use LLM to score each dimension independently, then fuse with rule scores
- **Approach**:
  - Structured prompt per dimension with scoring rubric
  - Support DashScope (Qwen), OpenAI, and local models (Ollama)
  - JSON output with score + reasoning
- **Fusion**: `final = α × rule_score + (1-α) × llm_score`, α configurable (default 0.5)
- **Fallback**: If LLM fails/unavailable → α=1.0 (pure rule)

#### A2. Negation & Context Awareness
- **Goal**: Correctly handle negation ("不开心"), conditionals ("如果当时..."), hypotheticals
- **Approach**: LLM prompt explicitly asks for sentiment polarity; rule engine adds basic negation detection (不/没/无/别 + emotion word)
- **Impact**: Fixes the biggest false-positive category in v0.5

#### A3. Event Boundary Detection (LLM-assisted)
- **Goal**: Detect narrative event boundaries more accurately than sentence splitting
- **Approach**: LLM segments text into events, rule engine validates segment count/structure
- **Output**: Event list with type labels (central/peripheral/transitional)

### Phase B: Multi-Dialect Support (Priority: Medium)

#### B1. Dialect Vocabulary Extensions
- **Target dialects**: Cantonese (粤语), Wu/Shanghainese (吴语), Min/Hokkien (闽南语)
- **Approach**: 
  - Separate vocabulary modules per dialect
  - Auto-detection via character/phrase patterns
  - Community-contributed vocabulary via YAML files
- **Impact**: Expands addressable population by ~40% (China's elderly dialect speakers)

#### B2. Dialect-Aware Prompts
- **Goal**: LLM prompts adapted for dialect-specific narrative patterns
- **Approach**: Dialect tag in input → prompt template selection

### Phase C: Clinical Validation (Priority: High, but blocked on RCT)

#### C1. Human-AI Agreement Metrics
- **Goal**: Compute ICC, Cohen's κ, Pearson r between scorer output and human rater scores
- **Approach**: 
  - Collect 100+ human-rated narratives from pilot RCT
  - Run scorer (v0.5 and v0.6) on same texts
  - Report agreement per dimension
- **Blocker**: Requires RCT data collection (currently blocked on recruitment)

#### C2. Longitudinal Sensitivity
- **Goal**: Detect within-person changes over 2-week intervention
- **Approach**: Paired t-test / mixed-effects model on pre/post scores
- **Minimum detectable effect**: Cohen's d ≥ 0.3

### Phase D: Infrastructure (Priority: Medium)

#### D1. Test Suite Expansion
- Current: ~8 test cases → Target: 50+
- Edge cases: empty input, single-character, very long texts (>5000 chars), mixed language
- Regression tests: every bug fix gets a test case

#### D2. Benchmark Dataset
- Create a public benchmark: 30 narratives with gold-standard human scores
- Enable reproducible comparison with future methods

#### D3. CLI Improvements
- Batch scoring: `python scorer.py --batch input_dir/ --output results.json`
- Config file: `scorer.yaml` for weights, thresholds, LLM provider
- Progress bar for batch mode

#### D4. API Server
- FastAPI wrapper for production deployment
- Endpoints: `/score`, `/score/batch`, `/health`
- Docker image for one-command deployment

---

## Release Timeline (Estimated)

| Milestone | Target | Dependencies |
|-----------|--------|-------------|
| v0.6-alpha (A1+A2) | Q2 2026 | DashScope API key |
| v0.6-beta (+ A3, D1) | Q2 2026 | Alpha validation |
| v0.6 RC (+ B1, D3) | Q3 2026 | Dialect vocabulary curation |
| v0.6 GA | Q3 2026 | RC testing |
| v0.7 (C1+C2+D2) | Q4 2026 | RCT data collection |

---

## Technical Decisions (Pending)

| Decision | Options | Recommendation | Status |
|----------|---------|---------------|--------|
| LLM provider priority | DashScope / OpenAI / Local | DashScope first (China deployment, cost) | V 决策 |
| Fusion weight α | Fixed / Learned / Per-dimension | Per-dimension fixed, tuned on pilot data | 待验证 |
| Dialect detection | Rule-based / fastText / LLM | Rule-based (character patterns) for speed | 推荐 |
| API framework | FastAPI / Flask / Gradio-only | FastAPI (production-ready, async) | 推荐 |

---

## Success Metrics for v0.6

| Metric | v0.5 Baseline | v0.6 Target |
|--------|--------------|-------------|
| Human-AI agreement (ICC) | Unknown | ≥ 0.70 |
| Negation handling accuracy | ~50% (estimate) | ≥ 85% |
| Event detection F1 | ~60% (sentence-split proxy) | ≥ 75% |
| Supported dialects | 1 (Mandarin) | 3 (+ Cantonese, Wu) |
| Test cases | ~8 | ≥ 50 |
| Batch processing speed | N/A | ≥ 100 texts/min (rule-only) |

---

*Roadmap by Hulk 🟢 | Will be updated as pilot RCT data becomes available*
