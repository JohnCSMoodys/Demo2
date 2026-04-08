# Design a Story

**Focus:** Design Document + Active Partner + Reverse Direction + Knowledge Checkpoint + Text-Native
**Goal:** Create a design document for a data visualization — no code yet

---

## Overview

You'll work with exoplanet data — planets outside our solar system. The domain is unfamiliar on purpose. You don't know the data, so you *must* collaborate with the agent. You can't just tell it what to build — you need to explore together.

**What you'll figure out:**
- Goal and audience (who is this for?)
- Story hypothesis (what pattern to show)
- Visualization choice (and why)
- Key data columns (and what you're leaving out)

**What you'll produce:** `DESIGN.md` with a text diagram. Save before any implementation.

No code. Design only. What you produce here feeds directly into the next module (Plan + Implement).

---

## Your Tasks

1. **Explore the data** — Understand what's available, what's interesting
2. **Generate alternatives** — At least 2-3 different story ideas with trade-offs
3. **Choose and refine** — Pick one, articulate why
4. **Document the design** — Create `DESIGN.md` with goal, audience, hypothesis, viz choice, key columns, text diagram, risks
5. **Save** — Commit `DESIGN.md` before any code
6. **Encode** — Create your first ground rules (see below)

---

## Patterns to Practice

**Design Document** *(core)*
A structured artifact that captures what you've decided and why. This is the primary output of the design phase — goal, audience, hypothesis, constraints, diagram, risks.

How: Build `DESIGN.md` through conversation. Start with the problem, explore the solution space, converge on a hypothesis, stress-test, then write it down.

**Active Partner** *(core)*
The agent defaults to silent compliance. You need it to question, interpret, offer alternatives.

How: Set audience level. Require goal restatement before proposals. Ask for alternatives with trade-offs. Say: "Push back if something seems wrong."

**Reverse Direction** *(core)*
Prevents premature convergence. Gets you breadth before depth.

How: When agent asks you to decide → "show me options." When you're over-specifying → "what would you choose?" When stuck → "what questions do you have?"

**Knowledge Checkpoint** *(core)*
Separates design from implementation. Creates an artifact to return to. The Design Document is what you save; the Knowledge Checkpoint is the act of saving it.

How: Save `DESIGN.md` before any code. Include decisions, trade-offs, unknowns.

**Text-Native** *(supporting)*
The agent can read, diff, and edit text. Binary formats block collaboration.

How: Use markdown, text diagrams, structured tables. Avoid external tools during design.

---

## Obstacles to Watch

**Compliance Bias** — The agent says "Sure thing!" even when confused. If it agrees instantly without asking questions, that's a signal.

**Silent Misalignment** — The agent builds confidently in the wrong direction. Confidence does not equal correctness. If you can't explain the plan back, don't proceed.

## Anti-patterns to Recognize

**Answer Injection** — Narrowing the solution space to what you already thought of. You put your solution in the question, limiting the agent to your preconceived approach. The fix: present the problem, not your solution. State what you're trying to achieve, not how. Remove arbitrary constraints and let the agent's breadth reveal options you haven't considered.

---

## Definition of Done

**Core (everyone):**
- [ ] Set audience and explanation level in first interaction
- [ ] Explored at least 2 design concepts before choosing
- [ ] Agent restated goal before final design proposal
- [ ] Can explain chosen design without looking at the doc
- [ ] `DESIGN.md` includes: goal, audience, hypothesis, viz choice, key columns, text diagram, risks
- [ ] `DESIGN.md` committed before any code
- [ ] At least one instance of Reverse Direction
- [ ] First ground rules created and saved

**Optional (buffer):**
- [ ] Documented alternatives you rejected and why
- [ ] Agent summarized design back to test alignment
- [ ] Added "what's next" section

---

## Working with the Agent

**Stay in DESIGN mode.** This exercise is design only. If the agent starts planning implementation, choosing tech stack, or writing code — stop and redirect to design.

**Set audience.** "Explain for a non-technical reader" or "Explain for a data analyst." Ask for rephrasing until you can explain it back.

**Get alternatives.** Don't accept the first suggestion. "Show me 2-3 options with trade-offs."

**Test alignment.** "Tell me what you're going to do" before the agent proceeds. If you can't explain it back, don't move forward.

---

## Workflow Suggestion

**Phase 1: Explore** (~10 min)
Understand the data. Identify interesting patterns. Set audience.

**Phase 2: Diverge** (~10 min)
Generate 2-3 story concepts. Compare. Don't commit yet.

**Phase 3: Choose** (~10 min)
Pick one. Refine. Document in `DESIGN.md` with text diagram.

**Phase 4: Save + Encode** (~10 min)
Review `DESIGN.md`. Commit. Then create your first ground rules (see below).

---

## Encode: First Ground Rules

After finishing your design, ask the agent:

> "Review our conversation. What ground rules would have prevented our correction cycles?"

The agent reviews the session — struggles, redirections, misalignments — and surfaces what would improve future sessions.

Save 1-2 rules to your rules file:
- Cursor: `.cursor/rules/`
- Claude Code: `CLAUDE.md` or `AGENTS.md`

This is the meta-move: using the agent to improve its own operating environment.

---

*Your DESIGN.md is the input for the next module (Plan + Implement).*
