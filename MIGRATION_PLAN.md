# Bookdown → Quarto Migration Plan

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
