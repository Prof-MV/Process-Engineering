# Helper functions for ENGR-3027 Process Engineering Book
# These functions provide conditional output for HTML vs PDF rendering

#' Attach jQuery as an HTML dependency
#'
#' Quarto's Bootstrap 5 HTML theme does not ship jQuery, but kableExtra's
#' kePrint.js (used by kable_styling() for tooltips/popovers) assumes it is
#' present and otherwise throws "$ is not defined" in the browser console.
#' Call this once per chapter (in the setup chunk) to pull in the copy of
#' jQuery bundled with the rmarkdown package, offline, ahead of any table.
#'
#' @return An htmltools::tagList carrying the jQuery HTML dependency
inject_jquery <- function() {
  if (knitr::is_html_output(excludes = "epub")) {
    htmltools::tagList(rmarkdown::html_dependency_jquery())
  }
}

#' Central control for chart/diagram text sizing
#'
#' Figures are authored wide (fig.width ~9-12in) but displayed in a much
#' narrower book column, so text baked into the image (ggplot2's default
#' base_size = 11) ends up visually tiny once the browser scales the image
#' down to fit. Bump this ONE number to make all chart text larger or
#' smaller across the whole book at once, instead of hand-editing every
#' chunk. Every geom_text()/geom_label()/annotate("text", ...)/element_text()
#' call in the book's .qmd files multiplies its size by this value.
#' @export
diagram_text_scale <- 1.1

#' Text scale for axes, titles, legends and chart value labels (theme text).
#' Text drawn INSIDE boxes/shapes of hand-built diagrams uses the smaller
#' `diagram_text_scale` so it fits the shape it was laid out for.
#' @export
chart_text_scale <- 1.4

#' theme_minimal()/theme_void() wrappers with a larger default base_size
#'
#' Shadow ggplot2's versions so every existing bare theme_minimal()/
#' theme_void() call in the book picks up diagram_text_scale automatically,
#' without needing base_size passed explicitly at each call site.
theme_minimal <- function(base_size = 11 * chart_text_scale, ...) {
  ggplot2::theme_minimal(base_size = base_size, ...)
}
theme_void <- function(base_size = 11 * chart_text_scale, ...) {
  ggplot2::theme_void(base_size = base_size, ...)
}

# Also scale the default size of geom_text()/annotate("text", ...) layers
# that don't pass their own explicit `size =` (ggplot2's own default is
# 3.88). Layers that DO pass an explicit size (as `size = N * diagram_text_scale`)
# are unaffected by this and controlled directly by their own literal.
ggplot2::update_geom_defaults("text", list(size = 3.88 * chart_text_scale))

#' Embed a YouTube video with conditional output
#'
#' In HTML output, displays a responsive iframe embed.
#' In PDF/LaTeX output, displays a formatted link to the video.
#'
#' @param video_id The YouTube video ID (e.g., "dQw4w9WgXcQ")
#' @param title The title to display (used in PDF link text)
#' @return NULL (outputs directly via cat)
#' @examples
#' embed_youtube("dQw4w9WgXcQ", "Example Video")
embed_youtube <- function(video_id, title = "Watch Video") {
  # Clean video ID (remove any URL parts if full URL passed)
  if (grepl("youtube.com|youtu.be", video_id)) {
    # Extract video ID from URL
    video_id <- gsub(".*(?:youtube\\.com/embed/|youtube\\.com/watch\\?v=|youtu\\.be/)([^&?/]+).*", "\\1", video_id)
  }

  if (knitr::is_html_output()) {
    # HTML output - responsive iframe
    cat(sprintf('
<div style="position: relative; padding-bottom: 56.25%%; height: 0; overflow: hidden; max-width: 100%%;">
  <iframe
    style="position: absolute; top: 0; left: 0; width: 100%%; height: 100%%;"
    src="https://www.youtube.com/embed/%s"
    title="%s"
    frameborder="0"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    referrerpolicy="strict-origin-when-cross-origin"
    allowfullscreen>
  </iframe>
</div>
', video_id, title))
  } else {
    # PDF/LaTeX output - formatted link
    cat(sprintf('\n\n**%s:** [https://www.youtube.com/watch?v=%s](https://www.youtube.com/watch?v=%s)\n\n',
                title, video_id, video_id))
  }
}

#' Create a styled info box with conditional output
#'
#' In HTML output, displays a colored box.
#' In PDF output, displays a simple formatted block.
#'
#' @param content The content to display
#' @param type The type of box: "info", "warning", "tip", "note"
#' @return NULL (outputs directly via cat)
info_box <- function(content, type = "info") {
  colors <- list(
    info = "#3498DB",
    warning = "#E74C3C",
    tip = "#2ECC71",
    note = "#F39C12"
  )

  icons <- list(
    info = "Info",
    warning = "Warning",
    tip = "Tip",
    note = "Note"
  )

  color <- colors[[type]]
  icon <- icons[[type]]

  if (knitr::is_html_output()) {
    cat(sprintf('
<div style="padding: 15px; margin: 10px 0; border-left: 5px solid %s; background-color: %s20;">
<strong>%s:</strong> %s
</div>
', color, color, icon, content))
  } else {
    cat(sprintf('\n\n**%s:** %s\n\n', icon, content))
  }
}

#' One input field/slider for qwebr_calc_card()
#'
#' @param var The R variable name this input controls. Must match a
#'   `var <- value` (or `var = value`) assignment somewhere near the top of
#'   the paired `{webr-r}` cell's source — the calculator substitutes the
#'   input's current value into that exact line every time it re-runs the
#'   cell, so the card and the "show the code" panel never drift apart.
#' @param label Reader-facing label for the row.
#' @param value Default numeric value (should match the cell's own default).
#' @param min,max,step Passed straight through to the HTML `<input>`.
#' @param type `"number"` (a plain numeric field, optionally with a
#'   `prefix`/`suffix`) or `"slider"` (a `<input type="range">` with a live
#'   readout next to the label — use this for the one variable that's the
#'   "main" thing being explored, typically a volume/quantity/count).
#' @param prefix,suffix Optional short strings shown beside a `"number"`
#'   input, e.g. `prefix = "$"`, `suffix = "kg"`.
qwebr_calc_input <- function(var, label, value, min = NULL, max = NULL, step = NULL,
                              type = c("number", "slider"), prefix = "", suffix = "") {
  type <- match.arg(type)
  list(var = var, label = label, value = value, min = min, max = max, step = step,
       type = type, prefix = prefix, suffix = suffix)
}

#' One column of an editable table for qwebr_calc_card()
#'
#' @param name R column name (used when the table rebuilds a data frame).
#' @param values The default values, one per row.
#' @param var For a table of parallel vectors (no `frame`): the R variable in
#'   the cell that this column stands for, e.g. `"mass_g"`. The calculator
#'   rebuilds that `var <- c(...)` line from the column.
#' @param type `"number"`, `"text"`, `"select"` (needs `options`) or `"label"`
#'   (shown, not editable).
#' @param label Column heading (defaults to `name`).
#' @param options Choices for a `"select"` column.
#' @param min,max,step Passed to the `<input>` of a `"number"` column.
qwebr_calc_col <- function(name, values, var = NULL, type = c("number", "text", "select", "label"),
                           label = NULL, options = NULL, min = NULL, max = NULL, step = NULL) {
  type <- match.arg(type)
  if (type == "select") stopifnot(!is.null(options))
  list(name = name, label = if (is.null(label)) name else label, values = as.list(values),
       var = var, type = type, options = as.list(options), min = min, max = max, step = step)
}

#' An editable table for qwebr_calc_card()
#'
#' Stands in for a data frame (`frame = "name"`: the cell's whole
#' `name <- data.frame(...)` is rebuilt from the table) or for a set of
#' parallel vectors (each column carries its own `var`). Use it for the
#' "edit your own data" cells that are tables rather than a few numbers.
#'
#' @param columns A list of `qwebr_calc_col()` calls.
#' @param frame Name of the data frame in the cell, or NULL for vector mode.
#' @param add_rows Show "Add row" / "Remove last row" buttons.
#' @param note Optional hint shown under the table.
qwebr_calc_table <- function(columns, frame = NULL, add_rows = FALSE, note = NULL) {
  list(columns = columns, frame = frame, add_rows = add_rows, note = note)
}

#' Render an interactive "calculator" card in front of a {webr-r} cell
#'
#' Emits a styled card (see `style.css`, `.qwebr-calc-*` rules) with one row
#' per `input`, a results area, and a chart area. The card is wired up
#' entirely client-side by `js/qwebr-calculator.js`, which finds the
#' `{webr-r}` cell carrying `label` (via quarto-webr's own `qwebrCellDetails`
#' registry), substitutes the card's current input values into that cell's
#' *actual source*, and re-runs it headlessly through the page's existing
#' webR engine on every input change.
#'
#' Call this immediately before the `{webr-r}` cell it drives, then wrap that
#' cell in `<details class="qwebr-calc-source">` so curious students can
#' still open it, read it, edit it, and run it directly (see
#' 01-Types-of-Manufacturing.qmd, "Injection Molding", for the full
#' reference pattern — card, then collapsed source).
#'
#' Only produces output for HTML (webR doesn't run in PDF/EPUB); the
#' `{webr-r}` cell underneath already degrades to a plain static code block
#' there on its own, so nothing further is needed for those formats.
#'
#' @param label Must exactly match the `#| label:` of the `{webr-r}` cell
#'   this card drives.
#' @param title Card heading.
#' @param icon A Font Awesome solid-icon name, no prefix (e.g. `"gears"`,
#'   `"flask"`, `"bolt"`) — Font Awesome is already loaded on every page by
#'   quarto-webr itself.
#' @param inputs A list of `qwebr_calc_input()` calls, top to bottom.
#' @param tables Optional list of `qwebr_calc_table()` calls: editable data
#'   tables (a data frame, or parallel vectors) shown above the results.
#' @param fig_width,fig_height Pixel size for the captured plot (if the cell
#'   produces one); scales to fit the card via CSS either way.
#' @param goal Optional challenge shown under the results, e.g. "Get the cost
#'   per part below $4.00 without changing the equipment cost." Turns the
#'   card from "explore" into "solve".
#' @param goal_test An R expression (as a string) over the cell's own
#'   variables that is TRUE once the goal is reached, e.g.
#'   `"cost_per_part < 4"`. It is evaluated after the cell on every run. It
#'   must be FALSE at the default inputs, or there is nothing to solve.
#' @param rerun For a cell that simulates with random numbers: the name of
#'   the cell's seed variable (e.g. `"seed"`). The card gets a "Run again"
#'   button that moves that input on by one, so the student sees how much the
#'   result changes from run to run. The seed must also be one of `inputs`,
#'   and the cell must call `set.seed()` with it. In class, teams can each
#'   enter their team number as the run number to get different data.
qwebr_calc_card <- function(label, title, icon = "gears", inputs = list(), tables = list(),
                             fig_width = 1200, fig_height = 700,
                             goal = NULL, goal_test = NULL, rerun = NULL) {
  if (!knitr::is_html_output(excludes = "epub")) return(invisible(NULL))

  sanitize <- function(x) gsub("[^a-zA-Z0-9]+", "-", x)
  card_id <- paste0("qcalc-", sanitize(label))

  render_input <- function(inp) {
    input_id <- paste0(card_id, "-", sanitize(inp$var))
    # Plain decimals, never scientific notation: a field showing "5e+06" is
    # unreadable, and "1e+05" is not something a student would type back in.
    plain <- function(x) format(x, scientific = FALSE, trim = TRUE)
    attrs <- sprintf(
      'id="%s" data-var="%s" value="%s"%s%s%s',
      input_id, inp$var, plain(inp$value),
      if (!is.null(inp$min)) sprintf(' min="%s"', plain(inp$min)) else "",
      if (!is.null(inp$max)) sprintf(' max="%s"', plain(inp$max)) else "",
      if (!is.null(inp$step)) sprintf(' step="%s"', plain(inp$step)) else ""
    )

    if (inp$type == "slider") {
      readout_id <- paste0(input_id, "-readout")
      sprintf('
    <div class="qwebr-calc-row qwebr-calc-row-slider">
      <label for="%s">%s <span class="qwebr-calc-slider-readout" data-readout-for="%s" id="%s">%s</span></label>
      <input type="range" class="qwebr-calc-slider" %s>
    </div>',
        input_id, inp$label, input_id, readout_id,
        format(inp$value, big.mark = " ", scientific = FALSE), attrs)
    } else {
      sprintf('
    <div class="qwebr-calc-row">
      <label for="%s">%s</label>
      <div class="qwebr-calc-field">
        %s<input type="number" %s>%s
      </div>
    </div>',
        input_id, inp$label,
        if (nzchar(inp$prefix)) sprintf('<span class="qwebr-calc-prefix">%s</span>\n        ', inp$prefix) else "",
        attrs,
        if (nzchar(inp$suffix)) sprintf('\n        <span class="qwebr-calc-suffix">%s</span>', inp$suffix) else "")
    }
  }

  input_rows <- paste(vapply(inputs, render_input, character(1)), collapse = "\n")

  render_table <- function(tbl) {
    spec <- list(
      frame = tbl$frame, addRows = isTRUE(tbl$add_rows),
      columns = lapply(tbl$columns, function(col) col[!vapply(col, is.null, logical(1))]))
    json <- jsonlite::toJSON(spec, auto_unbox = TRUE, null = "null")
    sprintf('
    <div class="qwebr-calc-table" data-spec="%s"></div>%s',
      htmltools::htmlEscape(json, attribute = TRUE),
      if (is.null(tbl$note)) "" else sprintf('\n    <p class="qwebr-calc-table-note">%s</p>', tbl$note))
  }
  table_rows <- paste(vapply(tables, render_table, character(1)), collapse = "\n")

  rerun_row <- if (is.null(rerun)) "" else {
    stopifnot(rerun %in% vapply(inputs, function(inp) inp$var, character(1)))
    sprintf('
    <button type="button" class="qwebr-calc-rerun" data-seed-var="%s">Run again with new random numbers</button>', rerun)
  }

  stopifnot(is.null(goal) == is.null(goal_test))
  goal_row <- if (is.null(goal)) "" else sprintf('
  <div class="qwebr-calc-goal" data-goal-test="%s">
    <span><span class="qwebr-calc-goal-label">Challenge:</span> %s</span>
    <span class="qwebr-calc-goal-status" role="status" aria-live="polite"></span>
  </div>', htmltools::htmlEscape(goal_test, attribute = TRUE), goal)

  cat(sprintf('
```{=html}
<script src="js/qwebr-calculator.js"></script>

<div class="qwebr-calc-card" data-qwebr-label="%s" data-fig-width="%d" data-fig-height="%d">
  <div class="qwebr-calc-header">
    <i class="fa-solid fa-%s qwebr-calc-icon"></i>
    <h4>%s</h4>
  </div>
  <div class="qwebr-calc-inputs">%s%s%s
  </div>
  <div class="qwebr-calc-results"></div>%s
  <div class="qwebr-calc-graph"></div>
</div>
```
', label, fig_width, fig_height, icon, title, input_rows, table_rows, rerun_row, goal_row))
}

# "Try it yourself" exercises (tryit_number(), tryit_grid(), tryit_sort()).
options(tryit.course = "ENGR3027")
source("R/tryit.R")
