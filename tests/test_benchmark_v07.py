#!/usr/bin/env python3
"""
Benchmark Tests for Narrative Scorer v0.7 (Hybrid Rule + LLM)

GEO #71: Initial v0.7 benchmark skeleton
- Compares v0.7 hybrid (rule + LLM) vs v0.6 rule-only
- Tests LLM feature extraction accuracy on implicit emotions, event boundaries, causality
- Requires DASHSCOPE_API_KEY for live testing

Status: Skeleton (V3 — code written, awaiting API key for V4 validation)
"""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scorer import score_narrative

# Try to import LLM feature extractor (may fail if not installed)
try:
    from llm_feature_extractor import LLMFeatureExtractor, LLMConfig
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False


# ============================================================================
# Test Samples for v0.7 LLM Enhancement
# ============================================================================

V07_BENCHMARK_SAMPLES = [
    {
        "id": "v07-001",
        "label": "Implicit emotion (no explicit emotion words)",
        "text": (
            "那天我站在车站，看着火车慢慢开走。"
            "手里的信封已经被汗水浸湿了。"
            "站台上的广播声越来越远，我转身离开了。"
        ),
        "expected_implicit_emotions": [
            {"emotion": "sadness", "confidence": 0.7},
            {"emotion": "nostalgia", "confidence": 0.6},
        ],
        "rule_only_emotion_count": 0,  # No explicit emotion words
        "llm_expected_emotion_count": 2,  # LLM should detect implicit emotions
    },
    {
        "id": "v07-002",
        "label": "Implicit causality (no causal markers)",
        "text": (
            "他连续三天没有接电话。"
            "我决定不再等他了。"
        ),
        "expected_implicit_causality": [
            {"cause": "他连续三天没有接电话", "effect": "我决定不再等他了", "strength": "moderate"},
        ],
        "rule_only_causal_count": 0,  # No causal markers like 因为/所以
        "llm_expected_causal_count": 1,  # LLM should infer causality
    },
    {
        "id": "v07-003",
        "label": "Event boundary (semantic transition)",
        "text": (
            "小时候我最喜欢去外婆家。"
            "外婆会给我做各种好吃的，有红烧肉、清蒸鱼。"
            "后来我上大学了，离家越来越远。"
            "工作以后，每年只能回去一两次。"
            "外婆走的那年，我没能赶回去见她最后一面。"
        ),
        "expected_events": 3,  # Childhood visits → University/adulthood → Grandmother's passing
        "rule_only_expected_events": 4,  # May over-segment by sentence
        "llm_expected_events": 3,  # LLM should group by semantic events
    },
    {
        "id": "v07-004",
        "label": "Mixed explicit and implicit emotions",
        "text": (
            "得知被录取的那一刻，我高兴得跳了起来。"
            "但随即又有些担心，不知道能不能适应新环境。"
            "晚上躺在床上，脑海里反复想着未来的日子。"
        ),
        "expected_explicit_emotions": ["高兴"],
        "expected_implicit_emotions": [
            {"emotion": "anxiety", "confidence": 0.7},
            {"emotion": "uncertainty", "confidence": 0.6},
        ],
        "rule_only_emotion_count": 1,  # Only 高兴 detected
        "llm_expected_emotion_count": 3,  # 高兴 + anxiety + uncertainty
    },
    {
        "id": "v07-005",
        "label": "Complex causal chain",
        "text": (
            "公司效益不好，开始裁员。"
            "我所在的部门被整个裁掉了。"
            "失业后的三个月，我每天都在投简历。"
            "终于找到新工作时，工资只有原来的一半。"
            "那段时间我经常失眠，觉得自己很失败。"
        ),
        "expected_causal_chain": [
            {"cause": "公司效益不好", "effect": "开始裁员"},
            {"cause": "部门被裁掉", "effect": "失业"},
            {"cause": "失业", "effect": "每天投简历"},
            {"cause": "找到新工作", "effect": "工资减半"},
            {"cause": "工资减半 + 失业压力", "effect": "失眠 + 觉得自己失败"},
        ],
        "rule_only_causal_count": 0,  # No explicit causal markers
        "llm_expected_causal_count": 5,  # LLM should infer full causal chain
    },
]


# ============================================================================
# Test Cases
# ============================================================================

@unittest.skipUnless(LLM_AVAILABLE, "LLM feature extractor not available")
class TestV07HybridVsRuleOnly(unittest.TestCase):
    """Compare v0.7 hybrid (rule + LLM) vs v0.6 rule-only"""

    def setUp(self):
        """Initialize LLM feature extractor"""
        # Check for API key
        self.api_key = os.getenv('DASHSCOPE_API_KEY')
        if not self.api_key:
            self.skipTest("DASHSCOPE_API_KEY not set — skipping live LLM tests")
        
        self.extractor = LLMFeatureExtractor()

    def test_implicit_emotion_detection(self):
        """v07-001: LLM should detect implicit emotions where rule-based fails"""
        sample = next(s for s in V07_BENCHMARK_SAMPLES if s["id"] == "v07-001")
        
        # Rule-only baseline
        rule_result = score_narrative(sample["text"], return_features=True)
        rule_emotion_count = rule_result['emotion_words_count']
        
        # LLM enhancement
        llm_features = self.extractor.extract(sample["text"])
        llm_emotion_count = len(llm_features.emotions)
        
        # Assertions
        self.assertEqual(rule_emotion_count, sample["rule_only_emotion_count"],
            f"Rule-only emotion count mismatch: {rule_emotion_count} != {sample['rule_only_emotion_count']}")
        
        self.assertGreaterEqual(llm_emotion_count, sample["llm_expected_emotion_count"],
            f"LLM should detect at least {sample['llm_expected_emotion_count']} emotions, got {llm_emotion_count}")
        
        print(f"\n✓ v07-001: Rule={rule_emotion_count}, LLM={llm_emotion_count} emotions")

    def test_implicit_causality_detection(self):
        """v07-002: LLM should infer causality without explicit markers"""
        sample = next(s for s in V07_BENCHMARK_SAMPLES if s["id"] == "v07-002")
        
        # Rule-only baseline
        rule_result = score_narrative(sample["text"], return_features=True)
        rule_causal_count = rule_result['causal_markers_count']
        
        # LLM enhancement
        llm_features = self.extractor.extract(sample["text"])
        llm_causal_count = len(llm_features.causal_relations)
        
        # Assertions
        self.assertEqual(rule_causal_count, sample["rule_only_causal_count"],
            f"Rule-only causal count mismatch: {rule_causal_count} != {sample['rule_only_causal_count']}")
        
        self.assertGreaterEqual(llm_causal_count, sample["llm_expected_causal_count"],
            f"LLM should detect at least {sample['llm_expected_causal_count']} causal relations, got {llm_causal_count}")
        
        print(f"\n✓ v07-002: Rule={rule_causal_count}, LLM={llm_causal_count} causal relations")

    def test_event_segmentation_accuracy(self):
        """v07-003: LLM should segment by semantic events, not just sentences"""
        sample = next(s for s in V07_BENCHMARK_SAMPLES if s["id"] == "v07-003")
        
        # LLM event segmentation
        llm_features = self.extractor.extract(sample["text"])
        llm_event_count = len(llm_features.events)
        
        # Assertions
        self.assertEqual(llm_event_count, sample["llm_expected_events"],
            f"LLM should detect {sample['llm_expected_events']} events, got {llm_event_count}")
        
        print(f"\n✓ v07-003: LLM detected {llm_event_count} semantic events")

    def test_mixed_emotion_detection(self):
        """v07-004: LLM should detect both explicit and implicit emotions"""
        sample = next(s for s in V07_BENCHMARK_SAMPLES if s["id"] == "v07-004")
        
        # Rule-only baseline
        rule_result = score_narrative(sample["text"], return_features=True)
        rule_emotion_count = rule_result['emotion_words_count']
        
        # LLM enhancement
        llm_features = self.extractor.extract(sample["text"])
        llm_emotion_count = len(llm_features.emotions)
        
        # Assertions
        self.assertEqual(rule_emotion_count, sample["rule_only_emotion_count"],
            f"Rule-only emotion count mismatch: {rule_emotion_count} != {sample['rule_only_emotion_count']}")
        
        self.assertGreaterEqual(llm_emotion_count, sample["llm_expected_emotion_count"],
            f"LLM should detect at least {sample['llm_expected_emotion_count']} emotions, got {llm_emotion_count}")
        
        print(f"\n✓ v07-004: Rule={rule_emotion_count}, LLM={llm_emotion_count} emotions")

    def test_causal_chain_extraction(self):
        """v07-005: LLM should extract complex causal chains"""
        sample = next(s for s in V07_BENCHMARK_SAMPLES if s["id"] == "v07-005")
        
        # Rule-only baseline
        rule_result = score_narrative(sample["text"], return_features=True)
        rule_causal_count = rule_result['causal_markers_count']
        
        # LLM enhancement
        llm_features = self.extractor.extract(sample["text"])
        llm_causal_count = len(llm_features.causal_relations)
        
        # Assertions
        self.assertEqual(rule_causal_count, sample["rule_only_causal_count"],
            f"Rule-only causal count mismatch: {rule_causal_count} != {sample['rule_only_causal_count']}")
        
        self.assertGreaterEqual(llm_causal_count, sample["llm_expected_causal_count"],
            f"LLM should detect at least {sample['llm_expected_causal_count']} causal relations, got {llm_causal_count}")
        
        print(f"\n✓ v07-005: Rule={rule_causal_count}, LLM={llm_causal_count} causal relations")


class TestV07FallbackBehavior(unittest.TestCase):
    """Test graceful degradation when LLM API fails"""

    def setUp(self):
        """Set up extractor with fallback enabled"""
        config = LLMConfig(
            fallback_to_rule_only=True,
            timeout=1,  # Short timeout for testing
            max_retries=1,
        )
        self.extractor = LLMFeatureExtractor(config)

    @patch('llm_feature_extractor.Generation')
    def test_fallback_on_api_failure(self, mock_generation):
        """When LLM API fails, should fall back to rule-only mode"""
        # Simulate API failure
        mock_generation.call.side_effect = Exception("API timeout")
        
        text = "今天天气很好，我去公园散步了。"
        
        # Should not raise exception
        result = self.extractor.extract(text)
        
        # Should have used fallback
        self.assertTrue(result.used_fallback, "Should use fallback on API failure")
        
        # Should still return valid features (rule-only)
        self.assertIsNotNone(result.to_dict())
        
        print(f"\n✓ Fallback test: used_fallback={result.used_fallback}")

    def test_extract_with_fallback_graceful_degradation(self):
        """extract_with_fallback() should work even without LLM"""
        text = "我记得小时候的事。"
        
        # Get rule-based features first
        rule_features = score_narrative(text, return_features=True)
        
        # LLM enhancement with fallback (will use rule-only if API unavailable)
        enhanced = self.extractor.extract_with_fallback(text, rule_features)
        
        # Should return valid features
        self.assertIsNotNone(enhanced.to_dict())
        
        print(f"\n✓ extract_with_fallback: graceful degradation works")


class TestV07CostTracking(unittest.TestCase):
    """Test cost estimation for LLM API calls"""

    def test_cost_estimation_per_narrative(self):
        """Estimate cost per narrative (based on v0.7 integration guide)"""
        # From v0.7-llm-integration-guide.md:
        # - Average input: ~200 tokens
        # - Average output: ~100 tokens
        # - qwen-plus: ¥0.0028 / 1K tokens (input + output)
        # - Cost per narrative: (200 + 100) / 1000 * 0.0028 = ¥0.00084
        
        estimated_cost_per_narrative = 0.00084  # ¥
        
        # Pilot RCT (150 narratives)
        pilot_cost = 150 * estimated_cost_per_narrative
        self.assertAlmostEqual(pilot_cost, 0.126, places=2)
        
        # Large-scale study (1500 narratives)
        large_cost = 1500 * estimated_cost_per_narrative
        self.assertAlmostEqual(large_cost, 1.26, places=2)
        
        print(f"\n✓ Cost estimation: ¥{estimated_cost_per_narrative:.4f}/narrative")
        print(f"  Pilot RCT (150): ¥{pilot_cost:.2f}")
        print(f"  Large-scale (1500): ¥{large_cost:.2f}")


# ============================================================================
# Integration Test (Manual Run)
# ============================================================================

def manual_integration_test():
    """
    Manual integration test for v0.7 hybrid scoring.
    Run this only when DASHSCOPE_API_KEY is available.
    
    Usage:
        python -c "from tests.test_benchmark_v07 import manual_integration_test; manual_integration_test()"
    """
    if not os.getenv('DASHSCOPE_API_KEY'):
        print("❌ DASHSCOPE_API_KEY not set. Set it and retry.")
        return
    
    print("=" * 60)
    print("V0.7 Hybrid Scoring Integration Test")
    print("=" * 60)
    
    extractor = LLMFeatureExtractor()
    
    sample_text = (
        "那年冬天，我收到了大学的录取通知书。"
        "全家人都为我高兴，妈妈特意做了一桌好菜。"
        "但夜深人静时，我却有些迷茫："
        "真的要离开家乡，去一个完全陌生的城市吗？"
    )
    
    print(f"\nInput text: {sample_text[:50]}...\n")
    
    # Rule-only baseline
    rule_result = score_narrative(sample_text, return_features=True)
    print(f"Rule-only scores:")
    print(f"  Emotion words: {rule_result['emotion_words_count']}")
    print(f"  Causal markers: {rule_result['causal_markers_count']}")
    print(f"  Events: {rule_result['total_events']}")
    print(f"  Composite: {rule_result['composite_score']:.1f}\n")
    
    # LLM enhancement
    llm_features = extractor.extract(sample_text)
    print(f"LLM-enhanced features:")
    print(f"  Emotions detected: {len(llm_features.emotions)}")
    print(f"  Events segmented: {len(llm_features.events)}")
    print(f"  Causal relations: {len(llm_features.causal_relations)}")
    print(f"  Used fallback: {llm_features.used_fallback}")
    print(f"  API latency: {llm_features.api_latency_ms:.0f}ms")
    if llm_features.cost_cny:
        print(f"  API cost: ¥{llm_features.cost_cny:.4f}")
    
    print("\n" + "=" * 60)
    print("Integration test complete!")
    print("=" * 60)


if __name__ == "__main__":
    # Check if running manual test
    if len(sys.argv) > 1 and sys.argv[1] == "--manual":
        manual_integration_test()
    else:
        # Run unit tests
        unittest.main(verbosity=2)
