# "Try it yourself" exercises: the student commits to an answer and the page
# marks it.
#
# Companion to the calculator cards in helpers.R. A calculator card lets the
# student change an input and watch the output; a tryit exercise makes the
# student do the method and then checks the result. Each exercise is ONE call
# in a `results='asis'` chunk -- no hand-written HTML or <script> in chapters:
#
#   tryit_number()  one or more numeric answers, each marked against a tolerance
#   tryit_grid()    a table with blank cells to fill in, marked cell by cell
#   tryit_sort()    cards to assign to categories
#   tryit_order()   steps to put in the right sequence
#
# How it fits together:
#   - The helper serialises the exercise (including its answer key) to JSON
#     inside a `.tryit` div. `js/tryit.js` finds every such div on the page
#     and builds the widget. Plain JavaScript, no webR, so it also works in
#     chapters that do not load webR.
#   - Answer keys are computed here, at render time, from the same R objects
#     the chapter uses to print its worked solution, so the checker and the
#     solution cannot disagree.
#   - A `<details class="tryit-solution">` placed directly after an exercise
#     stays locked until the student has checked an answer at least once.
#   - PDF/EPUB get a printable worksheet instead (blanks to fill in by hand).
#   - Every exercise given a `question` also gets a graded twin: a Brightspace
#     import file is written to quizzes/tryit_<chapter>.csv on each HTML
#     render. Answers sit in the page source, so the on-page version is
#     practice only; pass `show = FALSE` to declare a twin with different
#     numbers that is exported but never shown in the book.
#
# Styling lives in style.css (".tryit-*" rules).

# Course code used as the prefix of exported Brightspace question IDs.
# Set options(tryit.course = "...") before sourcing this file to change it.
tryit_course <- function() getOption("tryit.course", "COURSE")

.tryit_state <- new.env()
.tryit_state$questions <- list()

tryit_html <- function() knitr::is_html_output(excludes = "epub")

tryit_id <- function(id) gsub("[^a-zA-Z0-9]+", "-", id)

# Decimal places a student is expected to give, inferred from the tolerance
# (tol = 0.01 -> 2 places, tol = 0.0005 -> 4 places).
tryit_digits <- function(tol) max(0, ceiling(-log10(tol)))

#' One numeric answer for tryit_number() or the `answers` of tryit_grid()
#'
#' @param label Reader-facing label for the answer field.
#' @param answer The correct value -- pass the R object the solution is
#'   computed from, not a retyped literal.
#' @param tol Absolute tolerance. An entry is correct within +/- `tol`.
#' @param tol_pct Optional relative tolerance in percent; an entry within
#'   either tolerance is accepted.
#' @param prefix,suffix Short strings shown beside the field ("$", "mm").
#' @param hint Shown under the field after a wrong entry.
#' @param digits Decimal places asked for in the print/Brightspace versions.
tryit_answer <- function(label, answer, tol = 0.01, tol_pct = NULL,
                         prefix = "", suffix = "", hint = NULL,
                         digits = tryit_digits(tol)) {
  stopifnot(is.numeric(answer), length(answer) == 1, !is.na(answer))
  list(label = label, answer = answer, tol = tol, tolPct = tol_pct,
       prefix = prefix, suffix = suffix, hint = hint, digits = digits)
}

# Emit the widget shell. `spec` becomes the JSON that js/tryit.js reads.
tryit_emit <- function(type, id, spec) {
  json <- jsonlite::toJSON(spec, auto_unbox = TRUE, null = "null", digits = NA)
  # Keep a literal "</script>" in any label from closing the JSON block early.
  json <- gsub("<", "\\u003c", json, fixed = TRUE)
  cat(sprintf('
```{=html}
<script src="js/tryit.js"></script>
<div class="tryit" id="tryit-%s" data-tryit="%s">
<script type="application/json">%s</script>
</div>
```
', tryit_id(id), type, json))
}

tryit_blank <- function(a) {
  sprintf("%s\\_\\_\\_\\_\\_\\_\\_\\_ %s", a$prefix, a$suffix)
}

# Printable version of a list of tryit_answer()s.
tryit_print_answers <- function(answers) {
  for (a in answers) {
    cat(sprintf("- %s: %s *(to %d decimal place%s)*\n", a$label, tryit_blank(a),
                a$digits, if (a$digits == 1) "" else "s"))
  }
  cat("\n")
}

#---- Brightspace graded twins -------------------------------------------------

tryit_csv_field <- function(x) {
  x <- as.character(x)
  quote <- grepl('[",\n]', x)
  x[quote] <- paste0('"', gsub('"', '""', x[quote], fixed = TRUE), '"')
  x
}

# Register one question (a list of rows, each a character vector of fields)
# and rewrite this chapter's import file with everything registered so far.
tryit_export <- function(rows) {
  input <- knitr::current_input()
  if (is.null(input) || !tryit_html()) return(invisible(NULL))

  .tryit_state$questions[[length(.tryit_state$questions) + 1]] <- rows

  stem <- tools::file_path_sans_ext(basename(input))
  header <- list(
    sprintf("//Graded twins of the 'Try it yourself' exercises in %s", stem),
    "//Generated by R/tryit.R on every HTML render of the chapter -- do not edit by hand.",
    "//Import into the Brightspace Question Library. Save as CSV UTF-8 before importing."
  )
  lines <- vapply(header, function(r) paste(tryit_csv_field(r), collapse = ","), character(1))
  for (q in .tryit_state$questions) {
    lines <- c(lines, "", vapply(q, function(r) paste(tryit_csv_field(r), collapse = ","), character(1)))
  }

  if (!dir.exists("quizzes")) dir.create("quizzes")
  con <- file(file.path("quizzes", sprintf("tryit_%s.csv", stem)), open = "wb")
  on.exit(close(con))
  writeLines(enc2utf8(c(paste0("﻿", lines[1]), lines[-1])), con, useBytes = TRUE)
  invisible(NULL)
}

tryit_qid <- function(id, n) {
  sprintf("%s-TRYIT-%s-%02d", tryit_course(), toupper(tryit_id(id)), n)
}

# The strings a Short Answer twin accepts for one numeric answer: the rounded
# value, its neighbours in the last decimal place where the tolerance allows
# them (0.0475 may be rounded to 0.047 or 0.048), and each of those without
# trailing zeros.
tryit_accepted <- function(a) {
  scale <- 10^a$digits
  nearest <- round(a$answer * scale)
  nearby <- nearest + c(0, -1, 1)
  nearby <- nearby[nearby == nearest | abs(nearby / scale - a$answer) <= a$tol + 1e-9]
  full <- formatC(nearby / scale, digits = a$digits, format = "f")
  trimmed <- if (a$digits > 0) sub("\\.$", "", sub("0+$", "", full)) else full
  unique(c(full, trimmed))
}

# Short Answer question for one numeric answer. Brightspace matches text, so
# the rounding is stated and the common ways of writing the value are accepted.
tryit_export_answer <- function(id, n, title, question, a) {
  accepted <- tryit_accepted(a)
  unit <- trimws(paste(a$prefix, a$suffix))
  text <- sprintf("%s<p><b>%s</b>: give your answer to %d decimal place%s%s. Enter the number only.</p>",
                  question, a$label, a$digits, if (a$digits == 1) "" else "s",
                  if (nzchar(unit)) sprintf(" (%s)", unit) else "")
  tryit_export(c(
    list(c("NewQuestion", "SA"),
         c("ID", tryit_qid(id, n)),
         c("Title", sprintf("%s - %s", title, a$label)),
         c("QuestionText", text, "HTML"),
         c("Points", "1"),
         c("Difficulty", "3"),
         c("InputBox", "1", "20")),
    lapply(accepted, function(x) c("Answer", "100", x)),
    if (!is.null(a$hint)) list(c("Hint", a$hint))
  ))
}

tryit_html_table <- function(header, rows) {
  cells <- function(x, tag) paste0("<", tag, ">", x, "</", tag, ">", collapse = "")
  paste0('<table border="1" cellpadding="4"><tr>', cells(header, "th"), "</tr>",
         paste0("<tr>", vapply(rows, cells, character(1), tag = "td"), "</tr>", collapse = ""),
         "</table>")
}

#---- tryit_number -------------------------------------------------------------

#' Numeric answers the student types in and checks
#'
#' Put the problem statement in the chapter text above the call, and the
#' worked solution in a `<details class="tryit-solution">` directly below it
#' (it unlocks after the first check).
#'
#' @param id Unique within the chapter.
#' @param title Card heading.
#' @param answers A list of `tryit_answer()` calls, top to bottom.
#' @param intro Optional one-line instruction shown under the heading.
#' @param question The full problem statement as HTML. Supplying it exports a
#'   Brightspace twin (one Short Answer question per answer).
#' @param show `FALSE` exports the twin without showing the exercise.
tryit_number <- function(id, title, answers, intro = NULL, question = NULL, show = TRUE) {
  if (!is.null(question)) {
    for (i in seq_along(answers)) tryit_export_answer(id, i, title, question, answers[[i]])
  }
  if (!show) return(invisible(NULL))

  if (tryit_html()) {
    tryit_emit("number", id, list(title = title, intro = intro, answers = answers))
  } else {
    cat(sprintf("\n\n**%s**\n\n", title))
    if (!is.null(intro)) cat(intro, "\n\n")
    tryit_print_answers(answers)
  }
}

#---- tryit_grid ---------------------------------------------------------------

#' A table with blank cells for the student to fill in
#'
#' @param id Unique within the chapter.
#' @param title Card heading.
#' @param data The SOLVED table as a data frame -- the same object the chapter
#'   prints in its worked solution. Column names become the column headings.
#' @param blank Names of the (numeric) columns the student fills in. Every
#'   other column is shown as given.
#' @param tol Absolute tolerance for blank cells: one number, or a named
#'   vector with one entry per blank column.
#' @param hints Optional named character vector, one hint per blank column,
#'   shown under the table after a wrong entry in that column.
#' @param digits Decimal places for displaying given numeric columns.
#' @param answers Optional list of `tryit_answer()`s asked below the table
#'   (totals, averages, limits, ...).
#' @param intro,question,show As for `tryit_number()`. The twin is one Short
#'   Answer question per entry in `answers`, plus one Written Response
#'   question for the table itself.
tryit_grid <- function(id, title, data, blank, tol = 0.005, hints = NULL, digits = 2,
                       answers = list(), intro = NULL, question = NULL, show = TRUE) {
  stopifnot(is.data.frame(data), all(blank %in% names(data)))
  if (is.null(names(tol))) tol <- stats::setNames(rep(tol, length(blank)), blank)

  given <- function(x) if (is.numeric(x)) formatC(x, digits = digits, format = "f") else as.character(x)
  given_cols <- setdiff(names(data), blank)
  given_rows <- lapply(seq_len(nrow(data)), function(i) {
    vapply(given_cols, function(col) given(data[[col]][i]), character(1))
  })

  if (!is.null(question)) {
    stated <- paste0(question, tryit_html_table(given_cols, given_rows))
    solved <- lapply(seq_len(nrow(data)), function(i) {
      vapply(names(data), function(col) {
        if (col %in% blank) formatC(data[[col]][i], digits = tryit_digits(tol[[col]]), format = "f")
        else given(data[[col]][i])
      }, character(1))
    })
    tryit_export(list(
      c("NewQuestion", "WR"),
      c("ID", tryit_qid(id, 0)),
      c("Title", sprintf("%s - table", title)),
      c("QuestionText", sprintf("%s<p>For every row, calculate: <b>%s</b>. Show one sample calculation.</p>",
                                stated, paste(blank, collapse = ", ")), "HTML"),
      c("Points", as.character(length(blank))),
      c("Difficulty", "3"),
      c("AnswerKey", tryit_html_table(names(data), solved), "HTML")
    ))
    for (i in seq_along(answers)) tryit_export_answer(id, i, title, stated, answers[[i]])
  }
  if (!show) return(invisible(NULL))

  if (tryit_html()) {
    columns <- lapply(names(data), function(col) {
      is_blank <- col %in% blank
      list(label = col, blank = is_blank,
           tol = if (is_blank) tol[[col]] else NULL,
           hint = if (is_blank && !is.null(hints) && col %in% names(hints)) hints[[col]] else NULL)
    })
    rows <- lapply(seq_len(nrow(data)), function(i) {
      lapply(names(data), function(col) {
        if (col %in% blank) data[[col]][i] else given(data[[col]][i])
      })
    })
    tryit_emit("grid", id, list(title = title, intro = intro, columns = columns,
                                rows = rows, answers = answers))
  } else {
    cat(sprintf("\n\n**%s**\n\n", title))
    if (!is.null(intro)) cat(intro, "\n\n")
    sheet <- data
    for (col in names(sheet)) {
      sheet[[col]] <- if (col %in% blank) "" else given(data[[col]])
    }
    print(knitr::kable(sheet, align = "c"))
    cat("\n\n")
    tryit_print_answers(answers)
  }
}

#---- tryit_sort ---------------------------------------------------------------

#' Cards the student assigns to categories
#'
#' @param id Unique within the chapter.
#' @param title Card heading.
#' @param bins Character vector of category names, in display order.
#' @param cards A data frame with columns `text` (the card), `bin` (its
#'   correct category, one of `bins`) and optionally `why` (a one-line
#'   explanation shown once the card has been checked).
#' @param intro,question,show As for `tryit_number()`. The twin is a single
#'   Matching question; `question` defaults to the intro.
#' @param print_key Print the answer key under the worksheet in PDF/EPUB.
tryit_sort <- function(id, title, bins, cards, intro = NULL, question = intro,
                       show = TRUE, print_key = TRUE) {
  stopifnot(is.data.frame(cards), all(c("text", "bin") %in% names(cards)),
            all(cards$bin %in% bins))
  has_why <- "why" %in% names(cards)

  if (!is.null(question)) {
    tryit_export(c(
      list(c("NewQuestion", "M"),
           c("ID", tryit_qid(id, 1)),
           c("Title", title),
           c("QuestionText", question, "HTML"),
           c("Points", as.character(nrow(cards))),
           c("Difficulty", "2"),
           c("Scoring", "EquallyWeighted")),
      lapply(seq_along(bins), function(i) c("Choice", as.character(i), bins[i])),
      lapply(seq_len(nrow(cards)), function(i) {
        c("Match", as.character(match(cards$bin[i], bins)), cards$text[i])
      })
    ))
  }
  if (!show) return(invisible(NULL))

  if (tryit_html()) {
    tryit_emit("sort", id, list(
      title = title, intro = intro, bins = as.list(bins),
      cards = lapply(seq_len(nrow(cards)), function(i) {
        list(text = cards$text[i], bin = match(cards$bin[i], bins) - 1,
             why = if (has_why) cards$why[i] else NULL)
      })
    ))
  } else {
    cat(sprintf("\n\n**%s**\n\n", title))
    if (!is.null(intro)) cat(intro, "\n\n")
    cat(sprintf("Categories: %s\n\n", paste(bins, collapse = " / ")))
    cat(sprintf("%d. %s \\_\\_\\_\\_\\_\\_\\_\\_\n", seq_len(nrow(cards)), cards$text), sep = "")
    if (print_key) {
      cat(sprintf("\n*Answers: %s.*\n\n",
                  paste(sprintf("%d %s", seq_len(nrow(cards)), cards$bin), collapse = "; ")))
    }
  }
}

#---- tryit_order --------------------------------------------------------------

#' Steps the student puts in the right sequence
#'
#' @param id Unique within the chapter.
#' @param title Card heading.
#' @param steps Character vector of steps IN THE CORRECT ORDER. The page
#'   shuffles them; the student moves each one up or down.
#' @param intro,question,show As for `tryit_number()`. The twin is a single
#'   Ordering question; `question` defaults to the intro.
#' @param print_key Print the answer key under the worksheet in PDF/EPUB.
tryit_order <- function(id, title, steps, intro = NULL, question = intro,
                        show = TRUE, print_key = TRUE) {
  stopifnot(is.character(steps), length(steps) >= 2, !anyDuplicated(steps))

  if (!is.null(question)) {
    tryit_export(c(
      list(c("NewQuestion", "O"),
           c("ID", tryit_qid(id, 1)),
           c("Title", title),
           c("QuestionText", question, "HTML"),
           c("Points", as.character(length(steps))),
           c("Difficulty", "2"),
           c("Scoring", "EquallyWeighted")),
      lapply(steps, function(step) c("Item", step, "NOT HTML"))
    ))
  }
  if (!show) return(invisible(NULL))

  if (tryit_html()) {
    tryit_emit("order", id, list(title = title, intro = intro, steps = as.list(steps)))
  } else {
    # Alphabetical rather than random, so printing never touches the
    # chapter's random-number stream.
    listed <- order(steps)
    cat(sprintf("\n\n**%s**\n\n", title))
    if (!is.null(intro)) cat(intro, "\n\n")
    cat("Number these in the correct order:\n\n")
    cat(sprintf("- \\_\\_\\_\\_ %s\n", steps[listed]), sep = "")
    if (print_key) {
      cat(sprintf("\n*Answers, in the order listed: %s.*\n\n",
                  paste(listed, collapse = ", ")))
    }
  }
}
