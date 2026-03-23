#!/usr/bin/env python3
"""
Unit tests for Narrative Scorer v0.5
Expanded from 11 → 32 test cases (GEO #60)
Covers: marker counting, event extraction, scoring dimensions,
        edge cases, boundary conditions, mixed-language inputs
"""

import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scorer import (
    score_narrative,
    count_time_markers,
    count_causal_markers,
    count_self_references,
    count_emotion_words,
    extract_events_simple,
    get_letter_grade,
    score_event_richness,
    score_temporal_coherence,
    score_causal_coherence,
    score_emotional_depth,
    score_identity_integration,
    score_information_density,
    calculate_composite_score,
    generate_feedback,
    NarrativeScore,
    Event,
    DEFAULT_WEIGHTS,
)


# ============================================================================
# 1. Marker Counting Tests (original 4 + 5 new)
# ============================================================================

class TestMarkerCounting(unittest.TestCase):
    """Test marker counting functions"""

    def test_time_markers(self):
        text = "然后我去了公园，之后又去了商店"
        count = count_time_markers(text)
        self.assertGreater(count, 0)

    def test_causal_markers(self):
        text = "因为下雨，所以我们取消了计划"
        count = count_causal_markers(text)
        self.assertGreater(count, 0)

    def test_self_references(self):
        text = "我觉得很开心，我的家人也很高兴"
        count = count_self_references(text)
        self.assertGreater(count, 0)

    def test_emotion_words(self):
        text = "我感到快乐和幸福"
        count = count_emotion_words(text)
        self.assertGreater(count, 0)

    # --- New tests ---

    def test_time_markers_no_markers(self):
        """Text with no time markers should return 0"""
        text = "天空很蓝，草地很绿"
        count = count_time_markers(text)
        self.assertEqual(count, 0)

    def test_causal_markers_multiple(self):
        """Multiple causal markers in one text"""
        text = "因为天冷，所以穿大衣。因为路远，所以坐车去。因此迟到了。"
        count = count_causal_markers(text)
        self.assertGreaterEqual(count, 3)

    def test_self_references_none(self):
        """Text with no self-references"""
        text = "山上的花开了，河水在流淌"
        count = count_self_references(text)
        self.assertEqual(count, 0)

    def test_emotion_words_negative(self):
        """Negative emotion words should be counted"""
        text = "我感到悲伤和痛苦，心里很难过"
        count = count_emotion_words(text)
        self.assertGreater(count, 0)

    def test_time_markers_dense(self):
        """Dense time markers in a rich narrative"""
        text = "首先我们出发了，然后到了山脚下，接着开始爬山，最后到达山顶。后来我们下山了。"
        count = count_time_markers(text)
        self.assertGreaterEqual(count, 3)


# ============================================================================
# 2. Event Extraction Tests (original 2 + 4 new)
# ============================================================================

class TestEventExtraction(unittest.TestCase):
    """Test event extraction"""

    def test_extract_events(self):
        text = "我记得那是一个春天。我和奶奶去公园。我们很开心。"
        events = extract_events_simple(text)
        self.assertGreater(len(events), 0)

    def test_event_classification(self):
        text = "那天是 2020 年 3 月 15 日。我觉得很感动。"
        events = extract_events_simple(text)
        self.assertGreater(len(events), 0)

    # --- New tests ---

    def test_extract_events_single_sentence(self):
        """Single sentence should produce at least 1 event"""
        text = "我和妈妈一起去了医院"
        events = extract_events_simple(text)
        self.assertGreaterEqual(len(events), 1)

    def test_extract_events_long_narrative(self):
        """Long narrative should produce multiple events"""
        text = (
            "那是1985年的夏天，我刚从大学毕业。"
            "我回到了家乡，看到了久违的父母。"
            "父亲带我去了田里，我们一起收割庄稼。"
            "晚上全家人围坐在一起吃饭，母亲做了我最爱的红烧肉。"
            "那天晚上我睡得很香，梦里都是金色的麦田。"
        )
        events = extract_events_simple(text)
        self.assertGreaterEqual(len(events), 3)

    def test_event_type_is_valid(self):
        """All events should have valid type"""
        text = "我记得那天下雨了。我和朋友在家里聊天。后来我们一起看了一部电影。"
        events = extract_events_simple(text)
        for event in events:
            self.assertIn(event.event_type, ["central", "peripheral"])

    def test_event_description_not_empty(self):
        """Event descriptions should not be empty"""
        text = "奶奶给我讲了很多故事。她说年轻时生活很艰苦。但是家人在一起就很幸福。"
        events = extract_events_simple(text)
        for event in events:
            self.assertTrue(len(event.description.strip()) > 0)


# ============================================================================
# 3. Scoring Tests (original 4 + 3 new)
# ============================================================================

class TestScoring(unittest.TestCase):
    """Test narrative scoring"""

    def test_score_narrative_basic(self):
        text = "我记得那天阳光明媚。我和家人一起去了公园，玩得很开心。"
        result = score_narrative(text)
        self.assertIsInstance(result.composite_score, float)
        self.assertIsInstance(result.letter_grade, str)
        self.assertIsInstance(result.feedback, str)

    def test_score_empty_text(self):
        text = ""
        result = score_narrative(text)
        self.assertEqual(result.composite_score, 0.0)

    def test_letter_grades(self):
        self.assertEqual(get_letter_grade(95), "S")
        self.assertEqual(get_letter_grade(85), "A")
        self.assertEqual(get_letter_grade(75), "B")
        self.assertEqual(get_letter_grade(65), "C")
        self.assertEqual(get_letter_grade(55), "D")
        self.assertEqual(get_letter_grade(45), "F")

    def test_score_dimensions(self):
        text = "我记得那是一个春天的下午。我和奶奶一起去公园散步。她讲述年轻时的故事，生活很艰苦但家人在一起很幸福。我觉得很感动。"
        result = score_narrative(text)
        self.assertTrue(0 <= result.event_richness <= 100)
        self.assertTrue(0 <= result.temporal_coherence <= 100)
        self.assertTrue(0 <= result.causal_coherence <= 100)
        self.assertTrue(0 <= result.emotional_depth <= 100)
        self.assertTrue(0 <= result.identity_integration <= 100)
        self.assertTrue(0 <= result.information_density <= 100)

    # --- New tests ---

    def test_composite_within_range(self):
        """Composite score must be 0-100"""
        text = "那年我十八岁，第一次离开家。因为要去上大学，所以父母送我到火车站。我感到既兴奋又紧张。后来我在大学认识了很多朋友，那段时光让我成长了很多。"
        result = score_narrative(text)
        self.assertTrue(0 <= result.composite_score <= 100)

    def test_rich_narrative_scores_higher(self):
        """A rich narrative should score higher than a minimal one"""
        minimal = "我去了公园。"
        rich = (
            "1990年的秋天，我第一次去北京。因为工作调动，所以带着全家搬到了首都。"
            "我记得那天阳光很好，我们坐了一天一夜的火车。到了北京站，看到那么多人，"
            "我感到既兴奋又害怕。后来慢慢适应了，那段经历让我变得更加独立和坚强。"
            "回想起来，那是我人生中最重要的转折点。"
        )
        score_minimal = score_narrative(minimal)
        score_rich = score_narrative(rich)
        self.assertGreater(score_rich.composite_score, score_minimal.composite_score)

    def test_score_to_dict(self):
        """NarrativeScore.to_dict() should return a valid dict"""
        text = "我记得那天下雨了，我和朋友在家里聊天。"
        result = score_narrative(text)
        d = result.to_dict()
        self.assertIsInstance(d, dict)
        self.assertIn("composite_score", d)
        self.assertIn("letter_grade", d)
        self.assertIn("event_richness", d)


# ============================================================================
# 4. Edge Cases & Boundary Tests (all new — 8 tests)
# ============================================================================

class TestEdgeCases(unittest.TestCase):
    """Edge case and boundary condition tests"""

    def test_single_character(self):
        """Single character input should not crash"""
        result = score_narrative("我")
        self.assertIsInstance(result.composite_score, float)

    def test_whitespace_only(self):
        """Whitespace-only input should return 0"""
        result = score_narrative("   \n\t  ")
        self.assertEqual(result.composite_score, 0.0)

    def test_punctuation_only(self):
        """Punctuation-only input should return 0 or very low score"""
        result = score_narrative("。。。，，，！！")
        self.assertTrue(result.composite_score <= 10.0)

    def test_very_long_text(self):
        """Very long text should not crash and should score reasonably"""
        # ~2000 chars
        base = "那年夏天我和家人去了海边。我们在沙滩上玩耍，捡贝壳，堆沙堡。我感到非常快乐。"
        long_text = base * 25
        result = score_narrative(long_text)
        self.assertIsInstance(result.composite_score, float)
        self.assertTrue(0 <= result.composite_score <= 100)

    def test_mixed_language_chinese_english(self):
        """Mixed Chinese-English text should not crash"""
        text = "我记得那天是 Christmas Eve，2019年。We went to 外婆家，我感到很温暖。"
        result = score_narrative(text)
        self.assertIsInstance(result.composite_score, float)

    def test_numbers_only(self):
        """Pure numeric input should return very low score"""
        result = score_narrative("123456789 2020 3 15")
        self.assertTrue(result.composite_score <= 20.0)

    def test_repeated_sentence(self):
        """Repeated identical sentence should not inflate score unreasonably"""
        single = "我去了公园。"
        repeated = single * 20
        score_single = score_narrative(single)
        score_repeated = score_narrative(repeated)
        # Repeated text shouldn't score dramatically higher
        # (may score somewhat higher due to length, but not 5x)
        self.assertTrue(score_repeated.composite_score < score_single.composite_score * 5)

    def test_none_handling(self):
        """None-like empty string should be handled gracefully"""
        result = score_narrative("")
        self.assertEqual(result.composite_score, 0.0)
        self.assertEqual(result.letter_grade, "F")


# ============================================================================
# 5. Dimension Scoring Functions (all new — 4 tests)
# ============================================================================

class TestDimensionFunctions(unittest.TestCase):
    """Test individual dimension scoring functions"""

    def test_score_event_richness_no_events(self):
        """No events should produce low richness score"""
        score = score_event_richness([], 100)
        self.assertEqual(score, 0.0)

    def test_score_temporal_coherence_basic(self):
        """Temporal coherence with time markers"""
        events = [Event(description="test", event_type="central")]
        score = score_temporal_coherence(events, 3, 100)
        self.assertTrue(0 <= score <= 100)

    def test_score_information_density_mixed(self):
        """Information density with mixed event types"""
        events = [
            Event(description="核心事件", event_type="central"),
            Event(description="边缘事件", event_type="peripheral"),
            Event(description="另一个核心", event_type="central"),
        ]
        score = score_information_density(events)
        self.assertTrue(0 <= score <= 100)

    def test_calculate_composite_score_weights(self):
        """Composite score with default weights should be weighted average"""
        scores = {
            "event_richness": 80.0,
            "temporal_coherence": 70.0,
            "causal_coherence": 60.0,
            "emotional_depth": 90.0,
            "identity_integration": 50.0,
            "information_density": 75.0,
        }
        composite = calculate_composite_score(scores, DEFAULT_WEIGHTS)
        self.assertTrue(50 <= composite <= 90)
        # Should be the weighted average
        expected = sum(scores[k] * DEFAULT_WEIGHTS[k] for k in scores)
        self.assertAlmostEqual(composite, expected, places=1)


# ============================================================================
# 6. Feedback & Grade Tests (all new — 2 tests)
# ============================================================================

class TestFeedbackAndGrades(unittest.TestCase):
    """Test feedback generation and grade boundaries"""

    def test_grade_boundaries(self):
        """Test exact grade boundaries"""
        self.assertEqual(get_letter_grade(100), "S")
        self.assertEqual(get_letter_grade(90), "S")
        self.assertEqual(get_letter_grade(89), "A")
        self.assertEqual(get_letter_grade(80), "A")
        self.assertEqual(get_letter_grade(79), "B")
        self.assertEqual(get_letter_grade(70), "B")
        self.assertEqual(get_letter_grade(69), "C")
        self.assertEqual(get_letter_grade(60), "C")
        self.assertEqual(get_letter_grade(59), "D")
        self.assertEqual(get_letter_grade(50), "D")
        self.assertEqual(get_letter_grade(49), "F")
        self.assertEqual(get_letter_grade(0), "F")

    def test_feedback_is_nonempty(self):
        """Feedback for any narrative should be non-empty"""
        text = "我记得小时候，爷爷常带我去河边钓鱼。那些日子很美好。"
        result = score_narrative(text)
        self.assertTrue(len(result.feedback) > 0)


if __name__ == "__main__":
    unittest.main()
