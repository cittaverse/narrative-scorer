#!/usr/bin/env python3
"""
CittaVerse Narrative Scorer v0.5
Automated narrative quality assessment for Chinese autobiographical memories

Six dimensions:
1. Event Richness (内部/外部细节)
2. Temporal Coherence (时间连贯性)
3. Causal Coherence (因果连贯性)
4. Emotional Depth (情感深度)
5. Identity Integration (自我认同整合)
6. Information Density Distribution (中心/外围信息比)

Author: Hulk 🟢 for CittaVerse
License: MIT
"""

import json
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime


# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class Event:
    """Extracted event from narrative"""
    description: str
    event_type: str = "central"  # "central" or "peripheral"
    time_marker: Optional[str] = None
    people: List[str] = field(default_factory=list)


@dataclass
class NarrativeScore:
    """Six-dimension narrative quality score"""
    event_richness: float = 0.0  # 0-100
    temporal_coherence: float = 0.0  # 0-100
    causal_coherence: float = 0.0  # 0-100
    emotional_depth: float = 0.0  # 0-100
    identity_integration: float = 0.0  # 0-100
    information_density: float = 0.0  # 0-100
    
    # Detailed metrics
    central_count: int = 0
    peripheral_count: int = 0
    central_ratio: float = 0.0
    total_events: int = 0
    time_markers_count: int = 0
    causal_markers_count: int = 0
    self_references_count: int = 0
    emotion_words_count: int = 0
    
    # Composite
    composite_score: float = 0.0
    letter_grade: str = "F"
    feedback: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


# ============================================================================
# Configuration
# ============================================================================

DEFAULT_WEIGHTS = {
    "event_richness": 0.15,
    "temporal_coherence": 0.15,
    "causal_coherence": 0.15,
    "emotional_depth": 0.20,
    "identity_integration": 0.15,
    "information_density": 0.20
}

# Chinese time markers
TIME_MARKERS = [
    "然后", "接着", "随后", "之后", "之前", "当时", "那时", "现在",
    "今天", "昨天", "明天", "去年", "今年", "明年", "小时候", "长大后",
    "首先", "其次", "最后", "一开始", "后来", "终于", "突然", "渐渐"
]

# Chinese causal markers
CAUSAL_MARKERS = [
    "因为", "所以", "因此", "于是", "结果", "导致", "由于", "既然",
    "为了", "以便", "从而", "致使", "怪不得", "难怪"
]

# Chinese self-reference markers
SELF_MARKERS = ["我", "我的", "我自己", "咱", "咱们", "自己"]

# Chinese emotion words (simplified list for MVP)
EMOTION_WORDS = [
    # Positive
    "开心", "快乐", "高兴", "幸福", "满足", "欣慰", "骄傲", "自豪",
    "温暖", "感动", "感激", "喜欢", "爱", "兴奋", "激动", "期待",
    # Negative
    "难过", "伤心", "悲伤", "痛苦", "害怕", "恐惧", "焦虑", "紧张",
    "生气", "愤怒", "失望", "遗憾", "后悔", "孤独", "无助", "疲惫",
    # Neutral/Complex
    "惊讶", "意外", "困惑", "迷茫", "平静", "放松", "复杂", "矛盾"
]


# ============================================================================
# Core Scoring Functions
# ============================================================================

def count_time_markers(text: str) -> int:
    """Count temporal coherence markers in text"""
    count = 0
    for marker in TIME_MARKERS:
        count += text.count(marker)
    return count


def count_causal_markers(text: str) -> int:
    """Count causal coherence markers in text"""
    count = 0
    for marker in CAUSAL_MARKERS:
        count += text.count(marker)
    return count


def count_self_references(text: str) -> int:
    """Count self-reference markers in text"""
    count = 0
    for marker in SELF_MARKERS:
        count += text.count(marker)
    return count


def count_emotion_words(text: str) -> int:
    """Count emotion words in text"""
    count = 0
    for word in EMOTION_WORDS:
        count += text.count(word)
    return count


def extract_events_simple(text: str) -> List[Event]:
    """
    Simple event extraction (rule-based for MVP)
    Split by sentence boundaries and classify as central/peripheral
    """
    events = []
    
    # Simple sentence splitting (Chinese punctuation)
    sentences = re.split(r'[。！？!?]', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    for sentence in sentences:
        if len(sentence) < 5:  # Skip very short fragments
            continue
        
        # Simple classification heuristic
        # Central: contains specific details (numbers, names, places)
        # Peripheral: general statements, reflections
        has_specifics = bool(re.search(r'\d+|[一二三四五六七八九十百千万]', sentence))
        is_reflection = any(word in sentence for word in ["觉得", "认为", "想", "感觉", "可能", "也许"])
        
        if has_specifics and not is_reflection:
            event_type = "central"
        else:
            event_type = "peripheral"
        
        # Extract time marker if present
        time_marker = None
        for marker in TIME_MARKERS:
            if marker in sentence:
                time_marker = marker
                break
        
        events.append(Event(
            description=sentence,
            event_type=event_type,
            time_marker=time_marker
        ))
    
    return events


def score_event_richness(events: List[Event], text_length: int) -> float:
    """
    Score event richness (0-100)
    Based on total events and text length normalization
    """
    if not events:
        return 0.0
    
    # Base score: events per 100 characters
    events_per_100_chars = (len(events) / max(text_length, 1)) * 100
    
    # Normalize to 0-100 (cap at 10 events per 100 chars = 100 points)
    score = min(events_per_100_chars * 10, 100.0)
    
    return round(score, 2)


def score_temporal_coherence(events: List[Event], time_markers_count: int, text_length: int) -> float:
    """
    Score temporal coherence (0-100)
    Based on time markers density and event temporal structure
    """
    if not events:
        return 0.0
    
    # Time markers per 100 characters
    marker_density = (time_markers_count / max(text_length, 1)) * 100
    
    # Events with time markers ratio
    events_with_time = sum(1 for e in events if e.time_marker)
    time_coverage = (events_with_time / len(events)) * 100 if events else 0
    
    # Combined score (50% marker density, 50% coverage)
    score = (min(marker_density * 20, 50) + time_coverage * 0.5)
    
    return round(min(score, 100.0), 2)


def score_causal_coherence(causal_markers_count: int, text_length: int) -> float:
    """
    Score causal coherence (0-100)
    Based on causal marker density
    """
    # Causal markers per 100 characters
    marker_density = (causal_markers_count / max(text_length, 1)) * 100
    
    # Normalize (5 markers per 100 chars = 100 points)
    score = min(marker_density * 20, 100.0)
    
    return round(score, 2)


def score_emotional_depth(emotion_words_count: int, text_length: int) -> float:
    """
    Score emotional depth (0-100)
    Based on emotion word density
    """
    # Emotion words per 100 characters
    emotion_density = (emotion_words_count / max(text_length, 1)) * 100
    
    # Normalize (3 emotion words per 100 chars = 100 points)
    score = min(emotion_density * 33, 100.0)
    
    return round(score, 2)


def score_identity_integration(self_references_count: int, text_length: int) -> float:
    """
    Score identity integration (0-100)
    Based on self-reference density
    """
    # Self references per 100 characters
    self_density = (self_references_count / max(text_length, 1)) * 100
    
    # Normalize (2 self-refs per 100 chars = 100 points)
    score = min(self_density * 50, 100.0)
    
    return round(score, 2)


def score_information_density(events: List[Event]) -> float:
    """
    Score information density distribution (0-100)
    Based on central vs peripheral ratio
    Optimal ratio: ~60% central, 40% peripheral (research-based)
    """
    if not events:
        return 0.0
    
    central_count = sum(1 for e in events if e.event_type == "central")
    peripheral_count = len(events) - central_count
    
    central_ratio = central_count / len(events)
    
    # Optimal central ratio: 0.6 (60%)
    # Score based on distance from optimal
    optimal_ratio = 0.6
    deviation = abs(central_ratio - optimal_ratio)
    
    # Perfect match = 100, deviation of 0.5 = 0
    score = max(0, 100 - (deviation * 200))
    
    return round(score, 2)


def calculate_composite_score(scores: Dict[str, float], weights: Dict[str, float]) -> float:
    """Calculate weighted composite score"""
    composite = sum(scores[dim] * weights.get(dim, 1/6) for dim in scores)
    return round(composite, 2)


def get_letter_grade(score: float) -> str:
    """Convert numeric score to letter grade"""
    if score >= 90:
        return "S"
    elif score >= 80:
        return "A"
    elif score >= 70:
        return "B"
    elif score >= 60:
        return "C"
    elif score >= 50:
        return "D"
    else:
        return "F"


def generate_feedback(score: NarrativeScore) -> str:
    """Generate natural language feedback based on scores"""
    feedback_parts = []
    
    # Overall assessment
    if score.composite_score >= 80:
        feedback_parts.append("这是一段高质量的叙事，细节丰富且结构清晰。")
    elif score.composite_score >= 60:
        feedback_parts.append("这是一段不错的叙事，有一些亮点可以继续加强。")
    else:
        feedback_parts.append("这段叙事有提升空间，可以尝试增加更多细节和连贯性。")
    
    # Strengths
    dimensions = [
        ("event_richness", "事件丰富度"),
        ("temporal_coherence", "时间连贯性"),
        ("causal_coherence", "因果连贯性"),
        ("emotional_depth", "情感深度"),
        ("identity_integration", "自我认同整合"),
        ("information_density", "信息密度分布")
    ]
    
    scores_list = [
        score.event_richness,
        score.temporal_coherence,
        score.causal_coherence,
        score.emotional_depth,
        score.identity_integration,
        score.information_density
    ]
    
    # Find strongest dimension
    max_idx = scores_list.index(max(scores_list))
    feedback_parts.append(f"特别突出的是{dimensions[max_idx][1]}（{scores_list[max_idx]:.0f}分）。")
    
    # Find weakest dimension
    min_idx = scores_list.index(min(scores_list))
    if scores_list[min_idx] < 70:
        feedback_parts.append(f"建议加强{dimensions[min_idx][1]}（{scores_list[min_idx]:.0f}分）。")
    
    return " ".join(feedback_parts)


# ============================================================================
# Main Scoring Function
# ============================================================================

def score_narrative(text: str, weights: Optional[Dict[str, float]] = None) -> NarrativeScore:
    """
    Score a Chinese narrative text on six dimensions
    
    Args:
        text: Chinese narrative text
        weights: Optional custom weights for dimensions
    
    Returns:
        NarrativeScore object with all dimensions and composite score
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS
    
    # Preprocessing
    text = text.strip()
    text_length = len(text)
    
    # Extract features
    events = extract_events_simple(text)
    time_markers_count = count_time_markers(text)
    causal_markers_count = count_causal_markers(text)
    self_references_count = count_self_references(text)
    emotion_words_count = count_emotion_words(text)
    
    # Count central/peripheral
    central_count = sum(1 for e in events if e.event_type == "central")
    peripheral_count = len(events) - central_count
    central_ratio = central_count / len(events) if events else 0.0
    
    # Calculate dimension scores
    scores = {
        "event_richness": score_event_richness(events, text_length),
        "temporal_coherence": score_temporal_coherence(events, time_markers_count, text_length),
        "causal_coherence": score_causal_coherence(causal_markers_count, text_length),
        "emotional_depth": score_emotional_depth(emotion_words_count, text_length),
        "identity_integration": score_identity_integration(self_references_count, text_length),
        "information_density": score_information_density(events)
    }
    
    # Calculate composite
    composite = calculate_composite_score(scores, weights)
    
    # Build result
    result = NarrativeScore(
        event_richness=scores["event_richness"],
        temporal_coherence=scores["temporal_coherence"],
        causal_coherence=scores["causal_coherence"],
        emotional_depth=scores["emotional_depth"],
        identity_integration=scores["identity_integration"],
        information_density=scores["information_density"],
        central_count=central_count,
        peripheral_count=peripheral_count,
        central_ratio=round(central_ratio, 3),
        total_events=len(events),
        time_markers_count=time_markers_count,
        causal_markers_count=causal_markers_count,
        self_references_count=self_references_count,
        emotion_words_count=emotion_words_count,
        composite_score=composite,
        letter_grade=get_letter_grade(composite),
        feedback=generate_feedback(NarrativeScore(
            event_richness=scores["event_richness"],
            temporal_coherence=scores["temporal_coherence"],
            causal_coherence=scores["causal_coherence"],
            emotional_depth=scores["emotional_depth"],
            identity_integration=scores["identity_integration"],
            information_density=scores["information_density"],
            composite_score=composite
        ))
    )
    
    return result


# ============================================================================
# CLI Entry Point
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python scorer.py <narrative_text>")
        print("   or: python scorer.py --demo")
        sys.exit(1)
    
    if sys.argv[1] == "--demo":
        # Demo with sample text
        demo_text = """
        我记得那是一个春天的下午，阳光明媚。我和奶奶一起去公园散步，那是她最喜欢的地方。
        我们坐在湖边的长椅上，奶奶开始讲述她年轻时的故事。她说那时候生活很艰苦，但家人在一起就很幸福。
        我觉得很感动，因为奶奶很少提起过去的事情。那天我们聊了很多，我感觉更了解她了。
        """
        
        result = score_narrative(demo_text)
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        # Score provided text
        text = " ".join(sys.argv[1:])
        result = score_narrative(text)
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
