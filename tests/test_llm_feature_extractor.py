"""
Unit Tests for LLM Feature Extractor

Tests cover:
1. Configuration loading
2. Prompt template loading
3. JSON parsing
4. Mock API responses
5. Fallback behavior
6. Integration with rule-based scorer

Author: Hulk (CittaVerse)
Version: v0.7.0-alpha
"""

import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from llm_feature_extractor import (
    LLMConfig,
    LLMFeatureExtractor,
    LLMFeatures,
    EmotionFeature,
    EventBoundary,
    CausalRelation,
    extract_llm_features,
)


class TestLLMConfig:
    """Test LLMConfig class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = LLMConfig()
        
        assert config.model == "qwen-plus"
        assert config.timeout == 5
        assert config.max_retries == 2
        assert config.rate_limit_delay == 0.1
        assert config.use_emotion_detection is True
        assert config.use_event_segmentation is True
        assert config.use_causality_detection is True
        assert config.fallback_to_rule_only is True
    
    def test_config_from_dict(self):
        """Test configuration from dictionary."""
        config_dict = {
            'model': 'qwen-turbo',
            'timeout': 10,
            'max_retries': 3,
            'use_emotion_detection': False,
        }
        config = LLMConfig(**config_dict)
        
        assert config.model == "qwen-turbo"
        assert config.timeout == 10
        assert config.max_retries == 3
        assert config.use_emotion_detection is False
    
    def test_config_to_dict(self):
        """Test configuration to dictionary conversion."""
        config = LLMConfig(model='qwen-max', timeout=8)
        config_dict = config.to_dict()
        
        assert config_dict['model'] == 'qwen-max'
        assert config_dict['timeout'] == 8
        assert isinstance(config_dict, dict)
    
    def test_config_from_yaml(self, tmp_path):
        """Test loading configuration from YAML file."""
        yaml_content = """
model: qwen-max
timeout: 10
max_retries: 3
use_emotion_detection: false
use_event_segmentation: true
use_causality_detection: true
"""
        yaml_path = tmp_path / "test_config.yaml"
        yaml_path.write_text(yaml_content)
        
        config = LLMConfig.from_yaml(str(yaml_path))
        
        assert config.model == "qwen-max"
        assert config.timeout == 10
        assert config.max_retries == 3
        assert config.use_emotion_detection is False
    
    def test_config_from_yaml_not_found(self):
        """Test loading non-existent YAML file."""
        with pytest.raises(FileNotFoundError):
            LLMConfig.from_yaml("/nonexistent/path/config.yaml")


class TestLLMFeatures:
    """Test LLMFeatures dataclass."""
    
    def test_default_features(self):
        """Test default LLMFeatures initialization."""
        features = LLMFeatures()
        
        assert features.emotions == []
        assert features.events == []
        assert features.causal_relations == []
        assert features.llm_call_success is False
        assert features.llm_calls_made == 0
        assert features.llm_calls_failed == 0
        assert features.total_cost == 0.0
        assert features.latency_ms == 0.0
        assert features.used_fallback is False
    
    def test_features_to_dict(self):
        """Test LLMFeatures to dictionary conversion."""
        features = LLMFeatures(
            emotions=[
                EmotionFeature(
                    text="很高兴",
                    emotion="joy",
                    emotion_type="explicit",
                    confidence=0.95,
                )
            ],
            events=[],
            causal_relations=[],
            llm_call_success=True,
            llm_calls_made=1,
            llm_calls_failed=0,
            total_cost=0.0028,
            latency_ms=150.5,
        )
        
        result = features.to_dict()
        
        assert 'emotions' in result
        assert 'events' in result
        assert 'causal_relations' in result
        assert 'metadata' in result
        assert len(result['emotions']) == 1
        assert result['emotions'][0]['emotion'] == 'joy'
        assert result['metadata']['llm_call_success'] is True


class TestLLMFeatureExtractor:
    """Test LLMFeatureExtractor class."""
    
    @pytest.fixture
    def extractor(self):
        """Create extractor with mock config."""
        config = LLMConfig(
            api_key='test-key',
            model='qwen-plus',
            timeout=5,
            max_retries=2,
            use_cache=False,
        )
        return LLMFeatureExtractor(config)
    
    def test_extractor_initialization(self, extractor):
        """Test extractor initialization."""
        assert extractor.config is not None
        assert extractor.config.model == 'qwen-plus'
        assert isinstance(extractor.prompt_templates, dict)
    
    def test_prompt_template_loading(self, extractor):
        """Test prompt templates are loaded."""
        assert 'emotion_detection' in extractor.prompt_templates
        assert 'event_segmentation' in extractor.prompt_templates
        assert 'causality_detection' in extractor.prompt_templates
    
    def test_prepare_prompt(self, extractor):
        """Test prompt preparation."""
        input_text = "今天天气很好，我很开心。"
        prompt = extractor._prepare_prompt('emotion_detection', input_text)
        
        assert '{input_text}' not in prompt
        assert input_text in prompt
    
    def test_prepare_prompt_not_found(self, extractor):
        """Test prompt preparation with invalid template key."""
        prompt = extractor._prepare_prompt('nonexistent_template', "test")
        assert prompt == ""
    
    def test_parse_json_response_valid(self, extractor):
        """Test parsing valid JSON response."""
        response = json.dumps({
            'emotions': [
                {'text': '开心', 'emotion': 'joy', 'type': 'explicit', 'confidence': 0.9}
            ],
            'total_explicit': 1,
            'total_implicit': 0,
        })
        
        parsed = extractor._parse_json_response(response)
        
        assert parsed is not None
        assert len(parsed['emotions']) == 1
        assert parsed['total_explicit'] == 1
    
    def test_parse_json_response_with_markdown(self, extractor):
        """Test parsing JSON response with markdown code blocks."""
        response = """```json
{
  "emotions": [],
  "total_explicit": 0,
  "total_implicit": 0
}
```"""
        
        parsed = extractor._parse_json_response(response)
        
        assert parsed is not None
        assert 'emotions' in parsed
    
    def test_parse_json_response_invalid(self, extractor):
        """Test parsing invalid JSON response."""
        response = "This is not JSON"
        parsed = extractor._parse_json_response(response)
        
        assert parsed is None
    
    def test_parse_json_response_empty(self, extractor):
        """Test parsing empty response."""
        parsed = extractor._parse_json_response("")
        assert parsed is None
    
    @patch('llm_feature_extractor.Generation')
    def test_call_llm_success(self, mock_generation, extractor):
        """Test successful LLM API call."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.output.text = '{"result": "success"}'
        mock_generation.call.return_value = mock_response
        
        result = extractor._call_llm("test prompt")
        
        assert result == '{"result": "success"}'
        mock_generation.call.assert_called_once()
    
    @patch('llm_feature_extractor.Generation')
    def test_call_llm_api_error(self, mock_generation, extractor):
        """Test LLM API error handling."""
        mock_generation.call.side_effect = Exception("API Error")
        
        result = extractor._call_llm("test prompt")
        
        assert result is None
    
    @patch('llm_feature_extractor.Generation')
    def test_call_llm_status_error(self, mock_generation, extractor):
        """Test LLM API non-200 status code."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_generation.call.return_value = mock_response
        
        result = extractor._call_llm("test prompt")
        
        assert result is None
    
    @patch('llm_feature_extractor.Generation')
    def test_call_llm_no_api_key(self, extractor):
        """Test LLM call without API key."""
        extractor.config.api_key = None
        
        result = extractor._call_llm("test prompt")
        
        assert result is None
    
    @patch('llm_feature_extractor.DASHSCOPE_AVAILABLE', False)
    def test_call_llm_dashscope_not_available(self, extractor):
        """Test LLM call when DashScope is not available."""
        result = extractor._call_llm("test prompt")
        assert result is None
    
    @patch.object(LLMFeatureExtractor, '_call_llm')
    def test_extract_emotions(self, mock_call_llm, extractor):
        """Test emotion extraction."""
        mock_response = json.dumps({
            'emotions': [
                {'text': '开心', 'emotion': 'joy', 'type': 'explicit', 'confidence': 0.9}
            ],
            'total_explicit': 1,
            'total_implicit': 0,
            'emotional_density': 2.5,
        })
        mock_call_llm.return_value = mock_response
        
        emotions = extractor.extract_emotions("今天我很开心。")
        
        assert len(emotions) == 1
        assert emotions[0].emotion == 'joy'
        assert emotions[0].emotion_type == 'explicit'
        assert emotions[0].confidence == 0.9
    
    @patch.object(LLMFeatureExtractor, '_call_llm')
    def test_extract_emotions_disabled(self, extractor):
        """Test emotion extraction when disabled."""
        extractor.config.use_emotion_detection = False
        
        emotions = extractor.extract_emotions("今天我很开心。")
        
        assert emotions == []
    
    @patch.object(LLMFeatureExtractor, '_call_llm')
    def test_extract_events(self, mock_call_llm, extractor):
        """Test event segmentation extraction."""
        mock_response = json.dumps({
            'events': [
                {
                    'event_id': 1,
                    'start_char': 0,
                    'end_char': 10,
                    'text': '早上起床后',
                    'summary': '起床',
                    'boundary_before': {
                        'char_position': 0,
                        'cue_type': 'none',
                        'confidence': 1.0,
                    }
                }
            ],
            'total_events': 1,
            'avg_event_length': 10.0,
        })
        mock_call_llm.return_value = mock_response
        
        events = extractor.extract_events("早上起床后，我去买早餐。")
        
        assert len(events) == 1
        assert events[0].event_id == 1
        assert events[0].text == '早上起床后'
        assert events[0].summary == '起床'
    
    @patch.object(LLMFeatureExtractor, '_call_llm')
    def test_extract_causal_relations(self, mock_call_llm, extractor):
        """Test causal relation extraction."""
        mock_response = json.dumps({
            'causal_relations': [
                {
                    'relation_id': 1,
                    'cause': {'text': '因为下雨', 'start_char': 0, 'end_char': 4},
                    'effect': {'text': '所以没出门', 'start_char': 6, 'end_char': 11},
                    'type': 'explicit',
                    'strength': 'strong',
                    'cue_type': 'lexical',
                    'cue_text': '因为...所以...',
                    'confidence': 0.95,
                }
            ],
            'total_explicit': 1,
            'total_implicit': 0,
            'causal_density': 2.0,
        })
        mock_call_llm.return_value = mock_response
        
        relations = extractor.extract_causal_relations("因为下雨，所以没出门。")
        
        assert len(relations) == 1
        assert relations[0].relation_type == 'explicit'
        assert relations[0].strength == 'strong'
        assert relations[0].cue_text == '因为...所以...'
    
    @patch.object(LLMFeatureExtractor, 'extract_emotions')
    @patch.object(LLMFeatureExtractor, 'extract_events')
    @patch.object(LLMFeatureExtractor, 'extract_causal_relations')
    def test_extract_all_features(
        self, mock_causal, mock_events, mock_emotions, extractor
    ):
        """Test extracting all features at once."""
        mock_emotions.return_value = [
            EmotionFeature('开心', 'joy', 'explicit', 0.9)
        ]
        mock_events.return_value = [
            EventBoundary(1, 0, 10, '早上起床后', '起床', {})
        ]
        mock_causal.return_value = []
        
        features = extractor.extract("早上起床后，我很开心。")
        
        assert features.llm_calls_made == 3
        assert features.llm_calls_failed == 0
        assert features.llm_call_success is True
        assert len(features.emotions) == 1
        assert len(features.events) == 1
        assert len(features.causal_relations) == 0
    
    @patch.object(LLMFeatureExtractor, 'extract_emotions')
    @patch.object(LLMFeatureExtractor, 'extract_events')
    @patch.object(LLMFeatureExtractor, 'extract_causal_relations')
    def test_extract_with_failures(
        self, mock_causal, mock_events, mock_emotions, extractor
    ):
        """Test extraction with some failures."""
        mock_emotions.side_effect = Exception("API Error")
        mock_events.return_value = []
        mock_causal.return_value = []
        
        features = extractor.extract("test text")
        
        assert features.llm_calls_made == 3
        assert features.llm_calls_failed == 1
        assert features.llm_call_success is False
        assert features.used_fallback is True
    
    @patch.object(LLMFeatureExtractor, 'extract')
    def test_extract_with_fallback_success(self, mock_extract, extractor):
        """Test extract_with_fallback when LLM succeeds."""
        from llm_feature_extractor import LLMFeatures, EmotionFeature
        
        mock_extract.return_value = LLMFeatures(
            emotions=[EmotionFeature('开心', 'joy', 'explicit', 0.9)],
            llm_call_success=True,
            used_fallback=False,
        )
        
        rule_features = {'emotion_count': 2, 'causal_count': 1}
        enhanced = extractor.extract_with_fallback("test", rule_features)
        
        assert enhanced['emotion_count'] > 2  # Enhanced with LLM
        assert 'llm_metadata' in enhanced
    
    @patch.object(LLMFeatureExtractor, 'extract')
    def test_extract_with_fallback_failure(self, mock_extract, extractor):
        """Test extract_with_fallback when LLM fails."""
        from llm_feature_extractor import LLMFeatures
        
        mock_extract.return_value = LLMFeatures(
            emotions=[],
            llm_call_success=False,
            used_fallback=True,
        )
        
        rule_features = {'emotion_count': 2, 'causal_count': 1}
        enhanced = extractor.extract_with_fallback("test", rule_features)
        
        assert enhanced['emotion_count'] == 2  # Unchanged (rule-only)
        assert enhanced == rule_features  # No LLM enhancement


class TestExtractLLMFeatures:
    """Test convenience function."""
    
    @patch('llm_feature_extractor.LLMFeatureExtractor')
    def test_extract_llm_features(self, mock_extractor_class):
        """Test extract_llm_features convenience function."""
        from llm_feature_extractor import LLMFeatures
        
        mock_extractor = MagicMock()
        mock_extractor.extract.return_value = LLMFeatures()
        mock_extractor_class.return_value = mock_extractor
        
        result = extract_llm_features("test text")
        
        assert isinstance(result, LLMFeatures)
        mock_extractor.extract.assert_called_once()


class TestIntegration:
    """Integration tests with mock API."""
    
    @pytest.fixture
    def sample_narrative(self):
        """Sample Chinese life narrative for testing."""
        return """
        那年夏天，我考上了大学。收到录取通知书的那天，全家人都很高兴。
        母亲特意做了一桌好菜，父亲还开了瓶珍藏多年的白酒。
        
        九月初，我独自来到杭州。火车站人潮汹涌，我拖着行李箱，
        心里既兴奋又紧张。学长在出站口等我，带我坐校车去学校。
        
        大学生活开始了。我选择了计算机专业，因为我对编程很感兴趣。
        第一年很吃力，但我很享受学习的过程。
        """
    
    def test_full_extraction_pipeline(self, sample_narrative):
        """Test full extraction pipeline with mocked API."""
        config = LLMConfig(api_key='test-key', use_cache=False)
        extractor = LLMFeatureExtractor(config)
        
        # Mock all LLM calls
        with patch.object(extractor, '_call_llm') as mock_call:
            mock_call.return_value = json.dumps({
                'emotions': [
                    {'text': '很高兴', 'emotion': 'joy', 'type': 'explicit', 'confidence': 0.9},
                    {'text': '既兴奋又紧张', 'emotion': 'anxiety', 'type': 'implicit', 'confidence': 0.7},
                ],
                'total_explicit': 1,
                'total_implicit': 1,
                'emotional_density': 1.5,
            })
            
            emotions = extractor.extract_emotions(sample_narrative)
            
            assert len(emotions) == 2
            assert any(e.emotion == 'joy' for e in emotions)
            assert any(e.emotion == 'anxiety' for e in emotions)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
