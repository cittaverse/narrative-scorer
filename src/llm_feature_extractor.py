"""
LLM Feature Extractor for Narrative Scorer v0.7

This module provides LLM-enhanced feature extraction for Chinese life narratives.
It augments the rule-based pipeline with implicit feature detection:
- Implicit emotion detection
- Semantic event boundary detection
- Implicit causal link detection

Architecture: Rule-based primary + LLM augmentation with graceful degradation.
If LLM API fails, falls back to rule-only mode (v0.6 behavior).

Author: Hulk (CittaVerse)
Version: v0.7.0-alpha
"""

import json
import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

# DashScope import (optional - graceful degradation if not available)
try:
    from dashscope import Generation
    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False
    Generation = None

logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """Configuration for LLM feature extraction."""
    
    # API Configuration
    api_key: Optional[str] = None
    model: str = "qwen-plus"  # Recommended: qwen-plus for cost/performance balance
    timeout: int = 5  # seconds
    max_retries: int = 2
    rate_limit_delay: float = 0.1  # seconds between requests
    
    # Feature Toggles
    use_emotion_detection: bool = True
    use_event_segmentation: bool = True
    use_causality_detection: bool = True
    
    # Fallback Configuration
    fallback_to_rule_only: bool = True  # If True, return rule-only features on LLM failure
    
    # Cost Tracking
    track_cost: bool = True
    cost_per_1k_input_tokens: float = 0.0028  # CNY (DashScope qwen-plus)
    cost_per_1k_output_tokens: float = 0.0028  # CNY
    
    # Caching (optional)
    use_cache: bool = False
    cache_dir: Optional[str] = None
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> "LLMConfig":
        """Load configuration from YAML file."""
        with open(yaml_path, 'r', encoding='utf-8') as f:
            config_dict = yaml.safe_load(f)
        return cls(**config_dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'api_key': self.api_key,
            'model': self.model,
            'timeout': self.timeout,
            'max_retries': self.max_retries,
            'rate_limit_delay': self.rate_limit_delay,
            'use_emotion_detection': self.use_emotion_detection,
            'use_event_segmentation': self.use_event_segmentation,
            'use_causality_detection': self.use_causality_detection,
            'fallback_to_rule_only': self.fallback_to_rule_only,
            'track_cost': self.track_cost,
            'cost_per_1k_input_tokens': self.cost_per_1k_input_tokens,
            'cost_per_1k_output_tokens': self.cost_per_1k_output_tokens,
            'use_cache': self.use_cache,
            'cache_dir': self.cache_dir,
        }


@dataclass
class EmotionFeature:
    """Detected emotion feature."""
    text: str
    emotion: str
    emotion_type: str  # 'explicit' or 'implicit'
    confidence: float
    start_char: Optional[int] = None
    end_char: Optional[int] = None


@dataclass
class EventBoundary:
    """Detected event boundary."""
    event_id: int
    start_char: int
    end_char: int
    text: str
    summary: str
    boundary_before: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CausalRelation:
    """Detected causal relation."""
    relation_id: int
    cause_text: str
    cause_start: int
    cause_end: int
    effect_text: str
    effect_start: int
    effect_end: int
    relation_type: str  # 'explicit' or 'implicit'
    strength: str  # 'strong', 'moderate', 'weak'
    cue_type: str  # 'lexical', 'inferential', 'none'
    cue_text: Optional[str]
    confidence: float


@dataclass
class LLMFeatures:
    """Container for all LLM-extracted features."""
    emotions: List[EmotionFeature] = field(default_factory=list)
    events: List[EventBoundary] = field(default_factory=list)
    causal_relations: List[CausalRelation] = field(default_factory=list)
    
    # Metadata
    llm_call_success: bool = False
    llm_calls_made: int = 0
    llm_calls_failed: int = 0
    total_cost: float = 0.0
    latency_ms: float = 0.0
    
    # Fallback flag
    used_fallback: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for integration with scorer."""
        return {
            'emotions': [
                {
                    'text': e.text,
                    'emotion': e.emotion,
                    'type': e.emotion_type,
                    'confidence': e.confidence,
                    'start_char': e.start_char,
                    'end_char': e.end_char,
                }
                for e in self.emotions
            ],
            'events': [
                {
                    'event_id': ev.event_id,
                    'start_char': ev.start_char,
                    'end_char': ev.end_char,
                    'text': ev.text,
                    'summary': ev.summary,
                    'boundary_before': ev.boundary_before,
                }
                for ev in self.events
            ],
            'causal_relations': [
                {
                    'relation_id': cr.relation_id,
                    'cause': {
                        'text': cr.cause_text,
                        'start_char': cr.cause_start,
                        'end_char': cr.cause_end,
                    },
                    'effect': {
                        'text': cr.effect_text,
                        'start_char': cr.effect_start,
                        'end_char': cr.effect_end,
                    },
                    'type': cr.relation_type,
                    'strength': cr.strength,
                    'cue_type': cr.cue_type,
                    'cue_text': cr.cue_text,
                    'confidence': cr.confidence,
                }
                for cr in self.causal_relations
            ],
            'metadata': {
                'llm_call_success': self.llm_call_success,
                'llm_calls_made': self.llm_calls_made,
                'llm_calls_failed': self.llm_calls_failed,
                'total_cost': self.total_cost,
                'latency_ms': self.latency_ms,
                'used_fallback': self.used_fallback,
            }
        }


class LLMFeatureExtractor:
    """
    LLM-enhanced feature extractor for narrative scoring.
    
    Usage:
        config = LLMConfig.from_yaml('config/llm_config.yaml')
        extractor = LLMFeatureExtractor(config)
        features = extractor.extract(text)
        
        # Integrate with rule-based scorer
        enhanced_emotion_count = len(features.emotions)
        enhanced_event_count = len(features.events)
        enhanced_causal_count = len(features.causal_relations)
    """
    
    def __init__(self, config: Optional[LLMConfig] = None):
        """
        Initialize LLM feature extractor.
        
        Args:
            config: LLMConfig object. If None, uses environment variables.
        """
        self.config = config or self._load_config_from_env()
        self.prompt_templates: Dict[str, str] = {}
        self._load_prompt_templates()
    
    def _load_config_from_env(self) -> LLMConfig:
        """Load configuration from environment variables."""
        api_key = os.getenv('DASHSCOPE_API_KEY')
        if not api_key:
            logger.warning("DASHSCOPE_API_KEY not set. LLM features will use fallback mode.")
        return LLMConfig(api_key=api_key)
    
    def _load_prompt_templates(self) -> None:
        """Load prompt templates from llm_prompts/ directory."""
        prompts_dir = Path(__file__).parent.parent / 'llm_prompts'
        
        template_files = {
            'emotion_detection': 'emotion_detection.txt',
            'event_segmentation': 'event_segmentation.txt',
            'causality_detection': 'causality_detection.txt',
        }
        
        for key, filename in template_files.items():
            template_path = prompts_dir / filename
            if template_path.exists():
                with open(template_path, 'r', encoding='utf-8') as f:
                    self.prompt_templates[key] = f.read()
                logger.debug(f"Loaded prompt template: {key}")
            else:
                logger.warning(f"Prompt template not found: {template_path}")
                self.prompt_templates[key] = ""
    
    def _prepare_prompt(self, template_key: str, input_text: str) -> str:
        """
        Prepare prompt by filling in template.
        
        Args:
            template_key: Key for prompt template
            input_text: Input narrative text
            
        Returns:
            Filled prompt string
        """
        template = self.prompt_templates.get(template_key, "")
        if not template:
            logger.error(f"Prompt template not loaded: {template_key}")
            return ""
        
        return template.replace('{input_text}', input_text)
    
    def _call_llm(self, prompt: str) -> Optional[str]:
        """
        Call LLM API with retry and fallback logic.
        
        Args:
            prompt: Prompt string
            
        Returns:
            LLM response text, or None if failed
        """
        if not DASHSCOPE_AVAILABLE:
            logger.warning("DashScope not available. Using fallback mode.")
            return None
        
        if not self.config.api_key:
            logger.warning("API key not set. Using fallback mode.")
            return None
        
        for attempt in range(self.config.max_retries):
            try:
                start_time = time.time()
                
                response = Generation.call(
                    model=self.config.model,
                    prompt=prompt,
                    timeout=self.config.timeout,
                    api_key=self.config.api_key,
                )
                
                latency = (time.time() - start_time) * 1000  # ms
                
                if response.status_code == 200:
                    logger.debug(f"LLM API call successful (latency: {latency:.0f}ms)")
                    
                    # Cost estimation (approximate)
                    if self.config.track_cost:
                        input_tokens = len(prompt) // 4  # Rough estimation
                        output_tokens = len(response.output.text) // 4
                        cost = (
                            input_tokens * self.config.cost_per_1k_input_tokens / 1000 +
                            output_tokens * self.config.cost_per_1k_output_tokens / 1000
                        )
                        logger.debug(f"Estimated cost: ¥{cost:.4f}")
                    
                    # Rate limiting
                    if self.config.rate_limit_delay > 0:
                        time.sleep(self.config.rate_limit_delay)
                    
                    return response.output.text
                else:
                    logger.warning(
                        f"LLM API returned error (status: {response.status_code}, "
                        f"attempt {attempt + 1}/{self.config.max_retries})"
                    )
                    
            except Exception as e:
                logger.warning(
                    f"LLM API exception (attempt {attempt + 1}/{self.config.max_retries}): {e}"
                )
        
        logger.error("LLM API call failed after all retries")
        return None
    
    def _parse_json_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        Parse JSON response from LLM.
        
        Args:
            response_text: Raw LLM response
            
        Returns:
            Parsed JSON dict, or None if parsing failed
        """
        if not response_text:
            return None
        
        try:
            # Try to extract JSON from response (handle markdown code blocks)
            if '```json' in response_text:
                json_str = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                json_str = response_text.split('```')[1].split('```')[0].strip()
            else:
                json_str = response_text.strip()
            
            return json.loads(json_str)
            
        except (json.JSONDecodeError, IndexError) as e:
            logger.error(f"Failed to parse LLM JSON response: {e}")
            logger.debug(f"Raw response: {response_text[:500]}...")
            return None
    
    def extract_emotions(self, text: str) -> List[EmotionFeature]:
        """
        Extract emotion features from text.
        
        Args:
            text: Input narrative text
            
        Returns:
            List of EmotionFeature objects
        """
        if not self.config.use_emotion_detection:
            return []
        
        prompt = self._prepare_prompt('emotion_detection', text)
        if not prompt:
            return []
        
        response = self._call_llm(prompt)
        if not response:
            return []
        
        parsed = self._parse_json_response(response)
        if not parsed or 'emotions' not in parsed:
            return []
        
        emotions = []
        for emo in parsed['emotions']:
            emotions.append(EmotionFeature(
                text=emo.get('text', ''),
                emotion=emo.get('emotion', ''),
                emotion_type=emo.get('type', 'explicit'),
                confidence=emo.get('confidence', 0.0),
                start_char=None,  # Could be added if needed
                end_char=None,
            ))
        
        return emotions
    
    def extract_events(self, text: str) -> List[EventBoundary]:
        """
        Extract event boundaries from text.
        
        Args:
            text: Input narrative text
            
        Returns:
            List of EventBoundary objects
        """
        if not self.config.use_event_segmentation:
            return []
        
        prompt = self._prepare_prompt('event_segmentation', text)
        if not prompt:
            return []
        
        response = self._call_llm(prompt)
        if not response:
            return []
        
        parsed = self._parse_json_response(response)
        if not parsed or 'events' not in parsed:
            return []
        
        events = []
        for ev in parsed['events']:
            events.append(EventBoundary(
                event_id=ev.get('event_id', 0),
                start_char=ev.get('start_char', 0),
                end_char=ev.get('end_char', 0),
                text=ev.get('text', ''),
                summary=ev.get('summary', ''),
                boundary_before=ev.get('boundary_before', {}),
            ))
        
        return events
    
    def extract_causal_relations(self, text: str) -> List[CausalRelation]:
        """
        Extract causal relations from text.
        
        Args:
            text: Input narrative text
            
        Returns:
            List of CausalRelation objects
        """
        if not self.config.use_causality_detection:
            return []
        
        prompt = self._prepare_prompt('causality_detection', text)
        if not prompt:
            return []
        
        response = self._call_llm(prompt)
        if not response:
            return []
        
        parsed = self._parse_json_response(response)
        if not parsed or 'causal_relations' not in parsed:
            return []
        
        relations = []
        for rel in parsed['causal_relations']:
            cause = rel.get('cause', {})
            effect = rel.get('effect', {})
            relations.append(CausalRelation(
                relation_id=rel.get('relation_id', 0),
                cause_text=cause.get('text', ''),
                cause_start=cause.get('start_char', 0),
                cause_end=cause.get('end_char', 0),
                effect_text=effect.get('text', ''),
                effect_start=effect.get('start_char', 0),
                effect_end=effect.get('end_char', 0),
                relation_type=rel.get('type', 'explicit'),
                strength=rel.get('strength', 'moderate'),
                cue_type=rel.get('cue_type', 'inferential'),
                cue_text=rel.get('cue_text'),
                confidence=rel.get('confidence', 0.0),
            ))
        
        return relations
    
    def extract(self, text: str) -> LLMFeatures:
        """
        Extract all LLM features from text.
        
        This is the main entry point. It calls all feature extractors
        and aggregates results into a single LLMFeatures object.
        
        Args:
            text: Input narrative text
            
        Returns:
            LLMFeatures object with all extracted features
        """
        start_time = time.time()
        features = LLMFeatures()
        
        # Extract emotions
        try:
            features.emotions = self.extract_emotions(text)
            features.llm_calls_made += 1
        except Exception as e:
            logger.error(f"Emotion extraction failed: {e}")
            features.llm_calls_failed += 1
        
        # Extract events
        try:
            features.events = self.extract_events(text)
            features.llm_calls_made += 1
        except Exception as e:
            logger.error(f"Event extraction failed: {e}")
            features.llm_calls_failed += 1
        
        # Extract causal relations
        try:
            features.causal_relations = self.extract_causal_relations(text)
            features.llm_calls_made += 1
        except Exception as e:
            logger.error(f"Causal relation extraction failed: {e}")
            features.llm_calls_failed += 1
        
        # Determine overall success
        features.llm_call_success = features.llm_calls_failed == 0
        features.latency_ms = (time.time() - start_time) * 1000
        
        # Check if fallback is needed
        if features.llm_calls_failed > 0 and self.config.fallback_to_rule_only:
            features.used_fallback = True
            logger.info("Using rule-only fallback mode")
        
        return features
    
    def extract_with_fallback(self, text: str, rule_features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract LLM features and merge with rule-based features.
        
        This method provides graceful degradation: if LLM fails,
        returns rule-based features unchanged.
        
        Args:
            text: Input narrative text
            rule_features: Rule-based features (from scorer.py)
            
        Returns:
            Enhanced features dict (LLM + rule-based)
        """
        llm_features = self.extract(text)
        
        if llm_features.used_fallback:
            # LLM failed, return rule-only features
            return rule_features
        
        # Merge LLM features with rule-based features
        enhanced = rule_features.copy()
        
        # Enhance emotion count with implicit emotions
        if 'emotion_count' in enhanced:
            implicit_emotions = [e for e in llm_features.emotions if e.emotion_type == 'implicit']
            # Weight implicit emotions at 0.5 (configurable)
            enhanced['emotion_count'] += len(implicit_emotions) * 0.5
        
        # Enhance event segmentation
        if llm_features.events:
            enhanced['event_boundaries'] = [
                {
                    'position': ev.start_char,
                    'cue_type': ev.boundary_before.get('cue_type', 'inferential'),
                    'confidence': ev.boundary_before.get('confidence', 0.5),
                }
                for ev in llm_features.events
            ]
        
        # Enhance causality count
        if 'causal_count' in enhanced:
            enhanced['causal_count'] += len(llm_features.causal_relations)
        
        # Add LLM metadata
        enhanced['llm_metadata'] = llm_features.to_dict()['metadata']
        
        return enhanced


# Convenience function for quick integration
def extract_llm_features(text: str, config: Optional[LLMConfig] = None) -> LLMFeatures:
    """
    Quick extraction function for ad-hoc use.
    
    Args:
        text: Input narrative text
        config: Optional LLMConfig (uses env vars if not provided)
        
    Returns:
        LLMFeatures object
    """
    extractor = LLMFeatureExtractor(config)
    return extractor.extract(text)


if __name__ == '__main__':
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python llm_feature_extractor.py <text>")
        sys.exit(1)
    
    text = ' '.join(sys.argv[1:])
    
    # Load config from environment
    config = LLMConfig.from_env()
    
    # Extract features
    extractor = LLMFeatureExtractor(config)
    features = extractor.extract(text)
    
    # Print results
    print(json.dumps(features.to_dict(), indent=2, ensure_ascii=False))
