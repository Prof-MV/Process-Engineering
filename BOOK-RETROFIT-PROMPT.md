# Prompt: bring a book up to the Process Engineering standard

Paste everything below the line into Claude Code, opened in the book you want to change
(Sustainability_BusinessPractices, the DFM book, or any other Quarto book).
Reference implementation: `C:\Textbooks_MV\ProcessEngineering`.
Skill with the full rules: `/quarto-chapter` (re-read it first; it was updated for this).

---

Bring this book up to the standard of C:\Textbooks_MV\ProcessEngineering in two areas: (A) every
`{webr-r}` cell has a calculator card, and (B) every generated figure is readable. Do A and B as
separate commits' worth of work. Do not commit or push until I say so.

Read the `/quarto-chapter` skill first, in particular "Editable tables", "Converting every remaining
cell", "Chart text sizing" and "Before You Finish".

## Part A: calculator cards on every {webr-r} cell

1. Check whether this book has the card mechanism and table support: `qwebr_calc_card`,
   `qwebr_calc_input`, `qwebr_calc_col`, `qwebr_calc_table` in `R/helpers.R`; `buildTable` and
   `expressionEnd` in `js/qwebr-calculator.js`; `table.qwebr-calc-grid` in `style.css`; and `js/` under
   `project: resources:` in `_quarto.yml`. If anything is missing, port it from
   C:\Textbooks_MV\ProcessEngineering (copy the JS file whole; copy only the `.qwebr-calc-*` and
   `table.qwebr-calc-grid` blocks of the CSS; keep this book's own helpers and styles). The reference
   book needs `jsonlite` (ships with rmarkdown).
2. With a script, list every `{webr-r}` chunk label and every `qwebr_calc_card(label = ...)` in the
   chapters. Report the list of cells without a card BEFORE editing.
3. For each cell without a card build one, following the skill:
   - scalar inputs: `qwebr_calc_input()` (slider for the main quantity, number fields for the rest),
     one `var <- value` per line in the cell;
   - data frames: `qwebr_calc_table(frame = "df", ...)`; parallel vectors: one `var =` column each;
     `type = "label"` for fixed row names, `add_rows = TRUE` only where adding items makes sense,
     validity rule in `note`;
   - matrices: split into parallel vectors plus `cbind()` and say so;
   - do not change formulas or default data; change only what the cell prints (headline first, then
     `label<2+ spaces>value` rows, `!!text!!` for a failing verdict, `%g` not `%d`, no
     `print(data.frame)`);
   - small base-R plot only where it helps: `par(mar = c(5, 5, 3, 1))`, no `legend()`, no `las = 1`;
   - pattern: an R chunk `calc-<label>` with `qwebr_calc_card(...)`, then
     `<details class="qwebr-calc-source"><summary>Show the live R code behind this card</summary>` with
     the original cell inside, then `</details>`. The card label must equal the cell's `#| label:`.
   - leave a run-in-order lab pipeline (setup cell + dependent cells) alone and report it.
4. Check the prose next to each worked answer against what the cell now computes; fix prose that
   disagrees with the code.

## Part B: figure review and text fit

1. In `R/helpers.R` there must be two knobs: `chart_text_scale <- 1.4` (axes, titles, legends,
   `theme_minimal`/`theme_void` base size, default `geom_text` size) and `diagram_text_scale <- 1.1`
   (labels inside boxes, circles and pills). If the book has only one knob, split it: every
   `element_text(... * diagram_text_scale)` becomes `chart_text_scale`, theme wrappers and
   `update_geom_defaults` use `chart_text_scale`.
2. Render every chapter (`quarto render X.qmd --to html`). Build contact sheets of
   `docs/*_files/figure-html/*.png` (4 per sheet, 1000 px each, labelled chapter / file name, e.g. with
   Python PIL) and look at ALL of them.
3. Fix every figure with: text overflowing its box or the same colour as its fill, text cut off at an
   image edge or by axis limits, labels overlapping other labels or lines, arrows through text,
   dashed reference lines striking through their labels, subtitles or titles cut off. Fix the chunk:
   wrap labels, shorten them, reduce the size, change the text colour, widen limits or the figure,
   move the label above the line (`vjust = -0.4`). Do not hide a problem by shrinking fonts below
   readability.
4. Re-render and re-look at every figure you changed. Report a before/after count and list anything
   you left (with the reason).

## Rules for both parts

- Files are often CRLF in the working tree. Edit with a script that preserves the file's line
  endings; never `sed -i` a .qmd. Check `file <name>` and `git diff --stat` stay sane.
- Test in a real browser: serve `docs/` over `http://` (stop the server before the next render; it
  blocks Quarto from clearing the output folder), use playwright-core with the local Edge
  (`C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`), open every ancestor `<details>`
  of a card before testing it, and for every card confirm the table appears, results show, and
  editing one field changes the result. Look at a few screenshots.
- Run any new R code under Rscript first (write it to a file; long `-e` strings break the shell
  wrapper here).
- Stage files by name; do not use `git add -A` (renders leave `.knit.md` and `.html` files behind).
- Finish with a report: what was converted, what was skipped and why, changed output wording,
  prose that was corrected, figures fixed and figures left.
