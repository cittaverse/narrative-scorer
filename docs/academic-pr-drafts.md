# Academic Community PR Drafts

> Prepared by GEO #60 — 2026-03-23
> Status: Ready to fork & submit (blocked on arXiv ID for 2 of 3 PRs)

---

## PR 1: Awesome-LLM-Eval (onejune2018/Awesome-LLM-Eval, 548⭐)

**Target section**: Domain > Healthcare (README.md table at line ~163)

**Branch name**: `add-narrative-scorer-healthcare-eval`

**PR Title**: `Add: CittaVerse Narrative Scorer — Healthcare domain LLM evaluation for autobiographical memory`

**PR Description**:
```
Adds CittaVerse Narrative Scorer to the Domain > Healthcare section.

**What**: Open-source automated scorer for Chinese autobiographical memory narratives,
measuring 6 dimensions (event richness, temporal coherence, causal coherence,
emotional depth, identity integration, information density).

**Why relevant**: First automated evaluation tool for narrative quality in digital
reminiscence therapy — extends LLM evaluation to a new healthcare vertical
(elderly cognitive assessment).

**Links**:
- GitHub: https://github.com/cittaverse/narrative-scorer
- Paper: [arXiv link pending]
- License: MIT
```

**Content to add** (README.md Domain table, after MedBench row):

```markdown
| Narrative Scorer | CittaVerse | Healthcare | [narrative-scorer](https://github.com/cittaverse/narrative-scorer) | Automated six-dimension narrative quality assessment for Chinese autobiographical memories in digital reminiscence therapy. Measures event richness, temporal/causal coherence, emotional depth, identity integration, and information density. MIT licensed, Gradio UI included. (2026-03) |
```

**Content to add** (README_EN.md, already present ✅)

**Content to add** (README_CN.md Domain table):

```markdown
| 叙事质量评分器 | CittaVerse | 医疗健康 | [narrative-scorer](https://github.com/cittaverse/narrative-scorer) | 面向中文自传体记忆的六维叙事质量自动评估工具，用于数字回忆疗法。评估事件丰富度、时间/因果连贯性、情感深度、自我认同整合和信息密度分布。MIT 开源，内含 Gradio 演示界面。(2026-03) |
```

**前置条件**: 
- ✅ Fork 已存在 (OiiOAI/Awesome-LLM-Eval)
- ✅ README_EN.md 已有条目
- ⚠️ README.md 和 README_CN.md 缺失条目
- ⚠️ arXiv ID 待 V 提交后替换

**Status**: 可以先提交 fork commit，arXiv 后再开 PR

---

## PR 2: awesome-dementia-detection (billzyx/awesome-dementia-detection, 42⭐)

**Target section**: `3. Novel research topics in dementia > Voice Assistant` or `Novel Speech Tasks`

**Branch name**: `add-cittaverse-narrative-scorer`

**PR Title**: `Add: CittaVerse Narrative Scorer — Automated narrative assessment for elderly cognitive screening`

**PR Description**:
```
Adds CittaVerse Narrative Scorer to the "Novel Speech Tasks" section.

**What**: Open-source tool that automatically scores Chinese autobiographical
memory narratives on 6 dimensions derived from the Autobiographical Interview
(Levine et al., 2002). Designed for MCI screening via digital reminiscence therapy.

**Why relevant**: Extends dementia detection from binary classification to
continuous narrative quality assessment — capturing cognitive decline signals
through storytelling ability rather than just speech acoustics.

**Links**:
- GitHub: https://github.com/cittaverse/narrative-scorer
- Paper: [arXiv link pending]
- License: MIT
```

**Content to add** (after "Novel Speech Tasks" section, 2026 subsection):

```markdown
- 2026
	- [Automated Narrative Quality Assessment for Chinese Autobiographical Memories in Digital Reminiscence Therapy](https://github.com/cittaverse/narrative-scorer) - CittaVerse, GitHub, (2026), Cited By: 0
```

**前置条件**:
- ⚠️ 需要 fork billzyx/awesome-dementia-detection
- ⚠️ arXiv link 待替换（当前用 GitHub link 占位）
- 📌 建议等 arXiv 提交后再开 PR，学术列表更重视论文链接

**Status**: Draft ready, 等 arXiv

---

## PR 3: awesome-ai-eval (Vvkmnn/awesome-ai-eval, 70⭐)

**Target section**: `Benchmarks > Domain`

**Branch name**: `add-narrative-scorer-domain-eval`

**PR Title**: `Add: CittaVerse Narrative Scorer — Domain-specific narrative evaluation for elderly healthcare`

**PR Description**:
```
Adds CittaVerse Narrative Scorer to the Domain benchmarks section.

**What**: Open-source automated scorer for Chinese autobiographical memory
narratives. Six-dimension evaluation framework (event richness, temporal coherence,
causal coherence, emotional depth, identity integration, information density)
designed for elderly cognitive assessment in digital reminiscence therapy.

**Why relevant**: First domain-specific AI evaluation tool for narrative quality
in healthcare, addressing an underserved population (Chinese elderly with MCI).

**Links**:
- GitHub: https://github.com/cittaverse/narrative-scorer
- Paper: [arXiv link pending]
- License: MIT
```

**Content to add** (after MedHELM entry in Domain section):

```markdown
- ![](https://img.shields.io/github/stars/cittaverse/narrative-scorer?style=social&label=github.com) [**Narrative Scorer**](https://github.com/cittaverse/narrative-scorer) - Six-dimension automated evaluation for Chinese autobiographical memory narratives in digital reminiscence therapy, measuring event richness, coherence, emotional depth, and identity integration.
```

**前置条件**:
- ⚠️ 需要 fork Vvkmnn/awesome-ai-eval
- ✅ 不强制要求 arXiv（GitHub 项目即可提交）

**Status**: 可以直接提交

---

## PR 4: nlg-metricverse (disi-unibo-nlp/nlg-metricverse, 94⭐)

**评估结论**: 暂不适合提交 PR

**原因**:
1. nlg-metricverse 是一个 Python 包，接受的是可安装的评估指标代码贡献
2. 我们的 narrative-scorer 是独立工具，不是 nlg-metricverse 的 plugin
3. 要提交需要按他们的 `Custom Metrics` 接口封装，工作量较大
4. ROI 不高：94⭐ 但学术导向，且需要代码集成而非 README 链接

**替代方案**: 等 v0.6 完成后，考虑将 6 维评分封装为 nlg-metricverse 插件

---

## 执行优先级

| PR | 仓库 | 可立即执行 | 依赖 arXiv | 预期影响 |
|----|------|-----------|-----------|---------|
| #3 | awesome-ai-eval | ✅ | 否 | 中 |
| #1 | Awesome-LLM-Eval | 部分（fork 已有） | 是（推荐） | 高 |
| #2 | awesome-dementia-detection | 否 | 是（必须） | 中 |
| #4 | nlg-metricverse | 否 | — | 低（暂不执行） |

**立即行动**: 执行 PR #3 (awesome-ai-eval) — fork + branch + commit + 开 PR
**下一步**: PR #1 补全 README.md 和 README_CN.md → arXiv 后开 PR
**等待**: PR #2 等 arXiv
