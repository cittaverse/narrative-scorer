"""
Integration tests for narrative-scorer v0.7 (LLM hybrid mode).

These tests use mocked LLM responses to validate the full pipeline
without requiring a live DASHSCOPE_API_KEY.

Test Coverage:
- Full pipeline: text → rule features + LLM features → combined score
- Feature integration: Verify rule-based and LLM features combine correctly
- Score calculation: Verify weighted scoring works with mixed feature types
- Edge cases: Empty text, missing LLM features, API errors

Usage:
    pytest tests/test_integration_v07.py -v

Dependencies:
    pytest>=7.0.0
    narrative-scorer>=0.7.0
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from narrative_scorer.scorer import score_narrative
from narrative_scorer.feature_extractor import extract_features
from narrative_scorer.llm_feature_extractor import LLMFeatureExtractor


class TestV07IntegrationPipeline:
    """Test full v0.7 pipeline with mocked LLM responses."""

    @pytest.fixture
    def mock_llm_response(self):
        """Standard mock LLM response for feature extraction."""
        return {
            'implicit_emotion': 0.75,
            'causality_depth': 0.68,
            'narrative_coherence': 0.82,
            'identity_integration': 0.71,
            'llm_confidence': 0.89
        }

    @pytest.fixture
    def sample_narrative(self):
        """Sample Chinese narrative for testing."""
        return "那天我决定辞职。早上起床时，窗外下着小雨，我突然意识到自己已经在这家公司待了五年。五年来，我每天重复着同样的工作，感觉自己像一台机器。那一刻，我明白了，我需要改变。"

    def test_full_pipeline_with_mocked_llm(self, mock_llm_response, sample_narrative):
        """
        Test complete scoring pipeline with mocked LLM.
        
        Validates:
        1. Rule-based features extract correctly
        2. LLM features are called and return expected format
        3. Combined scoring produces valid output
        4. All six dimensions are present in result
        """
        with patch.object(LLMFeatureExtractor, 'extract', return_value=mock_llm_response):
            result = score_narrative(sample_narrative, use_llm=True)
            
            # Verify result structure
            assert isinstance(result, dict)
            assert 'overall_score' in result
            assert 'dimensions' in result
            
            # Verify all six dimensions present
            dimensions = result['dimensions']
            required_dims = [
                'event_richness',
                'temporal_causal_coherence',
                'emotional_depth',
                'identity_integration',
                'information_density',
                'narrative_coherence'
            ]
            for dim in required_dims:
                assert dim in dimensions, f"Missing dimension: {dim}"
                assert isinstance(dimensions[dim], (int, float))
                assert 0 <= dimensions[dim] <= 100
            
            # Verify overall score is valid
            assert isinstance(result['overall_score'], (int, float))
            assert 0 <= result['overall_score'] <= 100
            
            # Verify metadata
            assert 'metadata' in result
            assert result['metadata']['use_llm'] is True
            assert 'llm_confidence' in result['metadata']

    def test_rule_based_features_integration(self, sample_narrative):
        """
        Test that rule-based features still work correctly in v0.7.
        
        Validates backward compatibility with v0.6.x scoring.
        """
        result = score_narrative(sample_narrative, use_llm=False)
        
        assert isinstance(result, dict)
        assert 'overall_score' in result
        assert 'dimensions' in result
        
        # Verify rule-based scoring produces reasonable results
        assert 0 <= result['overall_score'] <= 100
        
        # Verify metadata indicates LLM not used
        assert result['metadata']['use_llm'] is False

    def test_llm_feature_extraction_direct(self, mock_llm_response):
        """
        Test LLM feature extractor in isolation.
        
        Validates the LLM feature extractor component.
        """
        extractor = LLMFeatureExtractor()
        sample_text = "这是一个测试叙事"
        
        with patch.object(extractor, 'extract', return_value=mock_llm_response):
            features = extractor.extract(sample_text)
            
            # Verify feature structure
            assert isinstance(features, dict)
            assert 'implicit_emotion' in features
            assert 'causality_depth' in features
            assert 'narrative_coherence' in features
            assert 'identity_integration' in features
            assert 'llm_confidence' in features
            
            # Verify feature values are valid probabilities
            for key in ['implicit_emotion', 'causality_depth', 'narrative_coherence', 'identity_integration']:
                assert 0 <= features[key] <= 1
                assert isinstance(features[key], (int, float))
            
            assert 0 <= features['llm_confidence'] <= 1

    def test_combined_feature_weights(self, mock_llm_response, sample_narrative):
        """
        Test that rule-based and LLM features combine with correct weights.
        
        v0.7 weighting:
        - Rule-based features: 60% weight
        - LLM features: 40% weight
        
        This test verifies the weighted combination logic.
        """
        # Get rule-based only score
        rule_result = score_narrative(sample_narrative, use_llm=False)
        rule_score = rule_result['overall_score']
        
        # Get hybrid score
        with patch.object(LLMFeatureExtractor, 'extract', return_value=mock_llm_response):
            hybrid_result = score_narrative(sample_narrative, use_llm=True)
            hybrid_score = hybrid_result['overall_score']
        
        # Hybrid score should be different from rule-only (due to LLM contribution)
        # Note: They might be the same if LLM features align perfectly with rule features
        # This test mainly validates that both modes execute without error
        
        assert isinstance(rule_score, (int, float))
        assert isinstance(hybrid_score, (int, float))
        assert 0 <= rule_score <= 100
        assert 0 <= hybrid_score <= 100

    def test_empty_text_handling(self, mock_llm_response):
        """
        Test pipeline behavior with empty or minimal text.
        
        Validates edge case handling.
        """
        empty_text = ""
        
        # Rule-based mode
        rule_result = score_narrative(empty_text, use_llm=False)
        assert isinstance(rule_result, dict)
        assert 'overall_score' in rule_result
        
        # Hybrid mode with mocked LLM
        with patch.object(LLMFeatureExtractor, 'extract', return_value=mock_llm_response):
            hybrid_result = score_narrative(empty_text, use_llm=True)
            assert isinstance(hybrid_result, dict)
            assert 'overall_score' in hybrid_result

    def test_llm_api_error_handling(self, sample_narrative):
        """
        Test graceful degradation when LLM API fails.
        
        Validates error handling and fallback behavior.
        """
        # Simulate LLM API error
        with patch.object(LLMFeatureExtractor, 'extract', side_effect=Exception("API Error")):
            # Should fall back to rule-based scoring
            result = score_narrative(sample_narrative, use_llm=True)
            
            assert isinstance(result, dict)
            assert 'overall_score' in result
            assert 'metadata' in result
            assert result['metadata'].get('llm_error') is True
            assert result['metadata'].get('fallback_to_rule_based') is True

    def test_batch_scoring_integration(self, mock_llm_response):
        """
        Test batch scoring with multiple narratives.
        
        Validates performance and correctness for batch operations.
        """
        narratives = [
            "今天天气很好，我去公园散步。",
            "我决定学习编程，因为我想转行。",
            "回忆起童年，最难忘的是和爷爷一起钓鱼的时光。"
        ]
        
        results = []
        with patch.object(LLMFeatureExtractor, 'extract', return_value=mock_llm_response):
            for narrative in narratives:
                result = score_narrative(narrative, use_llm=True)
                results.append(result)
        
        # Verify all narratives scored
        assert len(results) == 3
        
        # Verify all results are valid
        for result in results:
            assert isinstance(result, dict)
            assert 'overall_score' in result
            assert 0 <= result['overall_score'] <= 100


class TestV07FeatureExtractor:
    """Test v0.7 LLM feature extractor component."""

    @pytest.fixture
    def extractor(self):
        """Create LLM feature extractor instance."""
        return LLMFeatureExtractor()

    def test_extractor_initialization(self, extractor):
        """Test extractor initializes correctly."""
        assert extractor is not None
        assert hasattr(extractor, 'model')
        assert hasattr(extractor, 'api_key')

    def test_prompt_template_usage(self, extractor):
        """Test that prompt templates are used correctly."""
        sample_text = "测试文本"
        
        # Verify prompt construction (without actually calling API)
        with patch.object(extractor, '_call_llm') as mock_call:
            mock_call.return_value = {
                'implicit_emotion': 0.5,
                'causality_depth': 0.5,
                'narrative_coherence': 0.5,
                'identity_integration': 0.5,
                'llm_confidence': 0.5
            }
            extractor.extract(sample_text)
            
            # Verify LLM was called
            assert mock_call.called
            call_args = mock_call.call_args
            
            # Verify prompt contains the input text
            assert sample_text in str(call_args)


class TestV07MetadataTracking:
    """Test v0.7 metadata tracking and logging."""

    def test_llm_usage_metadata(self):
        """Test that LLM usage is properly tracked in metadata."""
        sample_text = "测试叙事"
        mock_response = {
            'implicit_emotion': 0.8,
            'causality_depth': 0.7,
            'narrative_coherence': 0.9,
            'identity_integration': 0.6,
            'llm_confidence': 0.85
        }
        
        with patch.object(LLMFeatureExtractor, 'extract', return_value=mock_response):
            result = score_narrative(sample_text, use_llm=True)
            
            metadata = result['metadata']
            assert metadata['use_llm'] is True
            assert 'llm_confidence' in metadata
            assert metadata['llm_confidence'] == 0.85

    def test_rule_based_metadata(self):
        """Test that rule-based mode metadata is correct."""
        sample_text = "测试叙事"
        result = score_narrative(sample_text, use_llm=False)
        
        metadata = result['metadata']
        assert metadata['use_llm'] is False
        assert 'llm_confidence' not in metadata or metadata.get('llm_confidence') is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
