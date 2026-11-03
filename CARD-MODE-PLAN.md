# Calculator cards: demo or task

Every `qwebr_calc_card()` is now either a **demo** (the instructor drives it on the projector:
every scalar input is a slider, no `goal`; a table may drive it) or a **task** (students work it
on their own devices; it needs a `goal`/`goal_test`). `qwebr_calc_card()` stops the render if a
demo has a goal or a non-slider input (the `rerun` seed input is exempt), or if a task has no goal.

Decisions made by the author: table-driven demos are allowed (the skill was updated); where a
demo had a goal, the goal moves to the later or student version of the same concept, otherwise it
is dropped; `reba-step-by-step` stays one student task; the five review-answer cards are dropped.

## Result: 55 cards (was 61)

| Mode | Cards |
|---|---|
| Demo | 28 |
| Task | 27 |
| Unmarked | 0 |
| Removed | 6 |

## Demo (28)

| Ch | Card | Change |
|---|---|---|
| 2 | `dfa-example` | table demo, no scalar inputs |
| 3 | `payload-calc` | sliders, goal dropped, fixed-axis load chart added |
| 4 | `reba-example` | all 12 scores are sliders, risk-band chart added |
| 5 | `bias-calculation`, `linearity-calc`, `stability-control-chart`, `range-method` | table demos; scalar inputs now sliders |
| 6 | `metallurgy-lever-rule-live` | sliders, goal dropped, phase-fraction chart added |
| 7 | `testing-brittle-example-live`, `testing-vickers-live`, `testing-case-depth-live` | sliders with tighter ranges, fixed-axis charts added |
| 8 | `load-distance-calc`, `peak-people`, `line-balance-calc` | sliders, charts with fixed axes |
| 9 | `funnel-sim`, `cp-cpk-live`, `xbar-r-live`, `imr-live`, `p-chart-live`, `c-chart-live` | sliders; funnel axes fixed; Cp/Cpk goal dropped (the task twin is `cpk-ppk-calc`, ch 18) |
| 11 | `alarm-threshold` | sliders with tighter cost ranges, goal dropped, axes fixed |
| 14 | `rpn-calculation` | nine sliders, axis fixed to 0-1000 |
| 15 | `takt-calculation` | sliders, goal dropped (task twin `takt-vs-cycle`, ch 20), takt-against-demand chart added |
| 17 | `msa-capability-effect` | %GRR of both gauges are now inputs; goal dropped |
| 20 | `line-balance-example`, `downtime-analysis` | table demos with sliders |
| 21 | `pareto-interpretation` | table demo |
| 22 | `vfd-calculations` | sliders, goal dropped, axes fixed |

## Task (27)

Already had a goal (24): 1 `injection-molding-cost`; 2 `fixed-automation-economics`; 3 `gripper-selection`;
4 `niosh-example`; 5 `resolution-check`; 7 `testing-modulus-example-live`; 8 `niosh-example-plant`;
12 `safety-calc-example`; 13 `oee-calculation`; 14 `rpn-improvement`, `case-study-improvement`;
15 `push-pull-sim`; 17 `type1-gauge`, `attribute-rates`, `uncertainty-calc`; 18 `xbar-s-limits`,
`cpk-ppk-calc`, `arl-sim`; 19 `des-line-sim`; 20 `takt-vs-cycle`, `mct-mce`, `line-buffer-sim`;
21 `fta-calculation`; 22 `scan-time-calc`.

New goals written and checked with `challenge_check.R` (3):

| Ch | Card | Goal |
|---|---|---|
| 4 | `reba-step-by-step` | bring the final REBA score to 7 or less leaving the posture scores and Table C alone (remove the repeated-actions condition) |
| 4 | `roi-analysis` | find the annual injury saving at which the payback period is 1 year, everything else at default |
| 8 | `peak-costbenefit` | find the number of rush nights at which Option 1 becomes the better choice (this was the chapter's existing "Try It Yourself" challenge) |

## Removed (6)

The review-answer cards `q5-answer` (ch 3), `q3-answer` (ch 5), `q6-answer` (ch 16), `q7-answer` (ch 17),
`q4-answer` (ch 22) and `pareto-practice` (ch 21, also inside a review answer). The worked solution stays:
each is now a static R chunk with its code and output visible, so no calculation was lost.

Correction to the earlier plan: those review questions have no `tryit_number()`, so they are not
yet answer-then-reveal problems. The static solutions are a stop-gap; converting each to a
`tryit_number()` card with a Brightspace twin would bring them in line with the skill.

## Also changed

- `R/helpers.R`: `qwebr_calc_card(mode = )`, badge, validation, and slider read-outs that repeat prefix/suffix.
- `js/qwebr-calculator.js`: slider read-out uses the prefix/suffix and space thousands separators.
- `style.css`: `.qwebr-calc-badge`, `.qwebr-calc-demo`, `.qwebr-calc-task`.
- `peak-costbenefit`: the first line of the cell held four variables; split to one per line so the card and the checker can find each input.
- Skill (`SKILL.md`): demos may be table-driven; where a goal moves; one REBA-style worksheet stays one task.
