# Changelog

All notable changes to CittaVerse Narrative Scorer are documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

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
