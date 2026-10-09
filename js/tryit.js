// Shared runtime for "try it yourself" exercises.
//
// A tryit exercise is emitted by one of the `tryit_*()` R helpers (see
// R/tryit.R): a `.tryit` div carrying `data-tryit="<type>"` and a single
// <script type="application/json"> child holding the exercise, answer key
// included. This file auto-discovers every such div on the page and builds
// the widget inside it. Types:
//   number  one or more numeric answer fields, each marked against a tolerance
//   grid    a table whose blank cells the student fills in, marked per cell
//   sort    cards the student assigns to categories (click, not drag, so it
//           works by keyboard and on a touch screen)
//
// Every widget has Check and Reset buttons, allows unlimited attempts, marks
// each item with a tick or cross as well as a colour, and shows a hint under
// a wrong item when the exercise supplies one.
//
// A `<details class="tryit-solution">` placed directly after an exercise is
// its worked solution: it stays locked until the student has checked at
// least one answer.
//
// No dependencies and no webR, so this works in any chapter.

(function (global) {
  "use strict";

  if (global.__tryitLoaded) return; // guard against duplicate <script src> tags
  global.__tryitLoaded = true;

  // Tiny element builder: el("div", {class: "x"}, [child, "text"])
  function el(tag, attrs, children) {
    const node = document.createElement(tag);
    Object.entries(attrs || {}).forEach(([key, value]) => {
      if (value !== null && value !== undefined) node.setAttribute(key, value);
    });
    (children || []).forEach((child) => {
      if (child === null || child === undefined) return;
      node.appendChild(typeof child === "string" ? document.createTextNode(child) : child);
    });
    return node;
  }

  // Read what a student typed as a number. Accepts "12.5", "12,5", "1,250.5",
  // "$ 12.50" and "45 %"; returns null for a blank field and NaN for anything
  // that is not a number.
  function parseNumber(raw) {
    let text = String(raw).replace(/[\s$%]/g, "");
    if (text === "") return null;
    if (text.includes(",") && text.includes(".")) {
      text = text.replace(/,/g, "");
    } else {
      text = text.replace(",", ".");
    }
    return Number(text);
  }

  function isCorrect(value, spec) {
    if (value === null || isNaN(value)) return false;
    const error = Math.abs(value - spec.answer);
    if (error <= (spec.tol || 0) + 1e-9) return true;
    return spec.tolPct ? error <= Math.abs(spec.answer) * spec.tolPct / 100 + 1e-9 : false;
  }

  // One checkable numeric field. `wrap` is the element that carries the
  // right/wrong state (a table cell or an answer row).
  function numericField(spec, ariaLabel, wrap) {
    const input = el("input", { type: "text", inputmode: "decimal", autocomplete: "off", "aria-label": ariaLabel });
    const mark = el("span", { class: "tryit-mark", "aria-hidden": "true" });

    function clear() {
      wrap.classList.remove("tryit-ok", "tryit-no");
      mark.textContent = "";
      input.removeAttribute("aria-invalid");
    }

    input.addEventListener("input", clear); // an edited answer is unmarked until re-checked

    return {
      input,
      mark,
      // "blank" | "ok" | "no"
      check() {
        clear();
        const value = parseNumber(input.value);
        if (value === null) return "blank";
        const ok = isCorrect(value, spec);
        wrap.classList.add(ok ? "tryit-ok" : "tryit-no");
        mark.textContent = ok ? "✓" : "✗";
        if (!ok) input.setAttribute("aria-invalid", "true");
        return ok ? "ok" : "no";
      },
      reset() {
        input.value = "";
        clear();
      },
    };
  }

  // A labelled list of numeric answers (the whole of a "number" exercise,
  // and the part of a "grid" exercise that sits under the table).
  function answerList(answers) {
    const list = el("div", { class: "tryit-answers" });
    const fields = answers.map((spec) => {
      const row = el("div", { class: "tryit-answer" });
      const field = numericField(spec, spec.label, row);
      const hint = spec.hint ? el("div", { class: "tryit-hint", hidden: "" }, [spec.hint]) : null;
      row.appendChild(el("label", {}, [spec.label]));
      row.appendChild(el("div", { class: "tryit-field" }, [
        spec.prefix ? el("span", { class: "tryit-affix" }, [spec.prefix]) : null,
        field.input,
        spec.suffix ? el("span", { class: "tryit-affix" }, [spec.suffix]) : null,
        field.mark,
      ]));
      if (hint) row.appendChild(hint);
      list.appendChild(row);
      field.input.addEventListener("input", () => { if (hint) hint.hidden = true; });
      return {
        check() {
          const state = field.check();
          if (hint) hint.hidden = state !== "no";
          return state;
        },
        reset() {
          field.reset();
          if (hint) hint.hidden = true;
        },
      };
    });
    return { list, fields };
  }

  function summarise(states, noun) {
    const total = states.length;
    const right = states.filter((s) => s === "ok").length;
    const blank = states.filter((s) => s === "blank").length;
    if (right === total) return `All ${total} ${noun} correct.`;
    let text = `${right} of ${total} ${noun} correct.`;
    if (blank > 0) text += ` ${blank} left blank.`;
    if (total - right - blank > 0) text += " Fix the ones marked ✗ and check again.";
    return text;
  }

  function buildNumber(spec, body) {
    const { list, fields } = answerList(spec.answers);
    body.appendChild(list);
    return {
      check() {
        const states = fields.map((f) => f.check());
        return { states, message: summarise(states, states.length === 1 ? "answer" : "answers") };
      },
      reset() { fields.forEach((f) => f.reset()); },
    };
  }

  function buildGrid(spec, body) {
    const cells = []; // { field, column }
    const head = el("tr", {}, spec.columns.map((col) => el("th", { scope: "col" }, [col.label])));
    const rows = spec.rows.map((row, r) => el("tr", {}, row.map((value, c) => {
      const col = spec.columns[c];
      if (!col.blank) return el("td", {}, [String(value)]);
      const td = el("td", { class: "tryit-cell" });
      const field = numericField({ answer: value, tol: col.tol }, `${col.label}, row ${r + 1}`, td);
      td.appendChild(field.input);
      td.appendChild(field.mark);
      cells.push({ field, column: c });
      return td;
    })));
    body.appendChild(el("div", { class: "tryit-scroll" }, [
      el("table", { class: "tryit-grid" }, [el("thead", {}, [head]), el("tbody", {}, rows)]),
    ]));

    // One hint line per blank column, shown once that column has a wrong cell.
    const hints = new Map();
    spec.columns.forEach((col, c) => {
      if (!col.hint) return;
      const hint = el("div", { class: "tryit-hint", hidden: "" }, [`${col.label}: ${col.hint}`]);
      hints.set(c, hint);
      body.appendChild(hint);
    });

    const below = answerList(spec.answers || []);
    if (below.fields.length > 0) body.appendChild(below.list);

    return {
      check() {
        const wrongColumns = new Set();
        const states = cells.map(({ field, column }) => {
          const state = field.check();
          if (state === "no") wrongColumns.add(column);
          return state;
        });
        hints.forEach((hint, column) => { hint.hidden = !wrongColumns.has(column); });
        below.fields.forEach((f) => states.push(f.check()));
        return { states, message: summarise(states, "entries") };
      },
      reset() {
        cells.forEach(({ field }) => field.reset());
        hints.forEach((hint) => { hint.hidden = true; });
        below.fields.forEach((f) => f.reset());
      },
    };
  }

  function shuffle(items) {
    const out = items.slice();
    for (let i = out.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [out[i], out[j]] = [out[j], out[i]];
    }
    return out;
  }

  function buildSort(spec, body, id) {
    const list = el("ol", { class: "tryit-cards" });
    const cards = shuffle(spec.cards).map((card, i) => {
      const item = el("li", { class: "tryit-card" });
      const mark = el("span", { class: "tryit-mark", "aria-hidden": "true" });
      const why = card.why ? el("div", { class: "tryit-why", hidden: "" }, [card.why]) : null;
      const group = el("div", { class: "tryit-bins", role: "radiogroup", "aria-label": card.text });
      const radios = spec.bins.map((bin, b) => {
        const radio = el("input", { type: "radio", name: `${id}-card-${i}`, id: `${id}-card-${i}-bin-${b}`, value: String(b) });
        group.appendChild(radio);
        group.appendChild(el("label", { for: radio.id }, [bin]));
        return radio;
      });

      function clear() {
        item.classList.remove("tryit-ok", "tryit-no");
        mark.textContent = "";
        if (why) why.hidden = true;
      }
      radios.forEach((radio) => radio.addEventListener("change", clear));

      item.appendChild(el("div", { class: "tryit-card-text" }, [card.text, mark]));
      item.appendChild(group);
      if (why) item.appendChild(why);
      list.appendChild(item);

      return {
        check() {
          clear();
          const chosen = radios.find((radio) => radio.checked);
          if (!chosen) return "blank";
          const ok = Number(chosen.value) === card.bin;
          item.classList.add(ok ? "tryit-ok" : "tryit-no");
          mark.textContent = ok ? " ✓" : " ✗";
          // The explanation appears once the card is right, so it confirms
          // the reasoning without giving the answer away on a miss.
          if (why) why.hidden = !ok;
          return ok ? "ok" : "no";
        },
        reset() {
          radios.forEach((radio) => { radio.checked = false; });
          clear();
        },
      };
    });
    body.appendChild(list);

    return {
      check() {
        const states = cards.map((c) => c.check());
        return { states, message: summarise(states, "cards") };
      },
      reset() { cards.forEach((c) => c.reset()); },
    };
  }

  const builders = { number: buildNumber, grid: buildGrid, sort: buildSort };

  // The worked solution, if the chapter put one directly after the exercise.
  function findSolution(root) {
    let next = root.nextElementSibling;
    while (next && next.tagName === "SCRIPT") next = next.nextElementSibling;
    return next && next.matches("details.tryit-solution") ? next : null;
  }

  function init(root) {
    if (root.dataset.tryitBound === "true") return;
    root.dataset.tryitBound = "true";

    const source = root.querySelector('script[type="application/json"]');
    const build = builders[root.dataset.tryit];
    if (!source || !build) {
      console.warn(`tryit: cannot build exercise "${root.id}" (type "${root.dataset.tryit}").`);
      return;
    }
    const spec = JSON.parse(source.textContent);

    root.appendChild(el("div", { class: "tryit-header" }, [
      el("span", { class: "tryit-badge" }, ["Try it"]),
      el("h4", {}, [spec.title]),
    ]));
    if (spec.intro) root.appendChild(el("p", { class: "tryit-intro" }, [spec.intro]));

    const body = el("div", { class: "tryit-body" });
    root.appendChild(body);
    const widget = build(spec, body, root.id);

    const feedback = el("div", { class: "tryit-feedback", role: "status", "aria-live": "polite" });
    const checkButton = el("button", { type: "button", class: "tryit-btn" }, ["Check my answers"]);
    const resetButton = el("button", { type: "button", class: "tryit-btn tryit-btn-secondary" }, ["Reset"]);
    root.appendChild(el("div", { class: "tryit-controls" }, [checkButton, resetButton]));
    root.appendChild(feedback);

    const solution = findSolution(root);
    if (solution) {
      solution.classList.add("tryit-locked");
      solution.querySelector("summary").addEventListener("click", (event) => {
        if (!solution.classList.contains("tryit-locked")) return;
        event.preventDefault();
        feedback.textContent = "Check at least one answer first — then the worked solution unlocks.";
      });
    }

    checkButton.addEventListener("click", () => {
      const { states, message } = widget.check();
      const attempted = states.some((s) => s !== "blank");
      feedback.textContent = attempted ? message : "Nothing entered yet.";
      feedback.classList.toggle("tryit-all-ok", states.every((s) => s === "ok"));
      if (attempted && solution) solution.classList.remove("tryit-locked");
    });

    resetButton.addEventListener("click", () => {
      widget.reset();
      feedback.textContent = "";
      feedback.classList.remove("tryit-all-ok");
    });
  }

  function autoInit() {
    document.querySelectorAll(".tryit[data-tryit]").forEach(init);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", autoInit);
  } else {
    autoInit();
  }

  global.tryit = {
    init: init, // exposed in case an exercise is injected after DOMContentLoaded
    parseNumber: parseNumber,
    isCorrect: isCorrect,
  };
})(window);
