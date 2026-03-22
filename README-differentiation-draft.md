# README.md Differentiation Section Draft

**Target File**: `github-repos/narrative-scorer/README.md`  
**Date Prepared**: 2026-03-22 04:00 UTC  
**Status**: Ready for V review and merge

---

## Proposed Addition

Insert this section **after "Features"** and **before "Installation"**:

```markdown
## Positioning & Differentiation

CittaVerse Narrative Scorer occupies a unique position in the AI-assisted reminiscence therapy landscape:

### Workflow Stage Focus

| Tool | Stage | Core Function |
|------|-------|---------------|
| **Rememo** (CHI 2026) | Pre-session | Generate personalized visual memory triggers |
| **CittaVerse Narrative Scorer** | Post-session | Quantify narrative quality in session transcripts |
| **Future Integration** | End-to-end | Complete "Prepare → Execute → Assess" workflow |

### Key Differentiators

1. **Assessment Expertise**: 6-dimension framework grounded in autobiographical memory theory (vs. generation focus)
2. **Chinese Specificity**: First narrative quality assessment tool designed for Chinese older adults' autobiographical memory
3. **Explainability**: Neuro-symbolic AI (LLM extraction + rule-based scoring) with traceable, deterministic outputs
4. **Product Orientation**: Open-source tool + API designed for rapid integration into existing RT platforms

### Complementary, Not Competitive

Rememo and CittaVerse serve different stages of the reminiscence therapy workflow. They can be integrated into a complete toolchain:

```
┌─────────────────────────────────────────────────────────────┐
│                    RT Session Workflow                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Pre-Session          During Session        Post-Session    │
│  ┌─────────┐         ┌──────────┐          ┌───────────┐   │
│  │ Rememo  │         │ Therapist│          │ CittaVerse│   │
│  │ Images  │    →    │ +        │     →    │ Scoring   │   │
│  │ + Qs    │         │ Resident │          │ + Report  │   │
│  └─────────┘         └──────────┘          └───────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

We welcome collaboration with the Rememo team and other researchers in this space.
```

---

## Rationale

**Why Add This Section**:
1. **Pre-empts competitive concerns**: Readers may wonder "Isn't this what Rememo does?" — this clarifies upfront
2. **Highlights unique value**: 6-dimension framework, Chinese specificity, explainability are key differentiators
3. **Signals openness to collaboration**: Positions CittaVerse as community-oriented, not siloed
4. **Supports academic credibility**: Shows awareness of state-of-the-art (Rememo CHI 2026)

**Why This Placement**:
- After "Features": Readers first understand what the tool does, then how it fits in the landscape
- Before "Installation": Technical users can quickly assess relevance before diving into setup

---

## Alternative (Shorter Version)

If README is getting too long, here's a condensed version:

```markdown
## Positioning

**Rememo** (CHI 2026) generates memory triggers **before** sessions. **CittaVerse Narrative Scorer** assesses narrative quality **after** sessions. Together, they form a complete "Prepare → Execute → Assess" workflow.

**Unique to CittaVerse**:
- 6-dimension autobiographical memory framework
- Chinese older adult specificity
- Neuro-symbolic explainability (not black-box)
- Open-source + API for integration
```

---

## Next Steps

**Option A (V executes)**:
1. Open `github-repos/narrative-scorer/README.md`
2. Insert chosen version after "Features" section
3. Commit: `docs: Add positioning & differentiation section`
4. Push to `cittaverse/narrative-scorer`

**Option B (Hulk executes via PR)**:
1. Hulk creates branch `add-positioning-section`
2. Hulk makes edit and commits
3. Hulk opens PR on `cittaverse/narrative-scorer`
4. V reviews and merges

**Option C (Defer)**:
- Wait until after arXiv submission (positioning will be cited in paper)
- Add section as part of post-submission repo refresh

---

*Prepared by Hulk 🟢 for V review and execution*
