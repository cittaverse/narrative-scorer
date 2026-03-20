# CittaVerse Narrative Scorer v0.5

Automated narrative quality assessment for Chinese autobiographical memories in reminiscence therapy.

## Overview

This tool scores narrative quality across **six dimensions**:

1. **Event Richness** (事件丰富度) - Internal/external detail count
2. **Temporal Coherence** (时间连贯性) - Time markers and sequence clarity
3. **Causal Coherence** (因果连贯性) - Cause-effect reasoning
4. **Emotional Depth** (情感深度) - Emotion word density
5. **Identity Integration** (自我认同整合) - Self-reference frequency
6. **Information Density Distribution** (信息密度分布) - Central vs. peripheral information balance

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
- **Event Richness**: Events per 100 characters
- **Temporal Coherence**: Time marker density + coverage
- **Causal Coherence**: Causal marker density
- **Emotional Depth**: Emotion word density
- **Identity Integration**: Self-reference density
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

## Applications

- **Reminiscence Therapy**: Assess narrative quality in older adults
- **MCI Screening**: Detect cognitive decline through narrative patterns
- **Research**: Quantify narrative changes over time
- **Clinical Practice**: Track therapy progress

## Limitations (v0.5)

- Rule-based event extraction (no LLM)
- Simplified Chinese only (no Cantonese support yet)
- No ASR integration (text input only)
- Vocabulary lists are not exhaustive

## Future Work

- [ ] LLM-enhanced event extraction
- [ ] Cantonese support
- [ ] ASR integration (Whisper/Azure)
- [ ] Large-scale validation with expert ratings
- [x] Web UI (Gradio) - ✅ Completed v0.5

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
