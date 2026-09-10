# -*- coding: utf-8 -*-
"""Generate Brightspace/D2L question-import CSVs for the 14 lab quizzes.

Run:  python R/gen_lab_quizzes.py   (from the repo root, or anywhere)

Writes one file per lab to  quizzes/lab01_quiz.csv .. quizzes/lab14_quiz.csv .
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

def write_lab(n, lab_title, note_lines, questions):
    path = os.path.join(OUT, "lab%02d_quiz.csv" % n)
    with io.open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["//Lab %d -- %s" % (n, lab_title)])
        w.writerow(["//Import these questions into the Lab %d quiz on FOL (Brightspace)." % n])
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
            w.writerow(["ID", "%s-L%02d-%02d" % (CC, n, i)])
            w.writerow(["Title", q["title"]])
            # 3rd column "HTML" tells the D2L importer to render the body as
            # HTML instead of printing the tags literally.
            w.writerow(["QuestionText", q["text"], "HTML"])
            w.writerow(["Points", q["points"]])
            w.writerow(["Difficulty", q["difficulty"]])
            w.writerow(["InitialText", q["initial"]])
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

# ----------------------------------------------------------------------------- 1
write_lab(1, "Logic Thinking for Robot Control: Rocksi",
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

# ----------------------------------------------------------------------------- 2
write_lab(2, "Engineering Design Process Documentation",
 ["Case study: Precitech Components shaft-kit assembly & packing cell "
  "(see the Labs chapter, Lab 2). It is the single source of requirements.",
  "Tools: Microsoft Word/Visio, Microsoft Project, Microsoft Excel.",
  "Templates on FOL: Bill_of_Materials_Template_for_Excel.xlsx, Gantt_chart.mpp, "
  "HSE risk-assessment Word template.",
  "Keep your layout drawing -- you reuse it in Lab 3.",
  "AI use: not permitted for any part of this lab."],
 [DECL,
  q("Phase 1 - Specification sheets (2 marks)",
    "<p>Write a <b>specification sheet for the shaft kit</b> (customer, part "
    "number, kit contents, key dimensions and tolerances, packaging, marking, "
    "applicable standards) and a <b>specification sheet for at least one bought-in "
    "component</b> (e.g. the tapered roller bearing).</p>"
    "<p><b>Describe what you put in each field and where the value came from</b> "
    "(the case study, a standard, an assumption you state). Attach both spec "
    "sheets (PDF or DOCX).</p>",
    2, 3, "Summary of each spec sheet and the source of each key value.",
    "Kit spec: contents, dia 25.000 +/-0.050 mm, carton/tray, marking, standards. Component spec present. Traceable to the case study."),
  q("Phase 1 - Bill of materials (2 marks)",
    "<p>Fill in the Excel BOM template for <b>one complete kit</b>: every item, "
    "quantity, unit, and source (machined in-house vs. purchased).</p>"
    "<p><b>Describe how you built the BOM</b> and list the line items. Attach the "
    "completed .xlsx.</p>",
    2, 3, "BOM line items listed; .xlsx attached.",
    "All 7 kit items with correct quantities; in-house vs purchased marked; template format kept."),
  q("Phase 2 - Task list / process flow (2 marks)",
    "<p>Build a <b>chronological task list</b> for producing one kit (receive "
    "blanks -&gt; store components -&gt; pick components for one kit -&gt; press "
    "bearings -&gt; fit retaining ring and seal -&gt; inspect -&gt; place in tray "
    "-&gt; close and label carton -&gt; stage for dock). Add a <b>duration</b> "
    "column. Use the task-numbering scheme (Task 1 -&gt; Sub-task 11 -&gt; "
    "Sub-sub-task 121 ...) from the supplement. Draw the flow as a chart in Visio "
    "or Word.</p>"
    "<p><b>Describe your task list and the numbering you used.</b> Attach the "
    "task list and the flow chart.</p>",
    2, 3, "Task list with durations + numbering; flow chart attached.",
    "Chronological, matches the process outline, durations present, numbering scheme applied, chart matches the list."),
  q("Phase 3 - Project schedule & Gantt chart (2 marks)",
    "<p>Open the example .mpp file. Enter the tasks and durations for "
    "<b>standing up the cell</b> (procure racking and fixtures, install bearing "
    "press, set up inspection station, write the SOP, train operators, run a pilot "
    "batch) and generate a schedule and Gantt chart.</p>"
    "<p><b>Describe the tasks, durations and any dependencies you set.</b> Attach "
    "the .mpp file (and a PDF/image of the Gantt chart).</p>",
    2, 3, "Task/duration/dependency list; .mpp + Gantt attached.",
    "Cell-standup tasks (not kit-production tasks); durations and links sensible; Gantt generated."),
  q("Phase 4 & 5 - Facility layout drawing + HSE risk assessment (2 marks)",
    "<p><b>Layout:</b> from the task list, allocate space for each activity and "
    "draw a General Arrangement of the kitting cell. Show product in (blanks) and "
    "product out (kits), component storage rack, assembly station(s), bearing "
    "press, inspection station, packing bench, staging area, and the raw-material, "
    "finished-goods, waste and people-movement flows. <b>Mark where material "
    "starvation and material blockage could occur.</b></p>"
    "<p><b>HSE:</b> identify at least <b>five</b> health-and-safety risks in the "
    "cell (e.g. manual handling of the blank trolley, pinch points at the bearing "
    "press, sharp edges on retaining rings, repetitive assembly motion, the carton "
    "knife) and document each in the risk-assessment template (hazard, who is "
    "harmed and how, current controls, further action, owner, deadline, done).</p>"
    "<p><b>Describe your layout decisions and list your five risks.</b> Attach the "
    "layout drawing and the completed risk-assessment document.</p>",
    2, 4, "Layout decisions + the 5 risks; drawing + risk assessment attached.",
    "Layout has all stations/flows and the starvation/blockage marks; >=5 realistic risks fully filled in the template."),
  UPLOAD(["Shaft-kit spec sheet + component spec sheet",
          "Bill of materials (.xlsx)",
          "Task list + process-flow chart",
          "Project schedule (.mpp) + Gantt chart image",
          "Facility layout drawing (keep a copy - reused in Lab 3)",
          "Completed HSE risk assessment"]),
 ])

# ----------------------------------------------------------------------------- 3
write_lab(3, "Manufacturing Facility Design & Simulation (AnyLogic)",
 ["Software: AnyLogic Personal Learning Edition (installed) + the order-fulfilment "
  "/ warehouse demo model staged on FOL. Bring your Lab 2 documents.",
  "You run FOUR parameter sets, 3 simulated minutes each.",
  "AI use: not permitted for any part of this lab."],
 [DECL,
  q("Phase 1 - Electronic facility drawing (4 marks)",
    "<p>Recreate your Lab 2 kitting-cell layout <b>electronically</b> (Visio or "
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
    "Drawing is electronic and matches the Lab 2 layout; all 11 checklist items answered; starvation/blockage points identified."),
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

# ----------------------------------------------------------------------------- 4
write_lab(4, "Lean: Value Stream Mapping, Takt and Pull",
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
    "-&gt; inspect -&gt; the Lab 2 kitting cell -&gt; shipping.</p><ul>"
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

# ----------------------------------------------------------------------------- 5
write_lab(5, "Ergonomics in Automated Manufacturing (REBA & Inseer)",
 ["This quiz assigns you ONE of three sample tasks: (1) lifting boxes repeatedly, "
  "(2) computer-workstation setup, (3) floor cleaning with a buffer. Your "
  "assigned task is stated in Question 1.",
  "Tools: printed REBA Employee Assessment Worksheet + REBA cheat sheet; Inseer "
  "(web, login required).",
  "Inseer is a required lab instrument (it is an AI tool). Disclose any other AI "
  "tool you use."],
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
  q("Inseer report (2 marks)",
    "<p>Run the <b>same task</b> through Inseer. Generate the ergonomic "
    "risk-assessment report.</p>"
    "<p><b>Describe how you set the assessment up</b> (what you uploaded / "
    "selected) and <b>quote the key outputs</b> (overall risk rating, the "
    "body regions or time segments Inseer flags, any score it reports). Attach the "
    "Inseer report (PDF or screenshot).</p>",
    2, 3, "Setup described + Inseer outputs quoted + report attached.",
    "Assessment actually run; specific Inseer numbers/flags quoted, not paraphrased; report attached."),
  q("Manual vs automated comparison (2 marks)",
    "<p>Compare the manual REBA assessment with the Inseer report. <b>Quantify "
    "the comparison</b> (where do the two agree, where do they differ, by how "
    "much?). Reference the Chapter 7 risk factors. Give one advantage and one "
    "limitation of each method.</p>",
    2, 3, "Quantified agree/disagree + advantages and limitations of each, tied to Ch.7.",
    "Comparison uses actual numbers from both methods; advantages/limitations are specific, not generic."),
  q("Conclusion and recommended controls (1 mark)",
    "<p>In a short paragraph: why does ergonomics matter in an automated "
    "manufacturing facility, and what did the two tools add? Then <b>list the "
    "controls you would recommend for this task, ordered by the hierarchy of "
    "controls</b> (elimination -> substitution -> engineering -> administrative "
    "-> PPE).</p>",
    1, 3, "Conclusion + controls ordered by the hierarchy of controls.",
    "Controls are specific to the task and correctly ordered by the hierarchy."),
  UPLOAD(["Completed REBA worksheet (photo or scan)",
          "Inseer report (PDF or screenshot)",
          "Any additional screenshots you refer to",
          "AI-use disclosure line (Inseer is expected; note any other tool)"]),
 ])

# ----------------------------------------------------------------------------- 6
write_lab(6, "SPC and Gauge R&R: the Virtual Caliper",
 ["This lab runs inside the Labs chapter web page (webR cells). No external site, "
  "no account, no dataset file.",
  "You run the study SOLO: you play all three operator rounds yourself, in three "
  "separate sittings, reading blind each time (do not look at your earlier "
  "numbers).",
  "AI use: not permitted for the readings or the calculations. You may use an LLM "
  "to check the written reflection only, with disclosure."],
 [DECL,
  q("Task 1 - Calibrate your eye (0 marks, required)",
    "<p>Open the Lab 6 section of the Labs chapter. Run the <b>setup cell first</b>. "
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
    "<p>Type your 90 readings into the lab6-grr cell (op_A = round 1, op_B = round "
    "2, op_C = round 3) and run it.</p>"
    "<p><b>Paste every output</b>: EV (repeatability), AV (reproducibility), GRR, "
    "PV (part variation), TV (total variation), <b>%GRR</b> and <b>ndc</b>. State "
    "whether %GRR and ndc are internally consistent with EV/AV/PV.</p>",
    3, 3, "All seven outputs pasted; internal-consistency check.",
    "Values pasted from the cell; %GRR = 100*GRR/TV and ndc = floor(1.41*PV/GRR) consistent with the other figures."),
  q("Task 4 - Bias and linearity (1 mark)",
    "<p>Run the lab6-bias cell. It compares your mean reading of each part against "
    "that part's certified reference value, reports overall bias, and fits bias "
    "vs. size for linearity.</p>"
    "<p><b>Paste the output. State the overall bias in mm and whether the bias "
    "changes across the size range</b> (the linearity slope).</p>",
    1, 3, "Bias output pasted; bias in mm + linearity statement.",
    "Overall bias reported (expected around +0.03 mm); linearity slope quoted and interpreted."),
  q("Task 5 - X-bar / R chart and Cpk (3 marks)",
    "<p>Run the lab6-spc cell (a seeded 25-subgroup production dataset, 5 shafts "
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

# ----------------------------------------------------------------------------- 7
write_lab(7, "Machine Learning Week 1: AI Literacy and Prompt Engineering",
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
    "explain a line in Lab 8). Note any change you made to the generated code. "
    "<b>Attach spc_starter.py.</b></p>",
    2, 3, "Prompt + per-block explanation + spc_starter.py attached.",
    "Code meets every requirement and runs; student's per-block explanation shows understanding; file attached."),
  UPLOAD(["prompts.md (Exercises 1-3)",
          "spc_starter.py (Exercise 4)",
          "Screenshot(s) - hallucination verification (Exercise 3)"]),
 ])

# ----------------------------------------------------------------------------- 8
write_lab(8, "Machine Learning Week 2: Manufacturing Data and SPC",
 ["Tools: Google Colab. Files from FOL: spc_data.csv (90 days of CNC Cell 3 data "
  "with embedded problems) and week2_lab.ipynb (pre-structured). Bring "
  "spc_starter.py from Lab 7.",
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

# ----------------------------------------------------------------------------- 9
write_lab(9, "Machine Learning Week 3: The C-MAPSS Dataset",
 ["Capstone kickoff. Tools: Google Colab. Files from FOL: train_FD001.txt (NASA "
  "C-MAPSS FD001 training set) and predictive_maintenance.ipynb (pre-structured "
  "for Weeks 3-5).",
  "You keep working in the SAME notebook in Labs 10 and 11.",
  "Labs 9-12 are marked together against the capstone rubric (in FOL / the "
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

# ----------------------------------------------------------------------------- 10
write_lab(10, "Machine Learning Week 4: Building the Predictive-Maintenance Model",
 ["Capstone build. Continue in the SAME predictive_maintenance.ipynb from Lab 9. "
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
    "feature_cols.pkl</b> to this question (you need them for Lab 11).</p>",
    1, 1, "Attach both .pkl files.",
    "Both files attached; feature_cols is the exact training feature list in order."),
 ])

# ----------------------------------------------------------------------------- 11
write_lab(11, "Machine Learning Week 5: Deploying the App",
 ["Tools: GitHub (public repo 'rul-predictor') + Streamlit Community Cloud + "
  "Google Colab. Create the accounts as PREP, not in the lab.",
  "Files from FOL: streamlit_app.py starter (with TODO markers). Bring "
  "rul_model.pkl and feature_cols.pkl from Lab 10.",
  "Lab 14 (take-home RoboDK work cell) is released this week -- read its brief.",
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
    "your <b>actual Lab 10 RMSE</b>, one Precitech-specific limitation).</p>"
    "<p>Run it (streamlit run streamlit_app.py, or Colab + pyngrok). Test a CSV "
    "upload. <b>Describe each TODO you completed</b> and <b>attach a screenshot of "
    "the running app showing a prediction.</b></p>",
    3, 3, "Each TODO described + screenshot of local app with a prediction.",
    "All TODOs done; the Lab 10 RMSE is the student's real number; sample button works; screenshot shows a colour-coded RUL."),
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

# ----------------------------------------------------------------------------- 12
write_lab(12, "Machine Learning Week 6: Capstone Presentation",
 ["You demo your deployed predictive-maintenance app LIVE to the class (8-10 min) "
  "and take 3-5 min of questions. No slides required -- the app is the "
  "presentation.",
  "Your app URL and GitHub repo (submitted in Lab 11) must be live at "
  "presentation time.",
  "This quiz records the session; it carries the Labs 9-12 capstone rubric "
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

# ----------------------------------------------------------------------------- 13
write_lab(13, "TPM/OEE, Root Cause and a New Dataset",
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

# ----------------------------------------------------------------------------- 14
write_lab(14, "Robotic Work-Cell Design in RoboDK for Web (take-home)",
 ["TAKE-HOME lab: released in week 11, due at the end of week 14, done on your own "
  "computer. Individual work.",
  "Tool: RoboDK for Web (web.robodk.com/simulation) -- no install, no licence "
  "key. Plus a screen-recording tool (Windows Xbox Game Bar Win+G, macOS "
  "Shift+Cmd+5, or OBS Studio).",
  "You need your Lab 4 takt time for 250 kits/day.",
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
    "block-programming work in Lab 1 and to the Chapter 8 coordinate systems.</p>",
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
    "<p>Take the <b>takt time from Lab 4</b> for 250 kits/day. <b>Does one robot "
    "at your Task 3 cycle time meet takt?</b></p>"
    "<p>Then <b>optimise</b> -- reorder targets, raise joint speeds within limits, "
    "shorten approach and retract moves -- and record the <b>improved cycle "
    "time</b>. State <b>by how much you beat or missed takt</b>, and what a real "
    "cell would do if one robot could not keep up (parallel cells, a second arm, "
    "faster EOAT, etc.).</p>",
    3, 4, "Lab 4 takt stated + meet/miss before optimisation + optimised cycle time + gap quantified + real-cell mitigation.",
    "Uses the student's Lab 4 takt; before/after cycle times; optimisation changes are physically plausible (no joint speeds past limits); gap quantified."),
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

print("\nAll 14 lab quiz CSVs written to", OUT)
