#!/usr/bin/env python3
"""
CittaVerse Narrative Scorer - Gradio Web UI
A simple web interface for scoring Chinese autobiographical narratives.

Usage:
    python3 src/gradio_ui.py

Requirements:
    pip install gradio

Author: Hulk, CittaVerse Team
License: MIT
"""

import gradio as gr
import json
from datetime import datetime
from pathlib import Path

# Import the scorer
from scorer import NarrativeScorer

# Initialize scorer
scorer = NarrativeScorer()


def score_narrative(text: str) -> tuple:
    """
    Score a narrative and return formatted results.
    
    Args:
        text: Chinese narrative text
        
    Returns:
        Tuple of (json_output, feedback_text, score_breakdown)
    """
    if not text or len(text.strip()) == 0:
        return (
            json.dumps({"error": "请输入叙事文本"}, ensure_ascii=False, indent=2),
            "⚠️ 请输入一些文本进行评分。",
            ""
        )
    
    # Score the narrative
    result = scorer.score(text)
    
    # Format JSON output
    json_output = json.dumps(result, ensure_ascii=False, indent=2)
    
    # Extract feedback
    feedback = result.get("feedback", "无反馈")
    
    # Create score breakdown visualization
    dimensions = [
        ("事件丰富度", result.get("event_richness", 0)),
        ("时间连贯性", result.get("temporal_coherence", 0)),
        ("因果连贯性", result.get("causal_coherence", 0)),
        ("情感深度", result.get("emotional_depth", 0)),
        ("自我认同整合", result.get("identity_integration", 0)),
        ("信息密度分布", result.get("information_density", 0)),
    ]
    
    # Create markdown breakdown
    breakdown_md = "### 📊 六维度评分\n\n"
    breakdown_md += "| 维度 | 分数 | 等级 |\n"
    breakdown_md += "|------|------|------|\n"
    
    for name, score in dimensions:
        grade = get_letter_grade(score)
        emoji = get_grade_emoji(grade)
        breakdown_md += f"| {name} | {score:.1f} | {emoji} {grade} |\n"
    
    breakdown_md += f"\n**综合得分**: {result.get('composite_score', 0):.1f} / 100  \n"
    breakdown_md += f"**等级**: {result.get('letter_grade', 'N/A')}\n"
    
    # Add feature counts
    breakdown_md += "\n### 📈 特征统计\n\n"
    breakdown_md += f"- 事件总数：{result.get('total_events', 0)}\n"
    breakdown_md += f"- 时间标记：{result.get('time_markers_count', 0)}\n"
    breakdown_md += f"- 因果标记：{result.get('causal_markers_count', 0)}\n"
    breakdown_md += f"- 自我指涉：{result.get('self_references_count', 0)}\n"
    breakdown_md += f"- 情感词：{result.get('emotion_words_count', 0)}\n"
    breakdown_md += f"- 中心信息：{result.get('central_count', 0)}\n"
    breakdown_md += f"- 外围信息：{result.get('peripheral_count', 0)}\n"
    
    return (json_output, feedback, breakdown_md)


def get_letter_grade(score: float) -> str:
    """Convert numeric score to letter grade."""
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


def get_grade_emoji(grade: str) -> str:
    """Get emoji for letter grade."""
    emojis = {
        "S": "🏆",
        "A": "⭐",
        "B": "✓",
        "C": "○",
        "D": "△",
        "F": "✗"
    }
    return emojis.get(grade, "")


def load_example(example_name: str) -> str:
    """Load an example narrative from the examples directory."""
    example_path = Path(__file__).parent.parent / "examples" / f"{example_name}.txt"
    
    if example_path.exists():
        return example_path.read_text(encoding="utf-8")
    else:
        return f"示例文件不存在：{example_name}.txt"


def create_demo() -> gr.Blocks:
    """Create the Gradio demo interface."""
    
    with gr.Blocks(title="CittaVerse Narrative Scorer", theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # 🧠 CittaVerse Narrative Scorer v0.5
        
        **中文自传体记忆叙事质量自动评估工具**
        
        本工具基于六维度评分体系，自动评估中文叙事的质量：
        - 事件丰富度 (Event Richness)
        - 时间连贯性 (Temporal Coherence)
        - 因果连贯性 (Causal Coherence)
        - 情感深度 (Emotional Depth)
        - 自我认同整合 (Identity Integration)
        - 信息密度分布 (Information Density Distribution)
        
        ---
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                gr.Markdown("### 📝 输入叙事")
                narrative_input = gr.Textbox(
                    label="叙事文本",
                    placeholder="请输入您的中文叙事（建议 100-1000 字）...",
                    lines=10,
                    max_lines=50
                )
                
                with gr.Row():
                    score_btn = gr.Button("🚀 开始评分", variant="primary", size="lg")
                    clear_btn = gr.Button("🗑️ 清空", size="lg")
                
                gr.Markdown("### 📚 加载示例")
                example_dropdown = gr.Dropdown(
                    choices=["sample_input"],
                    label="选择示例",
                    info="点击加载示例叙事"
                )
            
            with gr.Column(scale=3):
                gr.Markdown("### 📊 评分结果")
                
                feedback_output = gr.Textbox(
                    label="自然语言反馈",
                    lines=3,
                    max_lines=5
                )
                
                breakdown_output = gr.Markdown(label="评分详情")
                
                json_output = gr.Code(
                    label="JSON 输出",
                    language="json",
                    lines=15
                )
        
        # Examples section
        gr.Markdown("---")
        gr.Markdown("### 💡 使用提示")
        gr.Markdown("""
        1. **输入叙事**：在左侧文本框中输入或粘贴您的中文叙事
        2. **点击评分**：点击"开始评分"按钮获取评分结果
        3. **查看反馈**：右侧将显示自然语言反馈、评分详情和 JSON 输出
        4. **加载示例**：从下拉菜单选择示例叙事进行学习
        
        **评分说明**：
        - S (90-100):  exceptional - 杰出
        - A (80-89):  excellent - 优秀
        - B (70-79):  good - 良好
        - C (60-69):  adequate - 合格
        - D (50-59):  needs improvement - 需改进
        - F (<50):  poor - 较差
        """)
        
        # Footer
        gr.Markdown("---")
        gr.Markdown("""
        **CittaVerse Narrative Scorer v0.5** | 
        [GitHub](https://github.com/cittaverse/narrative-scorer) | 
        MIT License | 
        一念万相科技 © 2026
        """)
        
        # Event handlers
        score_btn.click(
            fn=score_narrative,
            inputs=[narrative_input],
            outputs=[json_output, feedback_output, breakdown_output]
        )
        
        clear_btn.click(
            fn=lambda: ("", "", ""),
            inputs=[],
            outputs=[narrative_input, feedback_output, breakdown_output]
        )
        
        example_dropdown.change(
            fn=load_example,
            inputs=[example_dropdown],
            outputs=[narrative_input]
        )
    
    return demo


if __name__ == "__main__":
    print("🚀 Starting CittaVerse Narrative Scorer Web UI...")
    print("📍 Open http://localhost:7860 in your browser")
    print("ℹ️  Press Ctrl+C to stop the server")
    
    demo = create_demo()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
