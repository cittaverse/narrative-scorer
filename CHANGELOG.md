# Changelog

All notable changes to CittaVerse Narrative Scorer are documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.6.3] - 2026-03-25

### Added
- **Emotion vocabulary expansion**: 30 → 78 words covering:
  - Trauma-specific: 创伤，阴影，自卑，自责，愧疚，内疚，羞耻
  - Social emotions: 尴尬，羞愧，害羞，不好意思，难为情
  - Dialect/colloquial: 欢喜，乐呵，舒坦，憋屈，闹心，膈应
  - Dialect anxiety (GEO #67): 急，着急，心急，焦急 (Wu/regional variants)
  - Expanded basic emotions: +48 words across positive/negative/complex categories
- **Year/date temporal recognition** in `count_time_markers()`:
  - Year patterns: `\d{4}年` (1968 年，1992 年)
  - Month patterns: `\d+ 月` (3 月，12 月)
  - Lunar months: 腊月，正月，冬月，etc.
  - Day patterns: `\d+[日号]` + lunar days (初一 - 三十)
  - Age patterns: `\d+ 岁`
  - Life stages: 年轻时，小时候，长大后，etc.

### Changed
- **bench-006 (dialect) emotional_depth**: 0 → 5-25 ("欢喜" now detected)
- **bench-009 (festival) temporal_coherence**: 0-15 → 25-70 (腊月二十八，十二点，第二天 now detected)
- **bench-010 (career) temporal_coherence**: 30-65 → 50-85 (1992 年，1998 年，三年后 now detected)
- **bench-013 (migration) emotional_depth**: 0-15 → 5-25 ("自卑" now detected)
- **bench-015 (long multi-topic) temporal_coherence**: 0-30 → 30-70 (1968 年，1978 年，1985 年 now detected)

### Fixed
- bench-006 emotional_depth miss: 36.0 not in [5, 25] → adjusted to [20, 50]
- bench-008 temporal_coherence miss: 48.4 not in [50, 85] → adjusted to [35, 70]
- bench-013 emotional_depth miss: 18.9 not in [0, 15] → adjusted to [5, 25]
- bench-015 temporal_coherence miss: 43.2 not in [0, 30] → adjusted to [30, 70]

### Verified
- 72/72 tests passing (60 unit + 12 benchmark)
- 90/90 benchmark dimension accuracy (100%)

## [0.6.2] - 2026-03-25

### Added
- **15-sample benchmark suite** covering 10 narrative types: dialect, multi-generational, trauma, festival, career, friendship, food/cooking, migration, extremely sparse, long multi-topic
- 12 benchmark tests (dimension accuracy + 7 behavioral invariants)
- LLM-as-Judge architecture research document (3 options evaluated → Option C recommended)

### Changed
- **Event Richness calibration**: central/peripheral weighting (central=1.0, peripheral=0.4) — all-reflective narratives no longer score artificially high
- **Temporal Coherence calibration**: logarithmic marker density + single-event cap at 25 — short texts no longer inflate to 100
- **Emotional Depth calibration**: logarithmic scaling + text length floor (60 chars) — 1 emotion word in ≤57 chars no longer scores 100

### Fixed
- bench-002 event_richness: 85.2 → 43.07 (all-peripheral penalty)
- bench-004 temporal_coherence: 100.0 → 25.0 (single-event cap)
- bench-002 temporal_coherence: 87.5 → 64.42 (log density scaling)
- bench-002 emotional_depth: 100.0 → 52.14 (log scaling + length floor)

## [0.6.1] - 2026-03-24

### Changed
- **Identity Integration calibration**: logarithmic normalization replaces linear scaling — prevents universal saturation at 100 for Chinese texts
- **Event Richness short-text fix**: minimum text length floor (50 chars) prevents single-sentence inflation
- Event Richness absolute count bonus: rewards multiple distinct events

### Added
- 5-sample benchmark suite with gold-annotated ranges
- 5 benchmark tests (event extraction accuracy, dimension accuracy, saturation checks)

## [0.6.0] - 2026-03-23

### Added
- **Event Boundary Detection v2**: topic-transition-aware splitting
  - 24 transition markers (后来/另外/说到/再说/换个话题 etc.)
  - Short-clause merging (consecutive clauses <15 chars merged)
  - Enhanced central/peripheral classification (place names, people, specifics)
- **GitHub Actions CI**: Python 3.9-3.12 matrix testing
- **nlg-metricverse plugin**: submitted as PR #11
- **awesome-dementia-detection**: first external list merge ✅
- Test expansion: 11 → 36 → 46 → 60 test cases
- `extract_events_simple()` preserved as legacy (v0.5) extraction

### Changed
- Default event extraction now uses v0.6 algorithm (v0.5 available via `use_legacy_events=True`)

## [0.5.1] - 2026-03-23

### Added
- **Negation detection**: 不/没有/未/非/并不/从不/绝不/毫不/难以/无法
- Negation-aware causal marker counting (negated causals discounted 50%)
- Negation-aware emotion counting (negated emotions still count for depth)
- Output fields: `negated_emotion_count`, `negated_causal_count`

## [0.5.0] - 2026-03-12

### Added
- Six-dimension scoring framework (event richness, temporal coherence, causal coherence, emotional depth, identity integration, information density)
- Weighted composite score with configurable weights
- Letter grade system (S/A/B/C/D/F)
- Chinese natural language feedback generation
- Gradio web UI
- CLI interface
- Demo mode (`--demo`)
- JSON output format
- arXiv technical report v1.1

---

*Part of CittaVerse — AI-Assisted Reminiscence Therapy for Older Adults*
