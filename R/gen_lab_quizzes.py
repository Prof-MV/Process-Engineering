# -*- coding: utf-8 -*-
"""Generate Brightspace/D2L question-import CSVs for the lab quizzes (one per lab, named by lab).

Run:  python R/gen_lab_quizzes.py   (from the repo root, or anywhere)

Writes one file per lab to  quizzes/<lab-slug>_quiz.csv  (e.g. quizzes/logic-rocksi_quiz.csv).
Labs are identified by name, not number (see 30-Labs.qmd).
`quizzes/` is gitignored (like R/make_lab_data.R's output) -- the CSVs are staged
on FOL, not committed; this script is the source of record for them.

Every question is Written Response (WR) = manual grading, which is what these
labs need (describe-what-you-did answers + file/screenshot/video attachments).
Brightspace's import format has no file-upload question type, so upload steps are
WR questions whose text says exactly what to attach; turn on "Allow attachments"
on those questions (or quiz-wide) after import. Save each file as CSV UTF-8.
"""

import csv, os, io

# repo root = parent of this script's folder (R/); output dir = <root>/quizzes
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "quizzes")
os.makedirs(OUT, exist_ok=True)
CC = "ENGR3027"

def q(title, text, points, difficulty=3, initial="Type your answer here.", answerkey=""):
    return dict(title=title, text=text, points=points, difficulty=difficulty,
               initial=initial, answerkey=answerkey)

def write_lab(slug, lab_title, note_lines, questions):
    path = os.path.join(OUT, "%s_quiz.csv" % slug)
    with io.open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["//%s" % lab_title])
        w.writerow(["//Import these questions into the '%s' quiz on FOL (Brightspace)." % lab_title])
        w.writerow(["//All questions are Written Response (manual grading)."])
        w.writerow(['//Turn on "Allow attachments" on the questions that ask for a file, '
                    'screenshot or recording (or enable attachments for the whole quiz).'])
        for line in note_lines:
            w.writerow(["//" + line])
        w.writerow(["//Save this file as CSV UTF-8 before importing."])
        w.writerow([])
        i = 0
        for q in questions:
            i += 1
            w.writerow(["NewQuestion", "WR"])
            w.writerow(["ID", "%s-%s-%02d" % (CC, slug.upper(), i)])
            w.writerow(["Title", q["title"]])
            # 3rd column "HTML" tells the D2L importer to render the body as
            # HTML instead of printing the tags literally.
            w.writerow(["QuestionText", q["text"], "HTML"])
            w.writerow(["Points", q["points"]])
            w.writerow(["Difficulty", q["difficulty"]])
            # Same HTML flag as QuestionText -- several labs now pre-fill
            # InitialText with real formatting (tables, bold labels), not
            # just a plain sentence.
            w.writerow(["InitialText", q["initial"], "HTML"])
            if q["answerkey"]:
                w.writerow(["AnswerKey", q["answerkey"]])
            w.writerow([])
    total = sum(float(x["points"]) for x in questions)
    print("wrote %s  (%d questions, %g points)" % (path, len(questions), total))

DECL = q(
    "Start-of-lab declaration",
    "<p><b>Read before you begin.</b> This is an individual lab. Everything you "
    "submit must be your own work. Work through the questions below <b>in order</b> "
    "during the lab period; each one tells you what to do and asks you to describe, "
    "in your own words, what you actually did.</p>"
    "<p>In the box, type: (1) your full name and student number; (2) the computer / "
    "login you are working on; (3) confirmation that you understand this is an "
    "individual lab and the work is your own.</p>",
    0, 1, "Name, student number, workstation, and your confirmation.")

def UPLOAD(items):
    return q(
        "Upload your files",
        "<p><b>Attach every file listed below to this question</b> (use the "
        "attachment control). Name each file <i>Lastname_Firstname_Lab_&lt;item&gt;</i>. "
        "Do not zip them. If a file is missing you lose the marks for the task it "
        "belongs to.</p><ul>" + "".join("<li>%s</li>" % it for it in items) + "</ul>",
        0, 1, "Attach the files. Add a line here listing what you attached.")

# ----------------------------------------------------------------------------- logic-rocksi
write_lab("logic-rocksi", "Logic Thinking for Robot Control: Rocksi",
 ["Simulator: Rocksi (rocksi.net) -- browser, no login, no plug-in. LightBot is "
  "NOT used (it needs a plug-in the college machines do not have); all of the "
  "programming-logic work is done in Rocksi.",
  "Tools you will attach: your saved Rocksi program (Rocksi 'Save' downloads a "
  "workspace file) and Snipping Tool screenshots.",
  "AI use: not permitted -- the logic must be your own."],
 [DECL,
  q("Task 1 - Sequencing (1 mark)",
    "<p>In Rocksi, build a block program that drives the arm through a planned "
    "sequence of <b>at least four</b> positions and back to a safe/home pose "
    "(for example: home -&gt; A -&gt; B -&gt; C -&gt; home). Run it and confirm "
    "the arm follows the sequence.</p>"
    "<p><b>Describe, block by block, the exact sequence of commands you used</b>, "
    "and say how you set each position. Attach a Snipping Tool screenshot showing "
    "your block stack and the arm at the final pose.</p>",
    1, 2, "List every block in order; screenshot attached.",
    "Sequence of >=4 taught positions; every block named in order; screenshot shows the block stack."),
  q("Task 2 - Loops (2 marks)",
    "<p>Take a repetitive part of your motion (a move that repeats, or a "
    "pick-repeat pattern) and rebuild it using a <b>repeat / loop block</b> "
    "instead of duplicated blocks. Run it and confirm the behaviour is unchanged.</p>"
    "<p><b>State the number of blocks before and after</b> the change, and "
    "<b>explain how using the loop let you complete the task more efficiently</b>. "
    "Attach a screenshot of the looped program.</p>",
    2, 3, "Blocks before vs after; explanation of the efficiency gain; screenshot.",
    "Loop block genuinely replaces duplicated blocks; block count drops; explanation is about efficiency, not just 'it worked'."),
  q("Task 3 - Conditional / branching logic (2 marks)",
    "<p>Use a <b>conditional block</b> so the program does one thing in one case "
    "and something else in another -- for example branching on the gripper state, "
    "on a sensor/'is object present' check, or on a counter value. Run both "
    "branches.</p>"
    "<p>If your Rocksi block set has no usable <i>if</i> block, instead describe "
    "<b>precisely</b> how you would add a conditional: what input it would test, "
    "the condition, and exactly what each branch would do.</p>"
    "<p><b>Give your conditional as an example and explain its purpose</b> "
    "(what problem it solves). Attach a screenshot if you built one.</p>",
    2, 4, "The conditional (or the precise design), plus its purpose.",
    "A real branch on a testable input, or a precise hypothetical with input + condition + both branches. Purpose explained."),
  q("Task 4 - Pick-and-place sequence (2 marks)",
    "<p>Program a full pick-and-place cycle: move to a pick location, close the "
    "gripper, move to a place location, open the gripper, retract to a safe pose. "
    "Run it.</p>"
    "<p><b>List the complete block sequence</b> and describe how you set each "
    "target position (which coordinate frame, how you jogged/taught it). Attach a "
    "screenshot of the running program, and <b>upload your saved Rocksi program "
    "file</b> (Rocksi 'Save').</p>",
    2, 3, "Full block list; target-setting method described; screenshot + saved program file.",
    "Pick, gripper close, place, gripper open, retract all present; gripper on a digital output; program file attached and opens."),
  q("Task 5 - Simulate a digital input / output (1 mark)",
    "<p>Use an I/O or signal block (or the gripper output) to gate or troubleshoot "
    "an operation -- for example, only place the part when an 'input' is on, or "
    "toggle an output to represent a downstream signal.</p>"
    "<p><b>Explain what I/O you simulated, how you did it, and its effect on the "
    "run.</b></p>",
    1, 3, "What I/O, how simulated, and the observed effect."),
  q("Task 6 - Optimisation challenge (1 mark)",
    "<p>Reduce your pick-and-place program (Task 4) to the <b>fewest blocks</b> "
    "that still runs correctly. Techniques: loops, removing redundant moves, "
    "combining approach/retract, reusing targets.</p>"
    "<p><b>State the block count before and after, and describe every change you "
    "made</b> and why it is safe (the arm still reaches the same points without "
    "collisions).</p>",
    1, 4, "Block count before/after; each optimisation described and justified."),
  q("Task 7 - Reflection (1 mark)",
    "<p>In 3-5 sentences: (1) why do sequencing, loops and conditional logic "
    "matter for reliable, safe, repeatable automation? (2) describe the role of a "
    "<b>teach pendant</b> on a real robot -- jogging, teaching points, the "
    "deadman/E-stop, reduced-speed teach mode, and I/O testing.</p>",
    1, 3, "Your reflection.",
    "Links the three logic constructs to reliability/safety/repeatability; names the teach-pendant functions."),
  UPLOAD(["Saved Rocksi program file (from Task 4)",
          "Screenshot - Task 1 (block stack + final pose)",
          "Screenshot - Task 2 (looped program)",
          "Screenshot - Task 3 (conditional, if built)",
          "Screenshot - Task 4 (running pick-and-place)"]),
 ])

# ----------------------------------------------------------------------------- design-documentation
L2_BOM_ROWS = [
    # item, part_number, description, qty, source
    (1, "205-5478",  "Shaft (ANSI 4140)",                              1, "In-house"),
    (2, "1199N14",   "Spring-Loaded Rotary Shaft Seal with Wiper Lip", 1, "Purchased -- McMaster-Carr"),
    (3, "6677K88",   "Tapered-Roller Bearing with Steel Ring",         2, "Purchased -- McMaster-Carr"),
    (4, "91595A179", "Dowel Pin",                                      1, "Purchased -- McMaster-Carr"),
    (5, "98541A440", "External Retaining Ring",                        1, "Purchased -- McMaster-Carr"),
    (6, "1523T76",   "Desiccant Sachet",                                1, "Purchased -- McMaster-Carr"),
    (7, "910-1473",  "Moulded Tray",                                    1, "? -- research a packaging supplier"),
    (8, "911-4358",  "Labelled Carton",                                 1, "? -- research a packaging supplier"),
]

def _bom_table(cols):
    """cols: list of column headers; pulls the matching fields from L2_BOM_ROWS."""
    field_idx = {"Item": 0, "Part Number": 1, "Description": 2, "Qty": 3, "Source": 4}
    head = "<tr>" + "".join("<th>%s</th>" % c for c in cols) + "</tr>"
    body = ""
    for row in L2_BOM_ROWS:
        body += "<tr>" + "".join("<td>%s</td>" % row[field_idx[c]] for c in cols) + "</tr>"
    return ("<table border=\"1\" cellpadding=\"4\" cellspacing=\"0\">" + head + body
            + "</table>")

L2_SPEC_INITIAL = (
    "<p><b>SHAFT REPLACEMENT KIT -- SPECIFICATION SHEET</b> "
    "(edit every field below; delete this instruction line)</p>"
    "<p><b>Customer:</b> [state]<br>"
    "<b>Kit part number:</b> 410-2365, Rev B<br>"
    "<b>Kit description:</b> Shaft Replacement Kit</p>"
    "<p><b>Kit contents</b> (from assembly drawing 410-2365, Rev B):</p>"
    + _bom_table(["Item", "Part Number", "Description", "Qty", "Source"]) +
    "<p><b>Key dimensions and tolerances</b> (from shaft drawing 205-5478, Rev B):<br>"
    "- Overall shaft length: 100.00 +/-0.15 mm<br>"
    "- Shaft diameter: dia 25.00 +/-0.05 mm<br>"
    "- Cross hole: dia 4.20 +/-0.15 mm, countersink 1.00 x 90 deg, located "
    "6.50 +/-0.15 mm from one end<br>"
    "- Material: ANSI 4140 steel<br>"
    "- Dimensioning standard: ASME Y14.5</p>"
    "<p><b>Assembly requirements</b> (carry these into the spec sheet as process "
    "requirements, not just drawing notes):<br>"
    "- Bearing push-on force: between 200 N and 300 N<br>"
    "- Dowel pin inserted symmetric in the shaft<br>"
    "- Parts clean and free of oil before assembly</p>"
    "<p><b>Packaging and marking:</b> [describe -- tray + carton, what the carton "
    "label must show]</p>"
    "<p><b>Applicable standards:</b> [state]</p>"
    "<p><b>Target cycle time -- work this out yourself:</b><br>"
    "1. Precitech's target is 250 kits/day on one 8-hour shift. State your "
    "paid-break / planned-downtime assumption, then compute the <b>bare</b> "
    "cycle time = available seconds per shift / 250 -- what the cell would need "
    "if it never stopped.<br>"
    "2. That number has zero margin. Real cells lose time to washroom breaks, "
    "material shortages at the storage rack, and equipment breakdowns. State a "
    "total loss allowance for those three (a % or a minutes/shift figure) and "
    "justify it, then compute your <b>design target</b> cycle time -- faster "
    "than the bare number by that margin, so the cell still hits 250 kits/day "
    "despite the losses.<br>"
    "3. Bare cycle time: [value] s/kit. Design target cycle time (with margin): "
    "[value] s/kit.</p>"
)

L2_BOM_INITIAL = (
    "<p>Confirm/complete this list, then transfer it into "
    "<b>Bill_of_Materials_Template_for_Excel.xlsx</b> (already pre-filled with "
    "these part numbers, descriptions and quantities):</p>"
    + _bom_table(["Item", "Part Number", "Description", "Qty", "Source"]) +
    "<p>Fill in <b>Unit</b> and <b>Supplier</b> for every row in the Excel file. "
    "For the tray and carton, McMaster-Carr does not sell custom moulded trays "
    "or printed cartons -- research and name a real packaging supplier.</p>"
)

write_lab("design-documentation", "Engineering Design Process Documentation",
 ["Case study: Precitech Components shaft-kit assembly & packing cell "
  "(see the Labs chapter, Engineering Design Process Documentation). It is the single source of requirements.",
  "Drawings on FOL / in the Labs chapter: assembly drawing 410-2365 Rev B and "
  "shaft drawing 205-5478 Rev B. Purchased components are from McMaster-Carr.",
  "Tools: Microsoft Word/Visio, Microsoft Project, Microsoft Excel.",
  "Templates on FOL: Bill_of_Materials_Template_for_Excel.xlsx (pre-filled with "
  "the real part numbers), Gantt_chart_template.xlsx, HSE risk-assessment Word "
  "template.",
  "Read 'The automation decision' in the Engineering Design Process Documentation lab in the Labs chapter before the facility-"
  "layout question -- you choose and justify a cell configuration there.",
  "The task-list and Gantt-chart example chains given in this quiz are "
  "starting points only and are missing steps -- finding and adding what's "
  "missing is part of the mark.",
  "Keep your layout drawing -- you reuse it in the Facility Design & Simulation lab.",
  "AI use: not permitted for any part of this lab."],
 [DECL,
  q("Phase 1 - Specification sheet + cycle time (2.5 marks)",
    "<p>Complete the <b>specification sheet</b> pre-filled in the answer box "
    "below -- it already has the kit contents, part numbers and key dimensions "
    "from the assembly drawings. You fill in the customer, packaging/marking, "
    "applicable standards, and (the substantial part) <b>work out the target "
    "cycle time</b> with a realistic safety margin.</p>"
    "<p>Also write a short <b>specification sheet for one bought-in "
    "component</b> (e.g. the tapered roller bearing, 6677K88): part number, "
    "dimensions/spec, material, applicable standard, source.</p>"
    "<p>Attach both as a PDF or DOCX (retype/paste the completed content into "
    "your own document).</p>",
    2.5, 4, L2_SPEC_INITIAL,
    "All 8 kit items match drawing 410-2365 (part numbers, qty, source incl. "
    "McMaster-Carr); key dimensions from 205-5478 correct (100.00+/-0.15 mm, "
    "dia 25.00+/-0.05 mm, hole dia 4.20+/-0.15 mm at 6.50+/-0.15 mm, ANSI 4140); "
    "assembly notes carried over (200-300 N press force, symmetric dowel, "
    "clean/oil-free); bare cycle time = shift-available-seconds / 250, correctly "
    "computed with a stated break assumption; design target cycle time is "
    "FASTER than the bare figure by a justified, reasonable loss allowance "
    "(roughly 5-20% is typical -- judge the reasoning, not a single right "
    "number); component spec sheet present and consistent."),
  q("Phase 1 - Bill of materials (1.5 marks)",
    "<p>Open the Excel BOM template and complete it for <b>one complete "
    "kit</b> using the pre-filled list in the answer box below.</p>"
    "<p><b>Describe what you found for the tray/carton supplier</b> and "
    "confirm the rest matches. Attach the completed .xlsx.</p>",
    1.5, 3, L2_BOM_INITIAL,
    "All 8 kit items present with correct part numbers and quantities; "
    "Unit and Supplier filled for every row; a real (non-McMaster-Carr) "
    "packaging supplier named for the tray and carton with a one-line reason."),
  q("Phase 2 - Task list / process flow (2 marks)",
    "<p>Build a <b>chronological task list</b> for producing one kit. To get "
    "you started: receive blanks -&gt; store components -&gt; pick components "
    "for one kit -&gt; press bearings -&gt; fit retaining ring and seal -&gt; "
    "inspect -&gt; place in tray -&gt; close and label carton -&gt; stage for "
    "dock.</p>"
    "<p><b>That chain is a starting point only -- it is missing steps.</b> "
    "Cross-check it against the BOM (8 items, not 6) and the assembly notes on "
    "drawing 410-2365 (bearing press-on force, dowel pin symmetric, parts clean "
    "and oil-free) and add every task it is missing -- for example: where does "
    "the dowel pin actually get inserted? the desiccant sachet? is there an "
    "incoming-inspection step for the purchased components? a cleaning/"
    "degreasing step? Add a <b>duration</b> column for every task, including the "
    "ones you added. Use the task-numbering scheme (Task 1 -&gt; Sub-task 11 "
    "-&gt; Sub-sub-task 121 ...) from the supplement. Draw the flow as a chart "
    "in Visio or Word.</p>"
    "<p><b>List every step you added and why the starting chain was missing "
    "it.</b> Attach the task list and the flow chart.</p>",
    2, 4, "The steps you added beyond the starting chain, and why each is needed.",
    "Starting chain expanded with at least the dowel-pin insertion and desiccant "
    "placement, plus one more defensible addition (e.g. incoming inspection or "
    "degreasing) -- reasoning given for each; durations present for every task; "
    "numbering scheme applied; chart matches the list."),
  q("Phase 3 - Project schedule & Gantt chart (1.5 marks)",
    "<p>Open Gantt_chart_template.xlsx -- it already has six starter tasks for "
    "<b>standing up the cell</b> (procure racking and fixtures, install bearing "
    "press, set up inspection station, write the SOP, train operators, run a "
    "pilot batch).</p>"
    "<p><b>That list is a starting point only, and it is missing tasks -- which "
    "ones depends on the cell configuration you choose in the facility-layout "
    "question.</b> An automated-turntable cell needs tasks a manual U-cell "
    "doesn't, and vice versa (for example: turntable/tooling design and "
    "procurement plus station debug and guarding for the automated option; "
    "conveyor and fixture build plus operator cross-training for the manual "
    "option). Add every task your chosen configuration actually needs before it "
    "can run a pilot batch, with durations and dependencies. Then use Project's "
    "Import Wizard to turn the whole thing into a schedule and Gantt chart (see "
    "the template's 'Read me first' sheet).</p>"
    "<p><b>List every task you added beyond the starter six, and why your "
    "chosen configuration needs it.</b> Attach the .mpp file (and a PDF/image "
    "of the Gantt chart).</p>",
    1.5, 4, "Tasks added beyond the starter six, and why your configuration needs each.",
    "Starter six tasks kept; at least 2-3 configuration-specific tasks added and "
    "clearly tied to the Option A/B choice from the layout question; durations "
    "and dependencies sensible; Gantt generated from Project (not hand-drawn)."),
  q("Phase 4 - Facility layout + the automation decision (1.5 marks)",
    "<p><b>Configuration decision:</b> read 'The automation decision' in the "
    "Engineering Design Process Documentation lab -- Option A (automated turntable, 6-7 stations, one "
    "load/unload operator) vs. Option B (manual U-cell, one operator per "
    "station). <b>State which configuration you are designing</b> and justify "
    "it with <b>at least two pros and two cons</b> from the comparison table "
    "(or your own reasoning), tied to Precitech's actual volume (250 kits/day), "
    "timeline ('before it is built') and labour situation.</p>"
    "<p><b>Layout:</b> from your (now complete) task list, allocate space for "
    "each activity and draw a General Arrangement of the kitting cell "
    "<b>matching the configuration you chose</b>. Show product in (blanks) and "
    "product out (kits), component storage rack, every station your "
    "configuration needs, and the raw-material, finished-goods, waste and "
    "people-movement flows. <b>Mark where material starvation and material "
    "blockage could occur.</b></p>"
    "<p><b>Describe your configuration choice with its pros/cons, and your "
    "layout decisions.</b> Attach the layout drawing.</p>",
    1.5, 4, "Configuration choice + >=2 pros/cons; layout decisions.",
    "Configuration explicitly chosen (A or B) with >=2 pros and >=2 cons "
    "specific to Precitech's numbers, not generic; layout matches the chosen "
    "configuration (turntable + 1 station for A, ~6-7 stations for B) and the "
    "expanded Phase 2 task list; starvation/blockage points marked."),
  q("Phase 5 - HSE risk assessment (1 mark)",
    "<p>Identify at least <b>five</b> health-and-safety risks in the cell (e.g. "
    "manual handling of the blank trolley, pinch points at the bearing press, "
    "sharp edges on retaining rings, repetitive assembly motion, the carton "
    "knife) and document each in the risk-assessment template (hazard, who is "
    "harmed and how, current controls, further action, owner, deadline, done).</p>"
    "<p><b>List your five risks.</b> Attach the completed risk-assessment "
    "document.</p>",
    1, 3, "Your five risks, briefly.",
    ">=5 realistic risks fully filled in the template, including the hierarchy "
    "of controls in the 'further action' column."),
  UPLOAD(["Shaft-kit spec sheet + component spec sheet",
          "Bill of materials (.xlsx)",
          "Task list + process-flow chart (with the steps you added)",
          "Project schedule (.mpp) + Gantt chart image (with the tasks you added)",
          "Facility layout drawing, labelled with your configuration choice (keep a copy - reused in Facility Design & Simulation)",
          "Completed HSE risk assessment"]),
 ])

# ----------------------------------------------------------------------------- facility-anylogic
write_lab("facility-anylogic", "Manufacturing Facility Design & Simulation (AnyLogic)",
 ["Software: AnyLogic Personal Learning Edition (installed) + the order-fulfilment "
  "/ warehouse demo model staged on FOL. Bring your Engineering Design Process Documentation documents.",
  "You run FOUR parameter sets, 3 simulated minutes each.",
  "AI use: not permitted for any part of this lab."],
 [DECL,
  q("Phase 1 - Electronic facility drawing (4 marks)",
    "<p>Recreate your Engineering Design Process Documentation kitting-cell layout <b>electronically</b> (Visio or "
    "equivalent). Then work through this checklist and <b>record your finding for "
    "each item</b>:</p><ol>"
    "<li>product in / product out shown?</li>"
    "<li>work-sequence task list with timings shown?</li>"
    "<li>tools and component bins shown?</li>"
    "<li>component (raw-material) flow drawn?</li>"
    "<li>finished-kit flow drawn?</li>"
    "<li>waste-material flow drawn?</li>"
    "<li>people-movement flow drawn?</li>"
    "<li>how many stations, and which are automated (e.g. the bearing press)?</li>"
    "<li>where could component <b>starvation</b> occur?</li>"
    "<li>where could finished-kit <b>blockage</b> occur?</li>"
    "<li>are storage / assembly / inspection / packing / staging / social areas "
    "identified?</li></ol>"
    "<p>Attach the electronic drawing. Answer every checklist item in the box.</p>",
    4, 3, "One line per checklist item, plus the drawing attached.",
    "Drawing is electronic and matches the Design Documentation layout; all 11 checklist items answered; starvation/blockage points identified."),
  q("Phase 2 - AnyLogic Run 1: baseline (1.5 marks)",
    "<p>Start AnyLogic and follow the walk-through. Map the model onto the case "
    "study: orders = daily kit demand; goods = bought-in components in the storage "
    "rack; picking = kitting one order; reorder level = the stock at which the "
    "warehouse replenishes the rack.</p>"
    "<p><b>Run 1 parameters:</b> min goods/order = 3, max goods/order = 5, order "
    "interarrival = 25 s, reorder level = 45. Run for <b>3 simulated minutes</b>.</p>"
    "<p>Attach a <b>labelled screenshot of the Statistics screen</b>. In the box, "
    "record the key order statistics (preorder waiting time, picking time, full "
    "processing time) and goods statistics (unavailable goods, stored "
    "reserved/unreserved goods, storing time), and write a short <b>observation "
    "and analysis</b> tied to the cell.</p>",
    1.5, 3, "Run 1 numbers + observation/analysis + labelled screenshot.",
    "Correct parameters; screenshot labelled 'Run 1'; observation references specific statistics and the cell."),
  q("Phase 2 - AnyLogic Run 2: low reorder level (1.5 marks)",
    "<p>Change <b>only</b> the reorder level to <b>20</b> (min 3, max 5, "
    "interarrival 25 s). Run for 3 simulated minutes.</p>"
    "<p>Attach a labelled Statistics screenshot. Record the same statistics as "
    "Run 1 and write your observation and analysis. <b>Does the lower reorder "
    "level starve the kitting station?</b> Compare against Run 1 with numbers.</p>",
    1.5, 3, "Run 2 numbers + comparison to Run 1 + labelled screenshot.",
    "Only reorder level changed; comparison quantified; starvation reasoning correct (more unavailable goods -> longer waiting)."),
  q("Phase 2 - AnyLogic Run 3: variable order size (1.5 marks)",
    "<p>Reset reorder level to 45. Change <b>min goods/order to 1</b> (max 5, "
    "interarrival 25 s). Run for 3 simulated minutes.</p>"
    "<p>Attach a labelled Statistics screenshot. Record the statistics and write "
    "your observation and analysis: how does more variable order size affect "
    "waiting and picking time versus Run 1?</p>",
    1.5, 3, "Run 3 numbers + comparison + labelled screenshot.",
    "Only min goods/order changed; effect of variability explained against Run 1."),
  q("Phase 2 - AnyLogic Run 4: slower order arrival (1.5 marks)",
    "<p>Reset min goods/order to 3. Change <b>order interarrival to 45 s</b> "
    "(min 3, max 5, reorder level 45). Run for 3 simulated minutes.</p>"
    "<p>Attach a labelled Statistics screenshot. Record the statistics and write "
    "your observation and analysis: <b>does a slower order arrival rate clear the "
    "backlog?</b> Compare against Run 1.</p>",
    1.5, 3, "Run 4 numbers + comparison + labelled screenshot.",
    "Only interarrival changed; backlog/throughput reasoning correct against Run 1."),
  q("Wrap-up (0 marks - required)",
    "<p>In 3-4 sentences, state <b>what the four runs together tell you about "
    "component-stock policy</b> for this cell: where to hold buffer stock and how "
    "often to replenish, and the trade-off you would recommend to the plant "
    "manager.</p>",
    0, 3, "Your recommendation."),
  UPLOAD(["Electronic facility layout drawing",
          "Saved AnyLogic model file",
          "Statistics screenshot - Run 1 (labelled)",
          "Statistics screenshot - Run 2 (labelled)",
          "Statistics screenshot - Run 3 (labelled)",
          "Statistics screenshot - Run 4 (labelled)"]),
 ])

# ----------------------------------------------------------------------------- lean-vsm
write_lab("lean-vsm", "Lean: Value Stream Mapping, Takt and Pull",
 ["Everything runs in a browser: draw.io, Google Sheets, AnyLogic Cloud "
  "(free public tier). Nothing to install.",
  "Data: vsm_station_data.csv from FOL (Precitech shaft line). Demand = 250 "
  "kits/day on one 8-hour shift.",
  "AI use: permitted with disclosure, but NOT for the map itself or the takt / "
  "PCE calculations -- those must be your own. Name any tool you used and what for."],
 [DECL,
  q("Task 1 - Current-state value stream map (3 marks)",
    "<p>Open vsm_station_data.csv in Google Sheets and read the column headings. "
    "In draw.io, map the shaft line end to end: CNC turn -&gt; deburr -&gt; wash "
    "-&gt; inspect -&gt; the Design Documentation kitting cell -&gt; shipping.</p><ul>"
    "<li>For each process box record cycle time (C/T), changeover time (C/O), "
    "uptime and batch size from the supplied table.</li>"
    "<li>Put an inventory triangle with the WIP count between each pair of boxes.</li>"
    "<li>Add the supplier, the customer, the production-control box, and the "
    "information-flow arrows (forecast, daily order, schedule).</li>"
    "<li>Draw the lead-time ladder along the bottom: processing time on the lower "
    "step, inventory wait time (WIP / daily demand) on the upper step. Total it to "
    "a <b>production lead time</b> and a <b>value-added time</b>.</li></ul>"
    "<p><b>Describe how you built the map</b> and state your production lead time "
    "and value-added time with the arithmetic. Attach the draw.io export.</p>",
    3, 4, "Map description + ladder totals with arithmetic + draw.io export.",
    "All process boxes carry C/T,C/O,uptime,batch; WIP triangles; info flow; ladder totals and actually adds up."),
  q("Task 2 - Takt time and the operator balance chart (2 marks)",
    "<p>In Sheets, compute <b>takt time = available shift time / customer demand</b> "
    "for the 250 kits/day target. <b>State your planned/unplanned downtime "
    "assumption.</b> Build an operator balance chart: one bar per station, station "
    "C/T on the y-axis, a horizontal takt line across all bars.</p>"
    "<p><b>Name the bottleneck station and say by how much it exceeds takt.</b> "
    "Attach the chart (or the Sheets file).</p>",
    2, 3, "Takt value with assumptions + balance chart + bottleneck named and quantified.",
    "Takt arithmetic correct and stated; chart has the takt line; bottleneck identified with the gap in seconds."),
  q("Task 3 - Seven wastes and process cycle efficiency (2 marks)",
    "<p>Walk your map and classify every wait, move and rework against the "
    "<b>seven wastes</b> (transport, inventory, motion, waiting, overproduction, "
    "overprocessing, defects). Give at least one concrete example for each waste "
    "that is present.</p>"
    "<p>Compute <b>process cycle efficiency = value-added time / production lead "
    "time</b> from your Task 1 ladder. State whether the line is 'lean' by the "
    "usual 25% rule of thumb.</p>",
    2, 3, "Seven-wastes table with concrete examples + PCE value with arithmetic + lean judgement.",
    "One concrete example per present waste; PCE computed from the same ladder numbers as Task 1; interpreted."),
  q("Task 4 - Push vs pull vs supermarket on AnyLogic Cloud (2 marks)",
    "<p>Open the supplied push/pull model on AnyLogic Cloud. Run it three ways, "
    "changing <b>only the control policy</b>:</p><ol>"
    "<li><b>Push</b> -- every station runs whenever it has parts.</li>"
    "<li><b>Pull</b> -- downstream withdrawal triggers upstream.</li>"
    "<li><b>Kanban-capped supermarket</b> -- a fixed WIP cap between the bottleneck "
    "and its predecessor.</li></ol>"
    "<p>For each run record <b>average WIP</b> and <b>average lead time</b> from "
    "the model output, in a small table. <b>Interpret the results in two "
    "sentences</b> -- is the ordering what lean theory predicts? Attach the "
    "results table.</p>",
    2, 3, "Three-row results table (WIP, lead time) + interpretation consistent with the numbers.",
    "All three runs done; WIP and lead time for each; interpretation matches the numbers (pull/supermarket lower WIP)."),
  q("Task 5 - Future-state map (1 mark)",
    "<p>In draw.io, redraw the line with <b>one SMED change</b> (halve the "
    "changeover at one station -- justify the halving) and <b>one pull change</b> "
    "(a supermarket or FIFO lane where you had push). Recompute the lead-time "
    "ladder.</p>"
    "<p><b>State the projected lead-time reduction and which of the seven wastes "
    "each change attacks.</b> Attach the future-state draw.io export.</p>",
    1, 3, "Future-state map + recomputed ladder + projected reduction + wastes attacked.",
    "Both changes present and justified; ladder recomputed; reduction quantified against Task 1."),
  UPLOAD(["Current-state VSM (draw.io export)",
          "Future-state VSM (draw.io export)",
          "Google Sheets file (takt, balance chart, PCE, push/pull table)",
          "AI-use disclosure line (which tool, what for) if you used one"]),
 ])

# ----------------------------------------------------------------------------- ergonomics-reba
write_lab("ergonomics-reba", "Ergonomics in Automated Manufacturing (REBA)",
 ["This quiz assigns you ONE of three sample tasks: (1) lifting boxes repeatedly, "
  "(2) computer-workstation setup, (3) floor cleaning with a buffer. Your "
  "assigned task is stated in Question 1.",
  "Tools: printed REBA Employee Assessment Worksheet + REBA cheat sheet.",
  "Disclose any AI tool you use; not permitted for the REBA scoring itself."],
 [q("Start-of-lab declaration + your assigned task",
    "<p><b>Read before you begin.</b> This is an individual lab; the work is your "
    "own. Type: your full name and student number; your workstation; and "
    "<b>which sample task you have been assigned</b> -- Task 1 (lifting boxes), "
    "Task 2 (workstation), or Task 3 (floor cleaning). If you have not been given "
    "one, use the task whose number matches the last digit of your student number "
    "(0-3 = Task 1, 4-6 = Task 2, 7-9 = Task 3) and state that here.</p>",
    0, 1, "Name, student number, workstation, assigned task number."),
  q("Task observation (1 mark)",
    "<p>Watch the intro videos (importance of ergonomics; common risks and "
    "impacts; how to use the REBA worksheet). Then observe your assigned task "
    "clip/photo set.</p>"
    "<p><b>Describe the task and list the ergonomic risks you see</b> -- "
    "repetitive motion, awkward posture, heavy lifting, vibration, glare, chair "
    "height, reach, etc. Note the single worst posture you will score with REBA "
    "and why you picked that moment.</p>",
    1, 2, "Task description + observed risks + the posture you will score.",
    "Task correctly described; several relevant risks; a defensible worst-case posture chosen."),
  q("REBA scoring (4 marks)",
    "<p>Score your assigned task with the REBA Employee Assessment Worksheet. "
    "<b>Show every sub-score, not just the final number:</b></p><ul>"
    "<li>Group A: trunk, neck, legs -> Table A score; plus the load/force score.</li>"
    "<li>Group B: upper arm, lower arm, wrist -> Table B score; plus the coupling "
    "score.</li>"
    "<li>Table C score; plus the activity score.</li>"
    "<li><b>Final REBA score and its risk band</b> (negligible / low / medium / "
    "high / very high) and the recommended action level.</li></ul>"
    "<p>Type the full breakdown here and <b>attach a photo or scan of your "
    "completed worksheet</b>.</p>",
    4, 4, "Every sub-score shown; Table A/B/C; coupling + activity; final score + band; worksheet attached.",
    "Trunk/neck/leg and arm/wrist sub-scores correct for the chosen posture; coupling and activity adjustments applied; final score and band consistent."),
  q("Sources of error and limitations (4 marks)",
    "<p>A manual REBA assessment depends on the rater's judgement. <b>Identify at "
    "least three sources of error or disagreement</b> a REBA score is exposed to "
    "(e.g. which moment is scored as \"worst\", joint-angle estimation by eye, "
    "coupling/activity judgement calls, inter-rater variation). Reference the "
    "Chapter 7 risk factors. Give one advantage and one limitation of the manual "
    "method, and <b>propose one change to the scoring procedure</b> (e.g. scoring "
    "from a recorded video, a second independent rater, a standardised checklist) "
    "that would make the score more repeatable.</p>",
    4, 3, "At least three specific sources of error/disagreement + one advantage and one limitation, tied to Ch.7 + one proposed improvement.",
    "Sources of error are specific to REBA scoring, not generic; advantage/limitation are specific, not generic; proposed improvement is plausible and specific."),
  q("Conclusion and recommended controls (1 mark)",
    "<p>In a short paragraph: why does ergonomics matter in an automated "
    "manufacturing facility, and what did scoring this task teach you? Then "
    "<b>list the controls you would recommend for this task, ordered by the "
    "hierarchy of controls</b> (elimination -> substitution -> engineering -> "
    "administrative -> PPE).</p>",
    1, 3, "Conclusion + controls ordered by the hierarchy of controls.",
    "Controls are specific to the task and correctly ordered by the hierarchy."),
  UPLOAD(["Completed REBA worksheet (photo or scan)",
          "Any additional screenshots you refer to",
          "AI-use disclosure line (if you used one)"]),
 ])

# ----------------------------------------------------------------------------- virtual-caliper
write_lab("virtual-caliper", "SPC and Gauge R&R: the Virtual Caliper",
 ["This lab runs inside the Labs chapter web page (webR cells). No external site, "
  "no account, no dataset file.",
  "You run the study SOLO: you play all three operator rounds yourself, in three "
  "separate sittings, reading blind each time (do not look at your earlier "
  "numbers).",
  "AI use: not permitted for the readings or the calculations. You may use an LLM "
  "to check the written reflection only, with disclosure."],
 [DECL,
  q("Task 1 - Calibrate your eye (0 marks, required)",
    "<p>Open the <i>SPC and Gauge R&amp;R: the Virtual Caliper</i> section of the Labs chapter. Run the <b>setup cell first</b>. "
    "Then run the demo cell three times with demo = 1, 2, 3. Each time, write your "
    "reading to 0.05 mm <i>before</i> revealing the correct value.</p>"
    "<p>Report your three practice readings and the three correct values, and one "
    "sentence on where your eye was off.</p>",
    0, 2, "Three practice readings vs the three correct values."),
  q("Task 2 - The measurement run (2 marks)",
    "<p>Do <b>three rounds</b> (you are operator A, then B, then C -- three "
    "separate sittings). In each round read <b>all 10 parts, 3 trials each</b>, "
    "using draw_caliper(part, trial). Work through the parts in the randomised "
    "order the setup cell prints. Read blind: do not look at your previous round "
    "or your previous trial. That is 90 readings.</p>"
    "<p><b>Paste your complete 90-reading grid here</b> (10 parts x 3 trials for "
    "each of rounds A, B, C). You may also attach it as a file.</p>",
    2, 3, "The full 90-reading grid, laid out by round / part / trial.",
    "90 values present; genuine spread between trials and between rounds (identical rounds = not read blind); randomised order followed."),
  q("Task 3 - Range-method Gauge R&R (3 marks)",
    "<p>Type your 90 readings into the caliper-grr cell (op_A = round 1, op_B = round "
    "2, op_C = round 3) and run it.</p>"
    "<p><b>Paste every output</b>: EV (repeatability), AV (reproducibility), GRR, "
    "PV (part variation), TV (total variation), <b>%GRR</b> and <b>ndc</b>. State "
    "whether %GRR and ndc are internally consistent with EV/AV/PV.</p>",
    3, 3, "All seven outputs pasted; internal-consistency check.",
    "Values pasted from the cell; %GRR = 100*GRR/TV and ndc = floor(1.41*PV/GRR) consistent with the other figures."),
  q("Task 4 - Bias and linearity (1 mark)",
    "<p>Run the caliper-bias cell. It compares your mean reading of each part against "
    "that part's certified reference value, reports overall bias, and fits bias "
    "vs. size for linearity.</p>"
    "<p><b>Paste the output. State the overall bias in mm and whether the bias "
    "changes across the size range</b> (the linearity slope).</p>",
    1, 3, "Bias output pasted; bias in mm + linearity statement.",
    "Overall bias reported (expected around +0.03 mm); linearity slope quoted and interpreted."),
  q("Task 5 - X-bar / R chart and Cpk (3 marks)",
    "<p>Run the caliper-spc cell (a seeded 25-subgroup production dataset, 5 shafts "
    "per subgroup, against dia 25.000 +/- 0.050 mm -- the same for everyone).</p>"
    "<p><b>Attach a screenshot of the X-bar and R charts.</b> Then: (1) list every "
    "subgroup that breaks a <b>Western Electric rule</b> -- one point beyond 3 "
    "sigma; 2 of 3 beyond 2 sigma; 4 of 5 beyond 1 sigma; 8 in a row on one side "
    "-- and <b>name the rule</b> for each; (2) report Cpk and say whether the "
    "process clears the automotive Tier-1 bar of <b>1.33</b>.</p>",
    3, 4, "Chart screenshot + every rule break listed and named + Cpk vs 1.33.",
    "Beyond-3-sigma subgroups match the cell output; other WE rules applied by eye; Cpk reported and compared to 1.33; special-cause shift (subgroups ~12-16) noticed."),
  q("Task 6 - Reflection (1 mark)",
    "<p>Answer in a few sentences: (1) <b>Is your gauge acceptable?</b> Use the "
    "AIAG bands -- %GRR &lt; 10% acceptable, 10-30% marginal, &gt; 30% "
    "unacceptable; ndc &gt;= 5 required. (2) If the measurement system contributes "
    "the %GRR you found, <b>what does that do to the Cpk you computed in Task 5</b> "
    "-- is the true capability better or worse than the number? (3) <b>Would you "
    "release shafts to the customer on this gauge?</b></p>",
    1, 3, "Answers to the three questions.",
    "Acceptability judged against both %GRR and ndc bands; correctly reasons that gauge error inflates apparent spread so true Cpk differs; a clear release decision."),
  UPLOAD(["Screenshot of the X-bar / R charts (Task 5)",
          "90-reading grid as a file (optional if pasted in Task 2)",
          "AI-use disclosure line if you used an LLM to check the reflection"]),
 ])

# ----------------------------------------------------------------------------- ml-week1-ai-literacy
write_lab("ml-week1-ai-literacy", "Machine Learning Week 1: AI Literacy and Prompt Engineering",
 ["Tools: an LLM chat account (Claude.ai or ChatGPT, free tier) + Google Colab. "
  "No dataset this week.",
  "Create a text file prompts.md at the start; you add to it through the session "
  "and upload it at the end.",
  "AI use: REQUIRED -- you are assessed on directing an LLM well. You must be able "
  "to explain every line of code you submit."],
 [DECL,
  q("Exercise 1 - Bad prompt -> good prompt (3 marks)",
    "<p>Here are five real prompts that produced poor results: (1) 'explain SPC'; "
    "(2) 'what's wrong with my process'; (3) 'write code to plot data'; (4) 'is "
    "1.33 a good Cpk'; (5) 'summarize this FMEA' then paste 30 pages.</p>"
    "<p>Rewrite each using the <b>R-C-T-C-F</b> pattern (Role, Context, Task, "
    "Constraints, Format). Run the original and your rewrite and compare.</p>"
    "<p>For <b>each</b> of the five, put in the box (and in prompts.md): the "
    "original prompt; your R-C-T-C-F rewrite with each element labelled "
    "<b>R=</b>, <b>C=</b>, <b>T=</b>, <b>C=</b>, <b>F=</b>; and a <b>two-sentence "
    "reflection</b> on what changed in the output.</p>",
    3, 3, "Five rewrites, each with all five labelled elements + a two-sentence reflection.",
    "All five R-C-T-C-F elements present and meaningful for each prompt; reflection describes a real difference in output."),
  q("Exercise 2 - FMEA summarisation at three audiences (2 marks)",
    "<p>Using the CNC Cell 3 FMEA from Chapter 21 (Week 1), craft and run three "
    "prompts that summarise it for: (a) plant manager Sophie Tran -- top business "
    "risks in one paragraph; (b) a quality engineer -- top 5 risks by RPN with "
    "mitigation status; (c) a new operator -- a plain-language 'what to watch for' "
    "checklist.</p>"
    "<p>Put the three prompts, a short note on each output, and a <b>two-sentence "
    "reflection</b> on how the audience changed the prompt, in the box and in "
    "prompts.md.</p>",
    2, 3, "Three audience-specific prompts + output notes + reflection.",
    "Each prompt is genuinely tailored to its audience; outputs are audience-appropriate and technically accurate."),
  q("Exercise 3 - The hallucination hunt (3 marks)",
    "<p>Deliberately get the LLM to <b>fabricate</b> something and then <b>verify "
    "it is fabricated</b> -- e.g. a made-up ASTM standard number, made-up paper "
    "authors, or a made-up alloy designation.</p>"
    "<p>Record (in the box and prompts.md): <b>the exact prompt</b>; <b>the exact "
    "response, copy-pasted</b>; <b>how you verified it was false</b> (attach a "
    "screenshot of the empty standards search or the 'no results' scholar page -- "
    "not just 'I think this is made up'); and one sentence on how you would "
    "prevent this in your own workflow.</p>",
    3, 4, "Exact prompt + exact response + verification evidence (screenshot) + prevention sentence.",
    "A real fabrication captured verbatim; verification is documented with evidence, not asserted."),
  q("Exercise 4 - LLM-assisted Python starter code (2 marks)",
    "<p>Use the LLM to generate Python that, on a file spc_data.csv with columns "
    "timestamp, operator, part_id, diameter_mm, surface_roughness_um, "
    "cycle_time_sec, tool_age_cycles: loads the CSV and parses timestamp as "
    "datetime; plots diameter_mm over time with title and axis labels; prints the "
    "mean and standard deviation of diameter_mm; flags rows more than 3 sigma from "
    "the mean; and does not crash on missing values.</p>"
    "<p><b>Constrain the prompt:</b> pandas + matplotlib only; a comment above each "
    "logical block; runnable in Google Colab with no local paths; standard Colab "
    "libraries only.</p>"
    "<p>In the box: paste the prompt you used, and for each logical block write "
    "<b>one sentence explaining what it does</b> (the instructor will ask you to "
    "explain a line in ML Week 2). Note any change you made to the generated code. "
    "<b>Attach spc_starter.py.</b></p>",
    2, 3, "Prompt + per-block explanation + spc_starter.py attached.",
    "Code meets every requirement and runs; student's per-block explanation shows understanding; file attached."),
  UPLOAD(["prompts.md (Exercises 1-3)",
          "spc_starter.py (Exercise 4)",
          "Screenshot(s) - hallucination verification (Exercise 3)"]),
 ])

# ----------------------------------------------------------------------------- ml-week2-data-spc
write_lab("ml-week2-data-spc", "Machine Learning Week 2: Manufacturing Data and SPC",
 ["Tools: Google Colab. Files from FOL: spc_data.csv (90 days of CNC Cell 3 data "
  "with embedded problems) and week2_lab.ipynb (pre-structured). Bring "
  "spc_starter.py from ML Week 1.",
  "Never silently delete data -- every change goes in a quality log (ISO 9001 "
  "traceability).",
  "AI use: REQUIRED -- you direct an LLM to write the Python and must be able to "
  "explain every line."],
 [DECL,
  q("Task 1 - Run your Week 1 code on real data (1 mark)",
    "<p>Paste spc_starter.py into the first cell of week2_lab.ipynb and run it.</p>"
    "<p>In the box (and the first markdown cell of the notebook): <b>describe the "
    "spike</b> (approximate value), <b>whether your 3-sigma outlier detection "
    "worked</b> or flagged the wrong rows, and <b>any error or warning</b> you "
    "encountered.</p>",
    1, 2, "Spike value + did outlier detection work + any error.",
    "Spike magnitude reported; the 3-sigma detector's failure on raw data recognised."),
  q("Task 2 - Find and fix the data-quality issues (4 marks)",
    "<p>Find and correct each embedded problem. <b>Log every change</b> in a "
    "quality_log (one row per correction: row_index, column, original, corrected, "
    "reason, action). Never delete a row silently.</p>"
    "<p>Problems to find: (1) <b>two missing days</b> -- timestamp gap; document "
    "as a network outage, do <b>not</b> interpolate. (2) <b>one impossible "
    "diameter</b> (&gt; 30 mm) -- decimal-point correction. (3) <b>a block of rows "
    "with roughness in inches, not micrometres</b> -- convert (x 25400). (4) "
    "<b>one negative cycle time</b> -- flag and remove (logged). (5) <b>a real "
    "special-cause cluster around days 43-47</b> -- <b>KEEP it</b>; document that "
    "it is a genuine event.</p>"
    "<p>In the box: for <b>each</b> of the five, give the row index(es), what you "
    "found, and the quality_log row you wrote. Confirm the post-clean checks: no "
    "diameter &gt; 30 mm, no negative cycle time, quality_log populated.</p>",
    4, 4, "All five problems with row indices + quality_log rows + post-clean checks.",
    "All five identified; corrections match the intended fix; days 43-47 KEPT and labelled genuine; no silent deletion; post-clean checks confirmed."),
  q("Task 3 - Build an X-bar control chart (3 marks)",
    "<p>On the cleaned data, build an X-bar chart for diameter_mm (subgroup = 5 "
    "parts/day). <b>Control limits must use sigma / sqrt(n)</b> -- the standard "
    "deviation of individuals divided by root n -- <b>not</b> the standard "
    "deviation of the daily means. Spec limits USL = 25.050, LSL = 24.950.</p>"
    "<p>In the box: <b>which days are out of control</b>; cross-reference them with "
    "the operator and tool_age_cycles columns; and <b>compute Cpk</b> "
    "(min((USL-mu)/(3 sigma), (mu-LSL)/(3 sigma))). Expected Cpk ~ 1.1-1.2 "
    "(marginal, below 1.33). <b>Attach a screenshot of the chart.</b></p>",
    3, 4, "OOC days + operator/tool cross-ref + Cpk value + chart screenshot.",
    "Control limits use sigma/sqrt(n) (verify wording); OOC days include the 43-47 window; Cpk in ~1.1-1.2 and interpreted; chart attached."),
  q("Task 4 - Reflection (1 mark)",
    "<p>In a markdown cell (and the box), answer briefly: (1) how many parts had "
    "already been made during the days 43-47 event before the first "
    "out-of-control point appeared? (2) would a model predicting tomorrow's mean "
    "diameter from today's tool age, operator and the last 5 days of data have "
    "given earlier warning than SPC? (3) what data, not in this CSV, would you "
    "want to build a <b>predictive</b> rather than <b>reactive</b> model?</p>",
    1, 3, "Answers to the three questions."),
  q("Submit the notebook (1 mark)",
    "<p><b>Attach your completed week2_lab.ipynb</b> with all cells executed, the "
    "quality log populated, the chart generated, Cpk computed and the reflection "
    "answered.</p>",
    1, 1, "Attach week2_lab.ipynb.",
    "Notebook runs end to end; all four tasks visible and executed."),
 ])

# ----------------------------------------------------------------------------- ml-week3-cmapss
write_lab("ml-week3-cmapss", "Machine Learning Week 3: The C-MAPSS Dataset",
 ["Capstone kickoff. Tools: Google Colab. Files from FOL: train_FD001.txt (NASA "
  "C-MAPSS FD001 training set) and predictive_maintenance.ipynb (pre-structured "
  "for Weeks 3-5).",
  "You keep working in the SAME notebook in ML Weeks 4 and 5.",
  "ML Weeks 3-6 are marked together against the capstone rubric (in FOL / the "
  "instructor handbook). The points here are for tracking progress.",
  "AI use: REQUIRED -- you must be able to explain every line."],
 [DECL,
  q("Task 1 - Load and label the data (2 marks)",
    "<p>The file has no headers and is space-separated: 26 columns = unit number, "
    "time in cycles, 3 operating settings, 21 sensors, and 2 trailing empty "
    "columns to drop. Load it. Expected: <b>20631 rows, 100 engines</b>.</p>"
    "<p>Create the RUL label -- there is no RUL column, you compute it: for each "
    "engine the max cycle is the failure cycle; RUL at any row = that engine's "
    "failure cycle minus the current cycle.</p>"
    "<p>In the box: paste your row count and engine count, paste the "
    "groupby/map code you used for RUL, and confirm the RUL of the last row of "
    "engine 1 is 0.</p>",
    2, 3, "Row/engine counts + RUL code + RUL-at-failure check.",
    "20631 rows / 100 engines; RUL computed per engine (not globally); last row of each engine has RUL 0."),
  q("Task 2 - Visualise one engine's life (2 marks)",
    "<p>Plot all 21 sensors for <b>engine #1</b> over its whole life (a 7x3 grid).</p>"
    "<p>Classify each sensor as: <b>flat</b> (never changes -- useless), <b>noise</b> "
    "(varies without trend), or <b>trend</b> (drifts systematically toward failure "
    "-- useful). Write the three lists in the box (and a markdown cell). <b>Attach "
    "the 7x3 plot.</b></p>",
    2, 3, "Three sensor lists (flat / noise / trend) + the plot attached.",
    "Grid shows all 21 sensors; classification is defensible from the plot; trend list includes sensors 2,3,4,7,11,12,15,17,20,21-ish."),
  q("Task 3 - Identify constant sensors (2 marks)",
    "<p>Compute each sensor's standard deviation across the whole dataset. Sensors "
    "with <b>std &lt; 0.001</b> are effectively constant and carry no information. "
    "Expected: about 6 constant sensors in FD001 (sensor_1, 5, 10, 16, 18, 19).</p>"
    "<p>Paste your list of constant sensors and their std values.</p>",
    2, 3, "List of constant sensors + std values.",
    "About 6 sensors flagged; list matches sensor_1,5,10,16,18,19 (allowing minor variation)."),
  q("Task 4 - Correlation with RUL (2 marks)",
    "<p>For the <b>non-constant</b> sensors, compute the Pearson correlation "
    "between each sensor and RUL. <b>|r| &gt; 0.5</b> marks the most predictive raw "
    "features.</p>"
    "<p>Paste the correlations, sorted, and name your top features. Expected top "
    "sensors: sensor_11 (r ~ -0.71), sensor_4 (~ -0.69), sensor_12 (~ +0.67), "
    "sensor_7 (~ +0.66).</p>",
    2, 3, "Sorted correlations + named top features.",
    "Correlations computed only on non-constant sensors; top-4 roughly match the expected set and signs."),
  q("Task 5 - Reflection (2 marks)",
    "<p>In a markdown cell (and the box): (1) if you plot RUL for all 20631 rows "
    "in order, <b>what shape appears and why</b> -- and what does that shape say "
    "about the danger of splitting rows randomly between train and validation? "
    "(2) which <b>3 sensors</b> would you most want in a model, citing evidence "
    "from Task 2 or Task 4? (3) what would you do <b>before</b> dropping the 6 "
    "dead sensors in a real plant?</p>",
    2, 3, "Answers to the three questions.",
    "The 'sawtooth' shape identified and linked to why row-wise splitting leaks; 3 sensors justified with evidence; a sensible pre-drop investigation."),
  UPLOAD(["predictive_maintenance.ipynb (all four code tasks executed)",
          "7x3 sensor plot for engine #1 (Task 2)"]),
 ])

# ----------------------------------------------------------------------------- ml-week4-model
write_lab("ml-week4-model", "Machine Learning Week 4: Building the Predictive-Maintenance Model",
 ["Capstone build. Continue in the SAME predictive_maintenance.ipynb from ML Week 3. "
  "Tools: Google Colab (pandas, numpy, scikit-learn, matplotlib, joblib).",
  "Marked against the capstone rubric (FOL / instructor handbook). Points here "
  "track progress.",
  "AI use: REQUIRED -- you must be able to explain every line. The single biggest "
  "scoring risk is using train_test_split instead of a manual engine-wise split."],
 [DECL,
  q("Task 1 - Rolling-window features (2 marks)",
    "<p>For each useful sensor, compute a <b>rolling mean</b> and <b>rolling "
    "standard deviation</b> over a <b>5-cycle window</b>, <b>grouped by engine</b> "
    "so the window resets at each engine boundary.</p>"
    "<p><b>Verify the boundary:</b> engine #2's first-cycle rolling mean must "
    "equal its raw value and must not include any of engine #1's data. Paste the "
    "code and the check result.</p>",
    2, 3, "Rolling-feature code + boundary verification.",
    "groupby(engine).rolling (or transform) used; boundary check shown and passes."),
  q("Task 2 - Clip RUL at 125 (1 mark)",
    "<p>Create RUL_clipped = RUL.clip(upper=125) -- anything above 125 cycles is "
    "'basically healthy'. Plot the before/after histogram.</p>"
    "<p>Explain in one sentence <b>why</b> clipping helps the model. <b>Attach the "
    "histogram.</b></p>",
    1, 2, "Clipping done + before/after histogram + one-sentence why.",
    "Clip applied; histogram shows the pile-up at 125; rationale (model shouldn't waste capacity distinguishing 200 vs 300)."),
  q("Task 3 - Engine-wise train/validation split (2 marks)",
    "<p>Hold out <b>20 engines</b> for validation. <b>Do NOT split rows "
    "randomly.</b> End with an assert that must pass before you train:</p>"
    "<p><code>overlap = set(train_data['unit_number']) &amp; "
    "set(val_data['unit_number']); assert len(overlap) == 0</code></p>"
    "<p>Build X_train / y_train / X_val / y_val, excluding non-feature columns "
    "(unit_number, time_in_cycles, RUL, RUL_clipped, the constant sensors, and the "
    "mostly-constant op_setting_* columns).</p>"
    "<p>Paste the split code, the assert, confirmation it passed, and your final "
    "feature-column list.</p>",
    2, 4, "Split code + passing assert + excluded-columns list + feature list.",
    "Split is by engine id, not by row; assert present and passes; leakage columns excluded."),
  q("Task 4 - Train the Random Forest (1 mark)",
    "<p>Train RandomForestRegressor(n_estimators=100, max_depth=10, n_jobs=-1, "
    "random_state=42) on X_train / y_train (RUL_clipped as the target). Training "
    "takes 30-90 s in Colab.</p>"
    "<p>Confirm it fitted and paste the model parameters you used.</p>",
    1, 2, "Model params + confirmation it trained.",
    "Exact params; random_state set; trained on the clipped target."),
  q("Task 5 - Evaluate against the naive baseline (2 marks)",
    "<p>Compute validation <b>RMSE</b> and <b>MAE</b>. Compare with a naive "
    "baseline that predicts y_train.mean() for every row.</p>"
    "<p><b>Target: RMSE ~ 20-25 cycles, at least 2x better than naive.</b> If RMSE "
    "is suspiciously low (&lt; 10 cycles) you almost certainly have a data leak -- "
    "go back to Task 3.</p>"
    "<p>Paste your RMSE, MAE and the naive RMSE. Produce a predicted-vs-actual "
    "scatter plot and <b>describe the pattern</b> (are predictions pulled toward "
    "the centre? more error at high or low RUL?). <b>Attach the scatter plot.</b></p>",
    2, 4, "RMSE/MAE + naive RMSE + scatter plot + pattern description.",
    "RMSE ~20-25 and >=2x better than naive (RMSE<10 => leak, must be diagnosed); scatter described (compression toward the mean, more error at high RUL)."),
  q("Task 6 - Feature importance (1 mark)",
    "<p>Plot the <b>top 15 features</b> by mean-decrease-in-impurity. In a "
    "markdown cell compare with your Week 3 correlation analysis: are the top "
    "features raw or rolling? do they match the top-correlation sensors? what "
    "might explain a feature you expected but do not see? <b>Attach the "
    "chart.</b></p>",
    1, 3, "Top-15 chart + comparison to Week 3 correlations.",
    "Chart attached; comparison is specific (names features), not generic."),
  q("Task 7 - Save the model (1 mark)",
    "<p>Save <b>both</b> files -- the app needs the feature names and order:</p>"
    "<p><code>joblib.dump(model, 'rul_model.pkl'); joblib.dump(feature_cols, "
    "'feature_cols.pkl')</code></p>"
    "<p>Download both from the Colab file browser. <b>Attach rul_model.pkl and "
    "feature_cols.pkl</b> to this question (you need them for ML Week 5).</p>",
    1, 1, "Attach both .pkl files.",
    "Both files attached; feature_cols is the exact training feature list in order."),
 ])

# ----------------------------------------------------------------------------- ml-week5-deploy
write_lab("ml-week5-deploy", "Machine Learning Week 5: Deploying the App",
 ["Tools: GitHub (public repo 'rul-predictor') + Streamlit Community Cloud + "
  "Google Colab. Create the accounts as PREP, not in the lab.",
  "Files from FOL: streamlit_app.py starter (with TODO markers). Bring "
  "rul_model.pkl and feature_cols.pkl from ML Week 4.",
  "If the take-home Robotic Work-Cell Design lab is assigned, it is released this week -- read its brief.",
  "AI use: REQUIRED -- you must be able to explain every line."],
 [DECL,
  q("Task 1 - Run the Streamlit app locally (3 marks)",
    "<p>The streamlit_app.py template already has: page config, cached model "
    "loading, single-engine rolling features, CSV upload, colour-coded RUL "
    "display (red &lt; 30, orange &lt; 60, green &gt;= 60 cycles), a sensor-trend "
    "plot, and an 'About this model' expander.</p>"
    "<p>Complete the <b>TODOs</b>: add your name and course to the caption; build "
    "<b>sample_engine.csv</b> (last 30 cycles of engine #1) and wire up the "
    "'Use sample data' button; fill in the 'About this model' expander (your name, "
    "your <b>actual ML Week 4 RMSE</b>, one Precitech-specific limitation).</p>"
    "<p>Run it (streamlit run streamlit_app.py, or Colab + pyngrok). Test a CSV "
    "upload. <b>Describe each TODO you completed</b> and <b>attach a screenshot of "
    "the running app showing a prediction.</b></p>",
    3, 3, "Each TODO described + screenshot of local app with a prediction.",
    "All TODOs done; the ML Week 4 RMSE is the student's real number; sample button works; screenshot shows a colour-coded RUL."),
  q("Task 2 - Push to GitHub (2 marks)",
    "<p>Put these in the <b>public</b> repo rul-predictor: streamlit_app.py, "
    "rul_model.pkl, feature_cols.pkl, requirements.txt, sample_engine.csv.</p>"
    "<p>Use tested <b>pinned versions</b> in requirements.txt (streamlit==1.39.0, "
    "scikit-learn==1.5.2, pandas==2.2.3, numpy==1.26.4, matplotlib==3.9.2, "
    "joblib==1.4.2).</p>"
    "<p>Paste your <b>repo URL</b> and the list of files it contains, and the "
    "contents of your requirements.txt.</p>",
    2, 2, "Repo URL + file list + requirements.txt contents.",
    "Repo is public and has all five files; requirements pinned."),
  q("Task 3 - Deploy to Streamlit Community Cloud (3 marks)",
    "<p>At share.streamlit.io -&gt; New app -&gt; select your repo -&gt; main file "
    "streamlit_app.py -&gt; Deploy. Deployment takes 2-3 min.</p>"
    "<p>Common failures: rul_model.pkl &gt; 50 MB (retrain with n_estimators=50); "
    "version conflict in requirements.txt.</p>"
    "<p>Paste your <b>public app URL</b>. Describe <b>step by step what you did</b>, "
    "and <b>any failure you hit and how you fixed it</b>.</p>",
    3, 3, "Public URL + deploy steps + any failure and its fix.",
    "URL loads and predicts; deploy narrative is specific; failures (if any) diagnosed and resolved."),
  q("Task 4 - Polish the app (1 mark)",
    "<p>Make sure the app has: a plain-language title and description a plant "
    "manager would understand; a working sample-data button; a complete 'About "
    "this model' expander (training data = NASA C-MAPSS FD001 simulation; model = "
    "RF 100 trees / max depth 10; your validation RMSE; an explicit statement of "
    "what the model is <b>not</b> for); and graceful handling of a wrong-column "
    "CSV.</p>"
    "<p>Describe what you changed and paste your final 'About this model' text.</p>",
    1, 2, "Polish changes + final About text.",
    "Title/description are non-jargon; About expander complete incl. >=1 'not for' statement; wrong-column CSV handled without a raw traceback."),
  q("Task 5 - Test with another student (1 mark)",
    "<p>Swap URLs with a classmate. Try a valid CSV, an invalid CSV "
    "(wrong/extra columns, missing values), and edge cases (1-row, 1000-row).</p>"
    "<p>Record <b>one bug you found in their app</b> and <b>one they found in "
    "yours</b> (you do not need to fix it before submitting). Name the student "
    "whose app you tested.</p>",
    1, 2, "One bug in theirs + one in yours + the student's name.",
    "Concrete, reproducible bugs described (input -> wrong behaviour)."),
  UPLOAD(["Public Streamlit app URL (paste in Task 3 and here)",
          "Public GitHub repo URL",
          "Screenshot of the deployed app showing a prediction",
          "sample_engine.csv"]),
 ])

# ----------------------------------------------------------------------------- ml-week6-capstone
write_lab("ml-week6-capstone", "Machine Learning Week 6: Capstone Presentation",
 ["You demo your deployed predictive-maintenance app LIVE to the class (8-10 min) "
  "and take 3-5 min of questions. No slides required -- the app is the "
  "presentation.",
  "Your app URL and GitHub repo (submitted in ML Week 5) must be live at "
  "presentation time.",
  "This quiz records the session; it carries the ML Weeks 3-6 capstone rubric "
  "(held in FOL / the instructor handbook).",
  "AI use: allowed across the module, but the presentation and defence are your "
  "own."],
 [q("Start-of-session declaration",
    "<p>Type: your full name and student number; your <b>live app URL</b>; your "
    "<b>GitHub repo URL</b>; and confirmation that both load right now and the "
    "sample CSV produces a sensible prediction.</p>",
    0, 1, "Name, student number, live app URL, repo URL, both confirmed working."),
  q("Demo checklist (3 marks)",
    "<p>During your live demo you must: (1) open your app from the public URL and "
    "show it loads; (2) upload the sample CSV, show a prediction, and explain the "
    "colour coding and how a maintenance planner would act on it; (3) explain one "
    "key technical decision; (4) state one limitation honestly.</p>"
    "<p>In the box, <b>describe what you actually showed for each of the four "
    "points</b> and roughly how long you spent.</p>",
    3, 3, "A description of each of the four demo elements as delivered.",
    "All four elements delivered live; the planner-action explanation is concrete (what does red mean operationally)."),
  q("Technical decision defended (3 marks)",
    "<p>Write out, in full, the <b>one technical decision</b> you explained and "
    "defended: engine-wise vs. row-wise split (and the RMSE you would have got the "
    "wrong way); why RUL was clipped at 125; the rolling-window size; or what the "
    "feature-importance chart shows.</p>"
    "<p>Include the evidence you used and how you answered the follow-up "
    "question(s).</p>",
    3, 4, "The decision, the reasoning, the supporting numbers, and the follow-up handling.",
    "Decision explained correctly with numbers (e.g. row-wise leak gives RMSE 5-8 vs ~21 engine-wise); defence is sound."),
  q("One honest limitation (2 marks)",
    "<p>State <b>one specific limitation</b> of your model -- e.g. 'trained on a "
    "simulation of one fault mode in one operating condition; deploying on a real "
    "engine would need retraining on actual failure data and validation against "
    "known events'. Not a generic 'it could be more accurate'.</p>",
    2, 3, "One specific, technically grounded limitation.",
    "Limitation is concrete and correct (data domain, fault-mode coverage, calibration, drift, etc.)."),
  q("Question-and-answer notes (2 marks)",
    "<p>Record <b>2-3 questions</b> you were asked by the class or instructor and "
    "your answers. Examples you should be ready for: what does RMSE 22 cycles mean "
    "operationally? walk through exactly what happens when a user uploads a CSV? "
    "why can't Random Forest feature importance tell the maintenance team which "
    "physical sensor to buy? name three things needed before recommending this for "
    "the real CNC cells. ('I don't know, but I would check ...' is a professional "
    "answer; guessing is not.)</p>",
    2, 3, "2-3 questions and your answers.",
    "Answers are accurate or honestly bounded; no bluffing."),
 ])

# ----------------------------------------------------------------------------- tpm-oee-rca
write_lab("tpm-oee-rca", "TPM/OEE, Root Cause and a New Dataset",
 ["Tools: Google Sheets, draw.io, Google Colab. Files: precitech_shift_log.csv "
  "from FOL; AI4I 2020 Predictive Maintenance Dataset CSV from UCI "
  "(archive.ics.uci.edu, CC BY 4.0).",
  "This is CLASSIFICATION on a differently-shaped dataset -- the C-MAPSS capstone "
  "code does not carry over; transfer the workflow, not the code.",
  "AI use: REQUIRED for the classifier task; permitted with disclosure elsewhere. "
  "You must be able to explain every line."],
 [DECL,
  q("Task 1 - OEE and the Six Big Losses (2 marks)",
    "<p>From precitech_shift_log.csv, compute <b>availability</b> (run time / "
    "planned production time), <b>performance</b> (ideal cycle time x total count "
    "/ run time) and <b>quality</b> (good count / total count), then <b>OEE = the "
    "product</b>. Show the three factors separately.</p>"
    "<p>Take <b>each</b> downtime and loss entry in the log and assign it to one "
    "of the <b>Six Big Losses</b> (breakdowns; setup &amp; adjustment; small "
    "stops; reduced speed; startup rejects; production rejects). <b>State which "
    "Big Loss is costing the most OEE points.</b></p>"
    "<p>Attach your Sheets file. Paste the three factors, OEE, and the "
    "loss-attribution table.</p>",
    2, 3, "Availability/performance/quality shown separately + OEE + every log entry attributed + biggest loss named.",
    "All three factors correct; every log entry mapped to one Big Loss; largest loss identified with numbers."),
  q("Task 2 - Pareto the failure modes (1 mark)",
    "<p>In the AI4I data, count how many rows carry each of <b>TWF</b> (tool "
    "wear), <b>HDF</b> (heat dissipation), <b>PWF</b> (power), <b>OSF</b> "
    "(overstrain) and <b>RNF</b> (random). Build a <b>Pareto chart</b> in Sheets "
    "(bars descending, cumulative line).</p>"
    "<p><b>Identify the vital few</b> failure modes that account for most of the "
    "failures, and note <b>where RNF sits and why that matters</b> (it is random -- "
    "not addressable by root-cause action). Attach the chart.</p>",
    1, 3, "Counts + Pareto chart + vital few + RNF discussion.",
    "Descending bars + cumulative line; vital few named; RNF correctly treated as irreducible noise."),
  q("Task 3 - 5-Why and Ishikawa (2 marks)",
    "<p>Take the <b>top failure mode</b> from Task 2. Run a <b>5-Why</b> chain. "
    "Draw an <b>Ishikawa</b> diagram in draw.io with the six standard bones "
    "(machine, method, material, measurement, man, environment).</p>"
    "<p>Use the <b>measured feature columns as evidence</b> on the bones -- e.g. "
    "compare tool wear, torque, rotational speed and the air-vs-process "
    "temperature gap for the <b>failing</b> rows against the <b>healthy</b> rows, "
    "and <b>put the numbers on the diagram</b>.</p>"
    "<p>Paste the 5-Why chain. Attach the draw.io export.</p>",
    2, 4, "5-Why chain + six-bone fishbone + measured feature evidence with numbers + draw.io export.",
    "5-Why reaches a systemic cause; fishbone has all six bones; failing-vs-healthy feature comparisons with actual values on the bones."),
  q("Task 4 - Direct an LLM to build a failure classifier (4 marks)",
    "<p>In Colab, prompt an LLM to build a classifier that predicts the "
    "<b>machine-failure flag</b> from the five process features (air temp, "
    "process temp, rotational speed, torque, tool wear). You are transferring the "
    "capstone <b>workflow</b>, not its code -- this is tabular classification, not "
    "time-series RUL regression.</p>"
    "<p>Report a <b>confusion matrix</b> and <b>precision and recall for the "
    "failure class</b>. The failure rate in AI4I 2020 is about <b>3.4%</b>, so "
    "<b>accuracy is a useless metric here</b> -- a model that always predicts 'no "
    "failure' scores ~96.6% accuracy and catches nothing.</p>"
    "<p><b>State explicitly which class-imbalance trap you hit and how you "
    "detected it.</b> That is the lesson of this task. Paste your Colab notebook "
    "link, the confusion matrix, and precision/recall.</p>",
    4, 5, "Colab link + confusion matrix + precision/recall for the failure class + the imbalance trap named and how it was caught.",
    "Classifier is tabular (not reused C-MAPSS); confusion matrix + precision/recall reported; accuracy explicitly rejected; student noticed the imbalance and switched metric (or used class weights / resampling)."),
  q("Task 5 - 8D sections D4 and D5 (1 mark)",
    "<p>Write the <b>'D4 - root cause'</b> and <b>'D5 - permanent corrective "
    "action'</b> sections of an 8D report for the top failure mode.</p>"
    "<p>Tie the model's <b>feature importances</b> back to specific bones on your "
    "Task 3 fishbone, and propose a corrective action that a TPM programme could "
    "actually carry out (an autonomous-maintenance check, a setup standard, a "
    "condition limit).</p>",
    1, 3, "D4 and D5 with feature-importance-to-fishbone links + a TPM-executable action.",
    "D4 names a root cause supported by the feature evidence; D5 is concrete and something a TPM team could run."),
  UPLOAD(["Google Sheets file (OEE + Six Big Losses + Pareto chart)",
          "Ishikawa diagram (draw.io export)",
          "Colab notebook link (paste in Task 4 and here)",
          "AI-use disclosure line"]),
 ])

# ----------------------------------------------------------------------------- robodk-work-cell
write_lab("robodk-work-cell", "Robotic Work-Cell Design in RoboDK for Web (take-home)",
 ["TAKE-HOME lab: released in week 11, due at the end of week 14, done on your own "
  "computer. Individual work.",
  "Tool: RoboDK for Web (web.robodk.com/simulation) -- no install, no licence "
  "key. Plus a screen-recording tool (Windows Xbox Game Bar Win+G, macOS "
  "Shift+Cmd+5, or OBS Studio).",
  "You need your takt time from the Lean lab for 250 kits/day.",
  "AI use: permitted with disclosure. The station layout, the program and the "
  "cycle times must be your own work."],
 [q("Start-of-lab declaration",
    "<p>This is an individual take-home lab. Type: your full name and student "
    "number; the date you started; and confirmation the layout, program and cycle "
    "times are your own work. If you used an AI tool for anything, state which "
    "tool and what for.</p>",
    0, 1, "Name, student number, start date, AI-use disclosure."),
  q("Task 1 - Jog and observe (1 mark)",
    "<p>Load a 6-axis arm from the RoboDK library (any mid-size industrial arm -- "
    "<b>state which</b>). Jog it in <b>joint</b>, <b>linear</b> and <b>tool</b> "
    "coordinates.</p>"
    "<p>Drive it toward a <b>wrist singularity</b> and toward a <b>joint limit</b> "
    "and <b>record what the simulator does in each case</b>. Relate this to the "
    "block-programming work in the Logic Thinking (Rocksi) lab and to the Chapter 8 coordinate systems.</p>",
    1, 3, "Arm named + jog in all three frames + singularity and joint-limit behaviour recorded.",
    "Distinguishes the three jog frames; describes the specific simulator behaviour at a singularity and at a joint limit."),
  q("Task 2 - Build the kitting cell (2 marks)",
    "<p>Assemble the Precitech kitting cell around the robot: an infeed conveyor "
    "delivering shaft blanks, a bearing-press station, and a tray to be filled. "
    "Place a pick point and every place point.</p>"
    "<p><b>Check that every pick and place point is inside the reach envelope.</b> "
    "<b>Record the one reach limit that forces you to move a station</b>, and show "
    "the before/after positions. Attach screenshots of the cell and of the reach "
    "check.</p>",
    2, 3, "Cell built + all points reach-checked + the binding reach limit + before/after + screenshots.",
    "Every pick/place point verified in-envelope; one concrete reach constraint identified and resolved with a station move."),
  q("Task 3 - Program the pick-and-place (3 marks)",
    "<p>Create targets and a program that picks a blank from the conveyor, moves "
    "it to the press, then places the finished part in the tray, with gripper "
    "open/close on a <b>digital output</b>. Run it.</p>"
    "<p><b>Record the simulated cycle time for one part.</b> Describe the target "
    "list and the program structure. Attach a screenshot or short clip of the "
    "program running.</p>",
    3, 4, "Working program + gripper on DO + simulated cycle time + target/program description + screenshot/clip.",
    "Program runs end to end in the simulator; gripper actuated via I/O; a real cycle-time number reported."),
  q("Task 4 - Cycle time vs takt (3 marks)",
    "<p>Take the <b>takt time from the Lean lab</b> for 250 kits/day. <b>Does one robot "
    "at your Task 3 cycle time meet takt?</b></p>"
    "<p>Then <b>optimise</b> -- reorder targets, raise joint speeds within limits, "
    "shorten approach and retract moves -- and record the <b>improved cycle "
    "time</b>. State <b>by how much you beat or missed takt</b>, and what a real "
    "cell would do if one robot could not keep up (parallel cells, a second arm, "
    "faster EOAT, etc.).</p>",
    3, 4, "Lean-lab takt stated + meet/miss before optimisation + optimised cycle time + gap quantified + real-cell mitigation.",
    "Uses the student's Lean-lab takt; before/after cycle times; optimisation changes are physically plausible (no joint speeds past limits); gap quantified."),
  q("Task 5 - Safeguarding distance (1 mark)",
    "<p>Using the Chapter 6 minimum-distance / safeguarding-distance formula, "
    "<b>compute the minimum guarding distance</b> from an assumed robot-plus-sensor "
    "stopping time (<b>state your assumption</b>).</p>"
    "<p>State <b>which Chapter 6 safeguard you would specify</b> for this cell "
    "(fixed guard, interlocked gate, light curtain, area scanner, two-hand "
    "control) and <b>why</b>.</p>",
    1, 3, "Minimum distance computed with a stated stopping time + a specific safeguard chosen and justified.",
    "Formula applied correctly with stated assumptions; safeguard choice suits a pick-and-place cell and is justified."),
  UPLOAD(["Report (PDF) covering all five tasks with the reach-envelope evidence, "
          "the cycle-time vs takt comparison and the safeguarding calculation",
          "RoboDK station file (.rdk)",
          "Screen recording (3-5 min) showing the program running and you "
          "talking through one design decision",
          "AI-use disclosure line"]),
 ])



# =============================================================================
# Hands-on labs: metrology, statistical quality control, materials testing and
# virtual welding.  Source handouts / worksheets: LabInstructions/Quality_Labs,
# Materials_Labs and Virtural_Welding.  Corrected worksheet copies are in
# LabInstructions/Quality_Labs/fixed/.  Each quiz totals 10 marks.
# =============================================================================

def HANDS_DECL(kind="bench"):
    if kind == "swap":
        who = ("(2) the name and student number of your <b>swap partner</b> and the "
               "<b>serial numbers of both calipers</b>; ")
        rule = ("This is an <b>individual</b> lab: you take your own readings, with your own caliper "
                "and then your partner's. You and your partner exchange readings only after you have "
                "both finished; the calculations, graphs and written answers must be your own.")
    elif kind == "team":
        who = ("(2) the names and student numbers of the <b>other members of your "
               "team</b>, and the station / instrument you worked at; ")
        rule = ("This lab is done in a team, but <b>the write-up is individual</b>: "
                "your answers, calculations and graphs must be your own.")
    else:
        who = ("(2) the name of any <b>partner</b> you worked with (or 'none'), and "
               "the bench / instrument you worked at; ")
        rule = ("If you shared measurements with a partner, the calculations, graphs "
                "and written answers must still be your own.")
    return q(
        "Start-of-lab declaration",
        "<p><b>Read before you begin.</b> Work through the questions below <b>in "
        "order</b> during the lab period; each one tells you what to measure or "
        "calculate and asks you to record it and describe what you did. " + rule +
        "</p><p>In the box, type: (1) your full name and student number; " + who +
        "(3) confirmation that you have read the safety notes for this lab and that "
        "the write-up is your own work.</p>",
        0, 1, "Name, student number, partner/team, bench, and your confirmation.")

def SIM_DECL():
    return q(
        "Start-of-lab declaration",
        "<p><b>Read before you begin.</b> This is an individual lab on the Lincoln "
        "VRTEX 360+ virtual welding simulator. Work through the questions in "
        "order. In the box, type: (1) your full name and student number; (2) the "
        "<b>simulator ID / unit number</b> you used; (3) the <b>username</b> you "
        "logged in with (student ID + family name + first letter of given name, "
        "except in the first lab); (4) confirmation that the scores you report are "
        "your own and come from the simulator.</p>",
        0, 1, "Name, student number, simulator ID, username, confirmation.")

REPORT = UPLOAD

# ----------------------------------------------------------------------------- instruments
write_lab("instruments", "Linear and Angular Measuring Instruments",
 ["Bench lab in the metrology lab. Corrected assignment sheet: "
  "LabInstructions/Quality_Labs/fixed/Linear and Angular Measurements - fixed.docx.",
  "Answers to the two least-count problems: caliper 0.1 mm; micrometer 0.02 mm "
  "without the vernier and 0.004 mm with it.",
  "AI use: not permitted for the least-count calculations. Any AI used for "
  "background research must be disclosed."],
 [HANDS_DECL(),
  q("Task 1 - Vernier caliper (3 marks)",
    "<p>Attach a photo of the <b>vernier caliper</b> you are using. Then: "
    "(a) name the types of caliper you know of; (b) <b>label its main parts</b> "
    "(jaws, beam, main scale, vernier scale, depth rod, lock screw...); (c) state "
    "the <b>unit of each scale</b>; (d) write, step by step, <b>how to read it</b>; "
    "(e) give the <b>formula for its least count</b>.</p>"
    "<p><b>Problem:</b> on a vernier caliper each division of the main scale is "
    "1 mm and ten divisions of the vernier scale coincide with nine divisions of "
    "the main scale. Determine the least count. Show your working.</p>",
    3, 3, "Parts, units, reading procedure, least-count formula, and the worked problem.",
    "Least count = 1 mm - 0.9 mm = 0.1 mm (= value of one main-scale division / number of vernier divisions). Parts and units correct."),
  q("Task 2 - Vernier height gauge (2 marks)",
    "<p>Attach a photo of the <b>vernier height gauge</b>. Name the types that "
    "exist, <b>label its main parts</b> (base, beam, vernier slide, scriber...), "
    "state the <b>unit(s) of its scale(s)</b>, describe <b>how to read it</b> and "
    "give the <b>formula for its least count</b>.</p>",
    2, 3, "Types, labelled parts, units, reading procedure, least-count formula.",
    "Same least-count formula as the caliper; describes zeroing on the surface plate."),
  q("Task 3 - Vernier micrometer (3 marks)",
    "<p>Attach a photo of the <b>micrometer</b>. <b>Label its main parts</b> "
    "(frame, anvil, spindle, sleeve/barrel, thimble, ratchet, lock), state the "
    "<b>unit of each scale</b>, describe <b>how to read it</b> and give the "
    "<b>formula for its least count</b>.</p>"
    "<p><b>Problem:</b> the barrel scale of a vernier micrometer has graduations of "
    "1 mm. The thimble has 50 equal divisions, and one complete rotation of the "
    "thimble moves it 1 mm along the barrel. The vernier scale on the barrel has "
    "five divisions that correspond to six thimble divisions. Calculate the least "
    "count (a) without the vernier scale and (b) with it. Show your working.</p>",
    3, 4, "Parts, units, reading procedure, formula, and both least counts.",
    "(a) 1 mm / 50 = 0.02 mm. (b) 0.02 mm / 5 = 0.004 mm (five vernier divisions = six thimble divisions, so one vernier division is 1.2 thimble divisions)."),
  q("Task 4 - Gauge blocks (2 marks)",
    "<p>Slip gauges (gauge blocks) come in <b>rectangular, square and square-with-"
    "hole</b> shapes and in <b>grades</b>. (a) <b>What does the grade number refer "
    "to, and what is each grade typically used for?</b> (b) <b>Illustrate</b> (photo "
    "or sketch) the set you used. (c) <b>How is wringing achieved?</b> Illustrate "
    "with an example of building a stack of a given size.</p>",
    2, 3, "Grade meaning and uses; illustration of the set; wringing explained with an example.",
    "Grade = guaranteed accuracy (calibration / reference / inspection / workshop); wringing = clean, flat, thin oil film/molecular adhesion, slide-and-twist; stack example correct."),
  REPORT(["Photos of the caliper, height gauge, micrometer and gauge-block set",
          "Completed assignment sheet (.docx or PDF)"]),
 ])

# ----------------------------------------------------------------------------- v-groove
write_lab("v-groove", "Groove Angle Measurement (V-Block)",
 ["Bench lab in the metrology lab. Uses a V-block, two rollers of different "
  "diameters, a surface plate, a vernier height gauge and a vernier caliper.",
  "Answer key: groove angle = 2 x asin[ (d2 - d1) / ( 2(h2 - h1) - (d2 - d1) ) ], "
  "with d = roller diameter and h = height from the plate to the top of the roller.",
  "AI use: not permitted -- the measurements and calculations must be your own."],
 [HANDS_DECL(),
  q("Task 1 - Roller diameters (1 mark)",
    "<p>Measure the diameter of each roller with the vernier caliper, <b>at the "
    "middle of the roller</b>. Record <b>d1</b> (smaller) and <b>d2</b> (larger) "
    "for each of your four samples in a table, and state the caliper's resolution.</p>",
    1, 2, "Table of d1, d2 for each sample; caliper resolution stated."),
  q("Task 2 - Roller heights (2 marks)",
    "<p>Describe how you <b>set the height gauge to zero on the surface plate</b>. "
    "Then place the smaller roller in the groove, measure <b>h1</b> (plate to the "
    "top of the roller), swap to the larger roller and measure <b>h2</b>. Record "
    "h1 and h2 for every sample.</p><p>State the <b>precautions</b> you took so that "
    "the roller did not move and the scriber only just touched it.</p>",
    2, 3, "Zeroing method; table of h1, h2; the precautions taken.",
    "Zeroed on the plate; scriber just touching; roller not disturbed; readings to the gauge's resolution."),
  q("Task 3 - Calculate the groove angle (3 marks)",
    "<p>Write the equation from your sheet and <b>show one complete worked "
    "calculation</b> (all numbers substituted). Then give the <b>calculated groove "
    "angle for each of the four samples</b> in a table.</p>",
    3, 4, "Equation, one full worked calculation, table of four angles.",
    "angle = 2 asin[(d2-d1)/(2(h2-h1)-(d2-d1))]; units consistent; values plausible for a standard V-block (e.g. about 90 deg)."),
  q("Task 4 - Repeatability (2 marks)",
    "<p>Calculate the <b>mean and the range</b> of your four angles. Do your "
    "repeats agree? Suggest the <b>two largest sources of error</b> in this method "
    "and how each would show up in the results.</p>",
    2, 3, "Mean, range, and two sources of error explained.",
    "Mean and range correct; sources such as roller moved, scriber pressed on the roller, height gauge not zeroed, diameter not measured at mid-length."),
  q("Task 5 - Why two rollers? (2 marks)",
    "<p>Why does the method need <b>two rollers of different diameters</b> rather "
    "than one? What would go wrong if a roller were so large it touched the top "
    "corners of the block instead of only the sloping sides?</p>",
    2, 3, "Your explanation.",
    "Two unknowns (angle and apex height) need two equations; roller must touch only the sloping sides or the geometry no longer holds."),
  REPORT(["Table of diameters, heights and angles (.xlsx or PDF)",
          "Photo of your set-up"]),
 ])

# ----------------------------------------------------------------------------- sine-bar
write_lab("sine-bar", "Taper Angle Measurement with a Sine Bar",
 ["Bench lab in the metrology lab. Uses a surface plate, sine bar, dial "
  "indicator on a stand, gauge blocks and three tapers.",
  "The sheet takes theta as the taper's HALF-angle: sin(theta) = h / L; whole angle "
  "= 2 theta. Post the sine-bar length L.",
  "AI use: not permitted -- the measurements and calculations must be your own."],
 [HANDS_DECL(),
  q("Task 1 - The sine principle (2 marks)",
    "<p>Explain in your own words <b>how a sine bar turns an angle into a length "
    "measurement</b>: name the right triangle, which side is the bar and which is "
    "the gauge-block stack, and write sin(theta) = h / L. List the "
    "<b>requirements</b> for an accurate sine bar (roller diameters, spacing, "
    "roller axes, top surface).</p>",
    2, 3, "Triangle described, formula written, four requirements listed.",
    "Bar = hypotenuse L; stack = opposite side h; requirements: equal roller diameters, precisely known centre distance, parallel roller axes, flat top parallel to the roller axes."),
  q("Task 2 - Building the stack (2 marks)",
    "<p>Describe how you <b>wrung the gauge blocks</b> and how you decided which "
    "blocks to use. Explain how you used the <b>dial indicator</b> to find out "
    "whether the taper's top surface was parallel to the plate, and how the "
    "reading told you to add or remove blocks.</p>",
    2, 3, "Wringing, stack selection, and the dial-indicator procedure.",
    "Blocks wrung clean; indicator slid along the taper; zero deviation across the length = parallel; deflection direction tells which way to adjust."),
  q("Task 3 - Measure three tapers (3 marks)",
    "<p>For each of the three tapers record in a table: the <b>gauge-block height "
    "h</b>, the <b>sine-bar length L</b>, the <b>half-angle theta = asin(h / L)</b>, "
    "the <b>whole angle 2 theta</b>, and the <b>comparison with the actual taper "
    "angle</b>. <b>Show one complete worked calculation.</b></p>",
    3, 4, "Table for three tapers + a worked calculation.",
    "h and L in the same units; theta = asin(h/L); 2 theta compared with the stated angle; differences small."),
  q("Task 4 - Error analysis (2 marks)",
    "<p>A gauge-block stack is wrong by <b>0.01 mm</b>. Using your L, calculate "
    "the resulting error in theta for the <b>steepest</b> and the <b>shallowest</b> "
    "of your tapers. Which is more sensitive, and why does the sine bar lose "
    "accuracy at large angles?</p>",
    2, 4, "Two error calculations and the explanation.",
    "d(theta) = dh / (L cos theta) (radians); error grows with theta because cos theta shrinks."),
  q("Task 5 - Conclusion (1 mark)",
    "<p>State which taper agreed best with its stated angle and give one "
    "practical reason for any disagreement.</p>",
    1, 2, "Your conclusion."),
  REPORT(["Completed sine-bar table (.xlsx or PDF)", "Photo of your set-up"]),
 ])

# ----------------------------------------------------------------------------- calibration
write_lab("calibration", "Micrometer and Caliper Calibration",
 ["Bench lab in the metrology lab. The source sheet's check sizes are INCH sizes "
  "(micrometer 0.106 ... 0.954 in; 6 in or 8 in caliper in ten steps of range/10). "
  "If your instruments are metric, substitute an equivalent sequence.",
  "The gauge-block set must carry a serial number / certificate (traceability).",
  "AI use: not permitted -- the readings and the report must be your own."],
 [HANDS_DECL(),
  q("Task 1 - Preparation (1 mark)",
    "<p>Record the <b>instrument identification</b> for the micrometer and the "
    "caliper (owner, manufacturer, model, serial number, range, resolution, "
    "published accuracy) and the <b>standard</b> used (gauge-block set serial "
    "number). Describe how you <b>cleaned, inspected and stabilised</b> the "
    "instruments and blocks, and why each step matters.</p>",
    1, 2, "Both instruments identified; standard identified; cleaning, inspection and thermal soak described.",
    "Cleaned with methyl alcohol; inspected for damage; allowed to reach ambient temperature; zero set; published accuracy stated."),
  q("Task 2 - Micrometer calibration (3 marks)",
    "<p>Set the micrometer to zero, then wring the gauge blocks to each check size "
    "and record in a table the <b>standard, the reading and the deviation</b> "
    "(reading - standard). Record the <b>accuracy over the range</b> (the largest "
    "deviation).</p>",
    3, 3, "Table of standard, reading, deviation at each size; accuracy over the range.",
    "Deviation = reading - standard at every size; accuracy over the range = largest magnitude of deviation."),
  q("Task 3 - Caliper calibration (3 marks)",
    "<p>Repeat for the caliper at <b>ten equal steps across its range</b> (range "
    "&divide; 10). Record the table and the accuracy over the range.</p>",
    3, 3, "Table for ten sizes; accuracy over the range.",
    "Ten intervals of range/10; deviations correctly signed; accuracy over the range stated."),
  q("Task 4 - Findings (2 marks)",
    "<p>Compare each instrument's accuracy with its <b>published accuracy</b>. Is "
    "it <b>within tolerance</b>? Where is the largest deviation and what might "
    "cause it? What would you <b>recommend</b> (use, adjust, repair, remove from "
    "service) and what <b>calibration interval</b> would you suggest?</p>",
    2, 3, "Pass/fail against published accuracy, cause of the largest deviation, recommendation, interval.",
    "A real in/out-of-tolerance call with the numbers; a sensible action and interval."),
  q("Task 5 - Traceability (1 mark)",
    "<p>In two or three sentences: what does it mean that the gauge blocks are a "
    "<b>traceable standard</b>, and why does that matter for a customer receiving "
    "your parts? How does this connect to bias and linearity in a measurement "
    "systems analysis?</p>",
    1, 3, "Your explanation."),
  REPORT(["Micrometer calibration report", "Caliper calibration report"]),
 ])

# ----------------------------------------------------------------------------- excel-stats
write_lab("excel-stats", "Statistics with Excel for Quality Control",
 ["Computer lab with Microsoft Excel (VAR.P, VAR.S, STDEV.P, STDEV.S needed).",
  "Answer key (processing times, n = 12): mean 6.19, median 6.2, mode 6.2, range 3.7, "
  "population variance 1.279, sample variance 1.395, population SD 1.131, sample SD 1.181. "
  "Waiting times (n = 50): mean 30.88, median 30.45, two modes (31.8 and 28.5, three each); "
  "histogram counts for the ten bins 26.8-38.19: 8, 8, 7, 6, 8, 4, 4, 2, 2, 1 (right-skewed, "
  "not a clean normal curve).",
  "AI use: not permitted -- the calculations and graphs must be your own."],
 [HANDS_DECL(),
  q("Task 1 - Function warm-up (1 mark)",
    "<p>Using the statistics worksheet, list the <b>Excel function you used</b> for "
    "each parameter (average, median, mode, population and sample variance, "
    "population and sample standard deviation, count, minimum, maximum, range). "
    "When would you use the <b>sample</b> version instead of the <b>population</b> "
    "version?</p>",
    1, 2, "Function list and the sample-vs-population rule.",
    "AVERAGE, MEDIAN, MODE, VAR.P, VAR.S, STDEV.P, STDEV.S, COUNT, MIN, MAX, MAX-MIN; sample version when the data are a sample of a larger population."),
  q("Task 2 - Processing times (3 marks)",
    "<p>For the 12 processing times of hot-rolled steel compute the <b>mean, median "
    "and mode</b> and <b>interpret the difference between them</b>; then the "
    "<b>range, both variances and both standard deviations</b> and interpret them. "
    "Paste your results.</p>",
    3, 3, "All ten statistics + interpretation.",
    "Mean 6.19, median 6.2, mode 6.2 (close together, so roughly symmetric); range 3.7; var.p 1.279, var.s 1.395; sd.p 1.131, sd.s 1.181."),
  q("Task 3 - Scatterplot (2 marks)",
    "<p>Plot the 20 observations of <b>depth of cut against tool wear</b> as a "
    "scatterplot with <b>labelled axes and a title</b>. Attach the chart and "
    "describe the relationship you see (direction, strength, any outlier).</p>",
    2, 3, "Chart attached; relationship described.",
    "Both axes labelled with units; positive relationship - tool wear increases with depth of cut."),
  q("Task 4 - Histogram (3 marks)",
    "<p>Build a frequency table for the 50 waiting times using the ten cells on the "
    "worksheet (26.8-27.93 ... 37.06-38.19) and a <b>histogram</b>. Paste the "
    "table and attach the chart.</p>",
    3, 3, "Frequency table and histogram attached.",
    "Counts 8, 8, 7, 6, 8, 4, 4, 2, 2, 1; axes labelled; bars touching."),
  q("Task 5 - Interpret the waiting times (1 mark)",
    "<p>(a) What is the <b>mean waiting time</b>? (b) Are the <b>mode and the "
    "median the same</b>? (c) Does the histogram look like a <b>normal curve</b>? "
    "Justify from the shape.</p>",
    1, 3, "Mean, mode vs median, and a shape-based normality judgement.",
    "Mean 30.88; median 30.45 with two modes (31.8 and 28.5); shape is right-skewed / not clearly normal."),
  REPORT(["Completed Excel workbook (.xlsx) with the charts"]),
 ])

# ----------------------------------------------------------------------------- variable-charts
write_lab("variable-charts", "Variable Control Charts: X-bar, R and S",
 ["Bench + computer lab. Measure the LENGTH of 100 roller bearings in ten "
  "subgroups of ten (the bearings are tapered -- do not measure diameter).",
  "Constants for n = 10: A2 = 0.308, B3 = 0.284, B4 = 1.716, D3 = 0.223, D4 = 1.777. "
  "Use the corrected worksheet: LabInstructions/Quality_Labs/fixed/Variable "
  "Control Charts - fixed.xlsx (out-of-control rules aligned with Chapter 10).",
  "AI use: not permitted -- the measurements, calculations and charts must be your own."],
 [HANDS_DECL(),
  q("Task 1 - Collect the data (2 marks)",
    "<p>State the <b>instrument</b> and its resolution, how you took the "
    "measurements, and how you formed the <b>ten subgroups of ten</b> (why is "
    "taking consecutive parts in one subgroup a rational choice?). Paste your "
    "10 x 10 table of lengths.</p>",
    2, 3, "Instrument, method, subgrouping rationale, 10 x 10 table.",
    "100 readings in ten subgroups; consistent units; rational subgrouping explained (variation within a subgroup is short-term)."),
  q("Task 2 - X-bar chart (2 marks)",
    "<p>Give the ten <b>subgroup averages</b>, the <b>grand average</b>, the "
    "<b>average range</b>, and the <b>UCL and LCL</b> from "
    "UCL/LCL = grand average +/- A2 x average range (A2 = 0.308). Show one worked "
    "calculation.</p>",
    2, 3, "Subgroup averages, grand average, R-bar, UCL, LCL, worked calculation.",
    "Limits = X-double-bar +/- 0.308 x R-bar."),
  q("Task 3 - R chart (2 marks)",
    "<p>Give the ten <b>subgroup ranges</b>, the <b>average range</b>, and "
    "<b>UCL = D4 x R-bar</b> and <b>LCL = D3 x R-bar</b> (D4 = 1.777, D3 = 0.223).</p>",
    2, 3, "Ranges, R-bar, UCL, LCL.", "UCL = 1.777 R-bar; LCL = 0.223 R-bar."),
  q("Task 4 - S chart (2 marks)",
    "<p>Give the ten <b>subgroup standard deviations</b>, the average, and "
    "<b>UCL = B4 x S-bar</b>, <b>LCL = B3 x S-bar</b> (B4 = 1.716, B3 = 0.284). "
    "Attach the X-bar, R and S charts.</p>",
    2, 3, "Standard deviations, S-bar, limits, three charts attached.",
    "UCL = 1.716 S-bar; LCL = 0.284 S-bar; charts have centre line and limits."),
  q("Task 5 - Interpret (2 marks)",
    "<p>Apply the <b>out-of-control rules</b> on the worksheet to each chart. Is "
    "the process in statistical control? Quote any rule that is violated and the "
    "subgroups involved. What would you do next, and what does the R (or S) chart "
    "tell you that the X-bar chart does not?</p>",
    2, 4, "Rules applied to each chart, in/out-of-control judgement, next action.",
    "Rules 1-4 (Western Electric) checked; a justified call; R/S chart monitors within-subgroup spread, X-bar monitors the mean."),
  REPORT(["Completed Excel workbook with the X-bar, R and S charts"]),
 ])

# ----------------------------------------------------------------------------- attribute-charts
write_lab("attribute-charts", "Attribute Control Charts: p and np",
 ["Bench + computer lab. Ten samples of 50 beads; give each student or bench a "
  "different 'defective' colour so results cannot be copied.",
  "p limits: p-bar +/- 3 sqrt(p-bar(1 - p-bar)/n); np limits: np-bar +/- 3 "
  "sqrt(np-bar(1 - p-bar)); a negative LCL is set to 0. Expected 'what next' answer "
  "for the complementary tool: a Pareto chart.",
  "AI use: not permitted for the counts, calculations and charts."],
 [HANDS_DECL(),
  q("Task 1 - Sampling (1 mark)",
    "<p>State which colour was <b>defective</b> for your sample, how you drew "
    "each sample of <b>50 beads</b>, and whether you replaced the beads between "
    "samples (and why it matters).</p>",
    1, 2, "Defective colour, sampling method, replacement decision."),
  q("Task 2 - Counts (1 mark)",
    "<p>Paste the number defective (np) in each of the <b>ten samples</b>, and the "
    "proportion defective p = np / 50 for each.</p>",
    1, 2, "Ten counts and ten proportions."),
  q("Task 3 - p chart (3 marks)",
    "<p>Calculate <b>p-bar</b>, then <b>UCL and LCL</b> from "
    "p-bar +/- 3 sqrt(p-bar(1 - p-bar) / n) with n = 50 (set a negative LCL to "
    "0). Show one worked calculation and attach the <b>p chart</b>.</p>",
    3, 3, "p-bar, UCL, LCL, worked calculation, chart attached.",
    "n = 50 (sample size), not the number of samples; LCL floored at 0."),
  q("Task 4 - np chart (2 marks)",
    "<p>Calculate <b>np-bar</b> and the limits "
    "np-bar +/- 3 sqrt(np-bar(1 - p-bar)). Attach the <b>np chart</b> and say "
    "whether the process is in control.</p>",
    2, 3, "np-bar, limits, chart attached, in-control statement.",
    "Limits consistent with the p chart (np chart limits = n x p chart limits)."),
  q("Task 5 - Questions (3 marks)",
    "<p>(1) What <b>variation</b> is the p control chart examining? (2) Is the "
    "process in <b>statistical control</b>, and what does that mean? (3) What "
    "should be done <b>next</b> to improve the process? (4) What <b>other "
    "statistical tool</b> could be used with the p chart, and why?</p>",
    3, 3, "Four answers.",
    "Proportion defective between samples; in control = only common-cause variation; next = find and remove the causes of the defectives; Pareto chart of defect types."),
  REPORT(["Completed Excel workbook with the p and np charts"]),
 ])

# ----------------------------------------------------------------------------- capability
write_lab("capability", "Process Capability: Cp, Cpk and Distributions",
 ["Bench + computer lab. Measure the length of 50 roller bearings with a "
  "micrometer. Specification on the sheet: USL = 0.5008, LSL = 0.4992 (inches).",
  "Use the corrected worksheet: LabInstructions/Quality_Labs/fixed/Process Capability - fixed.xlsx. Cp = (USL - LSL) / (6 sigma); "
  "Cpk = min[(USL - mean)/(3 sigma), (mean - LSL)/(3 sigma)]; capable if >= 1.33. "
  "Cpk is the index for an off-centre process, not for a non-normal one.",
  "AI use: not permitted -- the measurements and calculations must be your own."],
 [HANDS_DECL(),
  q("Task 1 - Data and distribution (2 marks)",
    "<p>Paste your <b>50 lengths</b>. Plot them as a bar chart and then as an "
    "XY scatter plot as instructed on the worksheet, attach the chart, and "
    "<b>describe the distribution</b> (shape, centre, spread, anything unusual).</p>",
    2, 3, "50 values, chart attached, distribution described.",
    "Shape judged from the chart (bell-shaped / skewed / two humps); centre and spread described."),
  q("Task 2 - Statistics (2 marks)",
    "<p>Calculate the <b>average of the 50 points</b>, the <b>average range</b> "
    "(of the subgroups on the sheet), and the <b>standard deviation two ways</b>: "
    "STDEV.P of all 50 points and average range / d2 (d2 = 2.326). Compare them.</p>",
    2, 3, "Mean, R-bar, sigma from STDEV.P and from R-bar/d2, and a comparison.",
    "Both estimates of sigma close if the process is stable; a large gap suggests instability between subgroups."),
  q("Task 3 - Cp (2 marks)",
    "<p>Calculate <b>Cp = (USL - LSL) / (6 x sigma)</b> with USL = 0.5008 and "
    "LSL = 0.4992. State which sigma you used. Is the process capable "
    "(Cp &gt;= 1.33)?</p>",
    2, 3, "Cp with the sigma stated and a capable / not-capable decision."),
  q("Task 4 - Cpk (2 marks)",
    "<p>Calculate <b>Cpk</b> as the smaller of (USL - mean)/(3 sigma) and "
    "(mean - LSL)/(3 sigma). Is Cpk smaller than Cp? What does the gap tell you "
    "about the centring of the process, and what would you adjust?</p>",
    2, 3, "Cpk, comparison with Cp, centring conclusion.",
    "Cpk <= Cp; a large gap means the mean is off the middle of the specification - re-centre the process."),
  q("Task 5 - Capable? And how to run a real study (2 marks)",
    "<p>State whether the process is capable and what you would do about it. From "
    "the handout <b>Preparing a Capability Study</b>, name <b>three things a "
    "quality department must do before running a real study</b>, and explain why "
    "each matters (for example: stable process, calibrated gauges, parts straight "
    "from production, sequential numbering, defectives not discarded).</p>",
    2, 3, "Decision + three preparation steps with reasons.",
    "Any three of: review history, size the sample, confirm process stable, confirm gauge calibration, quarantine and number parts, do not discard defective parts."),
  REPORT(["Completed Excel workbook (data, chart, Cp and Cpk)"]),
 ])

# ----------------------------------------------------------------------------- gauge-rr
write_lab("gauge-rr", "Repeatability and Reproducibility (Gauge R&R)",
 ["Individual lab: each student takes their own readings and writes their own report. Students work in "
  "SWAP PAIRS: each has a serial-numbered caliper, they exchange calipers for the second half, and exchange "
  "readings (only) afterwards, so each student analyses a 2 operators x 2 calipers x 10 bars x 2 trials design "
  "for the diameter and the length of ten numbered sawn steel bars.",
  "Stage the data sheet on FOL: labs/templates/Gauge_RR_Bar_Stock_Data_Sheet.xlsx "
  "(python R/gen_grr_sheet.py). Replace the placeholder tolerances on its Setup sheet with the "
  "bars' real specification. Instructor answer key (SIMULATED readings): "
  "LabInstructions/Quality_Labs/fixed/Gauge RR Bar Stock - EXAMPLE (instructor).xlsx.",
  "Constants (5.15 sigma): EV = 5.15 R-bar / 1.128; operator AV = sqrt((5.15 Xdiff_op / 1.41)^2 - EV^2/40); "
  "caliper CV = sqrt((5.15 Xdiff_cal / 1.41)^2 - EV^2/40) (each operator or caliper average is over 40 readings); "
  "PV = 5.15 Rp / 3.18; GRR = sqrt(EV^2 + AV^2 + CV^2); TV = sqrt(GRR^2 + PV^2); %GRR = 100 GRR / TV; "
  "%tol = 100 GRR / (USL - LSL); ndc = INT(1.41 PV / GRR).",
  "Example key (simulated, inches, tolerances +/-0.005 in and +/-0.020 in): diameter EV 0.0021, AV 0.0006, CV 0.0029, "
  "GRR 0.0036, PV 0.0043, TV 0.0056 in, %GRR 65 %, %tol 36 %, ndc 1, largest component the caliper; length EV 0.0059, "
  "AV 0.0050, CV 0.0025, GRR 0.0082, PV 0.0541, TV 0.0547 in, %GRR 14.9 %, %tol 20 %, ndc 9. Caliper difference from the "
  "bars +0.0008 / +0.0007 in vs gauge-block +0.0007 in. The sheet is in INCHES at 0.0005 in resolution. Student results "
  "will differ; mark the working against their own numbers.",
  "AI use: not permitted -- the measurements and calculations must be your own."],
 [HANDS_DECL("swap"),
  q("Task 1 - Check both calipers against the gauge block (2 marks)",
    "<p>With your partner, clean the jaws and the gauge block. For <b>each</b> of the two calipers (yours and "
    "your partner's): close the jaws and record the <b>zero reading</b>, then measure the gauge block <b>three "
    "times</b>. Report the <b>serial number</b> of each caliper, the block's <b>certified size</b>, the zero "
    "readings, the three block readings and their mean for each caliper, the <b>bias</b> of each (mean minus "
    "certified size), whether each is within the acceptable limit, and the <b>difference in bias</b> between "
    "the two calipers. What would you do if a caliper were outside the limit? Name one thing this single-block "
    "check does <b>not</b> tell you.</p>",
    2, 2, "Serials, zeros, block readings, means, both biases, limit judgement, bias difference, action, one limitation.",
    "Bias = mean - certified. Outside the limit: do not use it / tell the instructor / re-zero or replace. "
    "Limitation: one size only (no linearity, nothing about the bar length), and nothing about operator technique."),
  q("Task 2 - How the data set was collected (2 marks)",
    "<p>You measured all ten bars, twice, with <b>your</b> caliper (phase 1), swapped calipers with your partner, "
    "and measured all ten bars, twice, with <b>their</b> caliper (phase 2) - diameter and length each time, in your "
    "randomised order. You then copied your partner's readings into your sheet. Paste your two data tables (diameter "
    "and length, all 8 reading columns per bar, showing which columns are yours and which are your partner's) with "
    "the bar numbers. Then describe: (a) your <b>operational definition</b> of how you measured the diameter and the "
    "length; (b) how you kept your readings independent (of your own earlier readings and of your partner's); "
    "(c) why the order is randomised; (d) what you would <b>not</b> be able to tell apart if you and your partner "
    "had each used only your own caliper.</p>",
    2, 3, "Both tables with all 8 columns, bar numbers, operational definitions, independence, why randomise, why swap.",
    "80 readings per characteristic in the sheet (40 own + 40 partner's); randomisation stops order effects; "
    "(d) with each operator on their own caliper, an operator difference and a caliper difference are confounded."),
  q("Task 3 - Diameter: Gauge R&R results (2 marks)",
    "<p>From the <b>Diameter</b> sheet, report: <b>R-bar</b>, <b>EV</b>, <b>operator X-diff</b>, <b>AV</b>, "
    "<b>caliper X-diff</b>, <b>CV</b>, <b>GRR</b>, <b>Rp</b>, <b>PV</b>, <b>TV</b>, <b>%GRR</b> (of total "
    "variation), <b>%GRR of tolerance</b> and <b>ndc</b>. Then show, with a calculator, <b>one hand calculation "
    "of EV and of AV</b> that reproduces the sheet's numbers (AV = 0 if the value under the root is "
    "negative).</p>",
    2, 4, "All thirteen values plus the hand calculation of EV and AV.",
    "EV = 5.15 x R-bar / 1.128; AV = sqrt((operator Xdiff x 5.15/1.41)^2 - EV^2/40); CV likewise with the caliper Xdiff; "
    "PV = 5.15 x Rp / 3.18. Accept any values that follow from the student's own data."),
  q("Task 4 - Length: Gauge R&R results (2 marks)",
    "<p>From the <b>Length</b> sheet, report the same thirteen values and state the unit of every one.</p>",
    2, 3, "All thirteen values with units.",
    "Same formulas as the diameter; values in inches."),
  q("Task 5 - Operator or caliper? Is the gauge adequate? (2 marks)",
    "<p>(a) For the diameter and for the length, judge the measurement system using %GRR of total variation (under "
    "10 % acceptable, 10-30 % marginal, over 30 % unacceptable), %GRR of tolerance and ndc (5 or more). Do the three "
    "measures agree, and why can the <b>same</b> calipers get different verdicts for the two characteristics "
    "(compare PV and the caliper resolution)? (b) For each characteristic, which component is largest - repeatability, "
    "operator or caliper - and what one action would you take? (c) Compare the <b>caliper difference</b> you found on "
    "the bars with the <b>difference in gauge-block bias</b>: does the block explain the caliper effect? Is the "
    "operator-by-caliper interaction noticeable, and what does that mean for splitting the two effects? (d) Name one "
    "limitation of separating operator from caliper with only you and one partner, and one way to improve it.</p>",
    2, 4, "Verdicts and agreement, why they differ, largest component and action, caliper vs block, interaction, one limitation and remedy.",
    "%GRR is relative to the spread of the parts: small part variation (bar-stock diameter) makes the same gauge look worse. "
    "The block explains the caliper effect if the two differences agree (one size only). Limitation: two operators and two calipers "
    "give crude estimates (d2* for two levels); improve by pooling the class's data or using more operators and calipers."),
  REPORT(["Completed Excel workbook (setup, caliper check, diameter and length sheets, summary)"]),
 ])

# ----------------------------------------------------------------------------- hardness
write_lab("hardness", "Hardness Testing: Rockwell and Brinell",
 ["Materials-testing rotation lab (one of three; the class is split into three "
  "groups). Team lab; each student submits their own report.",
  "Safety glasses and safety footwear required. Specimens: annealed, quenched "
  "(hardened) and normalized steel; Rockwell and Brinell testers.",
  "AI use: not permitted for the readings and calculations."],
 [HANDS_DECL("team"),
  q("Task 1 - Set-up (1 mark)",
    "<p>For each specimen state the <b>steel type</b>, the <b>Rockwell scale</b> "
    "you chose, the <b>minor and major loads</b> (kg) and the <b>Brinell "
    "load</b>. Explain <b>why</b> you chose each scale for each specimen.</p>",
    1, 3, "Scale and loads for each specimen with reasons.",
    "Soft (annealed) specimen on B scale; hard (quenched) on C scale; minor load 10 kg; loads consistent with the scale."),
  q("Task 2 - Rockwell readings (2 marks)",
    "<p>Paste your Rockwell readings (all observations) and the <b>average</b> for "
    "each specimen (Table 1 of the report template).</p>",
    2, 2, "Table 1 with all readings and averages."),
  q("Task 3 - Brinell readings (2 marks)",
    "<p>Paste your Brinell results: load, <b>indentation diameter (mm)</b>, "
    "<b>Brinell number</b> and the <b>equivalent Rockwell number</b> for each "
    "reading (Table 2 of the template), with the averages.</p>",
    2, 3, "Table 2 with diameters, Brinell numbers, converted values and averages.",
    "Brinell number from the diameter chart/formula; conversion to HRB/HRC from a chart."),
  q("Task 4 - Calculations (2 marks)",
    "<p>Calculate the <b>% deviation</b> (as defined in the template) for the "
    "annealed and hardened specimens, and the <b>reproducibility</b> "
    "(maximum reading minus minimum reading) of each test for each steel. Show "
    "one worked example.</p>",
    2, 3, "% deviation and reproducibility for each specimen and test.",
    "Reproducibility = max - min; worked example shown."),
  q("Task 5 - Questions (2 marks)",
    "<p>(a) Describe the <b>annealing</b>, <b>quenching</b> and <b>normalizing</b> "
    "processes. (b) Which specimen gave the <b>greatest range of results, and "
    "why</b>? (c) Using an online source: is Rockwell C 51 harder or softer than "
    "Brinell 500? Is Rockwell B 85 harder or softer than Brinell 165? Cite your "
    "source.</p>",
    2, 3, "Three heat treatments described; range explained; two conversions with a source.",
    "Annealing: heat, slow furnace cool; quenching: rapid cool in water/oil; normalizing: heat, air cool. The annealed (soft, coarse, multi-phase) specimen scatters more. HRC 51 is about HB 500 and HRB 85 is about HB 165 (roughly equal)."),
  q("Task 6 - Conclusion (1 mark)",
    "<p>How closely do the Rockwell and Brinell results agree for the three "
    "specimens? How reproducible was each method? Give reasons.</p>",
    1, 3, "Your conclusion.",
    "Agreement stated with numbers; reproducibility compared; reasons (indenter size, scale, surface finish, operator)."),
  REPORT(["Completed hardness report (Word/PDF) from the FOL template"]),
 ])

# ----------------------------------------------------------------------------- tensile-microhardness
write_lab("tensile-microhardness", "Tensile and Microhardness Testing of Case-Hardened Steel",
 ["Materials-testing rotation lab (one of three). Team lab; each student submits "
  "their own report. Case-hardened AISI 1566 specimen; Vickers microhardness "
  "traverse from the surface in 0.5 mm steps to 3.5 mm; tensile specimens.",
  "The template defines the effective case depth at HRC 50 and the true case depth "
  "at HRC 40. Safety glasses and safety footwear required; nital etchant and "
  "alcohol must be kept off skin.",
  "AI use: not permitted for the readings, calculations and graphs."],
 [HANDS_DECL("team"),
  q("Task 1 - Metallography (2 marks)",
    "<p>Examine the <b>case</b> and the <b>core</b> under the microscope. Attach a "
    "sketch or photo of each, state the <b>magnification</b>, and explain what "
    "each sample represents and how the two structures differ.</p>",
    2, 3, "Case and core sketches with magnification and an explanation.",
    "Case: hard, fine martensitic structure from carburising and quenching; core: softer, tougher ferrite/pearlite (lower carbon); magnification stated."),
  q("Task 2 - Microhardness traverse (2 marks)",
    "<p>Take a Vickers microhardness traverse at <b>0, 0.5, 1.0 ... 3.5 mm</b> from "
    "the surface. Paste a table of <b>depth, indentation diameter, Vickers number "
    "and Rockwell number</b>.</p>",
    2, 3, "Table of eight depths with diameters, HV and HRC.",
    "Hardness falls with depth toward the core value; conversions from a chart."),
  q("Task 3 - Graphs and case depths (3 marks)",
    "<p>Attach the two graphs on the template (Vickers vs depth and Rockwell vs "
    "depth). State the <b>effective case depth (hardness falls to HRC 50)</b> and "
    "the <b>true case depth (HRC 40)</b> and show how you read them from the "
    "graph.</p>",
    3, 4, "Two graphs, effective and true case depth, reading method shown.",
    "Depths interpolated from the plotted curve at HRC 50 and HRC 40; units mm."),
  q("Task 4 - Tensile test (2 marks)",
    "<p>For each tensile specimen record the original area and gauge length, the "
    "load at yield and the maximum load, and calculate <b>stress and strain</b> "
    "(show one full calculation). Using the graph, which material was the most "
    "<b>brittle</b>, which the most <b>ductile</b> and which had the greatest "
    "<b>toughness</b> (area under the curve)?</p>",
    2, 4, "Stress and strain calculated; brittle / ductile / toughest identified from the graph.",
    "Stress = load / original area; strain = extension / original length; toughness = area under the stress-strain curve."),
  q("Task 5 - Conclusion (1 mark)",
    "<p>Briefly describe the experiment, what you learned about case hardening "
    "and tensile behaviour, and the case depths you found.</p>",
    1, 2, "Your conclusion."),
  REPORT(["Completed report (Word/PDF) from the FOL template, with graphs"]),
 ])

# ----------------------------------------------------------------------------- charpy-dbtt
write_lab("charpy-dbtt", "Charpy Impact Testing and the Ductile-to-Brittle Transition",
 ["Materials-testing rotation lab (one of three). Team lab; each student submits "
  "their own report. NEEDS DRY ICE -- the technician needs two weeks' notice to "
  "order it for the three-week rotation.",
  "Notched AISI 1018 hot-rolled and cold-rolled specimens at about -60, -40, -20, 0 C, "
  "room temperature, 60 and 100 C. Hold several minutes; break within FIVE seconds of "
  "leaving the bath. Do not handle dry ice bare-handed; keep clear of the pendulum.",
  "AI use: not permitted for the readings, calculations and graphs."],
 [HANDS_DECL("team"),
  q("Task 1 - Safety and set-up (1 mark)",
    "<p>Describe how you prepared the <b>cold bath</b> (alcohol and dry ice) and the "
    "<b>hot bath</b>, how long each specimen was held at temperature, and how you "
    "kept the transfer-to-break time under <b>five seconds</b>. List the "
    "<b>safety precautions</b> for the dry ice and the pendulum.</p>",
    1, 3, "Bath preparation, hold time, transfer procedure, safety precautions.",
    "Insulated gloves for dry ice; not sealed in a container; ventilation; everyone clear of the pendulum before release; notch faces away from the striking edge."),
  q("Task 2 - Results table (2 marks)",
    "<p>Paste the table (Table 1 of the report): for each of the seven "
    "temperatures, the <b>energy absorbed (ft-lb)</b> for the <b>hot-rolled</b> and "
    "for the <b>cold-rolled</b> steel, and the actual bath temperature.</p>",
    2, 3, "Complete two-column table for seven temperatures.",
    "Energy low at low temperature and high at high temperature; values plausible."),
  q("Task 3 - Graph (2 marks)",
    "<p>Attach a graph of <b>impact toughness against temperature</b> with both "
    "steels on the same axes, labelled axes and a legend. Compare its shape with "
    "the reference graph.</p>",
    2, 3, "Graph attached with both curves; comparison with the reference graph.",
    "S-shaped transition curve for each steel."),
  q("Task 4 - DBTT (2 marks)",
    "<p>State the <b>ductile-to-brittle transition temperature</b> for each steel "
    "and <b>how you determined it</b> from the curve. Which steel had the higher "
    "impact values, and why?</p>",
    2, 4, "DBTT for each steel, method, and the comparison.",
    "DBTT read at the mid-point of the transition (or a stated energy); cold-rolled steel typically less tough / higher DBTT than hot-rolled - reason given (grain structure, work hardening)."),
  q("Task 5 - Fracture surfaces (1 mark)",
    "<p>Attach a photo or sketch of the <b>two fracture surfaces</b> you examined "
    "and describe each (fine granular / crystalline versus fibrous with necking).</p>",
    1, 2, "Two surfaces shown and described.",
    "Low-temperature: flat, granular (brittle); high-temperature: fibrous with necking (ductile)."),
  q("Task 6 - Questions and conclusion (2 marks)",
    "<p>(a) What is the Charpy value a measure of? (b) Which atomic lattice "
    "structure is susceptible to brittleness at low temperatures? (c) Write a "
    "short conclusion comparing the two steels' transition ranges.</p>",
    2, 3, "Two answers and a conclusion.",
    "Charpy value = energy absorbed in fracture (toughness); body-centred cubic (BCC); conclusion cites the DBTTs."),
  REPORT(["Completed Charpy report (Word/PDF) from the FOL template, with graph and fracture-surface photos"]),
 ])

# ----------------------------------------------------------------------------- virtual welding
def weld_quiz(slug, title, wps_note, parts, key_lines, extra_note=""):
    """parts: list of (label, passes, hint, bend_test) -> one set-up + one weld/score question each.
    Marks: set-up 3 in total, weld and score 6 in total, reflection 1 (quiz totals 10)."""
    n = len(parts)
    fmt = lambda v: ("%g" % round(v, 2))
    per_setup, per_weld = 3.0 / n, 6.0 / n
    qs = [SIM_DECL()]
    for (label, passes, hint, bend) in parts:
        pre = ("<p><b>%s</b></p>" % label) if label else ""
        suffix = (" - " + label) if label else ""
        qs.append(q(
            "Set-up from the WPS%s (%s marks)" % (suffix, fmt(per_setup)),
            pre + "<p>State which <b>WPS</b> you used (identification number or page "
            "in the WPS booklet). Record the values you took from it and entered on "
            "the machine: <b>shielding gas and composition, flow rate (cfh and l/min), "
            "wire feed speed, voltage, polarity</b>, and the WPS's tolerances on wire "
            "feed speed and voltage. " + hint + "</p>",
            round(per_setup, 2), 3,
            "WPS identified; gas, flow, WFS, voltage, polarity, tolerances.", "; ".join(key_lines)))
        qs.append(q(
            "Weld and score%s (%s marks)" % (suffix, fmt(per_weld)),
            pre + "<p>Weld the coupon%s. Record the <b>score for %s</b> and attach a "
            "<b>screenshot / photo of the scoring screen</b>. Describe <b>what you "
            "changed between attempts</b> (work angle, travel angle, travel speed, "
            "contact-tip-to-work distance) and what the monitor screens showed."
            % ("" if passes == 1 else " with %d passes" % passes,
               "the pass" if passes == 1 else "each of the %d passes" % passes)
            + (" Then <b>run the bend test</b>: did you earn a bend-test certificate "
               "(yes / no / not applicable)?" if bend else "") + "</p>",
            round(per_weld, 2), 3, "Score(s), scoring screenshot, adjustments, bend-test result."))
    qs.append(q("Best result and reflection (1 mark)",
        "<p>Which attempt was your <b>best</b>, and what score did it earn? What "
        "single change would most improve your next attempt, and why? %s</p>" % extra_note,
        1, 3, "Best score, the change you would make, and your reasoning."))
    qs.append(REPORT(["Your saved best weld file from the flash drive",
                      "Scoring-screen screenshots or photos"]))
    write_lab(slug, title,
      ["Virtual-welding lab on the Lincoln VRTEX 360+. " + wps_note,
       "Students save their best result to a flash drive and upload it here. This "
       "quiz replaces the source PDF assignment sheet (which had copy-paste slips).",
       "AI use: not applicable -- the work is hands-on in the simulator."], qs)

weld_quiz("weld-flat-single", "GMAW Flat Surfacing: Single Pass",
  "WPS 2010114: 1/4 in A36, ER70S-6 0.035 in, 75/25 Ar-CO2 at 25-35 cfh, WFS 250 +/-5 in/min, 18 +/-1 V, DCEP, CTWD 3/8 in, travel 15 in/min, stringer.",
  [("", 1, "As this is your <b>first</b> lab on the simulator, also answer the start-up questions: "
    "what does the <b>red</b> button open, what happens to the other coloured buttons, what is the "
    "<b>orange</b> button for on the login screen, what <b>units</b> options exist, why is the "
    "<b>green</b> icon inactive on the login screen, what can each saved weld be saved to, and list "
    "the <b>monitor views</b> available.", True)],
  ["75/25 argon-CO2", "25-35 cfh (12-16 l/min)", "WFS 250 +/-5 in/min", "18 +/-1 V", "DCEP", "CTWD 3/8 in", "travel 15 in/min"],
  "Also say what the monitor views showed you.")

weld_quiz("weld-flat-multi", "GMAW Flat Surfacing: Multi-Pass",
  "1/4 in mild-steel flat plate, GMAW short-circuit (Flat Plate 1/4 in GMAW-S). Use the WPS for flat surfacing (same machine settings as the single-pass lab unless your WPS says otherwise).",
  [("", 3, "Explain how you <b>placed each pass relative to the previous one</b>.", False)],
  ["75/25 argon-CO2", "25-35 cfh", "WFS 250 +/-5 in/min", "18 +/-1 V", "DCEP - confirm against the WPS issued"],
  "Did the score change from pass to pass? Why?")

weld_quiz("weld-groove-single", "GMAW Groove Weld: Single Pass",
  "WPS 2170114: 3/8 in A36 butt joint, 1G/PA, backing, 1/4 in root opening, 45 deg included groove, ER70S-6 0.035 in, 75/25 Ar-CO2 at 25-35 cfh, WFS 350 +/-5 in/min, 20 +/-1 V, DCEP, CTWD 3/8 in, pass 1 travel 10.9 in/min.",
  [("", 1, "Also describe the <b>joint</b> (type, position, backing, root opening, groove angle) from the WPS.", False)],
  ["75/25 argon-CO2", "25-35 cfh (12-16 l/min)", "WFS 350 +/-5 in/min", "20 +/-1 V", "DCEP", "butt joint, 1G/PA, backing, 1/4 in root opening, 45 deg groove"],
  "Explain how a groove joint differs from surfacing a plate.")

weld_quiz("weld-groove-multi", "GMAW Groove Weld: Multi-Pass",
  "Same WPS 2170114 as the single-pass groove lab (WFS 350 +/-5 in/min, 20 +/-1 V, DCEP; pass 1 travel 10.9 in/min, pass 2 12.8 in/min). The sheet has room to score up to seven passes.",
  [("", 7, "Also state the <b>travel speed the WPS gives for each pass listed</b>.", True)],
  ["75/25 argon-CO2", "25-35 cfh", "WFS 350 +/-5 in/min", "20 +/-1 V", "DCEP", "pass 1 travel 10.9 in/min; pass 2 12.8 in/min"],
  "Explain what a bend test checks and what a pass or fail tells you about the weld.")

weld_quiz("weld-t-lap", "GMAW T and Lap Welds",
  "Three WPSs, all fillet position 2F/PB, ER70S-6 0.035 in, 75/25 Ar-CO2: Part A T joint 10 GA, single pass (WFS 250 +/-5, 18 +/-1 V, 15 in/min); Part B lap joint 10 GA, single pass (250 +/-5, 18 +/-1 V, 15 in/min); Part C T joint 1/4 in, three passes (WFS 375 +/-5, 20 +/-1 V, travel 12.5 / 15.0 / 12.2 in/min).",
  [("Part A - T joint, 10 GA, single pass", 1, "", True),
   ("Part B - Lap joint, 10 GA, single pass", 1, "", True),
   ("Part C - T joint, 1/4 in, multi-pass", 3, "", True)],
  ["75/25 argon-CO2", "25-35 cfh", "Parts A/B: WFS 250 +/-5, 18 +/-1 V; Part C: WFS 375 +/-5, 20 +/-1 V", "DCEP"],
  "Compare the T and the lap joint: which was harder to score well, and why?")

weld_quiz("weld-vertical-t", "GMAW Vertical T Welds",
  "Vertical-position T joints. Set-up values come from the two WPSs for the vertical T welds (the WPS pages were not among the supplied files -- check them in the WPS booklet before the term).",
  [("Part A - T joint, 10 GA, single pass (vertical)", 1, "Also state the <b>direction of travel</b> the WPS specifies (up or down).", True),
   ("Part B - second vertical T weld", 3, "Also state the <b>direction of travel</b> the WPS specifies.", True)],
  ["values per the vertical-T WPSs in the booklet"],
  "Why is vertical welding harder to control than flat welding?")

print("\nAll lab quiz CSVs written to", OUT)
