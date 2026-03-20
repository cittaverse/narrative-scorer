#!/usr/bin/env python3
"""
Unit tests for Narrative Scorer v0.5
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
    get_letter_grade
)


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


class TestEventExtraction(unittest.TestCase):
    """Test event extraction"""
    
    def test_extract_events(self):
        text = "我记得那是一个春天。我和奶奶去公园。我们很开心。"
        events = extract_events_simple(text)
        self.assertGreater(len(events), 0)
    
    def test_event_classification(self):
        text = "那天是 2020 年 3 月 15 日。我觉得很感动。"
        events = extract_events_simple(text)
        # First sentence should be central (has specific date)
        # Second should be peripheral (reflection)
        self.assertGreater(len(events), 0)


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
        
        # All dimensions should be between 0 and 100
        self.assertTrue(0 <= result.event_richness <= 100)
        self.assertTrue(0 <= result.temporal_coherence <= 100)
        self.assertTrue(0 <= result.causal_coherence <= 100)
        self.assertTrue(0 <= result.emotional_depth <= 100)
        self.assertTrue(0 <= result.identity_integration <= 100)
        self.assertTrue(0 <= result.information_density <= 100)


class TestCentralPeripheralRatio(unittest.TestCase):
    """Test information density scoring"""
    
    def test_optimal_ratio(self):
        # Create text with roughly 60% central events
        text = """
        2020 年 3 月 15 日，我去了北京。
        那天温度 25 度。
        我和 3 个朋友一起。
        我觉得很开心。
        也许下次还会去。
        """
        result = score_narrative(text)
        # Should score well on information density
        self.assertGreater(result.information_density, 50)


if __name__ == '__main__':
    unittest.main()
