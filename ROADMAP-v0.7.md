# Narrative Scorer v0.7 Roadmap

> CittaVerse Narrative Scorer 从 v0.6 (rule-based + emotion vocabulary complete) → v0.7 (LLM-enhanced hybrid) 的演进规划
> 
> Created: 2026-03-26 | GEO #69

---

## v0.6 Current State (Baseline)

| Aspect | Status |
|--------|--------|
| Version | v0.6.4 (2026-03-26) |
| Architecture | Pure rule-based (regex + vocabulary lists + heuristic scoring) |
| Emotion vocabulary | 90 words (stable for v0.6.x) |
| Temporal markers | 24+ (including lunar calendar, relative time) |
| Causal markers | 14 words |
| Topic transition markers | 24 words |
| Benchmark samples | 18 gold-standard narratives |
| Test coverage | 72 tests (60 unit + 12 benchmark) |
| Benchmark accuracy | 108/108 = 100% dimension accuracy |
| Dependencies | Zero external API (fully offline) |
| Lines of code | ~500 (scorer.py) |
| UI | Gradio web interface |
| Clinical deployment | Pilot RCT N=50 (screening ready) |

### v0.6 Completed Milestones

- [x] v0.6.0: Event boundary detection v2 + CI/CD
- [x] v0.6.1: Identity integration de-saturation (log scaling)
- [x] v0.6.2: Dimension calibration (temporal/emotional short-text inflation fix)
- [x] v0.6.3: Emotion vocabulary expansion (78 → 82 words) + dialect anxiety terms
- [x] v0.6.4: Emotion vocabulary final audit (82 → 90 words) + benchmark expansion (15 → 18 samples)

### v0.6 Known Limitations (To Address in v0.7)

1. **No semantic understanding**: "心里空落落的" (implicit sadness) not detected without explicit emotion word
2. **Negation handling is rule-based**: Prefix detection (不/没/无/别) works but can miss complex negation
3. **No context awareness**: "我很开心" and "我假装很开心" score the same
4. **Event boundary detection is heuristic**: Topic transitions + sentence splitting, not semantic event segmentation
5. **Causal link detection is marker-based**: Misses paraphrased or implicit causality
6. **No holistic quality judgment**: Can't assess "narrative coherence" beyond marker counting
7. **Single language**: Chinese only (Mandarin); no multi-lingual support

---

## v0.7 Target Architecture: LLM-Enhanced Hybrid

### Core Principle

**LLM augments rule-based pipeline, doesn't replace it:**
- Rule-based: Fast, deterministic, transparent, offline-capable
- LLM: Semantic understanding, implicit feature detection, holistic judgment
- Hybrid: Best of both worlds with graceful degradation

### Architecture Diagram

```
Input Text
    │
    ├─── Rule-Based Feature Extractor ──→ Explicit markers (emotion/temporal/causal)
    │                                              │
    ├─── LLM Feature Extractor ──────────→ Implicit features
    │        ├─ Implicit emotions                │
    │        ├─ Semantic event boundaries        │
    │        └─ Implicit causality               │
    │                                              │
    └─── Fusion Layer ────────────────────────────┘
                     │
                     ↓
              Rule-Based Scorer (enhanced features)
                     │
                     ↓
              6-Dimension Scores (0-100)
                     │
                     ↓
              Confidence + Explanation (optional from LLM)
```

**Key design constraint**: LLM module is **optional**. When offline or API-unavailable, system degrades gracefully to v0.6 rule-only mode.

---

## Feature Plan

### Phase A: LLM Feature Extraction (Priority: High)

#### A1. Implicit Emotion Detection
- **Goal**: Detect emotions not expressed via explicit vocabulary
- **Examples**:
  - "心里空落落的" → sadness/loss (implicit)
  - "整个人都轻了" → relief (implicit)
  - "鼻子一酸" → sadness/touched (implicit)
- **Prompt design**:
  ```
  请分析以下叙事文本中表达的所有情感，包括明确表达的和隐含的情感。
  对于每个情感，请标注：
  1. 情感类型（如：喜悦、悲伤、愤怒、恐惧、惊讶、厌恶等）
  2. 表达方式（明确/隐含）
  3. 原文依据（引用触发该情感的短语或句子）
  
  文本：{input_text}
  
  请以 JSON 格式输出：
  [
    {"emotion": "悲伤", "type": "implicit", "evidence": "心里空落落的"},
    {"emotion": "喜悦", "type": "explicit", "evidence": "我很开心"}
  ]
  ```
- **Integration**: Augment `count_emotion_words()` with LLM-detected implicit emotions
- **Fallback**: If LLM fails → use only explicit emotion words (v0.6 behavior)

#### A2. Semantic Event Boundary Detection
- **Goal**: Detect narrative event boundaries more accurately than heuristic splitting
- **Current approach (v0.6)**: Sentence splitting + topic transition markers
- **LLM approach**: Semantic event segmentation
- **Prompt design**:
  ```
  请将以下叙事文本分割成独立的事件。每个事件应该是一个连贯的片段，
  描述一个具体的时间、地点、人物和发生的事。
  
  对于每个事件，请标注：
  1. 事件类型（核心事件/边缘事件/过渡事件）
  2. 时间标记（如有）
  3. 主要人物（如有）
  4. 事件摘要（一句话）
  
  文本：{input_text}
  
  请以 JSON 格式输出：
  [
    {
      "type": "central",
      "temporal_marker": "那年夏天",
      "participants": ["我", "奶奶"],
      "summary": "我和奶奶一起在院子里摘桂花"
    }
  ]
  ```
- **Integration**: Compare with rule-based `extract_events()` → use LLM when rule-based produces <3 events or low confidence
- **Fallback**: Use rule-based event extraction

#### A3. Implicit Causal Link Detection
- **Goal**: Detect cause-effect relationships not marked by explicit causal words
- **Current approach (v0.6)**: Marker counting (因为/所以/因此/由于...)
- **LLM approach**: Semantic causality detection
- **Prompt design**:
  ```
  请识别以下叙事文本中所有的因果关系，包括明确表达的和隐含的。
  
  对于每个因果关系，请标注：
  1. 原因（引用原文）
  2. 结果（引用原文）
  3. 表达方式（明确/隐含）
  4. 因果强度（强/中/弱）
  
  文本：{input_text}
  
  请以 JSON 格式输出：
  [
    {
      "cause": "我那晚烧到 39 度",
      "effect": "父母半夜抱着我往医院跑",
      "type": "explicit",
      "strength": "strong"
    }
  ]
  ```
- **Integration**: Augment `count_causal_markers()` with LLM-detected implicit causality
- **Fallback**: Use only explicit causal markers (v0.6 behavior)

### Phase B: Hybrid Scoring (Priority: Medium)

#### B1. Dimension-Specific Fusion
- **Goal**: Combine rule-based and LLM scores with dimension-specific weights
- **Approach**:
  - `event_richness`: 70% rule (event count) + 30% LLM (event quality)
  - `temporal_coherence`: 80% rule (marker count) + 20% LLM (temporal flow)
  - `causal_coherence`: 60% rule (marker count) + 40% LLM (implicit causality)
  - `emotional_depth`: 50% rule (explicit words) + 50% LLM (implicit emotions)
  - `identity_integration`: 90% rule (pronoun count) + 10% LLM (self-reference quality)
  - `information_density`: 100% rule (character/event ratio, no LLM needed)
- **Calibration**: Tune weights on pilot RCT data (when available)

#### B2. Confidence Intervals
- **Goal**: Provide uncertainty estimates for each dimension score
- **Approach**:
  - Rule-based scores: Low uncertainty (deterministic)
  - LLM-detected features: Higher uncertainty (model variance)
  - Fusion: Weighted uncertainty propagation
- **Output**: `score: 75, confidence: 0.85, ci_95: [68, 82]`

#### B3. LLM Explanation Generation
- **Goal**: Generate human-readable explanations for each dimension score
- **Prompt design**:
  ```
  请为以下叙事评分结果生成简短的解释说明：
  
  文本：{input_text}
  维度得分：
  - 事件丰富度：75/100
  - 时间连贯性：82/100
  - 因果连贯性：68/100
  - 情感深度：45/100
  - 身份整合度：55/100
  - 信息密度：70/100
  
  请为每个维度写 1-2 句话的解释，说明得分高或低的原因，并引用原文依据。
  ```
- **Use case**: Clinical reports, user feedback, research transparency

### Phase C: Multi-Dialect Support (Priority: Medium, Deferred to v0.8)

#### C1. Dialect Vocabulary Extensions
- **Target dialects**: Cantonese (粤语), Wu/Shanghainese (吴语), Min/Hokkien (闽南语)
- **Approach**: Community-contributed vocabulary via YAML files
- **Status**: Deferred to v0.8 (focus on LLM integration for v0.7)

#### C2. Dialect-Aware Prompts
- **Goal**: LLM prompts adapted for dialect-specific narrative patterns
- **Status**: Deferred to v0.8

### Phase D: Infrastructure (Priority: High)

#### D1. Test Suite Expansion
- **Current**: 72 tests (60 unit + 12 benchmark)
- **Target**: 100+ tests
- **Additions**:
  - LLM feature extraction tests (mock API responses)
  - Fallback behavior tests (API failure scenarios)
  - Edge cases: mixed language, dialect samples, very long texts (>5000 chars)
  - Regression tests: every bug fix gets a test case

#### D2. Benchmark Dataset Expansion
- **Current**: 18 gold-standard samples
- **Target**: 30+ samples
- **Additions**:
  - Dialect narratives (Cantonese, Wu, Min)
  - Multi-lingual narratives (Chinese-English code-switching)
  - Clinical samples (MCI, early dementia, depression)
  - Cross-cultural narratives (mainland China, Taiwan, Hong Kong, overseas Chinese)

#### D3. API Server (FastAPI)
- **Goal**: Production-ready API for integration with CittaVerse platform
- **Endpoints**:
  - `POST /score` — Single narrative scoring
  - `POST /score/batch` — Batch scoring (up to 100 narratives)
  - `GET /health` — Health check
  - `GET /metrics` — Prometheus metrics
- **Features**:
  - Async processing
  - Rate limiting
  - API key authentication
  - Request logging
- **Deployment**: Docker image for one-command deployment

#### D4. Cost Tracking
- **Goal**: Track LLM API costs per narrative
- **Metrics**:
  - API calls per narrative
  - Token usage (input + output)
  - Cost per narrative (by LLM provider)
  - Monthly cost projection
- **Dashboard**: Simple CLI or web UI for cost monitoring

---

## Release Timeline (Estimated)

| Milestone | Target | Dependencies | Status |
|-----------|--------|-------------|--------|
| v0.7.0-alpha (A1) | Q3 2026 (Jul) | DASHSCOPE_API_KEY | 🟡 Planned |
| v0.7.0-beta (+ A2, A3) | Q3 2026 (Aug) | Alpha validation | ⚪ Not started |
| v0.7.0 RC (+ B1, B2, D1) | Q3 2026 (Sep) | Beta testing, pilot data | ⚪ Not started |
| v0.7.0 GA | Q3 2026 (Oct) | RC testing, documentation | ⚪ Not started |
| v0.7.1 (+ D3, D4) | Q4 2026 (Nov) | GA feedback | ⚪ Not started |

---

## Technical Decisions

| Decision | Options | Recommendation | Status |
|----------|---------|---------------|--------|
| LLM provider | DashScope (Qwen) / GLM / GPT-4 | DashScope first (China deployment, cost, latency) | ✅ Decided |
| Prompt language | Chinese / English | Chinese (matches input narratives, better cultural alignment) | ✅ Decided |
| Fusion strategy | Fixed weights / Learned weights / Per-dimension fixed | Per-dimension fixed (tunable on pilot data) | ✅ Decided |
| Fallback behavior | Rule-only / Cached LLM / Error | Rule-only (graceful degradation) | ✅ Decided |
| API framework | FastAPI / Flask / Gradio-only | FastAPI (production-ready, async, ecosystem) | ✅ Decided |

---

## Success Metrics for v0.7

| Metric | v0.6 Baseline | v0.7 Target | Measurement |
|--------|--------------|-------------|-------------|
| Implicit emotion detection | 0% (rule-only) | ≥ 70% recall | LLM vs human annotation |
| Event boundary F1 | ~75% (heuristic) | ≥ 85% | LLM vs human segmentation |
| Causal link recall | ~60% (marker-based) | ≥ 80% | LLM vs human annotation |
| Human-AI agreement (ICC) | Unknown | ≥ 0.75 | Pilot RCT data |
| API cost per narrative | ¥0 | < ¥0.02 | DashScope pricing |
| Latency (single narrative) | < 100ms (rule-only) | < 3s (LLM-enhanced) | P95 latency |
| Test coverage | 72 tests | ≥ 100 tests | pytest count |
| Benchmark samples | 18 samples | ≥ 30 samples | test_benchmark.py |

---

## Dependencies & Blockers

| Blocker | Owner | Duration | Impact | Resolution |
|---------|-------|----------|--------|------------|
| DASHSCOPE_API_KEY | V | >246h | v0.7 LLM development blocked | V to provide API key |
| Pilot RCT data | V | >210h | Fusion weight calibration blocked | Path B recruitment execution |
| Benchmark annotation | Hulk | — | LLM validation baseline | Hulk to expand + annotate |

---

## Open Questions

1. **Cost threshold**: Is ¥0.02/narrative acceptable for pilot RCT (N=50, ~3 narratives/participant = ¥3 total)?
2. **Latency tolerance**: Is <3s acceptable for Gradio UI, or need async streaming?
3. **LLM model size**: Qwen-Max (best quality) vs Qwen-Plus (balanced) vs Qwen-Turbo (fastest)?
4. **Prompt optimization**: How many iterations needed to stabilize LLM feature extraction quality?
5. **A/B testing strategy**: How to compare v0.6 vs v0.7 on same narratives without human rater bias?

---

## v0.7 Development Checklist

### Phase A (LLM Feature Extraction)
- [ ] Create `llm_feature_extractor.py` module
- [ ] Implement DashScope API client (with retry logic, rate limiting)
- [ ] Design + test prompt templates (3 feature types)
- [ ] Implement fallback mechanism (rule-only on API failure)
- [ ] Write unit tests (mock API responses)
- [ ] A/B test on 18 benchmark samples

### Phase B (Hybrid Scoring)
- [ ] Implement dimension-specific fusion logic
- [ ] Add confidence interval calculation
- [ ] Implement explanation generation
- [ ] Calibrate fusion weights (pilot data or expert annotation)
- [ ] Update benchmark tests (hybrid scoring expected ranges)

### Phase D (Infrastructure)
- [ ] Expand test suite to 100+ tests
- [ ] Expand benchmark to 30+ samples
- [ ] Implement FastAPI server
- [ ] Add cost tracking + logging
- [ ] Create Docker image
- [ ] Write deployment documentation

---

## References

### Key Papers
1. **G-Eval** (Liu et al., 2023) — LLM + CoT for NLG evaluation
2. **FActScore** (Min et al., 2023) — Atomic fact evaluation
3. **Prometheus** (Kim et al., 2023) — Fine-tuned open-source evaluator
4. **LLM-as-Judge Survey** (Zheng et al., 2023) — Comprehensive survey

### Related Projects
- nlg-metricverse (nlg-metricverse.github.io) — NLG evaluation metric collection
- CittaVerse narrative-scorer (github.com/CittaVerse/narrative-scorer) — Base project

---

*Roadmap by Hulk 🟢 | Will be updated as DASHSCOPE_API_KEY becomes available and pilot RCT data is collected*
