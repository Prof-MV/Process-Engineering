# ENGR-3027 Process Engineering

Lecture notes for ENGR-3027 Process Engineering, built as a [Quarto](https://quarto.org) book.

Published at <https://prof-mv.github.io/Process-Engineering/> (HTML, PDF, and EPUB).

## Building locally

```sh
quarto render
```

Requires [Quarto](https://quarto.org/docs/get-started/), R with the packages listed in `R/required_packages.R` (auto-installed on first render), and [TinyTeX](https://quarto.org/docs/output-formats/pdf-basics.html#installation) for PDF output (`quarto install tinytex`).

## Structure

- `index.qmd`, `NN-Chapter-Name.qmd` — chapter source files, in `_quarto.yml`'s `book: chapters:` order
- `_quarto.yml` — book metadata and format settings (HTML/PDF/EPUB)
- `images/` — figures and diagrams referenced by chapters
- `R/` — shared helper functions (`helpers.R`) and package setup (`required_packages.R`)
- `.github/workflows/publish.yml` — CI: renders the book and deploys `docs/` to the `gh-pages` branch on every push to `master`

See `MIGRATION_PLAN.md` for the history of this project's conversion from bookdown to Quarto, including a list of kableExtra/LaTeX compatibility issues worth checking for in similar conversions.
