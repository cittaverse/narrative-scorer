#!/usr/bin/env python3
"""
Unit tests for Narrative Scorer v0.6
Expanded from 46 → 60 test cases (GEO #62)
Covers: marker counting, event extraction (v0.5 + v0.6), scoring dimensions,
        edge cases, boundary conditions, mixed-language inputs, negation detection,
        topic-transition event boundary detection
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
    extract_events,
    get_letter_grade,
    score_event_richness,
    score_temporal_coherence,
    score_causal_coherence,
    score_emotional_depth,
    score_identity_integration,
    score_information_density,
    calculate_composite_score,
    generate_feedback,
    _classify_event_type,
    _extract_time_marker,
    _extract_people,
    NarrativeScore,
    Event,
    DEFAULT_WEIGHTS,
    TOPIC_TRANSITION_MARKERS,
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


# ============================================================================
# Negation Detection Tests (v0.5.1)
# ============================================================================

class TestNegationDetection(unittest.TestCase):
    """Tests for negation-aware counting (v0.5.1)"""
    
    def test_negated_emotion_detected(self):
        """'不开心' should detect negation on '开心'"""
        from scorer import _is_negated
        text = "我那天不开心"
        pos = text.index("开心")
        self.assertTrue(_is_negated(text, pos, "开心"))
    
    def test_non_negated_emotion(self):
        """'很开心' should NOT be negated"""
        from scorer import _is_negated
        text = "我那天很开心"
        pos = text.index("开心")
        self.assertFalse(_is_negated(text, pos, "开心"))
    
    def test_negated_emotion_count_with_negation(self):
        """count_with_negation should separate negated vs non-negated"""
        from scorer import count_with_negation, EMOTION_WORDS
        text = "我很开心，但她不开心"
        positive, negated = count_with_negation(text, ["开心"])
        self.assertEqual(positive, 1)
        self.assertEqual(negated, 1)
    
    def test_negated_causal_discounted(self):
        """Negated causal markers should be discounted in count"""
        text = "没有因为下雨就取消"
        count = count_causal_markers(text)
        # "因为" is negated by "没有", should count at 50% → 0 (floor)
        self.assertEqual(count, 0)
    
    def test_non_negated_causal_full_count(self):
        """Non-negated causal markers should count fully"""
        text = "因为下雨所以取消了"
        count = count_causal_markers(text)
        self.assertEqual(count, 2)  # "因为" + "所以"
    
    def test_multiple_negation_prefixes(self):
        """Various negation prefixes should all be detected"""
        from scorer import _is_negated
        test_cases = [
            ("并不开心", "开心", True),
            ("从不害怕", "害怕", True),
            ("未感到悲伤", "悲伤", True),
            ("非常开心", "开心", False),  # "非常" is not negation
        ]
        for text, word, expected in test_cases:
            pos = text.index(word)
            result = _is_negated(text, pos, word)
            self.assertEqual(result, expected, 
                           f"Failed for '{text}': expected negated={expected}, got {result}")
    
    def test_emotion_count_includes_negated(self):
        """Emotion count should include negated emotions (they still show emotional depth)"""
        text = "我不开心，也不快乐，但很感激"
        count = count_emotion_words(text)
        # "开心"(negated) + "快乐"(negated) + "感激"(non-negated) = 3
        self.assertEqual(count, 3)
    
    def test_negation_tracking_in_score(self):
        """NarrativeScore should track negation counts"""
        text = "我不开心，因为那天很难过。没有因为别的原因。"
        result = score_narrative(text)
        self.assertIsInstance(result.negated_emotion_count, int)
        self.assertIsInstance(result.negated_causal_count, int)
        self.assertGreaterEqual(result.negated_emotion_count, 0)
    
    def test_negation_window_respected(self):
        """Negation too far from word should not count"""
        from scorer import _is_negated
        # "不" is 10+ chars away from "开心" — beyond window
        text = "不是那样的，我后来很开心"
        pos = text.index("开心")
        self.assertFalse(_is_negated(text, pos, "开心"))
    
    def test_double_negation(self):
        """'不是不开心' — double negation edge case"""
        from scorer import _is_negated
        text = "不是不开心"
        pos = text.index("开心")
        # The closest negation to "开心" is "不" (at pos 2), so it IS negated
        # Double negation semantics are beyond MVP scope
        self.assertTrue(_is_negated(text, pos, "开心"))


# ============================================================================
# 7. Event Boundary Detection v0.6 Tests (14 new tests)
# ============================================================================

class TestEventBoundaryV06(unittest.TestCase):
    """Tests for v0.6 topic-transition-aware event boundary detection"""

    def test_extract_events_basic(self):
        """Basic event extraction should produce events"""
        text = "我记得那是一个春天。我和奶奶去公园。我们很开心。"
        events = extract_events(text)
        self.assertGreater(len(events), 0)

    def test_topic_transition_splits(self):
        """Topic transition markers should create new event boundaries"""
        text = "我在学校读书。后来我去了北京工作。"
        events = extract_events(text)
        # Should produce at least 2 events (split by "后来")
        self.assertGreaterEqual(len(events), 2)

    def test_transition_marker_butshi(self):
        """'但是' should act as event boundary"""
        text = "那天天气很好。但是我的心情并不好，因为奶奶生病了。"
        events = extract_events(text)
        self.assertGreaterEqual(len(events), 2)

    def test_multi_transition_narrative(self):
        """Narrative with multiple transition markers should have more events"""
        text = (
            "1985年我在杭州出生。后来我去了北京上大学。"
            "之后我回到了杭州工作。不过最难忘的是大学那段时光。"
        )
        events = extract_events(text)
        self.assertGreaterEqual(len(events), 3)

    def test_short_clause_merging(self):
        """Very short clauses should be merged with neighbors"""
        text = "我去了。然后回来了。"
        events = extract_events(text)
        # "我去了" (5 chars) and "然后回来了" — short clauses may merge
        # Either way, we should get at least 1 event
        self.assertGreaterEqual(len(events), 1)

    def test_enhanced_classification_central(self):
        """Events with places and people should be classified as central"""
        clause = "我和妈妈一起去了医院检查"
        event_type = _classify_event_type(clause)
        self.assertEqual(event_type, "central")

    def test_enhanced_classification_peripheral(self):
        """Reflective statements should be classified as peripheral"""
        clause = "我觉得那段时光很美好，也许是我最快乐的日子"
        event_type = _classify_event_type(clause)
        self.assertEqual(event_type, "peripheral")

    def test_people_extraction(self):
        """People markers should be extracted from clauses"""
        clause = "爸爸和妈妈带我去了公园"
        people = _extract_people(clause)
        self.assertIn("爸爸", people)
        self.assertIn("妈妈", people)

    def test_time_marker_extraction(self):
        """Time markers should be correctly extracted"""
        clause = "后来我们搬到了新的城市"
        marker = _extract_time_marker(clause)
        self.assertEqual(marker, "后来")

    def test_v06_more_events_than_v05(self):
        """v0.6 should extract equal or more events than v0.5 for complex narratives"""
        text = (
            "1990年的秋天，我第一次去北京。因为工作调动，所以带着全家搬到了首都。"
            "后来慢慢适应了。不过最开始的日子很难。另外，北京的冬天特别冷。"
            "但是同事们都很热情，帮了我很多。"
        )
        events_v05 = extract_events_simple(text)
        events_v06 = extract_events(text)
        self.assertGreaterEqual(len(events_v06), len(events_v05))

    def test_empty_text_v06(self):
        """Empty text should return empty events list"""
        self.assertEqual(extract_events(""), [])
        self.assertEqual(extract_events("   "), [])

    def test_event_descriptions_nonempty_v06(self):
        """All v0.6 events should have non-empty descriptions"""
        text = "那年夏天我和家人去了海边。后来我们搬到了新家。不过我很怀念那段日子。"
        events = extract_events(text)
        for event in events:
            self.assertTrue(len(event.description.strip()) > 0)

    def test_legacy_mode_flag(self):
        """use_legacy_events=True should use v0.5 extraction"""
        text = "我记得那天阳光明媚。后来下起了雨。但是我们还是很开心。"
        result_v06 = score_narrative(text, use_legacy_events=False)
        result_v05 = score_narrative(text, use_legacy_events=True)
        # Both should produce valid scores (may differ)
        self.assertTrue(0 <= result_v06.composite_score <= 100)
        self.assertTrue(0 <= result_v05.composite_score <= 100)

    def test_punctuation_only_no_events_v06(self):
        """Punctuation-only input should produce no events"""
        events = extract_events("。。。，，，！！")
        self.assertEqual(len(events), 0)


if __name__ == "__main__":
    unittest.main()
