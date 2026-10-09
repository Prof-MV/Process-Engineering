# Interactive exercises — ideas and implementation plan

Scope: this book (Process Engineering). The reusable, book-agnostic version of
this work is `INTERACTIVE-EXERCISES-PROMPT.md`.

Status: **Phase 0 (library and chapter 10 pilot) is built on branch
`interactive-exercises`, awaiting review in a browser. Phases 1–4 not started.**

---

## 1. Where the book stands today

| What exists | Count | Where |
|---|---|---|
| Calculator cards (`qwebr_calc_card()` + `js/qwebr-calculator.js`) | 26 | 16 chapters |
| Bare `{webr-r}` cells without a card | ~25 | mostly 10, 11, 30 |
| `<details>` reveal blocks (discussion prompts, review questions) | ~245 | every chapter except 16, 21, 30 |
| "Fill in and get checked" exercises | **0** | — |

Three things stand out:

1. **Every interactive element is "change an input, watch the output".** The
   student never has to commit to an answer. The AON node-box exercise in the
   Sustainability book is a different kind of thing: the student does the
   method by hand and the page marks it. This book has none of those.
2. **Review Questions are reveal-only.** Each is a `<details>` whose body is
   the worked solution, so the cheapest path for a student is to open it and
   nod. Calculation questions have a single right number and could be checked.
3. **Four chapters have no calculator at all:** 13 Quality Systems,
   16 AnyLogic, 20 Working with AI, 21 Machine Learning. Chapters 16, 20 and 21
   do not load webR, so anything added there should be plain JavaScript.
   Chapter 20's "Rate These Prompts" exercise is currently a table of literal
   `________` blanks.

The AON widget itself is about 250 lines of hand-written HTML and inline
`<script>` for one exercise. Copying that pattern per exercise would not scale
to 20 chapters, so the plan starts with a small shared library.

---

## 2. Widget library (build once, reuse everywhere)

Nine widget types cover every idea in section 3. The library is called
`tryit`: `R/tryit.R`, `js/tryit.js`, `.tryit-*` CSS classes, and section
headings of the form "Try it yourself: …" (the wording the Sustainability book
already uses). Types A, B and D exist; the rest are added as phases need them.

| # | Type | What the student does | Generalises |
|---|---|---|---|
| A | **check-number** | Types a numeric answer; marked against a tolerance; hint after a miss; worked solution unlocks after an attempt | Review Questions |
| B | **fill-grid** | Fills blank cells of a table; each cell goes green or red; derived cells fill themselves | AON boxes, as a table |
| C | **fill-diagram** | Same as B, but the cells sit on nodes of a diagram with auto-drawn arrows | AON boxes |
| D | **sort-bins** | Assigns cards to categories (click-to-assign, so it works on touch and keyboard) | new |
| E | **order-steps** | Puts steps in the right sequence | new |
| F | **label-figure** | Matches numbered markers on a figure to terms | new |
| G | **challenge** | Drives an existing calculator card to a stated goal; the card checks the result | calculator cards |
| H | **sandbox** | Sets parameters, runs a stochastic simulation, compares runs | calculator cards |
| I | **scorer** | Works through a lookup-table method step by step (REBA, AP, PLr) | new |

Design rules for the library:

- **One declaration per exercise.** An R helper (`tryit_grid()`,
  `tryit_sort()`, …) in a `results='asis'` chunk emits the markup, the same way
  `qwebr_calc_card()` does. No hand-written HTML or `<script>` in chapters.
- **Answer keys are computed in R at render time** from the same data frame
  that produces the "show the solution" table, then embedded as JSON. One
  source of truth, so the checker and the printed solution cannot disagree.
- **A–F and I are plain JavaScript** with no webR dependency, so they load
  instantly and work in chapters 16, 20 and 21. Only G and H need webR.
- **Every widget degrades in PDF/EPUB** to a printable blank worksheet followed
  by the solution, using the existing `knitr::is_html_output()` pattern.
- **Fresh numbers.** An exercise never reuses the worked example's data.
  Widgets take an optional seed so a class can be split into teams with
  different datasets (`?team=3` or a small team picker).
- **Answers are in the page source.** These are practice, not assessment.
- **Graded twins for Brightspace.** Any exercise declared with a `question`
  is also written to `quizzes/tryit_<chapter>.csv` on each HTML render, in the
  Brightspace import format: numeric answers become Short Answer questions,
  sorters become Matching, orderings will become Ordering, and a fill-in table
  becomes a Written Response with the solved table as its answer key. Because
  the on-page answers are public, a twin that counts for marks should use
  different numbers: declare a second copy with `show = FALSE`, which is
  exported but not shown. `quizzes/` is gitignored, so the files are staged on
  FOL and not committed. These sit beside the existing chapter quizzes.
- **Label-figure uses numbered markers, not pixel hit-testing.** Mapping clicks
  onto a ggplot PNG is fragile; numbered markers are robust and also print.

Class use needs no backend: team seeds give each group a different problem, a
"predict first" lock hides a calculator's result until a guess is entered, and
a projector toggle enlarges the widget. Live polling is done in Brightspace,
not in the book.

---

## 3. Ideas by chapter

Mode: **S** = student alone, **C** = works well run as a class.
Effort assumes the library exists: **S** small, **M** medium, **L** large.
★ marks the one I would build first in that chapter.

### 01 Types of Manufacturing
| Idea | Type | Mode | Effort |
|---|---|---|---|
| ★ Process picker: 8 part cards (material, volume, tolerance) sorted into casting / molding / forming / machining / additive | D | S, C | S |
| Break-even challenge on the injection-molding card: find the volume where molding beats machining | G | S | S |
| Process-family ordering: route a part from raw stock to finished (cast → machine → heat treat → coat) | E | S | S |

### 02 Process and Design
| Idea | Type | Mode | Effort |
|---|---|---|---|
| ★ P&ID tag decoder: decode `FIC-101`, `PT-204`, `LAH-3` letter by letter | B | S | S |
| Three-way automation crossover: extend the fixed-automation card to plot fixed, programmable and flexible; find both crossover volumes | G | S, C | M |
| HAZOP grid: guideword × parameter matrix, fill in deviation / cause / consequence / safeguard for one node | B | C | M |
| DFA scorer: answer Boothroyd's three questions per part, get theoretical minimum part count and DFA efficiency | I | S | M |
| Deliverable sorter: assign deliverables to project phases | D | S | S |

### 03 Integrated Manufacturing Systems
| Idea | Type | Mode | Effort |
|---|---|---|---|
| ★ Line balancing board: precedence diagram, assign tasks to stations, live station time against cycle time, efficiency and balance delay | C | S, C | L |
| Station-failure sandbox: line of n stations with breakdowns, with and without buffers; compare throughput | H | C | M |
| Part-machine matrix: reorder rows and columns until cells appear (rank-order clustering) | B | S | M |

The line balancing board is the direct counterpart of the AON exercise and is
reused by chapter 04's pizza line.

### 04 Plant Layout
| Idea | Type | Mode | Effort |
|---|---|---|---|
| ★ Block-plan board: place six departments on a grid, live load-distance score; lowest score in the class wins | C | C | L |
| Pizza line balancing (reuses the chapter 03 board with different data) | C | S | S |
| Layout-type sorter: scenarios into process / product / cellular / fixed-position | D | S | S |

### 05 Lean Manufacturing
| Idea | Type | Mode | Effort |
|---|---|---|---|
| ★ VSM timeline: fill the data boxes and ladder, compute lead time, value-added time and process cycle efficiency | C | S | M |
| Waste spotter: 12 shop-floor observations sorted into the seven wastes | D | S, C | S |
| Push vs pull sandbox: same line run both ways, compare WIP and lead time (digital companion to a dice game) | H | C | M |
| SMED classifier: mark changeover steps internal or external, see the changeover time fall | D | S | M |
| Kanban sizing challenge | G | S | S |

### 06 Machine Guarding and Safety
| Idea | Type | Mode | Effort |
|---|---|---|---|
| ★ PLr risk graph walker: choose S, F, P for a scenario, arrive at the required performance level | I | S, C | M |
| Light-curtain placement: predict the minimum distance, then unlock the existing safety-distance card | G | S | S |
| Safeguard matcher: hazards to guard types and stop categories | D | S | S |

### 07 Ergonomics
| Idea | Type | Mode | Effort |
|---|---|---|---|
| ★ REBA scorer: score a posture photo step by step through Tables A, B and C; each step is checked | I | S, C | L |
| NIOSH multiplier fill-in: compute each multiplier by hand before the existing card confirms the RWL | B | S | S |
| Risk-factor spotter on a workstation figure | F | C | M |

### 08 Industrial Robotics
| Idea | Type | Mode | Effort |
|---|---|---|---|
| ★ Robot matcher: applications to configurations (SCARA, delta, 6-axis, Cartesian, cobot) | D | S | S |
| Accuracy vs repeatability: four target plots to classify | F | S | S |
| Payload challenge: find the heaviest part the robot can carry at a given offset | G | S | S |

### 09 Industrial Automation
| Idea | Type | Mode | Effort |
|---|---|---|---|
| ★ Ladder-logic stepper: toggle inputs on a start/stop seal-in rung and predict the output before each scan | C | S, C | L |
| Truth-table fill-in for three rungs | B | S | S |
| 4–20 mA scaling practice | A | S | S |
| PNP vs NPN wiring picker | F | S | M |
| Automation pyramid sorter | D | S | S |

### 10 SPC
| Idea | Type | Mode | Effort |
|---|---|---|---|
| ★ X-bar/R by hand: fill subgroup means and ranges, grand mean, R-bar and both sets of limits | B | S | M |
| Signal spotter: randomly generated control chart, mark the points that break a Western Electric rule and name the rule | F | S, C | M |
| Tampering sandbox (Deming funnel): adjust after every point and watch variation grow | H | C | M |
| Chart chooser: data descriptions sorted to X-bar/R, I-MR, p, c | D | S | S |

### 11 MSA
| Idea | Type | Mode | Effort |
|---|---|---|---|
| ★ Gauge R&R range method by hand: fill ranges, R-bar, repeatability, reproducibility, %GRR | B | S | M |
| Class GRR: paste the class's caliper readings, get the live study (pairs with the bar-stock Gauge R&R lab) | H | C | M |
| Kappa fill-in from a 2×2 agreement table | B | S | S |
| Bias / linearity / stability / repeatability sorter | D | S | S |

### 12 TPM
| Idea | Type | Mode | Effort |
|---|---|---|---|
| ★ OEE from a shift log: classify each event, then fill availability, performance, quality and OEE | B | S, C | M |
| Six Big Losses sorter | D | S | S |
| P-F curve: place detection technologies along the curve | E | S | S |

### 13 Quality Systems
| Idea | Type | Mode | Effort |
|---|---|---|---|
| ★ Audit finding classifier: 10 observations as major / minor / opportunity, with the clause | D | S, C | S |
| Cost of quality sorter with running totals per category | D | S | M |
| Clause matcher: scenarios to ISO 9001 clauses 4–10 | D | S | S |
| Document hierarchy ordering | E | S | S |

### 14 PFMEA
| Idea | Type | Mode | Effort |
|---|---|---|---|
| ★ Mode / effect / cause sorter: the distinction students most often get wrong | D | S, C | S |
| Rate and rank: assign S, O, D to five failure modes, then compare RPN ranking with Action Priority ranking | I | C | M |
| Action challenge on the before/after RPN card: reach a target with a fixed budget of actions | G | S | S |

### 15 Troubleshooting and RCA
| Idea | Type | Mode | Effort |
|---|---|---|---|
| ★ Fault tree by hand: fill the probability at each gate up to the top event | C | S | M |
| Fishbone sorter: causes into the 6M bones | D | S, C | S |
| 5 Whys chain ordering | E | S | S |
| Pareto builder: tally defects, mark the vital few | B | S | M |
| Is / Is Not sorter | D | S | S |

### 16 AnyLogic Simulation
| Idea | Type | Mode | Effort |
|---|---|---|---|
| ★ Three-station line sandbox in the browser: process times, buffers, arrival rate; throughput, WIP, utilisation | H | S, C | L |
| Paradigm sorter: problems into DES / agent-based / system dynamics | D | S | S |
| Checked practice problems 1 and 4 (takt time, AMR fleet size) | A | S | S |

### 17 Metallurgy Fundamentals
| Idea | Type | Mode | Effort |
|---|---|---|---|
| ★ Phase diagram reader: given carbon content and temperature, name the phases and fill the lever-rule fractions | B | S | M |
| Steel number decoder (AISI 1045, 4140, 1018) | A | S | S |
| Heat-treatment matcher: desired property to treatment and quench medium | D | S | S |
| Cooling-path picker on a TTT diagram | F | S, C | M |

### 18 Materials Testing
| Idea | Type | Mode | Effort |
|---|---|---|---|
| ★ Read the curve: a generated stress-strain curve; label its regions, then read off and compute E, 0.2 % yield, UTS, %EL | F + B | S | M |
| Charpy predict-first: commit to an energy ranking across temperatures before the curve is shown | G | C | S |
| Hardness scale chooser | D | S | S |

### 20 Working with AI
| Idea | Type | Mode | Effort |
|---|---|---|---|
| ★ Rate These Prompts made live: pick Bad / Medium / Good and tick the missing elements; replaces the `________` table | D | S, C | S |
| Red-flag spotter: mark the suspect claims in a sample AI answer | F | S, C | M |
| Seven-rules checklist against a student's own pasted prompt (self-assessed) | I | S | S |

### 21 Machine Learning
| Idea | Type | Mode | Effort |
|---|---|---|---|
| ★ Threshold slider: confusion matrix, precision, recall and maintenance cost as the alarm threshold moves | H | S, C | M |
| Leakage demo: row-wise vs unit-wise split on the same data, compare reported accuracy | H | C | M |
| Rolling-window feature explorer | H | S | M |
| Self-check questions with self-rating before reveal | A | S | S |

### Across all chapters
| Idea | Type | Mode | Effort |
|---|---|---|---|
| Convert every calculation Review Question to answer-then-reveal | A | S | S each |
| Add one goal to each of the 26 existing calculator cards | G | S | S each |

---

## 4. Implementation phases

Each phase ends with something visible in a rendered chapter.

**Phase 0 — Library and pilot. (Built; review pending.)**
`js/tryit.js`, `R/tryit.R` (sourced from `R/helpers.R`) and a `tryit` section
in `style.css`, with types A, B and D and the Brightspace export. Pilot in
chapter 10: X-bar/R by hand (B), chart chooser (D), Review Questions 4–6
checked (A). Review the pilot in a browser before going further; the API is
cheapest to change now.

**Phase 1 — Broad, cheap pass.**
Types A, D and E across all chapters: checked calculation questions, plus the
sorters and orderings in section 3. Add type G to the calculator runtime and
one goal per existing card. This reaches every chapter, including the four with
no calculator today.

**Phase 2 — Diagram exercises.**
Add type C. Build the line balancing board (03, reused in 04), fault tree (15),
VSM timeline (05), then the block-plan board (04) and ladder stepper (09).

**Phase 3 — Scorers and figures.**
Add types F and I. REBA scorer (07), PLr walker (06), rate-and-rank (14),
signal spotter (10), read-the-curve (18), phase diagram reader (17).

**Phase 4 — Sandboxes and class mode.**
Add type H and team seeds. Station-failure line (03), push vs pull (05),
tampering funnel (10), class GRR (11), three-station line (16), threshold
slider and leakage demo (21).

Working rules for every phase:

- One branch per phase, one commit per chapter.
- After each chapter: `quarto render <chapter>.qmd --to html`, open it, and
  exercise each widget with a right answer, a wrong answer and reset. Then
  render the PDF once per phase to confirm the fallbacks.
- No more than three or four widgets per chapter. An exercise earns its place
  by making the student do the step a learning objective names.

## 5. Decisions made

1. **Names.** `tryit`, as described in section 2.
2. **Graded twins.** Yes, exported automatically as described in section 2.
3. **Order of books.** This book first, then `../Sustainability_BusinessPractices`,
   then `../DesignForManufacturing`. The later books copy the library from
   here. In the Sustainability book the hand-written AON exercise should be
   re-expressed as a type C declaration once that type exists.
4. **Live polling.** Done in Brightspace; nothing to build.
