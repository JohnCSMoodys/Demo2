# Extend and Adapt Exercise

**Focus:** Plan evolution + Happy to Delete + Ground rules as working infrastructure
**Goal:** Incorporate a new dataset, evolve your plan, ship a working app, and extract meaningful ground rules

---

## Overview

You have a working app from the Plan + Implement Exercise, a `PLAN.md`, a `DESIGN.md`, and your first ground rules. Now: new data, new requirements. Your current plan may not account for this. Your implementation definitely doesn't.

This creates genuine churn — and that's the point. You'll practice evolving a plan under changing requirements, applying Happy to Delete when needed, and extracting ground rules from real experience.

---

## The Curveball

**New dataset:** Star/host information (`stars.csv`). Joins to your exoplanet data on `host_name`.

**New requirements:** Incorporate the star data into your visualization — system view, star properties, data join.

**Choose your approach:**
- **Evolve the plan** — update `PLAN.md` to incorporate new requirements, implement from there
- **Fresh plan** — create a new `PLAN.md` that accounts for the expanded scope

Both are valid. Both count as DPI. The only wrong move is skipping the plan and patching code directly.

---

## Your Tasks

1. **Assess** — Review the new data and requirements against your existing plan
2. **Choose approach** — Evolve the plan or start fresh
3. **Plan** — Update or create `PLAN.md` for the expanded scope
4. **Implement** — Build with parallel approaches and/or Happy to Delete behavior
5. **Extract ground rules** — Reflective dialogue with the agent (see below)
6. **Review** — Review your rules for specificity and actionability

---

## Patterns to Practice

**Plan Evolution** *(core)*
Plans are living documents. When requirements change, the plan adapts — either by updating or by starting fresh. DPI is iterative, not linear.

**Happy to Delete** *(core)*
When the curveball invalidates your implementation, deleting and restarting from an updated plan is faster than patching. Protect your thinking, not the code.

**Parallel Implementations** *(continuing from the Plan + Implement Exercise)*
Same checkpoint, different approaches. Compare and select. Especially valuable when the curveball makes your first approach uncertain.

**Ground Rules** *(core — encoding step)*
Specific lessons from specific failures, saved as standing instructions the agent reads every session.

---

## Obstacles to Watch

**Sunk Cost** — "But I spent thirty minutes on this implementation!" The plan took five minutes to update. A fresh implementation from the updated plan takes ten. Patching the misaligned code takes thirty and produces something fragile.

**Context Rot** — Long sessions with many corrections degrade quality. If you're on correction cycle four or five, a fresh session with the updated plan is faster.

---

## Definition of Done

- [ ] Star data joined to exoplanet data
- [ ] Working visualization incorporating both datasets
- [ ] Plan evolved or recreated for new requirements
- [ ] At least one instance of Parallel Implementations or Happy to Delete
- [ ] Ground rules extracted from reflective dialogue with the agent (at least 2-3 meaningful rules, not boilerplate)
- [ ] Optional: share rules with a colleague, check specificity, cross-pollinate
- [ ] Can articulate: "here's what I designed, planned, built, and would do differently"

## Stretch Goals - If you finish early

- [ ] Use **Worktrees** to run Parallel Implementations in isolated branches
- [ ] Explore using **Subagents** to spawn parallel specialists for independent tasks or phases (ask Claude about it)

---

## Extract Ground Rules (Encode Step)

After building your app, ask the agent:

> "Review our conversation across this session. What ground rules would have prevented our correction cycles? What did I have to explain more than once?"

The agent reviews the session — struggles, correction cycles, workflow choices — and surfaces what would improve future sessions.

**Quality check:** Are your rules specific and actionable?

| Vague | Actionable |
|---|---|
| "Be careful with data" | "Always validate join keys before merging datasets" |
| "Write clean code" | "Run type checks before committing — fix all errors" |
| "Think before coding" | "Create PLAN.md with phases and verification criteria before implementation" |

Save rules to:
- Cursor: `.cursor/rules/`
- Claude Code: `CLAUDE.md` or `AGENTS.md`

Optionally share your rules with a colleague. What did their agent flag that yours didn't? What patterns show up across multiple people's rules? Cross-pollination reveals blind spots.

---

## Workflow Suggestion

**Phase 1: Assess + Plan** (~10 min)
Review the new dataset. Decide: evolve the plan or start fresh? Update or create `PLAN.md`. Commit.

**Phase 2: Implement** (~15-20 min)
Fresh session with updated plan. Implement. If the first approach isn't working after 2-3 corrections, Happy to Delete — restart from the plan.

**Phase 3: Ground rules** (~5-10 min)
Reflective dialogue with the agent. Extract rules. Save to rules file.

**Phase 4: Review** (~5 min)
Review your rules. Optionally share with a colleague.

---

*By the end, you should have: a working app with both datasets, an evolved plan, and a meaningful set of ground rules based on three exercises of real experience.*
