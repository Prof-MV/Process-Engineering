# Prompt: add interactive exercises to a Quarto textbook

Paste everything below the line into a Claude Code session opened at the root
of the book's repository. Optionally append a line such as
`Scope: chapters 3–6 only` or `Start at phase 3`.

---

I teach from this Quarto book and want students to do more than read it. Please
review the book and add interactive exercises that a student can work through
alone, or that I can run with the whole class on a projector.

## What I am after

Most of what is interactive in my books today is "change an input and watch the
output". That is useful, but the student never has to commit to an answer. I
want more exercises where the student performs the method and the page tells
them whether they got it right.

Two reference examples show the range. Read both before proposing anything.

- **Calculator card.** A labelled-input card driving a live webR cell, with the
  R source collapsed underneath.
  Live: <https://prof-mv.github.io/Process-Engineering/02-Process-and-Design.html>
  ("Fixed Automation Cost Calculator").
  Source: `R/helpers.R` (`qwebr_calc_card`), `js/qwebr-calculator.js` and
  `style.css` in <https://github.com/Prof-MV/Process-Engineering>.
- **Fill-in-and-check diagram.** A pre-drawn network whose node boxes the
  student fills in by hand; cells turn green or red, and a solved version sits
  behind a reveal.
  Live: <https://prof-mv.github.io/Sustainability-and-Business-Practices/06-Network-Diagrams-and-AON.html#try-it-yourself-fill-in-the-aon-node-boxes>
  Source: `06-Network-Diagrams-and-AON.qmd` in
  <https://github.com/Prof-MV/Sustainability-and-Business-Practices>.

The second example is the kind I have least of and want most. Note that it is
about 250 lines of hand-written HTML and inline script for a single exercise.
Do not copy that approach. Build a small shared library so each exercise is a
short declaration.

## How to work

Work in four phases and stop where marked. The stops exist because the
exercise list and the library's interface are much cheaper to change before
they have been applied to twenty chapters.

### Phase 1 — Understand the book (read-only)

Find out, from the repository itself:

- The chapter list and reading order (`_quarto.yml`), the output formats, and
  how the site is built and deployed.
- What interactive machinery already exists: webR or other live-code
  extensions, calculator cards, any `tryit` library from a previous run of
  this prompt, custom JavaScript, CSS conventions, R helper files.
- How chapters are structured: learning objectives, worked examples, review or
  practice questions, and how reveals are written.
- Which chapters load webR and which do not.
- Any `CLAUDE.md`, README or planning notes that record conventions.

My books share one exercise library, called `tryit`: `R/tryit.R`,
`js/tryit.js` and the `.tryit-*` section of `style.css`. It currently provides
`tryit_number()`, `tryit_grid()`, `tryit_sort()`, `tryit_order()`,
`tryit_diagram()`, `tryit_balance()` and `tryit_layout()`, plus
`goal`/`goal_test` arguments on `qwebr_calc_card()` (in `R/helpers.R` and
`js/qwebr-calculator.js`) that turn a calculator into a challenge. Its home is the
Process Engineering book, which is usually a sibling folder of this one
(`../ProcessEngineering`) and otherwise the GitHub repository above. If this
repository does not have the library, copy it from there and keep its
interface, so my books stay consistent. Read that book's
`INTERACTIVE-EXERCISES-PLAN.md` as well; it shows what a finished proposal
looks like. If you add a widget type or fix a bug here, tell me, so I can
carry the change back.

### Phase 2 — Audit and propose, then stop

Read every chapter in scope. For each one, find the places where a student is
shown a method and could be asked to perform it: a calculation with one right
answer, a table or diagram filled in by procedure, a classification, a
sequence, a figure to read, a lookup-table method, a trade-off with a
crossover, a process with randomness.

Write the proposal to `INTERACTIVE-EXERCISES-PLAN.md` at the repository root:

1. A short inventory of what is interactive today, with counts per chapter,
   and which chapters have nothing.
2. The widget types you need, kept to as few as will cover the ideas. The
   types below have covered a full engineering textbook; add or drop types to
   suit the subject.

   | Type | The student… |
   |---|---|
   | check-number | types a numeric answer, marked against a tolerance, solution unlocks after an attempt |
   | fill-grid | fills blank table cells, each marked individually |
   | fill-diagram | fills cells sitting on the nodes of a diagram |
   | sort-bins | assigns cards to categories |
   | order-steps | arranges steps in sequence |
   | label-figure | matches numbered markers on a figure to terms |
   | challenge | drives an existing calculator to a stated goal |
   | sandbox | runs a stochastic simulation and compares runs |
   | scorer | works through a lookup-table method step by step |

3. For each chapter, two to five concrete ideas in a table: what the student
   does, widget type, solo or class, effort (S/M/L), and which one you would
   build first. Be specific to the chapter's content; "a quiz on section 3" is
   not an idea.
4. A phased build order in which each phase ends with something I can see in a
   rendered chapter, and the first phase is a pilot in a single chapter.
5. Open decisions that are mine to make.

Then stop and show me a summary. Do not build anything until I reply.

### Phase 3 — Build the library and a pilot, then stop

Build only the widget types the pilot chapter needs, and apply them there.
Then stop so I can try the pilot in a browser.

Requirements for the library:

- **One declaration per exercise.** An R helper called from a
  `results='asis'` chunk emits the markup, in the same style as
  `qwebr_calc_card()`. Chapters contain no hand-written widget HTML or
  `<script>` blocks. If the book does not use knitr, use the equivalent
  mechanism (a Lua filter or shortcode) and say so in the plan.
- **One source of truth for answers.** Compute the answer key at render time
  from the same data that produces the printed solution, and embed it as JSON.
  The checker and the solution must not be able to disagree.
- **No webR unless the widget needs to compute.** Checking, sorting, ordering
  and scoring are plain JavaScript, so they load instantly and work in
  chapters that do not load webR. Simulations and calculator goals may use it.
- **Multiple widgets per page.** Namespace IDs per instance, guard against the
  script being included twice, and keep one stylesheet section.
- **Print and EPUB.** Each widget degrades to a blank worksheet followed by
  the solution. A PDF render must not break or show raw HTML.
- **Accessible input.** Everything works by keyboard and on a touch screen:
  click-to-assign rather than drag-only, labelled inputs, feedback that does
  not rely on colour alone.
- **Feedback that teaches.** Mark per cell or per item, allow unlimited
  attempts, offer a hint after a miss where one is available, include a reset,
  and keep the full worked solution behind a reveal.
- **Match the book.** Reuse its colours, fonts, card styling and comment
  density. A widget should look like it belongs beside the existing calculator
  cards.
- **Graded twins.** I mark in Brightspace. Every exercise that has a single
  right answer should also be exported as a Brightspace import file
  (`quizzes/tryit_<chapter>.csv`), generated from the same declaration: Short
  Answer for numbers, Matching for sorters, Ordering for sequences, Written
  Response with an answer key for tables. Give each exercise the full problem
  statement so the twin stands alone, set the course code used in question
  IDs, and check whether `quizzes/` is committed or ignored in this
  repository. I already have a quiz per chapter; these are additions, not
  replacements.

Requirements for the exercises:

- Tie each one to a stated learning objective, and make the student perform
  the step that objective names.
- Use fresh data, never the worked example's numbers. Where it helps a class,
  accept a seed or team number so groups get different problems.
- Keep to three or four per chapter. Do not replace existing content unless
  the plan says so; add alongside it.
- These are practice. Answers are visible in the page source, so do not
  present them as graded. Where a twin will count for marks, give it different
  numbers from the on-page version.
- Do not build polling or anything else that needs a server. I run live polls
  in Brightspace.

### Phase 4 — Roll out

Work through the plan's phases on a branch, one commit per chapter, building
further widget types as chapters need them.

## Checking your work

After each chapter, render it to HTML and confirm in a browser, or with a
headless browser if one is available, that every new widget accepts a correct
answer, rejects a wrong one, and resets, and that the console is clean. If you
cannot run a browser, test the checking logic directly and tell me that the
visual check is still mine to do. Render the print format once per phase.

Three checks have caught real mistakes and are worth automating once, then
running on every chapter:

- Load each rendered page in a headless DOM, feed every exercise its own
  answer key (exact, and rounded the way a student would enter it), and
  require all-correct; then feed one wrong answer and require it to be
  flagged.
- For every calculator challenge, run the cell in plain R with the default
  inputs and require the goal to be unmet, then with one solution you have
  worked out and require it to be met. A challenge that is already met, or
  that cannot be met within the input ranges, is a defect.
- Recompute every answer you put in a checked review question from the
  question's own givens, and compare it with the book's printed solution. If
  they differ, tell me; do not silently pick one.

While writing exercises you will read worked examples closely. If you find an
example whose numbers are implausible or an answer that looks wrong, leave it
as it is and list it in your report.

Do not commit rendered output unless this repository already does. Stage files
by name, not with `git add -A`: a failed render can leave intermediate files
(`*.knit.md`, a stray `.html`) in the project root. If a render fails with a
file-access error, delete those leftovers and retry before investigating. Do
not push or deploy; I will do that.

## What to tell me

At each stop and at the end, report what you built and where, what you
verified and how, anything you could not verify, and any exercise you dropped
with the reason. Keep `INTERACTIVE-EXERCISES-PLAN.md` current by marking
items done, so a later session can resume from it.
