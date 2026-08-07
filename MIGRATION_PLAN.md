# Bookdown → Quarto Migration Plan

## Reusable: kableExtra/LaTeX gotchas found converting to PDF format

These are **generic bookdown→Quarto PDF issues**, not specific to this book —
worth checking for in any other kableExtra-heavy R Markdown/bookdown project
being converted, since bookdown's `pdf_book` target is often left untested
(CI usually only builds the HTML/gitbook target, so these bugs go unnoticed
until someone actually renders to PDF for the first time — exactly what
happened here). All are things that render fine in HTML/gitbook but break or
silently corrupt LaTeX/PDF output. Diagnostic approach: Quarto book PDF
output is always ONE merged LaTeX document (`index.tex`/`index.pdf`) — you
cannot render a single chapter's PDF in isolation to speed up iteration, so
budget for full-book recompiles (a few minutes each) while chasing these.

1. **`kable(format = "html", ...)` hardcoded.** Forces HTML table generation
   regardless of actual render target → PDF render fails outright with
   *"Functions that produce HTML output found in document targeting pdf
   output."* Fix: delete the hardcoded `format = "html", ` argument entirely
   and let knitr/kableExtra auto-detect the real output format (this is the
   default, correct, portable behavior — visible already in any chapters
   that never had the hardcoded argument in the first place).
2. **`kable_styling(..., full_width = TRUE, ...)`.** For LaTeX, `full_width`
   pushes kableExtra into an auto column-width-balancing engine
   (`tabu`/`longtabu`) that can overflow and abort compilation with
   *"Dimension too large... I can't work with sizes bigger than about 19
   feet"* on wide/text-heavy tables. Fix: make it format-aware —
   `full_width = knitr::is_html_output()` — so HTML keeps the original
   full-width behavior and PDF falls back to normal fixed-width tables.
3. **`column_spec(N, width = "18%")`.** CSS percentage widths are valid for
   HTML but not a valid LaTeX `p{}` dimension — produces malformed LaTeX
   (`p{18%}`) that can cascade into unrelated-looking errors much later in
   the document (e.g. *"Paragraph ended before ...LT@array was complete"*
   right after some *other* table). Fix: format-aware again —
   `width = if (knitr::is_html_output()) "18%" else NULL` (kableExtra treats
   `NULL` as "don't set a width," which is a safe LaTeX default).
4. **Literal special characters (`&`, likely also `%`/`#`/`_`/`$`) inside
   `caption = "..."` strings.** `kable()`'s default `escape = TRUE` escapes
   table *body* content automatically, but captions are passed to LaTeX
   verbatim — an un-escaped `&` produces *"Misplaced alignment tab
   character &."* Fix: format-aware escaping —
   `caption = if (knitr::is_latex_output()) "Gauge R\\&R" else "Gauge R&R"`
   (HTML/EPUB render literal `&` fine via pandoc's own text escaping, so only
   the LaTeX branch needs it).
5. **CSS/R named colors that aren't valid base `xcolor` names** (e.g.
   `"steelblue"`) passed to `row_spec()`/`column_spec(..., background = ...)`.
   Valid in HTML/CSS and even valid as an R/ggplot2 color name (so
   `geom_point(color = "steelblue")` in a *plot* is completely unaffected —
   only kableExtra *table* styling calls route through LaTeX's `xcolor`,
   which only recognizes ~19 base names). Fails with *"Undefined color
   `steelblue`."* Fix: swap in the hex equivalent (`"#4682B4"`) — works
   identically in both HTML and LaTeX, no conditional needed. Search
   specifically inside `row_spec(`/`column_spec(`/`cell_spec(` calls; don't
   flag every `color =`/`background =` in the file, since most hits will be
   unrelated ggplot2 aesthetics.

General diagnostic tip: when `quarto render --to pdf` fails, the error's
reported line number is in the *compiled* `index.tex`, not your source
`.qmd` — search the `.tex` file for the `\label{tab:...}` / caption text
near the failure to identify which chunk/table it came from, then find that
chunk by its label or caption text in the source.

## Context

This folder (`ProcessEngineering`) is a working copy of the ENGR-3027 "Process
Engineering" bookdown textbook (source of truth remains untouched elsewhere).
The goal is to:

1. Convert the bookdown project (17 `.Rmd` chapters + `index.Rmd`) to a Quarto
   book project.
2. Push the converted project to a **new, private** GitHub repo (working name
   **`Process-Engineering`** — GitHub repo names can't contain spaces; this
   plan assumes that slug unless corrected).
3. Host the rendered book on **GitHub Pages**, same pattern as today
   (render → `docs/` → push to `gh-pages` branch via Actions).
4. EC2 hosting was considered and **not** selected for now — GitHub Pages
   covers the "gitbook equivalent" need with zero server maintenance.

Decisions already made with the user:
- Keep all three output formats: HTML (Quarto book, replaces gitbook), PDF, EPUB.
- Keep the numbering gap between chapter 16 (`16-AnyLogic-Simulation`) and
  chapter 20 (`20-Teaching-with-AI`) — files 17–19 are reserved for future
  chapters, not renumbered now. Note: Quarto numbers chapters by their
  position in the `_quarto.yml` chapter list, not by filename prefix, so the
  *displayed* chapter number for `20-Teaching-with-AI.qmd` will just be
  "next in sequence" (18th chapter) until 17–19 exist — this is cosmetic only.
- Drop scratch/working-note files from the new repo: `chaptersuggestion.txt`,
  `ergonomics.txt`, `pfmea.txt`, `Teaching with AI.md`, `Teaching-with-AI.md`.
  Keep `quizzes/` and `Sample_Question_Import_UTF8.csv`.
- Quarto CLI is already installed locally, so each phase can be verified with
  `quarto render` / `quarto preview` before moving on.

**Open item to confirm before Phase 1 creates the actual GitHub repo:**
GitHub Pages sites built from a *private* repo are still publicly reachable
at the Pages URL by default (only the source code stays private) unless the
org is on GitHub Enterprise. If that's not the intended visibility model,
say so before Phase 5 (CI/Pages setup) — easy to change later, just flagging
it now.

## Known cleanup items (confirmed junk, not source content)

- `introduction.Rmd` (1.15 MB) and `introduction.tex` (848 KB) — bookdown's
  stale whole-book merge artifact (caused by `book_filename: "introduction"`
  + `delete_merged_file: false`). Delete, do not migrate.
- `docs/` (22 MB, pre-rendered gitbook HTML) and `_bookdown_files/` (11 MB,
  knitr figure cache) — both regeneratable build output. Recommend **not**
  committing rendered output in the new repo at all (let CI regenerate on
  every push); saves ~30+ MB versus the current repo.
- `.RData`, `.Rhistory`, `.Rproj.user/` — local R state, gitignore only.
- One pre-existing broken cross-reference in `16-AnyLogic-Simulation.Rmd`:
  `\@ref(fig-amr-simulation)` is missing the required colon
  (`fig:amr-simulation`) — fix while converting that chapter's refs anyway.

## Status

- **Phase 4: done.** Ported `_output.yml`'s `pdf_book`/`epub_book` settings
  into `_quarto.yml`'s `format: pdf:`/`format: epub:` blocks (xelatex,
  natbib, `keep-tex`, `documentclass: book`); moved the title-page logo
  LaTeX (`titling` package + Fanshawe logo pretitle) into `preamble.tex`
  alongside the existing `booktabs` include, referenced via
  `include-in-header`. Installed TinyTeX locally (`quarto install tinytex`)
  since PDF was never renderable before.
  **Found and fixed 5 systemic kableExtra/LaTeX bugs that were latent in
  the original bookdown project** (PDF was never actually tested there
  either — CI only ever built `gitbook`) — see the reusable "kableExtra/
  LaTeX gotchas" section at the top of this file for the generic pattern +
  fix for each, useful for other bookdown→Quarto conversions:
  hardcoded `kable(format = "html")` (148 occurrences / 10 chapters),
  `full_width = TRUE` causing LaTeX table-width overflow (223 occurrences /
  17 chapters), CSS percentage `column_spec(width = "N%")` (121 occurrences
  / 7 chapters), unescaped `&` in table captions (5 occurrences / 2
  chapters), and one non-standard color name (`"steelblue"`) in a
  `column_spec()` call. All fixes are format-aware (`knitr::is_html_output()`
  / `knitr::is_latex_output()`) so HTML appearance is byte-for-byte
  unchanged — only the PDF/LaTeX code path is affected. Final verification:
  full `quarto render` (all three formats together) succeeded — 18 HTML
  pages, `docs/ENGR-3027-Process-Engineering.pdf` (2.3 MB), `docs/
  ENGR-3027-Process-Engineering.epub` (5.4 MB), zero errors.
- **Phase 3: done.** All 17 chapter files renamed `NN-Name.Rmd` →
  `NN-Name.qmd` via `git mv` (content untouched — Quarto's knitr engine
  already handled `.Rmd` identically, confirmed in Phases 1–2). Converted
  the two bookdown `\@ref()` cross-references in `16-AnyLogic-Simulation.qmd`
  to native Quarto crossref syntax: the takt-time equation moved from a
  LaTeX `equation` environment with `(\#eq:takt-17)` to
  `$$ ... $$ {#eq-takt-time}`, referenced as `@eq-takt-time`; the AMR figure
  reference (previously broken — missing the bookdown colon) became
  `@fig-amr-simulation`, reusing the chunk label which was already
  Quarto-shaped. Verified in rendered HTML: both resolve correctly
  ("Equation 16.1" and "Figure 16.9", each properly linked). Confirmed no
  `\@ref()` or `(\#...)` bookdown crossref syntax remains anywhere in the
  repo. Full book render clean (18/18, zero errors) after all changes.
- **Phase 2: done.** `index.Rmd` → `index.qmd`: YAML front matter removed
  (now lives entirely in `_quarto.yml`'s `book:` block, which already had it
  from Phase 1), body content copied verbatim. Confirmed all 18 real chapter
  files already independently `source("R/helpers.R")` /
  `source("R/required_packages.R")` in their own setup chunks (not just
  `index.Rmd`) — important because Quarto books render each chapter in its
  own R session by default (unlike bookdown's single shared session), so
  this repo was already structured in a way that's Quarto-compatible with
  zero changes needed to `R/helpers.R` or `R/required_packages.R`. Full
  book render still clean (18/18 pages, zero errors) after the conversion.
- **Phase 1: done.** New private repo live at
  `https://github.com/Prof-MV/Process-Engineering` (fresh git history, old
  bookdown repo untouched). `_quarto.yml` scaffold in place, referencing the
  existing `NN-Name.Rmd` chapter files directly (Quarto's knitr engine
  renders `.Rmd` natively — renaming to `.qmd` is deferred to Phase 3 as a
  cleanup, not a functional requirement). Full local book render
  (`quarto render`) succeeded for all 18 pages with **zero errors** — good
  signal the migration is low-risk. `gh` CLI is now installed and
  authenticated as `Prof-MV` locally, so future phases can use it directly
  for repo/PR/Actions work. `execute: freeze: auto` is set in `_quarto.yml`
  but no `_freeze/` cache has been committed yet (first real render across
  all chapters in Phase 3 should commit it).
- `_bookdown.yml` / `_output.yml` were intentionally **left in place**
  (not yet superseded — PDF/EPUB settings still need porting in Phase 4);
  remove them in Phase 6 once `_quarto.yml` fully covers their content.
- Not yet done: renaming chapters to `.qmd`, converting `\@ref()` crossrefs,
  PDF/EPUB formats, CI workflow, `docs/` is currently gitignored (not
  committed) per the plan's recommendation.

## Phased execution (one phase ≈ one future chat)

**Phase 1 — Repo & scaffold**
- In this working copy: delete confirmed junk (`introduction.Rmd/.tex`,
  `docs/`, `_bookdown_files/`, stray `.txt`/duplicate `.md` files, `.RData`,
  `.Rhistory`).
- Create `_quarto.yml` (`project: type: book`) with `book:` metadata mirrored
  from `index.Rmd`/`_output.yml` (title, author, cover-image, bibliography,
  url, chapters list in current file order), `output-dir: docs`.
- Write a Quarto-appropriate `.gitignore` (`/.quarto/`, `docs/` or `_book/`
  depending on final call, `_freeze/` — decide freeze usage here too, since
  ~2,000 ggplot chunks make Quarto's `execute: freeze: auto` worth adopting
  for CI speed/reproducibility).
- `git init`, initial commit, create the private GitHub repo (via `gh repo
  create`), push.

**Phase 2 — Front matter**
- Convert `index.Rmd` → `index.qmd`; move its YAML into `_quarto.yml`
  `book:`/`format:` blocks per Quarto book conventions.
- Migrate `R/helpers.R` (`embed_youtube()`, `info_box()`) and
  `R/required_packages.R`; confirm they still work called from `.qmd`.
- Render just the front matter to confirm the scaffold works end-to-end.

**Phase 3 — Chapter conversion (likely 3–4 chats, ~5 chapters each)**
- Rename `NN-Name.Rmd` → `NN-Name.qmd` (content mostly copies straight over —
  `fig.cap=`, `kableExtra`, `ggplot2` chunks all work unchanged under Quarto's
  knitr engine).
- Convert the two `\@ref()` bookdown cross-references in
  `16-AnyLogic-Simulation.qmd` to Quarto's native `@fig-label`/`@eq-label`
  crossref syntax (rename the referenced chunk labels to match), fixing the
  broken one noted above.
- Spot-render each converted chapter (`quarto render <file>.qmd`) before
  moving to the next batch.

**Phase 4 — PDF & EPUB formats**
- Port `_output.yml`'s `pdf_book`/`epub_book` settings into `_quarto.yml`
  `format: pdf:` / `format: epub:` (xelatex, natbib, `preamble.tex` include,
  title-page logo, cover image).
- Confirm TinyTeX is available locally (`quarto install tinytex` if not),
  render full PDF + EPUB, compare against current output.

**Phase 5 — CI/CD**
- New `.github/workflows/*.yml` using `quarto-dev/quarto-actions/setup` +
  `render`, then `peaceiris/actions-gh-pages` to deploy `docs/` → `gh-pages`
  branch (same deploy pattern as the current workflow, swapped for Quarto's
  render step). Pin R packages explicitly as today does (no `renv.lock`
  planned unless the user wants one).
- Push, verify the Actions run, confirm the Pages URL serves the new site.

**Phase 6 — QA pass**
- Full local render of all three formats; check every chapter's images,
  citations, and cross-references resolve; diff chapter list/structure
  against the original book; confirm nothing from the "drop" list leaked in.

## Verification approach (every phase)

- `quarto render` (whole project) or `quarto render <file>` (single chapter)
  locally after each change — no chat should end with an unrendered/broken
  book.
- `quarto preview` for a visual check of navigation, TOC, and figures.
- Final check: GitHub Actions run green + Pages URL loads the deployed site.
