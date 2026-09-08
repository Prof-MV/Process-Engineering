# Handover: expand ENGR-3027 to 14 browser-only labs

**Read this whole file before touching anything.** It is written to be executed
by a session with no prior context. Line numbers are as of commit `1e99674`;
re-grep before editing.

---

## 1. Orientation

| | |
|---|---|
| Repo | `c:\Users\mvolk\OneDrive\Documents\Textbooks_MV\ProcessEngineering` |
| What it is | A Quarto **book** (`_quarto.yml`, `project.type: book`, `output-dir: docs`) that doubles as lecture notes for **ENGR-3027 Process Engineering**, Fanshawe College, program EMN |
| Audience | Second-year electromechanical/mechanical engineering technology students, heading into automotive, food and defence |
| Formats | HTML (`style.css`), PDF (xelatex, `preamble.tex`), EPUB |
| Interactivity | webR via the `coatless/webr` extension — 38 `{webr-r}` cells across 15 chapters |
| Illustration language | **R/ggplot2** for figures in chapters. Students are never asked to write R. Student-facing code is **Python in Google Colab**, and Ch 21 explicitly says students *direct an LLM* to write it |
| Gitignored | `LabInstructions/` (prior-term handouts, decks, the official course plan), `docs/`, `quizzes/`, `.claude/` |
| Data files | **None are committed.** Every dataset is "staged on FOL" (Fanshawe's D2L/Brightspace) |

Author/instructor is the user. All decisions in §3 are theirs, already made —
do not relitigate them.

---

## 2. Why this work exists

`30-Labs.qmd` defines **10 labs**; the FOL grade book budgets **12 slots**. Most
of the second half of the book has no lab at all — Ch 5 (Lean), Ch 10 (SPC),
Ch 11 (MSA), Ch 12 (TPM/OEE), Ch 15 (RCA) are lecture-only. The instructor
wants roughly three more weeks of labs.

**Hard constraint: no robots, no PLCs, no lab hardware, no software installs.**
Everything must be free and run in a browser. That rules out Webots,
CoppeliaSim, OpenPLC Editor and Factory I/O. Four tools were verified free and
browser-based:

| Tool | Verified | Used by |
|---|---|---|
| [RoboDK for Web](https://web.robodk.com/simulation) | Free, no install, **no licence key**, 600+ arms from 50+ makers | Lab 14 |
| [AnyLogic Cloud](https://www.anylogic.com/features/cloud/) | Free public tier, in-browser runs with editable input parameters | Lab 4 |
| [AI4I 2020](https://archive.ics.uci.edu/dataset/601/ai4i+2020+predictive+maintenance+dataset) | UCI, CC BY 4.0, 10 000 rows, 5 labelled failure modes | Lab 13 |
| webR (already installed) | The `coatless/webr` extension is in `_extensions/` | Lab 6 |

### The real course calendar — this drove the design

`LabInstructions/ENGR-3027-25F_CP.docx` is the authoritative course plan. Key
facts (extract it with `python -c` + `zipfile` on `word/document.xml`; there is
no PDF reader in this environment):

- The term is **14 weeks, not 15**.
- **Week 7 = Midterm Test.** No lab was scheduled. The midterm is in *lecture*
  time, so the lab period that week is actually free.
- **Week 14 = Final Test**, plus a make-up lab slot.
- **Lab 12 was a take-home lab, released week 11, due week 14, video
  submission.** This precedent is what makes a 14th lab possible.
- 12 labs at ~3.33 % each; Labs 1–10 mandatory; 25 %/session late penalty;
  "all work assigned before Week 7 must be completed by the end of Week 7".
- `LabInstructions/ENGR-3027 - Class Notes 25S.html` shows a prior offering
  running Lab 1 in **week 1**, so week 1's lab period is usable.

Mapping the current 10 labs onto that plan leaves only **two** free slots.
Using the week-7 lab period and week 1 as well gives **four**.

---

## 3. Decisions already made by the instructor

1. Topics: **SPC + MSA**, **Lean/TPM-OEE/RCA**, **robotics work cell**, and a
   **second ML dataset** — all four, as four separate labs.
2. **Browser-only.** No installs on lab PCs.
3. Gauge R&R uses an **in-book webR "virtual caliper"**, not paper or a
   pre-supplied dataset.
4. **Rearranging and renumbering labs is approved** — "feel free to re-arrange
   the labs to ensure a good flow."
5. Fill the three `TODO` rubrics.
6. Ship an **instructor prep document that renders to PDF** for FOL, for the
   next person teaching the course.
7. **Delete the grade breakdown from the book** — Brightspace is the single
   source of truth. Provide a grade-*item* list instead so FOL can be verified.
8. Rewrite the blanket AI ban into an explicit per-assessment policy.
9. **Week 7 runs a lab.** The midterm is written during *lecture* time, so the
   lab period that week goes ahead normally. Lab 7 is scheduled there
   deliberately — do not "helpfully" drop it to give students a clear week.

---

## 4. Target lab map

Lab number = week number. New labs in **bold**.

| # | Week | Lab | Prereq ch. | Was |
|---|---|---|---|---|
| 1 | 1 | Logic Thinking for Robot Control — LightBot & Rocksi | — | 1 |
| 2 | 2 | Engineering Design Process Documentation | 2, 4 | 2 |
| 3 | 3 | Manufacturing Facility Design & Simulation (AnyLogic) | 4, 16 | 3 |
| **4** | **4** | **Lean: Value Stream Mapping, Takt and Pull** | **3, 5** | — |
| 5 | 5 | Ergonomics in Automated Manufacturing (REBA & Inseer) | 7 | 4 |
| **6** | **6** | **SPC and Gauge R&R — the Virtual Caliper** | **10, 11** | — |
| 7 | 7 | ML Week 1 — AI literacy & prompt engineering | 20 | 5 |
| 8 | 8 | ML Week 2 — Manufacturing data & SPC | 21 | 6 |
| 9 | 9 | ML Week 3 — The C-MAPSS dataset | 21 | 7 |
| 10 | 10 | ML Week 4 — Building the model | 21 | 8 |
| 11 | 11 | ML Week 5 — Deploying the app | 21 | 9 |
| 12 | 12 | ML Week 6 — Capstone presentations | 21 | 10 |
| **13** | **13** | **TPM/OEE, Root Cause and a New Dataset** | **12, 15, 21** | — |
| **14** | **14** | **Robotic Work-Cell Design — RoboDK for Web** *(take-home, released wk 11)* | **3, 6, 8** | — |

**Rationale — preserve this reasoning in the lab text:**

- Lab 7 sits in midterm week *on purpose*, **confirmed by the instructor**: the
  midterm is written during lecture time, so the week-7 lab period runs as
  normal. ML Week 1 is the right lab for it — individual, browser-only, no
  dataset, no prep beyond a login, the lightest in the set.
- Lab 6 (SPC/R&R **by hand**) precedes Lab 8 (SPC **in Python**) by two weeks.
  That is deliberately the arc Ch 21 is built on: *do it yourself first, then
  direct an LLM to do it.*
- Lab 13 must follow the capstone — it reuses the ML pipeline on an unseen
  dataset, which only works once students have the skill.
- Lab 14 is the take-home, reusing the course plan's existing Lab-12 pattern.
  RoboDK for Web needs no install, so it genuinely works from home. It also
  bookends Lab 1: toy logic in week 1, a real industrial arm in week 14.

---

## 5. Lecture reorder

The current chapter order breaks two labs badly:

- **Ch 16 (AnyLogic) is chapter 16, but Lab 3 runs in week 3** — students
  currently simulate before any simulation lecture.
- **Ch 20 + 21 (AI, ML) are last, but the ML labs run weeks 7–12**, and Ch 21
  is explicitly a six-week module of "2 h theory + 2 h lab per week".

Target grid — every lab's prerequisite chapter now precedes it:

| Wk | Lecture | Lab |
|---|---|---|
| 1 | Ch 1 Types of Manufacturing | Lab 1 LightBot & Rocksi |
| 2 | Ch 2 Process & Design · Ch 8 Industrial Robotics | Lab 2 Design Documentation |
| 3 | Ch 4 Plant Layout · Ch 16 AnyLogic Simulation | Lab 3 Facility Design & Simulation |
| 4 | Ch 3 Integrated Mfg Systems · Ch 5 Lean | **Lab 4 Lean VSM** |
| 5 | Ch 7 Ergonomics · Ch 6 Guarding & Safety pt 1 | Lab 5 Ergonomics |
| 6 | Ch 10 SPC · Ch 11 MSA | **Lab 6 SPC & Gauge R&R** |
| 7 | **Midterm** · Ch 20 Working with AI | Lab 7 ML W1 |
| 8 | Ch 21 Weeks 1–2 | Lab 8 ML W2 |
| 9 | Ch 21 Week 3 · Ch 12 TPM | Lab 9 ML W3 |
| 10 | Ch 21 Week 4 · Ch 15 Troubleshooting & RCA | Lab 10 ML W4 |
| 11 | Ch 21 Week 5 · Ch 6 Safety pt 2 · Ch 9 Automation | Lab 11 ML W5 — **release Lab 14** |
| 12 | Ch 21 Week 6 · Ch 13 Quality Systems | Lab 12 ML Capstone |
| 13 | Ch 14 PFMEA | **Lab 13 TPM/OEE & RCA** |
| 14 | **Final Test** · review | **Lab 14 RoboDK due** |

> **Caveat for the instructor, not a blocker.** This grid is inferred. The 25F
> course plan has only 7 units while the book has 18 chapters, so the
> chapter→week mapping is a reconstruction, not the college's own sequence.
> Confirm it against what is actually taught before publishing it to students.

Reorder `_quarto.yml`'s `chapters:` list to:

```
index.qmd, 01-Types-of-Manufacturing.qmd, 02-Process-and-Design.qmd,
08-Industrial-Robotics.qmd, 04-Plant-Layout.qmd, 16-AnyLogic-Simulation.qmd,
03-Integrated-Manufacturing-Systems.qmd, 05-Lean-Manufacturing.qmd,
07-Ergnomics.qmd, 06-Machine-Guarding-and-Safety.qmd, 10-SPC.qmd, 11-MSA.qmd,
20-Working-with-AI.qmd, 21-Machine-Learning.qmd, 12-TPM.qmd,
15-Troubleshooting-RCA.qmd, 09-Industrial-Automation.qmd,
13-Quality-Systems.qmd, 14-PFMEA.qmd, 30-Labs.qmd
```

**Do NOT rename the files.** Quarto cross-references are label-based
(`@sec-chap-ml`, `@eq-ml-cpk`), so reordering the list is safe and touches one
file; renaming churns git history for no functional gain. Add a comment at the
top of `_quarto.yml` saying the numeric filename prefixes are historical and no
longer indicate order — otherwise the next maintainer will "fix" it.
(`07-Ergnomics.qmd` is misspelled in the repo. Leave it.)

---

## 6. House style — replicate exactly

### The eight-part lab skeleton

Every lab in `30-Labs.qmd` uses this. The `###` headings intentionally
duplicate the div banner text because PDF/EPUB do not render the CSS
`::before` labels (documented at `style.css:96–97`). Every lab ends with `---`.

````markdown
## Lab N — <Title> {#sec-lab-<slug>}

::: {.lab-overview}
<2–5 sentence framing paragraph; names the software in **bold**>
:::

### Learning outcomes

::: {.lab-outcomes}
After this lab you should be able to:

- <verb-first bullet>
:::

### Prep work

::: {.lab-prep}
- Read ...
- Watch ...
:::

### Materials & equipment

::: {.lab-materials}
- ...
:::

### Procedure

::: {.lab-procedure}
**Task 1 — <name> (<minutes>).** ... *(N marks)*
:::

### Deliverables & submission

::: {.lab-deliverables}
... Submit on FOL by the end of the lab period.
:::

### Rubric

::: {.lab-rubric}
| Deliverable | Marks |
|---|---|
:::

### Instructor notes

::: {.lab-instructor}
- **Prep:** ...
- **Marking:** ...
:::

---
````

All `.lab-*` classes already exist in `style.css:98–204`. **No CSS changes are
needed.** Available: `.lab-overview`, `.lab-outcomes`, `.lab-prep`,
`.lab-materials`, `.lab-procedure`, `.lab-deliverables`, `.lab-rubric`,
`.lab-instructor`, `.lab-shop`.

### Conventions

- **Canadian/British spelling** throughout (optimising, colour, labelled, µm).
- Em dashes, `≈`, `±`, `×` as literal Unicode.
- Marks inline in Procedure as `*(N marks)*`; minute budgets per task.
- Every lab set at **Précitech Components** (see below).
- YouTube via an `{r video-labN, echo=FALSE, results='asis'}` chunk calling
  `embed_youtube("<id>", "<title>")` from `R/helpers.R`.

### The course narrative — reuse it, do not invent a new one

**Précitech Components**, Tier-1 automotive supplier, Granby QC. CNC turning
cells make transmission **shaft blanks**, AISI 4140, **Ø 25.000 ± 0.050 mm**.
A kit = 1 shaft + 2 tapered roller bearings + 1 retaining ring + 1 lip seal +
1 dowel pin + 1 desiccant sachet, in a moulded tray in a labelled carton.
**Target 250 kits/day on one 8-hour shift.** Plant manager **Sophie Tran**.
Full case study at `30-Labs.qmd:206` (`{#sec-precitech-case}`).

---

## 7. Work items

### 7.1 `30-Labs.qmd` — renumber

~50 cross-references. **Ch 21 contains no lab-number references** (verified by
grep), so the blast radius is this file plus `index.qmd`.

- Six ML lab headings, 5–10 → 7–12, at lines 649, 779, 910, 1024, 1147, 1252.
- `## Lab 4 — Ergonomics …` → `## Lab 5 — …` at line 490.
- Back-references through the ML block: lines 595–596, 655, 736, 768, 774, 782,
  802, 813, 903, 1005, 1017, 1047, 1055, 1112, 1126, 1136, 1172, 1182, 1195,
  1233, 1284, 1318, 1349.
- Teacher-preparation checklist, lines 1441–1481.
- Rewrite the master map in the `callout-important` at lines 39–71 to the §4
  table.

### 7.2 `30-Labs.qmd` — add stable anchors

Give **every** lab heading an explicit `{#sec-lab-<slug>}` ID. This fixes the
fragile auto-generated link at `30-Labs.qmd:201`
(`#lab-3-manufacturing-facility-design-simulation-anylogic`), which breaks the
moment a title changes, and makes future renumbering safe.

### 7.3 `30-Labs.qmd` — write the four new labs

#### Lab 4 (week 4) — Lean: VSM, Takt and Pull

Teams of 2–3. [draw.io](https://app.diagrams.net), AnyLogic Cloud, Google
Sheets. Data: `vsm_station_data.csv` (§7.7).

1. *(30 min, 3 marks)* Current-state VSM in draw.io for the Précitech shaft
   line — CNC turn → deburr → wash → inspect → the Lab 2 kitting cell — from
   the supplied station table (C/T, C/O, uptime, WIP, batch size).
2. *(20 min, 2 marks)* Takt from customer demand; operator balance chart vs
   takt in Sheets; name the bottleneck.
3. *(25 min, 2 marks)* Classify waste against the seven wastes; compute process
   cycle efficiency (VA time ÷ lead time).
4. *(25 min, 2 marks)* Push-vs-pull model on AnyLogic Cloud; record WIP and
   lead time for push, pull, and a kanban-capped supermarket.
5. *(20 min, 1 mark)* Future-state VSM with one SMED and one pull change;
   justify the projected lead-time reduction.

Reuses Ch 5 takt material and Ch 3 line balancing. **10 marks.**

#### Lab 6 (week 6) — SPC and Gauge R&R: the Virtual Caliper

**The one net-new piece of software, and it lives inside the textbook.** Groups
of exactly 3 (the three operators). Tool: webR cells in this chapter.

A `draw_caliper(part, trial)` function renders a vernier caliper scale at a
seeded true value; students read the scale and type the value. This produces
*genuine human reading error* against *known ground truth*, so bias, linearity,
repeatability and reproducibility are all computable — something a physical
Gauge R&R cannot do. It has zero third-party dependency, which directly
addresses the risk Lab 1's own instructor notes flag at `30-Labs.qmd:181`
("third-party sites … the single point of failure").

> **Two implementation constraints.**
>
> 1. **Base R graphics only — no ggplot2.** `_quarto.yml` has no global `webr:`
>    package configuration, and loading packages in webR is slow and fragile.
> 2. `coatless/webr` cells **share one global environment per page**, so the
>    setup cell must be run first. Say so in the Procedure.

1. *(10 min)* Run the setup cell; practise on three demo calipers with printed
   answers.
2. *(35 min, 2 marks)* Each operator reads all 10 parts × 3 trials, blind, in
   randomised order → 90 readings.
3. *(20 min, 3 marks)* Range-method Gauge R&R: EV, AV, GRR, PV, TV, %GRR, ndc.
   **Reuse the method already coded in `11-MSA.qmd`** — cells `range-method`
   and `bias-calculation` (line 291).
4. *(15 min, 1 mark)* Bias and linearity against known true values.
5. *(25 min, 3 marks)* X-bar/R chart and Cpk on a seeded 25-subgroup dataset vs
   Ø 25.000 ± 0.050 mm; apply the Ch 10 Western Electric rules.
6. *(15 min, 1 mark)* Reflection: is the gauge acceptable (%GRR < 10 / 10–30 /
   > 30; ndc ≥ 5)? What does an inadequate gauge do to the Cpk just computed?

**10 marks.**

#### Lab 13 (week 13) — TPM/OEE, Root Cause and a New Dataset

Teams of 2–3. Sheets, draw.io, Google Colab. Data: **AI4I 2020** from UCI
(students download in-browser) + `precitech_shift_log.csv` (§7.7).

1. *(25 min, 2 marks)* OEE from the shift log — availability × performance ×
   quality — and attribute losses to the Six Big Losses (Ch 12 method).
2. *(20 min, 1 mark)* Pareto the five AI4I failure modes (TWF, HDF, PWF, OSF,
   RNF) in Sheets; identify the vital few.
3. *(25 min, 2 marks)* 5-Why + Ishikawa in draw.io on the top failure mode,
   using the real feature columns (tool wear, torque, rotational speed, air vs
   process temperature) as evidence. Ch 15 method.
4. *(35 min, 4 marks)* **Direct an LLM** to build a failure classifier on AI4I
   2020 in Colab. This is *classification* on a differently-shaped dataset, so
   the C-MAPSS recipe cannot be copied. Report confusion matrix and
   precision/recall, and state explicitly which class-imbalance trap was hit —
   the failure rate is ~3.4 %, so **accuracy is a useless metric here. That is
   the lesson.**
5. *(15 min, 1 mark)* Write the 8D "D4 root cause / D5 corrective action"
   sections tying feature importances back to the fishbone.

**10 marks.** This lab is also the fix for the dangling cross-reference at
`30-Labs.qmd:1398`, which promises "stretch goals" in Ch 21 that do not exist.
Rewrite that paragraph to point at Lab 13 and list the genuinely optional
extras (XGBoost, SHAP, FD002 generalisation, prediction intervals).

#### Lab 14 (week 14) — Robotic Work-Cell Design in RoboDK for Web

**Take-home**, released week 11, due end of week 14. Individual. Submission
includes a short screen recording, matching the course plan's existing
take-home precedent.

1. *(20 min, 1 mark)* Load a 6-axis arm; jog in joint vs linear vs tool
   coordinates; observe singularities and joint limits. Ties to Ch 8 coordinate
   systems and back to Lab 1's teach-pendant work.
2. *(30 min, 2 marks)* Build the Précitech kitting cell — robot, infeed
   conveyor, bearing-press station, tray. Verify every pick and place point is
   inside the reach envelope; record the reach limit that forces a layout
   change.
3. *(30 min, 3 marks)* Program the pick-and-place with targets and gripper
   open/close; run it; record simulated cycle time.
4. *(25 min, 3 marks)* Compare cycle time against the **takt computed in Lab 4**
   for 250 kits/day. Does one robot meet takt? Optimise — reorder targets,
   raise joint speed, shorten approach moves — and record the improved time.
5. *(15 min, 1 mark)* Mark the safety perimeter: compute minimum guarding
   distance from stopping time using the Ch 6 formula, and state which Ch 6
   safeguard you would specify.

**10 marks.**

### 7.4 `30-Labs.qmd` — fill the three `TODO` rubrics

Three rubrics are literal `TODO` placeholders. Each table below keeps the mark
split the chapter already suggests and adds the criterion detail needed to mark
consistently.

**Lab 5 — Ergonomics (was Lab 4) — 10 marks**

| Criterion | Marks |
|---|---|
| Procedure followed; all three assigned tasks assessed | 1 |
| REBA scoring — correct Table A/B/C lookups, coupling and activity adjustments, final score and risk band for each of the three tasks | 4 |
| Inseer report — assessment run, output correctly read and quoted | 2 |
| Manual vs automated comparison — quantified, references the Ch 7 risk factors | 2 |
| Conclusion and recommended controls, ordered by the hierarchy of controls | 1 |

**Lab 7 — ML Week 1 (was Lab 5) — 10 marks**

| Criterion | Marks |
|---|---|
| `prompts.md` — five prompts rewritten with all five R-C-T-C-F elements present | 3 |
| FMEA summarised at three audiences — audience-appropriate and technically accurate | 2 |
| Hallucination hunt — a fabrication documented, **with evidence of how it was verified** | 3 |
| `spc_starter.py` runs, is commented, and the student can explain it on request | 2 |

**Lab 8 — ML Week 2 (was Lab 6) — 10 marks**

| Criterion | Marks |
|---|---|
| Week 1 code runs against the real dataset | 1 |
| All five data-quality issues found; `quality_log` complete (row_index, column, original, corrected, reason, action); the days 43–47 special cause correctly **kept, not deleted** | 4 |
| X-bar chart with correct control limits — `sigma / sqrt(n)`, **not** the std of daily means | 3 |
| Cpk against USL 25.050 / LSL 24.950, in the expected 1.1–1.2 range and interpreted | 1 |
| Reflection | 1 |

### 7.5 `index.qmd` — remove weights, fix policy

- **Delete the grade breakdown table (lines 56–95).** FOL is the single source
  of truth; two copies means one is wrong the moment weights are tuned, and
  this change already breaks it (12 labs → 14). Replace with:

  > Grade items and their weights are maintained in FOL and are the single
  > source of truth. The course schedule below shows what is assessed and when;
  > for current weights and marks, check the FOL grade book.

- Keep `## Labs {-}` / `## Assignments {-}` / `## Quizzes {-}` / `## Tests {-}`
  — they carry *policy* (late penalties, attendance, open-book rules) — but
  strip any restated weight numbers the grade book owns.
- Line 99: "Labs 1-5 must be completed before Week 7" → **"Labs 1–6 must be
  completed before Week 7"**.
- Line 122: "mandatory labs (labs 1 though 10)" → **"labs 1 through 12"**,
  preserving the original structure of the last two labs being non-mandatory,
  and fixing the "though" typo.
- Add a `## Course schedule {-}` section with the §5 grid.
- **Replace the blanket AI ban at line 132** — see §7.6.

### 7.6 The AI policy rewrite

`index.qmd:132` currently reads "**This includes the use of 'AI' Technologies**"
as a blanket ban, while Labs 7–13 *require* an LLM. As written those two
statements contradict each other — the wrong footing for an integrity dispute.

The college statement is the hook that makes this fixable: generative AI "may
not be used … **without securing prior consent from the instructor**." A
documented per-assessment policy *is* that prior consent. Replace with:

> **Use of generative AI**
>
> Fanshawe policy A136 permits generative AI in this course only where the
> instructor has given prior consent. This section is that consent, and it is
> specific: for each assessment below, AI use is either **required**,
> **permitted with disclosure**, or **not permitted**. If an assessment is not
> listed, treat it as **not permitted** and ask.
>
> Where AI is **permitted or required**, you must still be able to explain
> every line you submit. If you are asked "why does this line do that?" and
> cannot answer, that work does not count as yours — regardless of whether it
> runs correctly.
>
> Where AI use is **permitted with disclosure**, add a short note naming the
> tool and what you used it for.

| Assessment | AI use | Why |
|---|---|---|
| Lab 1 — LightBot & Rocksi | **Not permitted** | The outcome *is* your own logic; an AI solving the puzzle removes the lab |
| Lab 2 — Design Documentation | **Not permitted** | Already stated in the lab |
| Lab 3 — AnyLogic Simulation | **Not permitted** | Already stated in the lab |
| Lab 4 — Lean VSM | Permitted with disclosure | Not for the map or the takt/PCE calculations |
| Lab 5 — Ergonomics | Permitted with disclosure | **Inseer is itself an AI tool and is required** — that is a lab instrument, not a generative AI writing your report |
| Lab 6 — SPC & Gauge R&R | **Not permitted** for readings and calculations; permitted for checking your written reflection | You are the measurement system being studied |
| Labs 7–12 — ML module | **Required** | You are assessed on directing an LLM well, not on writing Python |
| Lab 13 — TPM/OEE & RCA | **Required** for the classifier task; permitted with disclosure elsewhere | Same skill, unfamiliar dataset |
| Lab 14 — RoboDK work cell | Permitted with disclosure | The station, program and cycle times must be your own |
| Assignments 1–6 | Permitted with disclosure | |
| Pop quizzes, midterm, final | **Not permitted** | Closed-book, in-person |

Also add a **one-line AI status to each lab's `.lab-overview`** in
`30-Labs.qmd`, so a student reading a single lab sees it without going back to
`index.qmd`. Mirror the table into the instructor handbook.

### 7.7 `R/make_lab_data.R` (new)

One seeded generator the instructor runs once a term. Follows the repo
convention that lab data is staged on FOL, not committed.

Emits:

- `vsm_station_data.csv` — Lab 4 station table (C/T, C/O, uptime, WIP, batch).
- `precitech_shift_log.csv` — Lab 13 OEE shift log.

And prints the **Lab 6 answer key** (true caliper values, expected %GRR, ndc,
Cpk). Everything `set.seed()`-ed so answer keys stay valid across terms. Lab 6's
caliper and SPC data are generated inside the webR cell, so no file is needed.

### 7.8 `instructor/` (new) — the handbook

The next person teaching the course needs one uploadable document, including
material that must **not** appear in the student book.

Create `instructor/` as a **separate Quarto project** so the book render never
picks it up:

- `instructor/_quarto.yml` — `project: {type: default}`, `format: pdf`
  (xelatex, reusing `../preamble.tex`). A book project renders only files
  listed in `book.chapters`, and a subdirectory with its own `_quarto.yml` is
  isolated regardless — belt and braces.
- `instructor/instructor-guide.qmd` → `instructor/instructor-guide.pdf`, the
  file to upload to FOL.

Contents, in order:

1. **Quickstart** — "first time teaching this course", one page.
2. **Term grid** — the §5 lecture/lab table.
3. **Grade-item checklist** — §7.9.
4. **Paste-ready Course Plan Note 1 and Note 2** — §7.10.
5. **AI-use policy table** — mirrored from §7.6.
6. **Per-lab prep matrix** — room, software, accounts, data files, printing,
   for all 14 labs. Extends the existing `.lab-shop` matrix at
   `30-Labs.qmd:~1420` rather than replacing it.
7. **Data generation** — how to run `Rscript R/make_lab_data.R`, what it emits,
   which FOL folder each file goes in.
8. **Answer keys** — Lab 6 true caliper values and expected %GRR/ndc/Cpk;
   Lab 4 expected takt, PCE, bottleneck; Lab 13 expected OEE and Pareto order;
   Lab 14 expected cycle-time range.
9. **Rubric quick reference** — all 14 rubrics for marking.
10. **Software and accounts checklist** — exact URLs to test through the college
    firewall *the day before* each lab.
11. **Known failure modes and fallbacks** — per lab, extending the pattern
    already used in Lab 1's instructor notes.

### 7.9 Grade-item checklist (goes in the handbook)

**Deliberately no weights** — this verifies the right *items* exist with the
right names. Weights are Brightspace's alone.

| # | Grade item | Category | Type | Due |
|---|---|---|---|---|
| 1–14 | `Lab-1` … `Lab-14` | Lab-Tutorial | Numeric, submission | End of lab period, weeks 1–14 |
| 15–20 | `Assignment-1` … `Assignment-6` | Assignments | Numeric, quiz | Friday 23:59 of assigned week |
| 21–26 | `Lab Quiz-1` … `Lab Quiz-6` | Lab Pop-up Quizzes | Numeric, quiz | Random, 10-min login window |
| 27–32 | `Lecture Quiz-1` … `Lecture Quiz-6` | Lecture Pop-up Quizzes | Numeric, quiz | Random |
| 33 | `Mid Term Test` | Midterm Test | Numeric, quiz | Week 7 |
| 34 | `Final Test` | Final Test | Numeric, quiz | Week 14 |

**34 items in 6 categories.** The only change from the current FOL setup is two
new lab items: **`Lab-13` and `Lab-14`**. `Lab-14` is the take-home — released
week 11, due end of week 14 — so it needs a different availability window from
the other 13.

### 7.10 Course Plan notes (paste-ready, for the handbook)

`LabInstructions/ENGR-3027-25F_CP.docx` is gitignored and is not rendered from
this repo, so these are paste-ready blocks for whoever maintains it.

*Note: Note 1's pop-quiz figures are already self-consistent — "12 pop quizzes
at 0.5 % each" and the 6 lecture + 6 lab breakdown both reconcile to the
chart's 3 % + 3 %. Only the lab count and per-lab weight change.*

> **NOTE 1: ASSESSMENTS**
>
> There are 12 pop quizzes worth 0.5 % each: 6 at the end of lectures and 6 at
> the start of labs. Lab quizzes have a 10-minute login window starting at the
> beginning of the lab period. You must be in attendance at the lecture or lab
> to earn credit for the quiz.
>
> | Component | Detail | Weight |
> |---|---|---|
> | Lab activities | **14 labs, ~2.86 % each** | 40 % |
> | Assignments | 6 assignments, 2 % each | 12 % |
> | Lecture pop quizzes | 6 × 0.5 % | 3 % |
> | Lab pop quizzes | 6 × 0.5 % | 3 % |
> | Midterm test (week 7) | — | 17 % |
> | Final test (week 14) | — | 25 % |
> | **Total** | | **100 %** |

> **NOTE 2: LABS**
>
> **Labs 1 through 12 are mandatory to pass the course.**
> **Lab 14 is a take-home lab, released in week 11 and due at the end of week
> 14; it requires a short screen recording.** All other labs are due at the end
> of the scheduled lab period; the late penalty is 25 % per lab session. Lab
> marks may be deducted for not completing assigned safety training or reading,
> not completing prelab material before class, not being prepared with required
> materials, not cleaning your station, or unprofessional conduct.

### 7.11 `30-Labs.qmd` — extend Teacher preparation

Rows for Labs 4, 6, 13, 14 in the per-lab matrix; add draw.io / AnyLogic Cloud
/ RoboDK for Web / UCI AI4I to the firewall-check list; note that **Lab 6 needs
no external service at all**; point at the new handbook.

---

## 8. Files touched

**Modified:** `30-Labs.qmd` (primary), `index.qmd`, `_quarto.yml`

**New:** `R/make_lab_data.R`, `instructor/_quarto.yml`,
`instructor/instructor-guide.qmd`

**Not changing:** `style.css` (all `.lab-*` classes exist), `R/helpers.R`
(webR cannot source it — the caliper function is defined inside the first webR
cell)

---

## 9. Verification

1. `quarto render` — no unresolved cross-reference warnings. Watch
   `@sec-chap-ml`, `@eq-ml-cpk` and the new `{#sec-lab-*}` anchors, and confirm
   the reordered chapter list produces the intended sidebar order.
2. Open `docs/30-Labs.html`:
   - All 14 labs render with the correct coloured banners.
   - **Lab 6's webR cells load and run.** Confirm `draw_caliper()` renders a
     readable vernier scale in the browser, that the setup-cell-first
     instruction is accurate, and that the R&R arithmetic returns sane %GRR and
     ndc against the known true values.
   - The Lab 2 → Lab 3 link (previously the fragile auto-anchor) resolves.
3. `quarto render --to pdf` — each lab still readable without the CSS banners
   (via the duplicated `###` headings); no table overflows.
4. `quarto render instructor` produces `instructor/instructor-guide.pdf`, and
   `quarto render` at the root does **not** pull it into the book.
5. `Rscript R/make_lab_data.R` emits both CSVs; re-run and confirm output is
   identical (seeding works) so answer keys stay valid.
6. `rg "Lab (1[0-9]|[1-9])" 30-Labs.qmd index.qmd` — read every hit against §4.
7. `rg "%" index.qmd` — every hit must be policy text (e.g. the 25 % late
   penalty), **not** a grade weight.
8. Every lab has an AI status in both `index.qmd`'s table and its own
   `.lab-overview`, and the two agree.
9. Confirm from the **college network**: RoboDK for Web, AnyLogic Cloud,
   draw.io.
10. In Brightspace, walk the §7.9 checklist: 34 items, 6 categories; add
    `Lab-13` and `Lab-14` with the take-home window on `Lab-14`.

---

## 10. Do not

- Do not rename chapter files (§5).
- Do not add ggplot2 or any package to the Lab 6 webR cells (§7.3).
- Do not commit lab data files — the repo stages them on FOL (§7.7).
- Do not put answer keys in `30-Labs.qmd`; they go in `instructor/` (§7.8).
- Do not reintroduce grade weights into the book (§7.5).
- Do not edit `style.css` — every class needed already exists (§6).
