# Lab expansion — implementation notes

Companion to `LAB-EXPANSION-PLAN.md`. What was actually built, how it is wired,
the one bug that bit us, and how to get back into it.

Branch `labs/expand-to-14` → merged to `master` at `006a2f5`; webR fix at
`96e5966`.

---

## 1. What shipped

| Area | File(s) | Change |
|---|---|---|
| Lab chapter | `30-Labs.qmd` | 14 labs (lab # = week #). New: **Lab 4** Lean VSM, **Lab 6** SPC & Gauge R&R virtual caliper, **Lab 13** TPM/OEE + RCA + AI4I 2020, **Lab 14** RoboDK take-home. ML labs renumbered 5–10 → 7–12. Every lab heading has a `{#sec-lab-*}` anchor. Three `TODO` rubrics filled (Labs 5, 7, 8). Per-lab AI-use line in every `.lab-overview`. Teacher-prep matrix extended to 14. |
| Front matter | `index.qmd` | Grade-weight table deleted (FOL is source of truth); `## Course schedule {-}` added; blanket AI ban replaced with a per-assessment generative-AI policy table; "labs 1–5 before week 7" → "1–6"; "mandatory labs 1 though 10" → "1 through 12". |
| Chapter order | `_quarto.yml` | Chapters reordered to the teaching sequence so each lab's prerequisite chapter is taught first. **Files were NOT renamed** — the numeric filename prefixes are now historical; there is a comment in `_quarto.yml` saying so. Cross-refs are label-based so this is safe. |
| Lab data | `R/make_lab_data.R` (new) | One seeded generator. Writes `lab_data/vsm_station_data.csv` (Lab 4) and `lab_data/precitech_shift_log.csv` (Lab 13); prints the Lab 4 / 6 / 13 / 14 answer keys. `lab_data/` is gitignored — stage the CSVs on FOL, never commit. |
| Instructor handbook | `instructor/` (new) | Standalone Quarto project (`project: {type: default}`), isolated from the book. `quarto render instructor` → `instructor/instructor-guide.pdf` for FOL. 11 sections incl. all 14 rubrics, answer keys, grade-item checklist, paste-ready Course Plan notes, firewall checklist, failure-modes table. The PDF and `instructor/.quarto/` are gitignored; the `.qmd` is committed. |

The plan's own decisions (browser-only, webR virtual caliper, renumbering
approved, delete grade breakdown, per-assessment AI policy) are all in
`LAB-EXPANSION-PLAN.md` §3 — not relitigated here.

---

## 2. Deploy topology — read this before wondering "why isn't my change live"

- **`docs/` is gitignored.** The rendered site is never committed to `master`.
- **`.github/workflows/publish.yml` deploys on push to `master` only** (plus
  manual `workflow_dispatch`). It checks out `master`, runs `quarto render`
  (HTML + PDF + EPUB, tinytex), then force-pushes `docs/` to the **`gh-pages`**
  branch via `peaceiris/actions-gh-pages` with `keep_files: false`.
- GitHub Pages serves `gh-pages`. Live URL: <https://prof-mv.github.io/Process-Engineering/>.
- Consequence: **work on a feature branch is invisible on the site until it is
  merged to `master`.** A local `quarto render` or "re-deploy pages" from a
  `master` checkout that predates the merge just rebuilds the old content.
- After a merge, the Action takes ~7 min. Then the **GitHub Pages CDN edge cache**
  can serve the previous copy for several more minutes; `?cb=123` busts the
  browser but not always the edge. Check `curl -sI <url>` — `age: 0` and a
  `last-modified` after the deploy time mean it has propagated. `git show
  origin/gh-pages:30-Labs.html` is the ground truth.

Watch a run: `gh run list --workflow=publish.yml` / `gh run watch <id> --exit-status`.

---

## 3. The bug that bit us: webR filter is per-file, not global

**Symptom:** Lab 6's caliper cells rendered as a static grey code block
(`#| label: lab6-setup` shown literally), and the Labs page had no
"Initializing webR" status banner.

**Root cause:** in this book the `coatless/webr` extension is enabled **per
chapter, in each file's YAML front matter** — not in `_quarto.yml`. Every
webR-using chapter starts with:

```yaml
---
engine: knitr
filters:
  - webr
webr:
  show-startup-message: true
  cell-options:
    autorun: true
---
```

`30-Labs.qmd` originally had only `toc-depth: 2` (it never used webR before), so
the ```` ```{webr-r} ```` blocks fell through as plain fenced code and no webR
runtime was injected.

**Fix (`96e5966`):** added that same block to `30-Labs.qmd`'s front matter,
keeping `toc-depth: 2`.

**If you add webR cells to any other lecture-only chapter, do the same.**

**Verify a build has live webR** (local `docs/` or `git show origin/gh-pages:`):

```bash
grep -oE "qwebr-editor|qwebr-button-run|qwebr-monaco-editor-init" docs/30-Labs.html | sort | uniq -c
# expect ~18 qwebr-editor, ~7 qwebr-button-run, 2 monaco-editor-init
grep -c 'class="sourceCode webr' docs/30-Labs.html      # expect 0 (0 = not leaking as static)
```

The qwebr JS is inlined into the HTML (that is why the page is ~270 KB and has
no local `src=` to qwebr files); only the Monaco editor loads from
`cdn.jsdelivr.net` (CSP-allowed).

---

## 4. Lab 6 virtual caliper — how it works

All inside `30-Labs.qmd`, five `{webr-r}` cells, **base R graphics only** (no
ggplot2 — slow/fragile in webR). Cells share one page-global environment and
`autorun: true` runs them top-to-bottom on load, so `lab6-setup` (which defines
everything) always runs first.

| Cell label | Role |
|---|---|
| `lab6-setup` | `set.seed(3027)`; `caliper_ref` (10 certified part values, 24.90–25.10); `caliper_bias = 0.03 + 0.05*(ref-25)` (small size-dependent gauge bias); `caliper_shown(part,trial)` (ref + bias + N(0,0.015) slop, seeded per part×trial); `draw_caliper(part,trial)` draws a zoomed vernier (20 divisions over 19 mm → 0.05 mm resolution); `operator_order` = a randomised 1:10 per operator. |
| `lab6-demo` | 3 practice reads with the answer printed. |
| `lab6-grr` | Students paste 90 readings into `op_A/op_B/op_C` (10×3 each). AIAG average-and-range Gauge R&R (K1 0.5908, K2 0.5231, K3 0.3146) → EV, AV, GRR, PV, TV, %GRR, ndc. Ships with placeholder data. |
| `lab6-bias` | Uses `op_*` + `caliper_ref` → per-part bias, overall bias, linearity slope. |
| `lab6-spc` | Self-contained: `set.seed(250)`, 25 subgroups × 5, special-cause shift seeded at subgroups 12–16, USL/LSL 25.050/24.950 → X̄/R charts + Cp/Cpk. |

The R in all five cells was test-run under plain `Rscript` and is clean.

---

## 5. Regenerating lab data + answer keys

```bash
Rscript R/make_lab_data.R
```

Base R, fully `set.seed()`-ed, idempotent (re-run → identical CSVs and keys).
Emits to `./lab_data/` (gitignored): `vsm_station_data.csv`,
`precitech_shift_log.csv`. Prints the answer keys to stdout.

Current key values (as of the committed generator):

- **Lab 4:** takt **105.6 s/kit** (250/day, 8 h − two 20-min breaks = 26 400 s);
  bottleneck **CNC turn** (120 s C/T); PCE **≈ 0.22 %**.
- **Lab 6:** mean gauge bias **≈ +0.030 mm** (rising slightly with size);
  simulated %GRR **≈ 23 %**, ndc **≈ 6** — expect students in the 20–35 %
  marginal band, ndc 4–6. Seeded SPC set: X̄̄ 25.0082, R̄ 0.0255, σ̂ 0.0110;
  **Cp 1.52, Cpk 1.27**; beyond-3σ subgroups **12–16**.
- **Lab 13:** weekly OEE **≈ 75 %** (A 83.2 % · P 94.2 % · Q 95.9 %); dominant
  Big Loss **breakdowns**. AI4I 2020 Pareto: HDF ≈ OSF ≈ PWF > TWF > RNF;
  failure rate ~3.4 % → accuracy is a useless metric (the lesson).
- **Lab 14:** takt 105.6 s; expected sim cycle time ~12–22 s first pass,
  ~7–14 s optimised — one robot clears takt easily.

Full key text also lives in `instructor/instructor-guide.qmd` §8.

---

## 6. Instructor handbook

```bash
quarto render instructor        # -> instructor/instructor-guide.pdf
```

Separate Quarto project so the book render never picks it up (verified: not in
the 20-file book render). Does **not** reuse `../preamble.tex` (that injects the
book cover via a path that only resolves from the repo root); uses a tiny inline
`booktabs`+`longtable` header instead. `scrreprt`, xelatex.

---

## 7. Verification checklist (what was run, re-run if you touch this)

```bash
quarto render                                   # full book: exit 0, no unresolved xrefs
grep -oE 'id="sec-lab-[a-z0-9-]+"' docs/30-Labs.html | sort -u   # 14 anchors
grep -oE "qwebr-editor|qwebr-button-run" docs/30-Labs.html | sort | uniq -c
Rscript R/make_lab_data.R                        # both CSVs + keys, re-run identical
quarto render instructor                         # instructor-guide.pdf
```

Sidebar order in the built book (confirmed): index → 01 → 02 → 08 → 04 → 16 →
03 → 05 → 07 → 06 → 10 → 11 → 20 → 21 → 12 → 15 → 09 → 13 → 14 → 30-Labs.

Warnings in the render log that are **pre-existing and unrelated**: `tab:*` "Raw
LaTeX table found with non-tbl label" in several lecture chapters; `改善`
(kaizen) glyph conversion failure in the Lean chapter PNG.

---

## 8. Still open / to confirm before relying on it

- **Chapter → week mapping is reconstructed** from the 25F course plan (7 units
  vs 18 chapters). `index.qmd` "Course schedule" and the handbook term grid both
  say so. Confirm against the real timetable before publishing to students.
- **From the college network:** RoboDK for Web (`web.robodk.com/simulation`),
  AnyLogic Cloud (`cloud.anylogic.com`), draw.io (`app.diagrams.net`),
  UCI (`archive.ics.uci.edu`). Firewall checklist is in the handbook.
- **`draw_caliper()` in a real browser:** confirm the vernier scale is readable
  and the coincidence is findable at 0.05 mm. Tune the zoom window / division
  spacing in `lab6-setup` if not.
- **AnyLogic Cloud push/pull model for Lab 4** must be built/forked and published
  with the control-policy and WIP-cap parameters exposed on the public run
  screen. Not done — Lab 4 text and handbook both flag it.
- **FOL grade book:** add `Lab-13` and `Lab-14` (take-home availability window on
  `Lab-14`). Handbook §3 has the full 34-item / 6-category checklist.
- **AI4I 2020 CSV:** host a copy on FOL as a firewall fallback (Lab 13).
- `.vscode/settings.json` has an unrelated local modification — not part of this
  work, left unstaged.
