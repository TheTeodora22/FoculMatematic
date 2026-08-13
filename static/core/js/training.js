(function () {
    const dataEl = document.getElementById("training-data");
    if (!dataEl) {
        return;
    }

    let data;
    try {
        data = JSON.parse(dataEl.textContent);
    } catch (_err) {
        showBootError("Nu am putut citi datele antrenării.");
        return;
    }

    let currentIndex = data.currentIndex;

    const pageEl = document.querySelector(".training-page");
    const loaderEl = document.getElementById("training-loader");
    const layoutEl = document.getElementById("training-layout");
    const progressEl = document.getElementById("training-progress");
    const cardEl = document.getElementById("training-question");
    const gridEl = document.getElementById("training-grid");
    const prevArrow = document.querySelector(".training-arrow--prev");
    const nextArrow = document.querySelector(".training-arrow--next");
    const saveErrorEl = document.getElementById("training-save-error");

    function escapeHtml(text) {
        const div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML;
    }

    function getCsrfToken() {
        return document.querySelector("[name=csrfmiddlewaretoken]")?.value || "";
    }

    function isSolved(question) {
        return question.status === "correct";
    }

    function trainingUrl(index) {
        return `/quizzes/subiect/${data.topicId}/antrenare/${index}/`;
    }

    function parseIndexFromUrl() {
        const match = window.location.pathname.match(/\/antrenare\/(\d+)\/?$/);
        if (!match) {
            return data.currentIndex;
        }
        const index = parseInt(match[1], 10);
        if (Number.isNaN(index) || index < 0 || index >= data.questions.length) {
            return data.currentIndex;
        }
        return index;
    }

    function showBootError(message) {
        if (loaderEl) {
            loaderEl.classList.add("training-loader--error");
            loaderEl.innerHTML = `<p>${escapeHtml(message)}</p>`;
            loaderEl.style.display = "flex";
        }
        pageEl?.classList.remove("training-page--loading");
    }

    function revealPage() {
        pageEl?.classList.remove("training-page--loading");
        pageEl?.classList.add("training-page--ready");
        if (loaderEl) {
            loaderEl.hidden = true;
        }
        if (layoutEl) {
            layoutEl.style.visibility = "";
        }
    }

    function validatePayload(payload) {
        if (!payload.questions || !Array.isArray(payload.questions) || payload.questions.length === 0) {
            throw new Error("Nu am putut încărca întrebările.");
        }

        for (const question of payload.questions) {
            const isInteractive = [
                "parentheses_drag",
                "column_addition",
                "column_multiplication",
                "column_division",
                "column_subtraction",
                "missing_digits",
                "error_spotting",
                "parentheses_target",
                "input_output",
                "division_relation",
                "operation_chain",
                "division_table",
                "numeric_input",
                "factor_builder",
                "factor_error",
                "factor_match",
                "power_builder",
                "power_match",
                "power_table",
                "power_cycle",
                "power_square",
                "power_rule_chain",
                "power_compare",
                "power_order",
                "base_values",
                "base_match",
                "binary_toggle",
                "base_error",
                "unit_reduction",
                "comparison_method",
                "figurative_method",
                "reverse_method",
                "false_hypothesis_method",
                "operation_sequence",
                "operation_workbench",
                "divisibility_values",
                "divisibility_select",
                "divisibility_sort",
                "divisibility_error",
                "criteria_table",
                "prime_workbench",
                "decimal_workbench",
                "fraction_visual",
                "fraction_domino",
                "fraction_compare",
                "fraction_axis",
                "gcd_workbench",
                "fraction_scale",
                "fraction_reduce_path",
                "lcm_workbench",
                "common_denominator",
            ].includes(question.type);
            const hasInteractiveTokens =
                isInteractive && question.interactive && typeof question.interactive === "object";
            const hasOptions = Array.isArray(question.options) && question.options.length > 0;
            if (!question.text || (!hasOptions && !hasInteractiveTokens)) {
                throw new Error("Unele întrebări sunt incomplete.");
            }
        }
    }

    function buildGrid() {
        if (!gridEl) {
            return;
        }

        gridEl.innerHTML = data.questions
            .map((question, index) => {
                const status = question.status || "unanswered";
                const currentAttr = index === currentIndex ? ' aria-current="true"' : "";
                return (
                    `<a href="${trainingUrl(index)}"` +
                    ` class="training-cell training-cell--${status}"` +
                    ` data-training-index="${index}"` +
                    ` title="Întrebarea ${index + 1}"${currentAttr}></a>`
                );
            })
            .join("");
    }

    function feedbackHtml(question) {
        if (isSolved(question)) {
            return '<p class="training-feedback training-feedback--correct" style="margin:0 0 0.75rem;">Răspuns corect</p>';
        }
        if (question.status === "wrong") {
            return '<p class="training-feedback training-feedback--wrong" style="margin:0 0 0.75rem;">Încearcă din nou</p>';
        }
        return "";
    }

    function explanationHtml(question) {
        if (!isSolved(question) || !question.explanation) {
            return "";
        }
        return `<p class="training-explanation" style="margin:0 0 1rem;">${escapeHtml(question.explanation)}</p>`;
    }

    function optionsHtml(question, selectedOptionId, showWrongSelection) {
        const solved = isSolved(question);
        const options = question.options
            .map((option) => {
                let classes = "training-option";
                if (solved && option.id === question.correctOptionId) {
                    classes += " training-option--correct";
                } else if (
                    showWrongSelection &&
                    selectedOptionId === option.id &&
                    option.id !== question.correctOptionId
                ) {
                    classes += " training-option--wrong";
                }

                const checked =
                    (solved && option.id === question.correctOptionId) ||
                    (showWrongSelection && selectedOptionId === option.id)
                        ? " checked"
                        : "";
                const disabled = solved ? " disabled" : "";
                const required = solved ? "" : " required";

                return (
                    `<label class="${classes}">` +
                    `<input type="radio" name="option_id" value="${option.id}"${checked}${disabled}${required}>` +
                    `<span>${escapeHtml(option.text)}</span>` +
                    "</label>"
                );
            })
            .join("");

        const submitBtn = solved
            ? ""
            : '<button type="submit" class="btn btn-press" style="margin-top:1rem;">Verifică răspunsul</button>';

        return (
            `<form method="post" class="training-options-form" action="${escapeHtml(trainingUrl(currentIndex))}">` +
            '<fieldset style="border:none;padding:0;margin:0;">' +
            options +
            "</fieldset>" +
            submitBtn +
            "</form>"
        );
    }

    function parenthesesHtml(question) {
        const solved = isSolved(question);
        const tokens = question.interactive.tokens;
        if (!question.placement) {
            question.placement = { open: null, close: null };
        }
        if (solved) {
            question.placement.open = question.interactive.correct_open_index;
            question.placement.close = question.interactive.correct_close_index;
        }

        const slotHtml = (symbol, index, numberText) => {
            const isOpen = symbol === "open";
            const isFilled = question.placement[symbol] === index;
            const character = isOpen ? "(" : ")";
            const relation = isOpen ? "înainte de" : "după";
            const content = isFilled
                ? `<span class="paren-placed" draggable="${solved ? "false" : "true"}" data-symbol="${symbol}">${character}</span>`
                : "";
            return `<button type="button" class="paren-slot paren-slot--${symbol}${isFilled ? " paren-slot--filled" : ""}" data-slot-index="${index}" data-accepts="${symbol}" aria-label="Paranteză ${isOpen ? "deschisă" : "închisă"} ${relation} ${escapeHtml(numberText)}"${solved ? " disabled" : ""}>${content}</button>`;
        };

        const expression = tokens
            .map((rawToken, index) => {
                const token = rawToken.trim();
                const match = index > 0 ? token.match(/^([^\d]+)\s*(\d.*)$/) : null;
                const operator = match ? match[1].trim() : "";
                const numberText = match ? match[2].trim() : token;
                return (
                    (operator ? `<span class="paren-operator">${escapeHtml(operator)}</span>` : "") +
                    `<span class="paren-term">` +
                    slotHtml("open", index, numberText) +
                    `<span class="paren-token">${escapeHtml(numberText)}</span>` +
                    slotHtml("close", index + 1, numberText) +
                    `</span>`
                );
            })
            .join("");

        const target =
            question.type === "parentheses_target"
                ? `<p class="interactive-target">Rezultat-țintă: <strong>${escapeHtml(question.interactive.target)}</strong></p>`
                : "";
        const controls = solved
            ? ""
            : `<div class="paren-palette" aria-label="Paranteze disponibile">
                    <button type="button" class="paren-tile" draggable="true" data-symbol="open" aria-label="Paranteză deschisă">(</button>
                    <button type="button" class="paren-tile" draggable="true" data-symbol="close" aria-label="Paranteză închisă">)</button>
               </div>
               <p class="paren-help">Trage fiecare paranteză în locul potrivit. Pe telefon, atinge paranteza, apoi poziția.</p>`;
        const submit = solved
            ? ""
            : `<div class="paren-actions">
                    <button type="button" class="btn paren-clear">Șterge parantezele</button>
                    <button type="submit" class="btn btn-press">Verifică răspunsul</button>
               </div>`;

        return (
            `<form class="training-parentheses-form" action="${escapeHtml(trainingUrl(currentIndex))}">` +
            target +
            controls +
            `<div class="paren-expression" aria-label="Expresie cu poziții pentru paranteze">${expression}</div>` +
            `<p class="paren-local-error training-feedback--wrong" hidden>Așază ambele paranteze, cu „(” înainte de „)”.</p>` +
            submit +
            `</form>`
        );
    }

    function columnName(width, index) {
        const names = ["unităților", "zecilor", "sutelor", "miilor", "zecilor de mii", "sutelor de mii"];
        return names[width - index - 1] || `coloana ${index + 1}`;
    }

    function columnCalculationHtml(question) {
        const solved = isSolved(question);
        const item = question.interactive;
        const isAddition = question.type === "column_addition";
        const isMultiplication = question.type === "column_multiplication";
        const first = isMultiplication ? item.multiplicand : isAddition ? item.addend1 : item.minuend;
        const second = isMultiplication ? item.multiplier : isAddition ? item.addend2 : item.subtrahend;
        const markers = isAddition || isMultiplication ? item.carry_columns : item.borrow_columns;
        const width = item.correct_result.length;
        const decimalPlaces = Number(item.decimal_places || 0);
        const firstDecimalPlaces = Number(item.multiplicand_decimal_places ?? decimalPlaces);
        const secondDecimalPlaces = Number(item.multiplier_decimal_places ?? decimalPlaces);
        const paddedFirst = first.padStart(width, "0");
        const paddedSecond = second.padStart(width, "0");
        const paddedMarkers = Array(width - markers.length).fill(false).concat(markers);
        if (!question.columnAnswer) {
            question.columnAnswer = {
                digits: Array(width).fill(""),
                borrows: Array(width).fill(false),
            };
        }
        if (solved) {
            question.columnAnswer.digits = item.correct_result.split("");
            question.columnAnswer.borrows = [...paddedMarkers];
        }

        const borrowRow = question.columnAnswer.borrows
            .map(
                (active, index) =>
                    `<button type="button" class="column-borrow${active ? " column-borrow--active" : ""}" data-borrow-index="${index}" aria-pressed="${active}" aria-label="${isAddition || isMultiplication ? "Transport" : "Împrumut"} la coloana ${columnName(width, index)}"${solved ? " disabled" : ""}>${active ? "1" : ""}</button>`
            )
            .join("");
        const digitRow = (value, className = "", hideLeadingZeros = false, rowDecimalPlaces = decimalPlaces) =>
            value
                .split("")
                .map((digit, index) => {
                    const hidden = hideLeadingZeros && digit === "0" && value.slice(0, index + 1).split("").every((item) => item === "0") && index < value.length - 1;
                    const decimalClass = rowDecimalPlaces && index === value.length - rowDecimalPlaces - 1 ? " column-digit--decimal" : "";
                    return `<span class="column-digit ${className}${decimalClass}">${hidden ? "" : digit}</span>`;
                })
                .join("");
        const resultRow = question.columnAnswer.digits
            .map(
                (digit, index) =>
                    `<span class="column-result-cell"><input class="column-digit-input" data-result-index="${index}" inputmode="numeric" pattern="[0-9]" maxlength="1" value="${escapeHtml(digit)}" aria-label="Cifra rezultatului la coloana ${columnName(width, index)}"${solved ? " disabled" : ""}>${decimalPlaces && index === width - decimalPlaces - 1 ? '<i class="column-decimal-comma">,</i>' : ""}</span>`
            )
            .join("");

        return (
            `<form class="training-column-form interactive-form">` +
            `<p class="interactive-instruction">${isMultiplication ? "Apasă căsuțele în care ajunge un transport, apoi completează produsul." : isAddition ? "Apasă căsuțele în care ajunge un transport, apoi completează suma." : "Apasă căsuțele de sus unde se împrumută o zece, apoi completează rezultatul."}</p>` +
            `<div class="vertical-calculation" style="--column-count:${width}">` +
            `<span class="vertical-sign vertical-sign--borrow">${isAddition || isMultiplication ? "Transport" : "Împrumut"}</span><div class="vertical-digits">${borrowRow}</div>` +
            `<span class="vertical-sign"></span><div class="vertical-digits">${digitRow(paddedFirst, "", isMultiplication, firstDecimalPlaces)}</div>` +
            `<span class="vertical-sign">${isMultiplication ? "×" : isAddition ? "+" : "−"}</span><div class="vertical-digits">${digitRow(paddedSecond, "", isMultiplication, secondDecimalPlaces)}</div>` +
            `<span class="vertical-sign"></span><div class="vertical-rule"></div>` +
            `<span class="vertical-sign"></span><div class="vertical-digits">${resultRow}</div>` +
            `</div>` +
            (solved ? "" : `<button type="submit" class="btn btn-press">Verifică răspunsul</button>`) +
            `</form>`
        );
    }

    function missingDigitsHtml(question) {
        const solved = isSolved(question);
        const item = question.interactive;
        const isAddition = item.operation === "add";
        const isMultiplication = item.operation === "multiply";
        const isDivision = item.operation === "divide";
        const rowNames = isDivision
            ? ["dividend", "divisor", "quotient"]
            : isMultiplication
            ? ["factor1", "factor2", "result"]
            : isAddition
                ? ["addend1", "addend2", "result"]
                : ["minuend", "subtrahend", "result"];
        const width = item[rowNames[0]].length;
        const missing = new Set(item.missing);
        if (!question.answerValues) question.answerValues = {};
        if (solved) {
            item.missing.forEach((key) => {
                const [rowName, rawIndex] = key.split(":");
                question.answerValues[key] = item[rowName][Number(rawIndex)];
            });
        }

        const rowLabels = {
            addend1: "primul termen",
            addend2: "al doilea termen",
            factor1: "primul factor",
            factor2: "al doilea factor",
            dividend: "deîmpărțit",
            divisor: "împărțitor",
            quotient: "cât",
            minuend: "descăzut",
            subtrahend: "scăzător",
            result: "rezultat",
        };
        const rowHtml = (rowName) =>
            item[rowName]
                .split("")
                .map((digit, index) => {
                    const key = `${rowName}:${index}`;
                    const leadingPadding = (isMultiplication || isDivision) && digit === "0" && item[rowName].slice(0, index + 1).split("").every((value) => value === "0") && index < item[rowName].length - 1;
                    if (leadingPadding && !missing.has(key)) return `<span class="column-digit"></span>`;
                    if (!missing.has(key)) return `<span class="column-digit">${digit}</span>`;
                    return `<input class="column-digit-input missing-digit-input" data-answer-key="${key}" inputmode="numeric" pattern="[0-9]" maxlength="1" value="${escapeHtml(question.answerValues[key] || "")}" aria-label="Cifra lipsă din ${rowLabels[rowName]} la coloana ${columnName(width, index)}"${solved ? " disabled" : ""}>`;
                })
                .join("");

        return (
            `<form class="training-missing-form interactive-form">` +
            `<p class="interactive-instruction">Completează toate căsuțele cu cifrele potrivite.</p>` +
            `<div class="vertical-calculation" style="--column-count:${width}">` +
            `<span class="vertical-sign"></span><div class="vertical-digits">${rowHtml(rowNames[0])}</div>` +
            `<span class="vertical-sign">${isDivision ? ":" : isMultiplication ? "×" : isAddition ? "+" : "−"}</span><div class="vertical-digits">${rowHtml(rowNames[1])}</div>` +
            `<span class="vertical-sign"></span><div class="vertical-rule"></div>` +
            `<span class="vertical-sign"></span><div class="vertical-digits">${rowHtml("result")}</div>` +
            `</div>` +
            (solved ? "" : `<button type="submit" class="btn btn-press">Verifică răspunsul</button>`) +
            `</form>`
        );
    }

    function errorSpottingHtml(question) {
        const solved = isSolved(question);
        const item = question.interactive;
        const isAddition = item.operation === "add";
        const isMultiplication = item.operation === "multiply";
        const isDivision = item.operation === "divide";
        const first = isDivision ? item.dividend : isMultiplication ? item.factor1 : isAddition ? item.addend1 : item.minuend;
        const second = isDivision ? item.divisor : isMultiplication ? item.factor2 : isAddition ? item.addend2 : item.subtrahend;
        if (solved) question.selectedColumn = item.error_column;
        const width = first.length;
        const columns = first
            .split("")
            .map((digit, index) => {
                let classes = "error-column";
                if (solved && index === item.error_column) classes += " error-column--correct";
                else if (question.status === "wrong" && index === question.selectedColumn) classes += " error-column--wrong";
                else if (index === question.selectedColumn) classes += " error-column--selected";
                return (
                    `<button type="button" class="${classes}" data-error-column="${index}" aria-label="Coloana ${columnName(width, index)}"${solved ? " disabled" : ""}>` +
                    `<span>${(isMultiplication || isDivision) && digit === "0" && first.slice(0, index + 1).split("").every((value) => value === "0") && index < width - 1 ? "" : digit}</span><span>${(isMultiplication || isDivision) && second[index] === "0" && second.slice(0, index + 1).split("").every((value) => value === "0") && index < width - 1 ? "" : second[index]}</span><span class="error-column__rule"></span><span>${item.shown_result[index]}</span>` +
                    `</button>`
                );
            })
            .join("");
        return (
            `<form class="training-error-form interactive-form">` +
            `<p class="interactive-instruction">Apasă coloana în care cifra rezultatului este greșită.</p>` +
            `<div class="error-calculation"><span class="error-minus">${isDivision ? ":" : isMultiplication ? "×" : isAddition ? "+" : "−"}</span><div class="error-columns">${columns}</div></div>` +
            (solved ? "" : `<button type="submit" class="btn btn-press">Verifică răspunsul</button>`) +
            `</form>`
        );
    }

    function inputOutputHtml(question) {
        const solved = isSolved(question);
        const item = question.interactive;
        if (!question.answerValues) question.answerValues = {};
        if (solved) {
            item.rows.forEach((row, index) => {
                if (row.input === null) question.answerValues[`${index}:input`] = String(item.operation === "divide" ? row.output * item.value : item.operation === "multiply" ? row.output / item.value : item.operation === "add" ? row.output - item.value : row.output + item.value);
                else question.answerValues[`${index}:output`] = String(item.operation === "divide" ? row.input / item.value : item.operation === "multiply" ? row.input * item.value : item.operation === "add" ? row.input + item.value : row.input - item.value);
            });
        }
        const cell = (value, key, label) => {
            if (value !== null) return `<span>${escapeHtml(value)}</span>`;
            return `<input class="machine-input" data-answer-key="${key}" inputmode="numeric" pattern="[0-9]+" value="${escapeHtml(question.answerValues[key] || "")}" aria-label="${label}"${solved ? " disabled" : ""}>`;
        };
        const rows = item.rows
            .map(
                (row, index) =>
                    `<tr><td>${cell(row.input, `${index}:input`, `Intrarea lipsă de pe rândul ${index + 1}`)}</td><td class="machine-arrow">→</td><td>${cell(row.output, `${index}:output`, `Ieșirea lipsă de pe rândul ${index + 1}`)}</td></tr>`
            )
            .join("");
        return (
            `<form class="training-machine-form interactive-form">` +
            `<p class="machine-rule">Regulă: <strong>${item.operation === "divide" ? "împarte la" : item.operation === "multiply" ? "înmulțește cu" : item.operation === "add" ? "adună" : "scade"} ${escapeHtml(item.value)}</strong></p>` +
            `<table class="machine-table"><thead><tr><th>Intrare</th><th></th><th>Ieșire</th></tr></thead><tbody>${rows}</tbody></table>` +
            (solved ? "" : `<button type="submit" class="btn btn-press">Verifică răspunsul</button>`) +
            `</form>`
        );
    }

    function columnDivisionHtml(question) {
        const solved = isSolved(question);
        const item = question.interactive;
        if (!question.divisionAnswer) question.divisionAnswer = { quotient: "", remainders: Array(item.remainders.length).fill("") };
        if (solved) question.divisionAnswer = { quotient: String(item.quotient), remainders: item.remainders.map(String) };
        const steps = item.remainders.map((_, index) =>
            `<label class="division-step"><span>${index === item.remainders.length - 1 ? "Rest final" : `Rest după cifra ${index + 1}`}</span><input data-remainder-index="${index}" inputmode="numeric" value="${escapeHtml(question.divisionAnswer.remainders[index])}"${solved ? " disabled" : ""}></label>`
        ).join("");
        return `<form class="training-division-column-form interactive-form">` +
            `<div class="division-equation"><strong>${escapeHtml(item.dividend)}</strong><span>:</span><strong>${escapeHtml(item.divisor)}</strong><span>=</span><input class="division-quotient-input" inputmode="numeric" aria-label="Câtul împărțirii" value="${escapeHtml(question.divisionAnswer.quotient)}"${solved ? " disabled" : ""}></div>` +
            `<p class="interactive-instruction">Completează câtul și restul obținut după coborârea fiecărei cifre. Restul final trebuie să fie mai mic decât împărțitorul.</p>` +
            `<div class="division-steps">${steps}</div>` +
            (solved ? "" : `<button type="submit" class="btn btn-press">Verifică răspunsul</button>`) + `</form>`;
    }

    function divisionRelationHtml(question) {
        const solved = isSolved(question), item = question.interactive;
        if (question.numericValue === undefined) question.numericValue = "";
        if (solved) question.numericValue = String(item[item.missing]);
        const labels = { dividend: "deîmpărțit", divisor: "împărțitor", quotient: "cât", remainder: "rest" };
        const cell = (key) => key === item.missing
            ? `<input class="relation-input" data-numeric-value inputmode="numeric" aria-label="${labels[key]}" value="${escapeHtml(question.numericValue)}"${solved ? " disabled" : ""}>`
            : `<strong>${escapeHtml(item[key])}</strong>`;
        const hasRemainder = Object.prototype.hasOwnProperty.call(item, "remainder");
        const remainder = hasRemainder ? `<span>+</span>${cell("remainder")}` : "";
        return `<form class="training-single-value-form interactive-form"><div class="division-relation">${cell("dividend")}<span>=</span>${cell("divisor")}<span>×</span>${cell("quotient")}${remainder}</div>` +
            `<p class="interactive-instruction">${hasRemainder ? "Folosește relația: deîmpărțitul = împărțitor × cât + rest, unde restul este mai mic decât împărțitorul." : "Folosește relația: deîmpărțitul = împărțitor × cât."}</p>` +
            (solved ? "" : `<button type="submit" class="btn btn-press">Verifică răspunsul</button>`) + `</form>`;
    }

    function operationChainHtml(question) {
        const solved = isSolved(question), item = question.interactive;
        if (!question.chainValues) question.chainValues = Array(item.steps.length).fill("");
        if (solved) question.chainValues = item.steps.map(step => String(step.result));
        const labels = { divide: ":", multiply: "×", add: "+", subtract: "−" };
        const steps = item.steps.map((step, index) => `<span class="chain-operation">${labels[step.operation]} ${escapeHtml(step.value)}</span><span class="chain-arrow">→</span><input data-chain-index="${index}" inputmode="numeric" aria-label="Rezultatul pasului ${index + 1}" value="${escapeHtml(question.chainValues[index])}"${solved ? " disabled" : ""}>`).join("");
        return `<form class="training-chain-form interactive-form"><div class="operation-chain"><strong>${escapeHtml(item.start)}</strong><span class="chain-arrow">→</span>${steps}</div>` +
            (solved ? "" : `<button type="submit" class="btn btn-press">Verifică răspunsul</button>`) + `</form>`;
    }

    function divisionTableHtml(question) {
        const solved = isSolved(question), item = question.interactive;
        if (!question.answerValues) question.answerValues = {};
        const hasRemainder = item.rows.some(row => Object.prototype.hasOwnProperty.call(row, "remainder"));
        const cells = hasRemainder ? ["dividend", "divisor", "quotient", "remainder"] : ["dividend", "divisor", "quotient"];
        const labels = { dividend: "Deîmpărțit", divisor: "Împărțitor", quotient: "Cât", remainder: "Rest" };
        if (solved) item.rows.forEach((row, index) => question.answerValues[`${index}:${row.missing}`] = String(row[row.missing]));
        const rows = item.rows.map((row, index) => `<tr>${cells.map(key => `<td>${key === row.missing ? `<input data-answer-key="${index}:${key}" inputmode="numeric" aria-label="${labels[key]} lipsă pe rândul ${index + 1}" value="${escapeHtml(question.answerValues[`${index}:${key}`] || "")}"${solved ? " disabled" : ""}>` : escapeHtml(row[key])}</td>`).join("")}</tr>`).join("");
        return `<form class="training-table-form interactive-form"><table class="division-data-table"><thead><tr><th>Deîmpărțit</th><th>Împărțitor</th><th>Cât</th>${hasRemainder ? "<th>Rest</th>" : ""}</tr></thead><tbody>${rows}</tbody></table>` +
            (solved ? "" : `<button type="submit" class="btn btn-press">Verifică răspunsul</button>`) + `</form>`;
    }

    function numericInputHtml(question) {
        const solved = isSolved(question), item = question.interactive;
        if (question.numericValue === undefined) question.numericValue = "";
        if (solved) question.numericValue = String(item.answer);
        return `<form class="training-single-value-form interactive-form"><div class="numeric-answer-wrap"><input data-numeric-value inputmode="numeric" aria-label="Răspuns numeric" value="${escapeHtml(question.numericValue)}"${solved ? " disabled" : ""}>${item.suffix ? `<span>${escapeHtml(item.suffix)}</span>` : ""}</div>` +
            (solved ? "" : `<button type="submit" class="btn btn-press">Verifică răspunsul</button>`) + `</form>`;
    }

    function factorBuilderHtml(question) {
        const solved = isSolved(question);
        const item = question.interactive;
        if (!question.answerValues) question.answerValues = {};
        if (solved) {
            question.answerValues.factor = String(item.common_factor);
            question.answerValues.result = String(item.result);
            item.inner_terms.forEach((term, index) => {
                question.answerValues[`inner:${index}`] = String(term);
            });
        }
        const input = (key, label) =>
            `<input class="factor-number-input" data-answer-key="${key}" inputmode="numeric" pattern="[0-9]+" value="${escapeHtml(question.answerValues[key] || "")}" aria-label="${label}"${solved ? " disabled" : ""}>`;
        const inner = item.inner_terms
            .map((_, index) => {
                const operator = index ? `<span class="factor-operator">${escapeHtml(item.operators[index - 1])}</span>` : "";
                return `${operator}${input(`inner:${index}`, `Termenul ${index + 1} din paranteză`)}`;
            })
            .join("");
        return (
            `<form class="training-factor-builder-form interactive-form">` +
            `<p class="factor-original-expression">${escapeHtml(item.expression)}</p>` +
            `<p class="interactive-instruction">Scoate factorul comun, completează paranteza și rezultatul.</p>` +
            `<div class="factor-builder">${input("factor", "Factorul comun")}<span>·</span><span>(</span>${inner}<span>)</span><span>=</span>${input("result", "Rezultatul final")}</div>` +
            (solved ? "" : `<button type="submit" class="btn btn-press">Verifică răspunsul</button>`) +
            `</form>`
        );
    }

    function factorErrorHtml(question) {
        const solved = isSolved(question);
        const item = question.interactive;
        if (solved) question.selectedStep = item.error_index;
        const steps = item.steps
            .map((step, index) => {
                let classes = "factor-step";
                if (solved && index === item.error_index) classes += " factor-step--correct";
                else if (question.status === "wrong" && index === question.selectedStep) classes += " factor-step--wrong";
                else if (index === question.selectedStep) classes += " factor-step--selected";
                return `<button type="button" class="${classes}" data-factor-step="${index}"${solved ? " disabled" : ""}><span class="factor-step__number">${index + 1}</span><span>${escapeHtml(step)}</span></button>`;
            })
            .join("");
        return (
            `<form class="training-factor-error-form interactive-form">` +
            `<p class="interactive-instruction">Apasă primul pas în care rezolvarea devine greșită.</p>` +
            `<div class="factor-steps">${steps}</div>` +
            (solved ? "" : `<button type="submit" class="btn btn-press">Verifică răspunsul</button>`) +
            `</form>`
        );
    }

    function factorMatchHtml(question) {
        const solved = isSolved(question);
        const item = question.interactive;
        if (!question.matchValues) question.matchValues = {};
        if (solved) item.pairs.forEach((_, index) => { question.matchValues[index] = index; });
        const left = item.pairs
            .map((pair, index) => {
                const matched = question.matchValues[index];
                return `<button type="button" class="factor-match-card factor-match-card--left${question.activeMatchLeft === index ? " factor-match-card--active" : ""}" data-match-left="${index}"${solved ? " disabled" : ""}><span>${escapeHtml(pair.left)}</span>${matched === undefined ? "" : `<b>${Number(index) + 1}</b>`}</button>`;
            })
            .join("");
        const right = item.right_order
            .map((pairIndex) => {
                const owner = Object.keys(question.matchValues).find((key) => Number(question.matchValues[key]) === pairIndex);
                return `<button type="button" class="factor-match-card factor-match-card--right${owner === undefined ? "" : " factor-match-card--paired"}" data-match-right="${pairIndex}"${solved ? " disabled" : ""}><span>${escapeHtml(item.pairs[pairIndex].right)}</span>${owner === undefined ? "" : `<b>${Number(owner) + 1}</b>`}</button>`;
            })
            .join("");
        return (
            `<form class="training-factor-match-form interactive-form">` +
            `<p class="interactive-instruction">Alege o expresie din stânga, apoi forma ei echivalentă din dreapta.</p>` +
            `<div class="factor-match-board"><div>${left}</div><div>${right}</div></div>` +
            (solved ? "" : `<button type="submit" class="btn btn-press">Verifică perechile</button>`) +
            `</form>`
        );
    }

    function powerInput(key, value, label, solved, className = "power-number-input") {
        return `<input class="${className}" data-answer-key="${escapeHtml(key)}" inputmode="numeric" pattern="[0-9]+" value="${escapeHtml(value || "")}" aria-label="${escapeHtml(label)}"${solved ? " disabled" : ""}>`;
    }

    function powerBuilderHtml(question) {
        const solved = isSolved(question), item = question.interactive;
        if (!question.answerValues) question.answerValues = {};
        if (solved) {
            if (item.mode === "compose") {
                question.answerValues.base = String(item.base);
                question.answerValues.exponent = String(item.exponent);
            } else if (item.mode === "expand") {
                item.factors.forEach((factor, index) => question.answerValues[`factor:${index}`] = String(factor));
            } else {
                question.answerValues[item.missing] = String(item[item.missing]);
            }
        }
        let body = "";
        let instruction = "";
        if (item.mode === "compose") {
            const factors = item.factors.map(factor => `<strong>${escapeHtml(factor)}</strong>`).join("<span>·</span>");
            body = `<div class="power-compose-row"><div class="power-factor-strip">${factors}</div><span>=</span><span class="power-notation">${powerInput("base", question.answerValues.base, "Baza puterii", solved)}<sup>${powerInput("exponent", question.answerValues.exponent, "Exponentul puterii", solved, "power-exponent-input")}</sup></span></div>`;
            instruction = "Scrie produsul sub forma unei puteri.";
        } else if (item.mode === "expand") {
            const factors = item.factors.map((_, index) => powerInput(`factor:${index}`, question.answerValues[`factor:${index}`], `Factorul ${index + 1}`, solved)).join("<span>·</span>");
            body = `<div class="power-compose-row"><strong class="power-display">${escapeHtml(item.base)}<sup>${escapeHtml(item.exponent)}</sup></strong><span>=</span><div class="power-factor-strip">${factors}</div></div>`;
            instruction = "Desfă puterea ca produs de factori egali.";
        } else {
            const base = item.missing === "base" ? powerInput("base", question.answerValues.base, "Baza lipsă", solved) : `<strong>${escapeHtml(item.base)}</strong>`;
            const exponent = item.missing === "exponent" ? powerInput("exponent", question.answerValues.exponent, "Exponentul lipsă", solved, "power-exponent-input") : `<strong>${escapeHtml(item.exponent)}</strong>`;
            const value = item.missing === "value" ? powerInput("value", question.answerValues.value, "Valoarea lipsă", solved) : `<strong>${escapeHtml(item.value)}</strong>`;
            body = `<div class="power-compose-row"><span class="power-notation">${base}<sup>${exponent}</sup></span><span>=</span>${value}</div>`;
            instruction = "Completează caseta astfel încât egalitatea să fie adevărată.";
        }
        return `<form class="training-power-values-form interactive-form"><p class="interactive-instruction">${instruction}</p>${body}${solved ? "" : '<button type="submit" class="btn btn-press">Verifică răspunsul</button>'}</form>`;
    }

    function powerTableHtml(question) {
        const solved = isSolved(question), item = question.interactive;
        if (!question.answerValues) question.answerValues = {};
        if (solved) item.rows.forEach((row, index) => question.answerValues[`${index}:${row.missing}`] = String(row[row.missing]));
        const cells = ["base", "exponent", "value"];
        const labels = {base: "Bază", exponent: "Exponent", value: "Valoare"};
        const rows = item.rows.map((row, index) => `<tr>${cells.map(key => `<td>${key === row.missing ? powerInput(`${index}:${key}`, question.answerValues[`${index}:${key}`], `${labels[key]} lipsă pe rândul ${index + 1}`, solved) : escapeHtml(row[key])}</td>`).join("")}</tr>`).join("");
        return `<form class="training-power-values-form interactive-form"><table class="power-data-table"><thead><tr>${cells.map(key => `<th>${labels[key]}</th>`).join("")}</tr></thead><tbody>${rows}</tbody></table>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică răspunsul</button>'}</form>`;
    }

    function powerCycleHtml(question) {
        const solved = isSolved(question), item = question.interactive;
        if (!question.answerValues) question.answerValues = {};
        if (solved) {
            item.cycle.forEach((digit, index) => question.answerValues[`cycle:${index}`] = String(digit));
            question.answerValues.last_digit = String(item.last_digit);
        }
        const cycle = item.cycle.map((_, index) => `<label class="power-cycle-cell"><span>${escapeHtml(item.base)}<sup>${index + 1}</sup></span>${powerInput(`cycle:${index}`, question.answerValues[`cycle:${index}`], `Ultima cifră pentru puterea ${index + 1}`, solved)}</label>`).join("");
        return `<form class="training-power-values-form interactive-form"><p class="interactive-instruction">Completează ciclul ultimelor cifre, apoi folosește-l pentru puterea cerută.</p><div class="power-cycle">${cycle}</div><div class="power-cycle-target"><span>Ultima cifră a lui ${escapeHtml(item.base)}<sup>${escapeHtml(item.exponent)}</sup> este</span>${powerInput("last_digit", question.answerValues.last_digit, "Ultima cifră", solved)}</div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică răspunsul</button>'}</form>`;
    }

    function powerSquareHtml(question) {
        const solved = isSolved(question), item = question.interactive;
        if (!question.answerValues) question.answerValues = {};
        if (solved) question.answerValues = {base: String(item.side), exponent: "2", value: String(item.value)};
        const cells = Array.from({length: item.value}, () => '<span class="power-square-cell"></span>').join("");
        return `<form class="training-power-values-form interactive-form"><p class="interactive-instruction">Privește pătratul și completează puterea care arată numărul total de pătrățele.</p><div class="power-square-layout"><div class="power-square-grid" style="--power-side:${item.side}">${cells}</div><div class="power-compose-row"><span class="power-notation">${powerInput("base", question.answerValues.base, "Baza", solved)}<sup>${powerInput("exponent", question.answerValues.exponent, "Exponentul", solved, "power-exponent-input")}</sup></span><span>=</span>${powerInput("value", question.answerValues.value, "Numărul de pătrățele", solved)}</div></div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică răspunsul</button>'}</form>`;
    }

    function powerRuleChainHtml(question) {
        const solved = isSolved(question), item = question.interactive;
        if (!question.answerValues) question.answerValues = {};
        if (solved) item.stages.forEach((stage, index) => { question.answerValues[`stage:${index}`] = String(stage.exponent); });
        const stages = item.stages.map((stage, index) =>
            `<div class="power-rule-stage"><span>${escapeHtml(stage.label)}</span><span class="chain-arrow">→</span><span class="power-notation"><strong>${escapeHtml(stage.base)}</strong><sup>${powerInput(`stage:${index}`, question.answerValues[`stage:${index}`], `Exponentul de la pasul ${index + 1}`, solved, "power-exponent-input")}</sup></span></div>`
        ).join("");
        return `<form class="training-power-values-form interactive-form"><p class="power-original-expression">${escapeHtml(item.expression)}</p><p class="interactive-instruction">Completează exponentul obținut la fiecare pas.</p><div class="power-rule-chain">${stages}</div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică răspunsul</button>'}</form>`;
    }

    function powerCompareHtml(question) {
        const solved = isSolved(question), item = question.interactive;
        if (solved) question.selectedRelation = item.relation;
        const buttons = ["<", "=", ">"].map(relation => {
            let classes = "power-relation-button";
            if (relation === question.selectedRelation) classes += " power-relation-button--selected";
            if (solved && relation === item.relation) classes += " power-relation-button--correct";
            if (question.status === "wrong" && relation === question.selectedRelation) classes += " power-relation-button--wrong";
            return `<button type="button" class="${classes}" data-power-relation="${relation}"${solved ? " disabled" : ""}>${relation}</button>`;
        }).join("");
        return `<form class="training-power-compare-form interactive-form"><p class="interactive-instruction">Alege semnul potrivit fără să calculezi inutil numere foarte mari.</p><div class="power-comparison"><strong>${escapeHtml(item.left)}</strong><div class="power-relation-picker">${buttons}</div><strong>${escapeHtml(item.right)}</strong></div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică răspunsul</button>'}</form>`;
    }

    function powerOrderHtml(question) {
        const solved = isSolved(question), item = question.interactive;
        if (!question.orderValues) question.orderValues = [];
        const expected = [...item.items.keys()].sort((a, b) => item.direction === "asc" ? item.items[a].value - item.items[b].value : item.items[b].value - item.items[a].value);
        if (solved) question.orderValues = expected;
        const chosen = new Set(question.orderValues);
        const card = (index, placed) => `<button type="button" class="power-order-card${placed ? " power-order-card--placed" : ""}" data-power-order-index="${index}"${solved ? " disabled" : ""}>${escapeHtml(item.items[index].label)}</button>`;
        const available = item.display_order.filter(index => !chosen.has(index)).map(index => card(index, false)).join("");
        const sign = item.direction === "asc" ? "<" : ">";
        const ordered = question.orderValues.map((index, position) => `${position ? `<span class="power-order-sign">${sign}</span>` : ""}${card(index, true)}`).join("");
        return `<form class="training-power-order-form interactive-form"><p class="interactive-instruction">Apasă puterile în ordine ${item.direction === "asc" ? "crescătoare" : "descrescătoare"}. Apasă o putere așezată pentru a o retrage.</p><div class="power-order-pool">${available || '<span class="power-order-placeholder">Toate puterile au fost așezate.</span>'}</div><div class="power-order-result">${ordered || '<span class="power-order-placeholder">Ordinea construită va apărea aici.</span>'}</div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică ordinea</button>'}</form>`;
    }

    function baseInput(question, key, label, solved, kind = "digits", maxLength = null) {
        const value = question.answerValues[key] || "";
        const pattern = kind === "binary" ? "[01]+" : kind === "text" ? "[A-Za-zĂÂÎȘȚăâîșț]+" : "[0-9]+";
        return `<input class="base-answer-input" data-answer-key="${escapeHtml(key)}" data-input-kind="${kind}" inputmode="${kind === "text" ? "text" : "numeric"}" pattern="${pattern}"${maxLength ? ` maxlength="${maxLength}"` : ""} aria-label="${escapeHtml(label)}" value="${escapeHtml(value)}"${solved ? " disabled" : ""}>`;
    }

    function baseValuesHtml(question) {
        const solved = isSolved(question), item = question.interactive;
        if (!question.answerValues) question.answerValues = {};
        if (solved) Object.entries(item.answers).forEach(([key, value]) => { question.answerValues[key] = String(value); });
        let body = "";
        if (item.mode === "division_ladder") {
            const rows = item.rows.map((row, index) => `<tr><td>${escapeHtml(row.dividend)}</td><td>:</td><td>2</td><td>=</td><td>${baseInput(question, `${index}:quotient`, `Câtul de pe rândul ${index + 1}`, solved)}</td><td>rest</td><td>${baseInput(question, `${index}:remainder`, `Restul de pe rândul ${index + 1}`, solved, "digits", 1)}</td></tr>`).join("");
            body = `<p class="interactive-instruction">Completează câturile și resturile. Numărul binar se obține citind resturile de jos în sus.</p><table class="base-ladder"><tbody>${rows}</tbody></table>`;
        } else if (item.mode === "decompose") {
            const terms = item.terms.map((term, index) => `<div class="base-term-card"><span>${escapeHtml(term.digit)} · ${escapeHtml(item.base)}<sup>${escapeHtml(term.exponent)}</sup></span><span>=</span>${baseInput(question, `${index}:contribution`, `Contribuția termenului ${index + 1}`, solved)}</div>`).join("");
            body = `<div class="base-main-number">${escapeHtml(item.number)}<sub>(${escapeHtml(item.base)})</sub></div><div class="base-terms">${terms}</div>`;
        } else if (item.mode === "compose") {
            const terms = item.terms.map(term => `<span class="base-chip">${escapeHtml(term.label)}</span>`).join('<span class="base-plus">+</span>');
            body = `<p class="interactive-instruction">Calculează suma și scrie numărul în baza ${escapeHtml(item.base)}.</p><div class="base-compose"><div>${terms}</div><span>=</span>${baseInput(question, "number", "Numărul obținut", solved, item.base === 2 ? "binary" : "digits") }<sub>(${escapeHtml(item.base)})</sub></div>`;
        } else if (item.mode === "place_table") {
            const labels = {digit: "Cifră", exponent: "Exponent", contribution: "Contribuție"};
            const rows = item.rows.map((row, index) => `<tr>${["digit", "exponent", "contribution"].map(key => `<td>${row.missing === key ? baseInput(question, `${index}:${key}`, `${labels[key]} lipsă pe rândul ${index + 1}`, solved, "digits", key === "digit" ? 1 : null) : escapeHtml(row[key])}</td>`).join("")}</tr>`).join("");
            body = `<table class="base-place-table"><thead><tr><th>Cifră</th><th>Puterea lui ${escapeHtml(item.base)}</th><th>Contribuție</th></tr></thead><tbody>${rows}</tbody></table>`;
        } else if (item.mode === "missing_digits") {
            const missing = new Set(item.missing_indices);
            const boxes = item.digits.map((digit, index) => missing.has(index) ? baseInput(question, `digit:${index}`, `Cifra lipsă de pe poziția ${index + 1}`, solved, item.base === 2 ? "binary" : "digits", 1) : `<strong>${escapeHtml(digit)}</strong>`).join("");
            body = `<p class="interactive-instruction">Completează cifrele lipsă astfel încât egalitatea să fie adevărată.</p><div class="base-missing-row"><div class="base-digit-strip">${boxes}</div><sub>(${escapeHtml(item.base)})</sub><span>=</span><strong>${escapeHtml(item.decimal)}<sub>(10)</sub></strong></div>`;
        } else if (item.mode === "complete_equality") {
            body = `<div class="base-equality"><strong>${escapeHtml(item.left_value)}<sub>(${escapeHtml(item.left_base)})</sub></strong><span>=</span>${baseInput(question, "value", "Valoarea lipsă", solved, item.answer_base === 2 ? "binary" : "digits")}<sub>(${escapeHtml(item.answer_base)})</sub></div>`;
        } else {
            const boxes = item.items.map((code, index) => `<label class="secret-code-card"><span>${escapeHtml(code.binary)}<sub>(2)</sub></span>${baseInput(question, `letter:${index}`, `Litera pentru codul ${code.binary}`, solved, "text", 1)}</label>`).join("");
            body = `<p class="interactive-instruction">Transformă fiecare cod binar în baza 10, apoi folosește poziția obținută în alfabet.</p><div class="secret-code-board">${boxes}</div>`;
        }
        return `<form class="training-base-values-form interactive-form">${body}${solved ? "" : '<button type="submit" class="btn btn-press">Verifică răspunsul</button>'}</form>`;
    }

    function baseMatchHtml(question) {
        const solved = isSolved(question), item = question.interactive;
        if (!question.matchValues) question.matchValues = {};
        if (solved) item.pairs.forEach((_, index) => { question.matchValues[index] = index; });
        const left = item.pairs.map((pair, index) => `<button type="button" draggable="${solved ? "false" : "true"}" class="factor-match-card base-match-card${question.activeMatchLeft === index ? " factor-match-card--active" : ""}" data-match-left="${index}"${solved ? " disabled" : ""}><span>${escapeHtml(pair.left)}</span><span class="base-drag-handle">⋮⋮</span></button>`).join("");
        const right = item.right_order.map(pairIndex => { const owner = Object.keys(question.matchValues).find(key => Number(question.matchValues[key]) === pairIndex); return `<button type="button" class="factor-match-card base-match-card base-match-drop${owner === undefined ? "" : " factor-match-card--paired"}" data-match-right="${pairIndex}"${solved ? " disabled" : ""}><span>${escapeHtml(item.pairs[pairIndex].right)}</span>${owner === undefined ? "" : `<b>${Number(owner) + 1}</b>`}</button>`; }).join("");
        return `<form class="training-factor-match-form interactive-form"><p class="interactive-instruction">Trage fiecare cartonaș din stânga peste perechea sa. Poți și să le apeși pe rând.</p><div class="factor-match-board"><div>${left}</div><div>${right}</div></div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică perechile</button>'}</form>`;
    }

    function binaryToggleHtml(question) {
        const solved = isSolved(question), item = question.interactive;
        if (!question.answerValues) question.answerValues = {bits: "0".repeat(item.binary.length)};
        if (solved) question.answerValues.bits = item.binary;
        const bits = question.answerValues.bits.padStart(item.binary.length, "0").split("");
        const buttons = bits.map((bit, index) => `<button type="button" class="binary-switch binary-switch--${bit}" data-bit-index="${index}" aria-pressed="${bit === "1"}"${solved ? " disabled" : ""}><span>2<sup>${item.binary.length - index - 1}</sup></span><b>${bit}</b></button>`).join("");
        return `<form class="training-binary-toggle-form interactive-form"><p class="interactive-instruction">Apasă comutatoarele pentru a construi în baza 2 numărul ${escapeHtml(item.decimal)}.</p><div class="binary-switch-board">${buttons}</div><div class="binary-live-value"><strong>${escapeHtml(question.answerValues.bits)}</strong><sub>(2)</sub></div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică răspunsul</button>'}</form>`;
    }

    function unitInput(question, key, label, solved) {
        return `<input class="unit-answer-input" data-unit-key="${escapeHtml(key)}" inputmode="numeric" pattern="[0-9]+" aria-label="${escapeHtml(label)}" value="${escapeHtml(question.answerValues[key] || "")}"${solved ? " disabled" : ""}>`;
    }

    function unitIcons(icon, count, className = "unit-icon-cloud") {
        const visible = Math.min(Math.max(Number(count) || 0, 0), 30);
        return `<div class="${className}" aria-label="${visible} obiecte">${Array.from({length: visible}, () => `<span aria-hidden="true">${escapeHtml(icon || "●")}</span>`).join("")}</div>`;
    }

    function unitRange(question, key, label, min, max, step, fallback, solved) {
        const value = question.answerValues[key] ?? fallback;
        return `<label class="unit-range"><span>${escapeHtml(label)}: <strong data-range-output="${escapeHtml(key)}">${escapeHtml(value)}</strong></span><input type="range" data-unit-range="${escapeHtml(key)}" min="${min}" max="${max}" step="${step}" value="${escapeHtml(value)}"${solved ? " disabled" : ""}></label>`;
    }

    function unitOperationBoard(question, item, nodes, solved) {
        const slots = nodes.map((node, index) => {
            const slot = index < nodes.length - 1
                ? `<button type="button" class="unit-operation-slot${question.answerValues[`operation:${index}`] ? " unit-operation-slot--filled" : ""}" data-operation-slot="${index}"${solved ? " disabled" : ""}>${escapeHtml(question.answerValues[`operation:${index}`] || "trage operația")}</button>`
                : "";
            return `<div class="unit-path-node"><strong>${escapeHtml(node)}</strong>${slot}</div>`;
        }).join("");
        const choices = item.operation_choices.map(operation => `<button type="button" draggable="${solved ? "false" : "true"}" class="unit-operation-chip${question.activeUnitOperation === operation ? " unit-operation-chip--active" : ""}" data-operation-choice="${escapeHtml(operation)}"${solved ? " disabled" : ""}>${escapeHtml(operation)}</button>`).join("");
        return `<div class="unit-operation-palette">${choices}</div><div class="unit-path">${slots}</div>`;
    }

    function unitReductionHtml(question) {
        const solved = isSolved(question), item = question.interactive;
        if (!question.answerValues) question.answerValues = {};
        if (solved) Object.entries(item.answers).forEach(([key, value]) => { question.answerValues[key] = String(value); });
        if (!solved && Object.keys(question.answerValues).length === 0) {
            if (["visual_scale", "balance"].includes(item.mode)) question.answerValues = {quantity: String(item.initial_quantity), value: String(item.initial_value)};
            else if (item.mode === "basket") question.answerValues = {count: "0"};
            else if (item.mode === "faucets") question.answerValues = {count: String(item.initial_count)};
            else if (item.mode === "timeline") question.answerValues = {time: String(item.minimum)};
            else if (item.mode === "speed_simulator") question.answerValues = {time: "0"};
        }
        let body = "";
        if (item.mode === "visual_scale") {
            const quantity = question.answerValues.quantity ?? item.initial_quantity;
            const value = question.answerValues.value ?? item.initial_value;
            const maxQuantity = Math.max(item.initial_quantity, item.target_quantity) * 2;
            const maxValue = Math.max(item.initial_value, item.target_value) * 2;
            body = `<div class="unit-visual-compare"><section><h3>De la</h3>${unitIcons(item.icon, item.initial_quantity)}<strong>${escapeHtml(item.initial_quantity)} ${escapeHtml(item.unit)} → ${escapeHtml(item.initial_value)}</strong></section><span class="unit-big-arrow">→</span><section><h3>La</h3>${unitIcons(item.icon, quantity, "unit-icon-cloud unit-icon-cloud--target")}${unitRange(question, "quantity", "Cantitate", 1, maxQuantity, 1, quantity, solved)}${unitRange(question, "value", "Valoare", 1, maxValue, 1, value, solved)}</section></div>`;
        } else if (item.mode === "unit_path" || item.mode === "operation_drop") {
            const nodes = item.mode === "unit_path" ? item.values.map((value, index) => `${value}${index === 1 ? " unitate" : " unități"}`) : item.nodes;
            body = `<p class="interactive-instruction">Alege sau trage operațiile potrivite în spațiile dintre valori.</p>${unitOperationBoard(question, item, nodes, solved)}`;
            if (item.paired_values) body += `<div class="unit-paired-values">${item.paired_values.map(value => `<span>${escapeHtml(value)} ${escapeHtml(item.unit)}</span>`).join("<b>→</b>")}</div>`;
        } else if (item.mode === "balance") {
            const quantity = question.answerValues.quantity ?? item.initial_quantity;
            const value = question.answerValues.value ?? item.initial_value;
            body = `<div class="unit-balance"><div class="unit-balance__pan"><span>${escapeHtml(item.labels[0])}</span><strong>${escapeHtml(item.initial_quantity)}</strong><small>${escapeHtml(item.initial_value)} ${escapeHtml(item.labels[1])}</small></div><div class="unit-balance__beam"><span>${item.relation === "direct" ? "↗ împreună ↗" : "↗ una, cealaltă ↘"}</span></div><div class="unit-balance__pan">${unitRange(question, "quantity", item.labels[0], 1, Math.max(item.initial_quantity, item.target_quantity) * 2, 1, quantity, solved)}${unitRange(question, "value", item.labels[1], 1, Math.max(item.initial_value, item.target_value) * 2, 1, value, solved)}</div></div>`;
        } else if (item.mode === "basket") {
            const count = Number(question.answerValues.count || 0);
            body = `<div class="unit-basket"><div><p>O bucată costă <strong>${escapeHtml(item.unit_price)} ${escapeHtml(item.currency)}</strong></p>${unitIcons(item.icon, count, "unit-basket-items")}</div><div class="unit-counter"><button type="button" data-unit-counter="-1"${solved ? " disabled" : ""}>−</button><strong data-unit-count>${count}</strong><button type="button" data-unit-counter="1"${solved ? " disabled" : ""}>+</button></div><label>Totalul coșului ${unitInput(question, "total", "Cost total", solved)} ${escapeHtml(item.currency)}</label></div>`;
        } else if (item.mode === "faucets") {
            const count = Number(question.answerValues.count || item.initial_count);
            const maxCount = Math.max(item.initial_count, item.target_count) + 4;
            body = `<div class="unit-faucets"><p>${escapeHtml(item.initial_count)} robinete umplu bazinul în ${escapeHtml(item.initial_time)} ore.</p>${unitIcons(item.icon || "🚰", count, "unit-faucet-row")}<div class="unit-counter"><button type="button" data-unit-counter="-1"${solved ? " disabled" : ""}>−</button><strong data-unit-count>${count}</strong><button type="button" data-unit-counter="1" data-unit-max="${maxCount}"${solved ? " disabled" : ""}>+</button></div><label>Timpul necesar ${unitInput(question, "time", "Număr de ore", solved)} ore</label></div>`;
        } else if (item.mode === "dependency_direction") {
            body = `<div class="unit-change-pair"><span>${escapeHtml(item.first_change)}</span><span>↔</span><span>${escapeHtml(item.second_change)}</span></div><div class="unit-choice-row"><button type="button" data-unit-choice-key="relation" data-unit-choice="direct" class="${question.answerValues.relation === "direct" ? "is-selected" : ""}"${solved ? " disabled" : ""}>Cresc/scad împreună</button><button type="button" data-unit-choice-key="relation" data-unit-choice="inverse" class="${question.answerValues.relation === "inverse" ? "is-selected" : ""}"${solved ? " disabled" : ""}>Una crește, cealaltă scade</button></div>`;
        } else if (item.mode === "unit_table") {
            const rows = item.rows.map((row, index) => `<tr>${item.columns.map(column => `<td>${row.missing === column ? unitInput(question, `${index}:${column}`, `${column} lipsă pe rândul ${index + 1}`, solved) : escapeHtml(row[column])}</td>`).join("")}</tr>`).join("");
            body = `<table class="unit-data-table"><thead><tr>${item.columns.map(column => `<th>${escapeHtml(column)}</th>`).join("")}</tr></thead><tbody>${rows}</tbody></table>`;
        } else if (item.mode === "timeline") {
            body = `<div class="unit-timeline"><span>${escapeHtml(item.initial_label)}</span>${unitRange(question, "time", "Timp", item.minimum, item.maximum, item.step, item.minimum, solved)}<span>${escapeHtml(item.target_label)}</span></div>`;
        } else if (item.mode === "problem_builder") {
            body = `<div class="unit-problem-builder">${item.groups.map((group, groupIndex) => `<section><h3>${escapeHtml(group.label)}</h3>${group.choices.map((choice, choiceIndex) => `<button type="button" data-unit-choice-key="choice:${groupIndex}" data-unit-choice="${choiceIndex}" class="${String(question.answerValues[`choice:${groupIndex}`]) === String(choiceIndex) ? "is-selected" : ""}"${solved ? " disabled" : ""}>${escapeHtml(choice)}</button>`).join("")}</section>`).join("")}</div>`;
        } else if (item.mode === "speed_simulator") {
            const time = Number(question.answerValues.time || 0);
            const distance = Math.min(time * item.speed, item.target_distance);
            body = `<div class="unit-speed"><p>Viteză: <strong>${escapeHtml(item.speed)} unități într-o secundă</strong></p><div class="unit-speed-track"><span style="left:${item.target_distance ? (distance / item.target_distance) * 100 : 0}%">${escapeHtml(item.icon || "🐟")}</span><i></i></div>${unitRange(question, "time", "Timp", 0, item.maximum_time, 1, time, solved)}<p>Distanță parcursă: <strong data-speed-distance>${distance}</strong> / ${escapeHtml(item.target_distance)}</p></div>`;
        } else if (item.mode === "triple_match") {
            const options = (key, answerKey) => (item[`${key}_order`] || item.triples.map((_, index) => index)).map(index => `<option value="${index}"${String(question.answerValues[answerKey]) === String(index) ? " selected" : ""}>${escapeHtml(item.triples[index][key])}</option>`).join("");
            body = `<div class="unit-triple-match">${item.triples.map((triple, index) => `<section><strong>${escapeHtml(triple.problem)}</strong><label>Schemă<select data-unit-select="scheme:${index}"${solved ? " disabled" : ""}><option value="">Alege</option>${options("scheme", `scheme:${index}`)}</select></label><label>Răspuns<select data-unit-select="answer:${index}"${solved ? " disabled" : ""}><option value="">Alege</option>${options("answer", `answer:${index}`)}</select></label></section>`).join("")}</div>`;
        } else {
            body = `<div class="unit-true-false"><span class="unit-tf-icon">${escapeHtml(item.icon || "🔎")}</span><p>${escapeHtml(item.statement)}</p><small>${escapeHtml(item.visual_note)}</small><div class="unit-choice-row"><button type="button" data-unit-choice-key="answer" data-unit-choice="true" class="${question.answerValues.answer === "true" ? "is-selected" : ""}"${solved ? " disabled" : ""}>Adevărat</button><button type="button" data-unit-choice-key="answer" data-unit-choice="false" class="${question.answerValues.answer === "false" ? "is-selected" : ""}"${solved ? " disabled" : ""}>Fals</button></div></div>`;
        }
        return `<form class="training-unit-reduction-form interactive-form">${body}${solved ? "" : '<button type="submit" class="btn btn-press">Verifică răspunsul</button>'}</form>`;
    }

    function comparisonItems(items) {
        return `<div class="comparison-items">${items.map(item => `<span><b>${escapeHtml(item.count)}</b> ${escapeHtml(item.icon || "●")} <small>${escapeHtml(item.name)}</small></span>`).join("")}</div>`;
    }

    function comparisonFields(question, solved) {
        const reserved = new Set(["method", "step", "multiplier", "answer"]);
        const keys = Object.keys(question.interactive.answers).filter(key => !reserved.has(key) && !key.startsWith("scheme:") && !key.startsWith("answer:"));
        return `<div class="comparison-fields">${keys.map(key => `<label>${escapeHtml(key.replaceAll("_", " "))}<input data-comparison-key="${escapeHtml(key)}" inputmode="numeric" value="${escapeHtml(question.answerValues[key] || "")}"${solved ? " disabled" : ""}></label>`).join("")}</div>`;
    }

    function comparisonMethodHtml(question) {
        const solved = isSolved(question), item = question.interactive;
        if (!question.answerValues) question.answerValues = {};
        if (solved) Object.entries(item.answers).forEach(([key, value]) => question.answerValues[key] = String(value));
        const group = data => `<div class="comparison-group">${comparisonItems(data.items || [])}${data.total === undefined ? "" : `<strong>= ${escapeHtml(data.total)}</strong>`}</div>`;
        let body = "";
        if (["balance", "cancel_common", "align_rows", "equalize", "comparison_table"].includes(item.mode)) {
            body = `<div class="comparison-board">${item.rows.map((entry,index) => `<section class="comparison-row"><em>Situația ${index + 1}</em>${comparisonItems(entry.items)}<strong>= ${escapeHtml(entry.total)}</strong></section>`).join("")}<div class="comparison-minus">−</div></div>`;
            if (item.multiplier_choices) body += `<div class="comparison-choice-row">${item.multiplier_choices.map(value => `<button type="button" data-comparison-choice-key="multiplier" data-comparison-choice="${value}" class="${String(question.answerValues.multiplier) === String(value) ? "is-selected" : ""}"${solved ? " disabled" : ""}>× ${value}</button>`).join("")}</div>`;
            body += comparisonFields(question, solved);
        } else if (item.mode === "choose_method") {
            body = `<div class="comparison-situation">${escapeHtml(item.situation)}</div><div class="comparison-choice-row">${[["subtract","Eliminare prin scădere"],["add","Eliminare prin adunare"],["substitute","Înlocuire"]].map(([value,label]) => `<button type="button" data-comparison-choice-key="method" data-comparison-choice="${value}" class="${question.answerValues.method === value ? "is-selected" : ""}"${solved ? " disabled" : ""}>${label}</button>`).join("")}</div>`;
        } else if (item.mode === "substitution_machine") {
            body = `<div class="substitution-equivalence">${group(item.source_group)}<span>⇄</span>${group(item.target_group)}</div><div class="substitution-machine">${group(item.large_row)}<span>⚙️ înlocuiește</span>${group(item.result_row)}</div>${comparisonFields(question, solved)}`;
        } else if (item.mode === "comparison_error") {
            body = `<p class="interactive-instruction">Apasă primul pas greșit.</p><div class="comparison-steps">${item.steps.map((step,index) => `<button type="button" data-comparison-choice-key="step" data-comparison-choice="${index}" class="${String(question.answerValues.step) === String(index) ? "is-selected" : ""}"${solved ? " disabled" : ""}><b>${index + 1}</b>${escapeHtml(step)}</button>`).join("")}</div>`;
        } else if (item.mode === "animal_race") {
            body = `<div class="animal-race"><section><span>${escapeHtml(item.animal_a.icon)}</span><strong>${escapeHtml(item.animal_a.name)}</strong><small>${escapeHtml(item.animal_a.jumps)} sărituri = ${escapeHtml(item.animal_a.distance)} m</small></section><div class="race-track"><i></i><b>perioadă comună: ${escapeHtml(item.common_period)}</b></div><section><span>${escapeHtml(item.animal_b.icon)}</span><strong>${escapeHtml(item.animal_b.name)}</strong><small>${escapeHtml(item.animal_b.jumps)} sărituri = ${escapeHtml(item.animal_b.distance)} m</small></section></div>${comparisonFields(question, solved)}`;
        } else if (item.mode === "dancers") {
            body = `<div class="dancer-stage"><section>${unitIcons("🕺", item.initial_boys)}${unitIcons("💃", item.initial_girls)}<strong>${escapeHtml(item.initial_time)} minute</strong></section><span>→</span><section>${unitIcons("🕺", item.target_boys)}${unitIcons("💃", item.target_girls)}</section></div>${comparisonFields(question, solved)}`;
        } else if (item.mode === "comparison_match") {
            const opts = (key,answerKey) => item[`${key}_order`].map(index => `<option value="${index}"${String(question.answerValues[answerKey]) === String(index) ? " selected" : ""}>${escapeHtml(item.triples[index][key])}</option>`).join("");
            body = `<div class="comparison-match">${item.triples.map((triple,index) => `<section><strong>${escapeHtml(triple.problem)}</strong><label>Comparație<select data-comparison-select="scheme:${index}"${solved ? " disabled" : ""}><option value="">Alege</option>${opts("scheme",`scheme:${index}`)}</select></label><label>Răspuns<select data-comparison-select="answer:${index}"${solved ? " disabled" : ""}><option value="">Alege</option>${opts("answer",`answer:${index}`)}</select></label></section>`).join("")}</div>`;
        } else {
            body = `<div class="comparison-true-false"><span>${escapeHtml(item.icon)}</span><p>${escapeHtml(item.statement)}</p><small>${escapeHtml(item.note)}</small><div class="comparison-choice-row">${[["true","Adevărat"],["false","Fals"]].map(([value,label]) => `<button type="button" data-comparison-choice-key="answer" data-comparison-choice="${value}" class="${question.answerValues.answer === value ? "is-selected" : ""}"${solved ? " disabled" : ""}>${label}</button>`).join("")}</div></div>`;
        }
        return `<form class="training-comparison-form interactive-form">${body}${solved ? "" : '<button type="submit" class="btn btn-press">Verifică răspunsul</button>'}</form>`;
    }

    function figurativeSvg(scheme, activeDifference = true) {
        const small = Math.max(1, Number(scheme.small_parts || 1));
        const large = Math.max(small, Number(scheme.large_parts || small));
        const difference = Number(scheme.difference || 0);
        const unit = 62, start = 112, smallWidth = small * unit, largeWidth = large * unit;
        const maxWidth = 360, scale = Math.min(1, maxWidth / Math.max(largeWidth + (difference ? 72 : 0), 1));
        const w1 = smallWidth * scale, w2 = largeWidth * scale, extra = difference && large === small ? 70 * scale : 0;
        const parts = (count, y) => Array.from({length: count}, (_, i) => `<rect x="${start + i * unit * scale}" y="${y}" width="${unit * scale}" height="34" rx="5" class="figurative-part"></rect>`).join("");
        return `<svg class="figurative-svg" viewBox="0 0 560 150" role="img" aria-label="Reprezentare prin segmente">
            <text x="8" y="48">${escapeHtml(scheme.small_label || "numărul mic")}</text>${parts(small, 24)}
            <text x="8" y="108">${escapeHtml(scheme.large_label || "numărul mare")}</text>${parts(large, 84)}
            ${difference && large === small ? `<rect x="${start + w2}" y="84" width="${extra}" height="34" rx="5" class="figurative-difference${activeDifference ? "" : " is-removed"}"></rect><text x="${start + w2 + extra / 2}" y="107" text-anchor="middle">+${escapeHtml(difference)}</text>` : ""}
            ${difference && large > small ? `<path d="M ${start + w1} 75 v-7 h ${w2 - w1} v7" class="figurative-brace figurative-difference${activeDifference ? "" : " is-removed"}"></path><text x="${start + w1 + (w2-w1)/2}" y="62" text-anchor="middle">${escapeHtml(difference)}</text>` : ""}
            ${scheme.total !== null && scheme.total !== undefined ? `<path d="M ${start} 140 v6 h ${Math.max(w2 + extra, w1)} v-6" class="figurative-brace"></path><text x="${start + Math.max(w2 + extra, w1) / 2}" y="148" text-anchor="middle">${escapeHtml(scheme.total)}</text>` : ""}
        </svg>`;
    }

    function figurativeFields(question, solved, excluded = []) {
        const skip = new Set(excluded);
        return `<div class="figurative-fields">${Object.keys(question.interactive.answers).filter(key => !skip.has(key)).map(key => `<label>${escapeHtml(key.replaceAll("_", " ").replaceAll(":", " "))}<input data-figurative-key="${escapeHtml(key)}" inputmode="numeric" value="${escapeHtml(question.answerValues[key] ?? "")}"${solved ? " disabled" : ""}></label>`).join("")}</div>`;
    }

    function figurativeChoice(question, key, values, solved, labels = null) {
        return `<div class="figurative-choice-row">${values.map((value, index) => `<button type="button" data-figurative-choice-key="${escapeHtml(key)}" data-figurative-choice="${escapeHtml(value)}" class="${String(question.answerValues[key]) === String(value) ? "is-selected" : ""}"${solved ? " disabled" : ""}>${escapeHtml(labels ? labels[index] : value)}</button>`).join("")}</div>`;
    }

    function figurativeMethodHtml(question) {
        const solved = isSolved(question), item = question.interactive;
        if (!question.answerValues) question.answerValues = {};
        if (solved) Object.entries(item.answers).forEach(([key, value]) => { question.answerValues[key] = String(value); });
        let body = "";
        if (["choose_scheme", "equivalent_schemes"].includes(item.mode)) {
            body = `<p class="interactive-instruction">${item.mode === "choose_scheme" ? "Alege desenul corect." : "Alege cele două desene echivalente."}</p><div class="figurative-scheme-grid">${item.schemes.map((scheme, index) => `<button type="button" data-figurative-scheme="${index}" class="${Object.values(question.answerValues).includes(String(index)) ? "is-selected" : ""}"${solved ? " disabled" : ""}><b>${String.fromCharCode(65 + index)}</b>${figurativeSvg(scheme)}</button>`).join("")}</div>`;
        } else if (item.mode === "build_segments") {
            const preview = {...item.scheme, small_parts:Number(question.answerValues.small_parts || 1), large_parts:Number(question.answerValues.large_parts || 1), difference:Number(question.answerValues.difference || 0)};
            body = `${figurativeSvg(preview)}<p class="interactive-instruction">Construiește desenul alegând numărul de părți și diferența.</p><label>bara mică${figurativeChoice(question,"small_parts",[1,2,3],solved)}</label><label>bara mare${figurativeChoice(question,"large_parts",[1,2,3,4,5],solved)}</label><label>diferența${figurativeChoice(question,"difference",[0,item.scheme.difference || 0,14,19,28].filter((v,i,a)=>a.indexOf(v)===i),solved)}</label>`;
        } else if (item.mode === "divide_segments") {
            const value = Number(question.answerValues.parts || 1);
            body = `${figurativeSvg({...item.scheme, small_parts:1, large_parts:value, difference:0})}<label class="figurative-slider">Număr de părți: <strong>${value}</strong><input type="range" min="1" max="${item.maximum}" value="${value}" data-figurative-range="parts"${solved ? " disabled" : ""}></label>`;
        } else if (item.mode === "order_steps") {
            const options = position => item.steps.map((step,index) => `<option value="${index}"${String(question.answerValues[`position:${position}`]) === String(index) ? " selected" : ""}>${escapeHtml(step)}</option>`).join("");
            body = `${figurativeSvg(item.scheme)}<div class="figurative-order">${item.steps.map((_,position) => `<label><b>${position + 1}</b><select data-figurative-select="position:${position}"${solved ? " disabled" : ""}><option value="">Alege pasul</option>${options(position)}</select></label>`).join("")}</div>`;
        } else if (item.mode === "animate_difference") {
            const removed = Number(question.answerValues.removed || 0), remaining = Number(question.answerValues.remaining || 0);
            body = `${figurativeSvg(item.scheme, removed !== Number(item.scheme.difference))}<label class="figurative-slider">Diferență eliminată: <strong>${removed}</strong><input type="range" min="0" max="${item.scheme.difference}" value="${removed}" data-figurative-range="removed"${solved ? " disabled" : ""}></label><label>Ce sumă rămâne?<input data-figurative-key="remaining" inputmode="numeric" value="${remaining || ""}"${solved ? " disabled" : ""}></label>`;
        } else if (item.mode === "repair_scheme") {
            body = `${figurativeSvg(item.scheme)}<p class="interactive-instruction">Alege valoarea care repară desenul.</p>${figurativeChoice(question,"repair",item.choices,solved)}`;
        } else if (item.mode === "figurative_true_false") {
            body = `${figurativeSvg(item.scheme)}<p class="figurative-statement">${escapeHtml(item.statement)}</p>${figurativeChoice(question,"answer",["true","false"],solved,["Adevărat","Fals"])}`;
        } else if (item.mode === "remainder_slider") {
            const value = Number(question.answerValues.remainder || 0);
            body = `${figurativeSvg({...item.scheme,difference:value})}<label class="figurative-slider">Rest: <strong>${value}</strong><input type="range" min="0" max="${item.maximum}" value="${value}" data-figurative-range="remainder"${solved ? " disabled" : ""}></label>`;
        } else if (item.mode === "no_solution") {
            body = `${figurativeSvg(item.scheme)}<p class="interactive-instruction">${escapeHtml(item.note)}</p>${figurativeChoice(question,"possible",["yes","no"],solved,["Are soluție","Nu are soluție"])}`;
        } else if (item.mode === "benches") {
            body = `<div class="figurative-benches"><div>${Array.from({length:Math.min(item.occupied,12)},()=>`<span>🪑<i>${"●".repeat(item.students_per_bench)}</i></span>`).join("")}</div><p>${escapeHtml(item.occupied)} bănci ocupate · ${escapeHtml(item.free)} libere · ${escapeHtml(item.students_per_bench)} elevi/bancă</p></div>${figurativeFields(question,solved)}`;
        } else {
            body = `${figurativeSvg(item.scheme)}<p class="interactive-instruction">Completează toate etapele desenului.</p>${figurativeFields(question,solved)}`;
        }
        return `<form class="training-figurative-form interactive-form">${body}${solved ? "" : '<button type="submit" class="btn btn-press">Verifică răspunsul</button>'}</form>`;
    }

    function reverseOpLabel(operation) {
        return `${operation.op}${operation.value}`.replace("*","×").replace("/",":");
    }

    function reverseChainHtml(item, backward = false, values = {}) {
        const operations = backward ? (item.inverse_operations || []) : (item.operations || []);
        const knownNodes = backward ? (item.reverse_nodes || []) : (item.nodes || []);
        const nodes = operations.map((_,index) => {
            const key = `node:${index}`, shown = backward ? values[key] : knownNodes[index + 1];
            return `<span class="reverse-node">${escapeHtml(shown ?? "?")}</span>`;
        });
        let html = `<span class="reverse-node reverse-node--edge">${escapeHtml(backward ? item.end : item.start)}</span>`;
        operations.forEach((operation,index) => { html += `<span class="reverse-arrow${backward ? " is-backward" : ""}"><i>${backward ? "←" : "→"}</i><b>${escapeHtml(reverseOpLabel(operation))}</b></span>${nodes[index]}`; });
        return `<div class="reverse-chain">${html}</div>`;
    }

    function reverseFields(question, solved, keys = null) {
        const selected = keys || Object.keys(question.interactive.answers);
        return `<div class="reverse-fields">${selected.map(key => `<label>${escapeHtml(key.replaceAll(":"," ").replaceAll("_"," "))}<input data-reverse-key="${escapeHtml(key)}" value="${escapeHtml(question.answerValues[key] ?? "")}"${key.startsWith("op:") ? "" : ' inputmode="numeric"'}${solved ? " disabled" : ""}></label>`).join("")}</div>`;
    }

    function reverseChoices(question, key, choices, solved) {
        return `<div class="reverse-choice-row">${choices.map((choice,index) => { const value=typeof choice === "object" ? choice.value : choice, label=typeof choice === "object" ? choice.label : choice; return `<button type="button" data-reverse-choice-key="${escapeHtml(key)}" data-reverse-choice="${escapeHtml(value)}" class="${String(question.answerValues[key])===String(value)?"is-selected":""}"${solved?" disabled":""}>${escapeHtml(label)}</button>`; }).join("")}</div>`;
    }

    function reverseMethodHtml(question) {
        const solved=isSolved(question), item=question.interactive;
        if (!question.answerValues) question.answerValues={};
        if (solved) Object.entries(item.answers).forEach(([key,value])=>{ question.answerValues[key]=String(value); });
        let body="";
        if (item.mode === "build_reverse_path" || item.mode === "time_machine") {
            body=`${reverseChainHtml(item,false)}<div class="reverse-turn">${item.icon||"↩"} Pornim de la rezultat</div>${reverseChainHtml(item,true,question.answerValues)}${reverseFields(question,solved)}`;
        } else if (item.mode === "drag_inverse_ops") {
            const choices=item.operation_pool || item.inverse_operations.map(reverseOpLabel);
            const used=new Set(Object.values(question.answerValues));
            const card=value=>`<button type="button" draggable="true" data-reverse-drag-card="${escapeHtml(value)}"${solved?" disabled":""}>${escapeHtml(value)}</button>`;
            body=`${reverseChainHtml(item,false)}<p class="interactive-instruction">Trage cartonașele în drumul invers. Poți și apăsa un cartonaș, apoi un loc.</p><div class="reverse-drag-pool">${choices.filter(value=>!used.has(value)).map(card).join("")||"Toate operațiile sunt așezate."}</div><div class="reverse-drop-path">${item.inverse_operations.map((_,index)=>{const key=`op:${index}`,value=question.answerValues[key];return `<span>←</span><button type="button" data-reverse-drop="${key}" class="${value?"is-filled":""}"${solved?" disabled":""}>${value?escapeHtml(value):"Trage aici"}</button>`;}).join("")}</div>`;
        } else if (item.mode === "reverse_arrows") {
            body=`${reverseChainHtml(item,question.answerValues.direction==="reverse")}<p class="interactive-instruction">Întoarce sensul, apoi completează operațiile inverse.</p>${reverseChoices(question,"direction",[{value:"reverse",label:"Întoarce săgețile"},{value:"forward",label:"Păstrează sensul"}],solved)}${reverseFields(question,solved,Object.keys(item.answers).filter(k=>k.startsWith("op:")))}`;
        } else if (item.mode === "pair_inverse") {
            const rights=item.pairs.map(pair=>pair.right);
            body=`<div class="reverse-pairs">${item.pairs.map((pair,index)=>`<label><strong>${escapeHtml(pair.left)}</strong><span>↔</span><select data-reverse-select="pair:${index}"${solved?" disabled":""}><option value="">Alege inversa</option>${rights.map(value=>`<option value="${escapeHtml(value)}"${question.answerValues[`pair:${index}`]===value?" selected":""}>${escapeHtml(value)}</option>`).join("")}</select></label>`).join("")}</div>`;
        } else if (item.mode === "order_reverse") {
            body=`${reverseChainHtml(item,false)}<div class="reverse-order">${item.steps.map((_,position)=>`<label><b>${position+1}</b><select data-reverse-select="position:${position}"${solved?" disabled":""}><option value="">Alege pasul</option>${item.steps.map((step,index)=>`<option value="${index}"${String(question.answerValues[`position:${position}`])===String(index)?" selected":""}>${escapeHtml(step)}</option>`).join("")}</select></label>`).join("")}</div>`;
        } else if (item.mode === "reverse_error") {
            body=`${reverseChainHtml(item,false)}<p class="interactive-instruction">Apasă primul pas greșit.</p><div class="reverse-step-list">${item.shown_steps.map((step,index)=>`<button type="button" data-reverse-choice-key="step" data-reverse-choice="${index}" class="${String(question.answerValues.step)===String(index)?"is-selected":""}"${solved?" disabled":""}><b>${index+1}</b>${escapeHtml(step)}</button>`).join("")}</div>`;
        } else if (item.mode === "repair_chain") {
            body=`${reverseChainHtml(item,false)}<p class="interactive-instruction">Înlocuiește operația defectă.</p>${reverseChoices(question,"repair",item.choices,solved)}`;
        } else if (item.mode === "start_slider") {
            const start=Number(question.answerValues.start ?? 0); let value=start;
            (item.operations||[]).forEach(operation=>{ if(operation.op==="+")value+=operation.value;else if(operation.op==="-")value-=operation.value;else if(operation.op==="*")value*=operation.value;else value=value/operation.value; });
            body=`<label class="reverse-slider">Număr inițial: <strong>${start}</strong><input type="range" min="0" max="${item.maximum}" value="${start}" data-reverse-range="start"${solved?" disabled":""}></label><div class="reverse-live-result">Rezultat obținut: <strong>${escapeHtml(Number.isInteger(value)?value:value.toFixed(2))}</strong> · țintă: ${escapeHtml(item.end)}</div>${reverseChainHtml({...item,start},false)}`;
        } else if (["candies","water_transfer","reverse_table"].includes(item.mode)) {
            const icon=item.icon || (item.mode==="water_transfer"?"🛢️":"📋");
            body=`<div class="reverse-story-board"><span>${icon}</span>${item.stages.map((stage,index)=>`<div><small>${escapeHtml(stage.label)}</small>${index===0?`<strong>${escapeHtml(stage.value)}</strong>`:`<input data-reverse-key="stage:${index}" inputmode="numeric" value="${escapeHtml(question.answerValues[`stage:${index}`]??"")}"${solved?" disabled":""}>`}</div>`).join('<i>←</i>')}</div>`;
        } else if (item.mode === "choose_story") {
            body=`${reverseChainHtml(item,false)}<p class="interactive-instruction">Care enunț descrie exact traseul?</p><div class="reverse-story-choices">${item.stories.map((story,index)=>`<button type="button" data-reverse-choice-key="story" data-reverse-choice="${index}" class="${String(question.answerValues.story)===String(index)?"is-selected":""}"${solved?" disabled":""}>${escapeHtml(story)}</button>`).join("")}</div>`;
        } else if (item.mode === "full_reverse_puzzle") {
            body=`${reverseChainHtml(item,false)}<div class="reverse-turn">Construiește întregul drum înapoi</div>${reverseChainHtml(item,true,question.answerValues)}${reverseFields(question,solved)}`;
        } else {
            body=`${reverseChainHtml(item,false)}<div class="reverse-round-trip">Dus <span>→</span> Întors <span>←</span></div>${reverseFields(question,solved,["initial","final"])}${reverseChoices(question,"verified",[{value:"yes",label:"Drumul revine la început"},{value:"no",label:"Nu revine"}],solved)}`;
        }
        return `<form class="training-reverse-form interactive-form">${body}${solved?"":'<button type="submit" class="btn btn-press">Verifică răspunsul</button>'}</form>`;
    }

    function hypothesisBoard(scenario, highCount = 0) {
        const shown=Math.min(scenario.count,24), lowIcon=scenario.icons?.[0]||"●", highIcon=scenario.icons?.[1]||"◆";
        return `<div class="hypothesis-board"><div class="hypothesis-icons">${Array.from({length:shown},(_,index)=>`<span class="${index<highCount?"is-high":""}">${escapeHtml(index<highCount?highIcon:lowIcon)}</span>`).join("")}${scenario.count>shown?`<b>+${scenario.count-shown}</b>`:""}</div><p><strong>${escapeHtml(scenario.count)}</strong> obiecte · total real <strong>${escapeHtml(scenario.total)} ${escapeHtml(scenario.unit)}</strong></p></div>`;
    }

    function hypothesisFields(question,solved,keys=null){
        const selected=keys||Object.keys(question.interactive.answers).filter(key=>key!=="verified");
        return `<div class="hypothesis-fields">${selected.map(key=>`<label>${escapeHtml(key.replaceAll("_"," "))}<input data-hypothesis-key="${escapeHtml(key)}" inputmode="numeric" value="${escapeHtml(question.answerValues[key]??"")}"${solved?" disabled":""}></label>`).join("")}</div>`;
    }

    function hypothesisChoices(question,key,choices,solved){
        return `<div class="hypothesis-choices">${choices.map(choice=>{const value=typeof choice==="object"?choice.value:choice,label=typeof choice==="object"?choice.label:choice;return `<button type="button" data-hypothesis-choice-key="${escapeHtml(key)}" data-hypothesis-choice="${escapeHtml(value)}" class="${String(question.answerValues[key])===String(value)?"is-selected":""}"${solved?" disabled":""}>${escapeHtml(label)}</button>`;}).join("")}</div>`;
    }

    function falseHypothesisHtml(question){
        const solved=isSolved(question),item=question.interactive,s=item.scenario;
        if(!question.answerValues)question.answerValues={};
        if(solved)Object.entries(item.answers).forEach(([key,value])=>{question.answerValues[key]=String(value);});
        let body="";
        if(item.mode==="choose_hypothesis"){
            body=`${hypothesisBoard(s)}<p class="interactive-instruction">Cu ce tip presupunem că sunt toate obiectele?</p>${hypothesisChoices(question,"hypothesis",[{value:"low",label:`Toate: ${s.low_name} (${s.low})`},{value:"high",label:`Toate: ${s.high_name} (${s.high})`}],solved)}`;
        }else if(item.mode==="all_same_simulator"){
            const value=Number(question.answerValues.assumed_total??0);
            body=`${hypothesisBoard(s)}<div class="hypothesis-equation">${escapeHtml(s.count)} × ${escapeHtml(s.low)} = ${value||"?"}</div>${hypothesisFields(question,solved)}`;
        }else if(item.mode==="mismatch_meter"){
            const mismatch=Number(question.answerValues.mismatch??0),max=Math.max(Math.abs(s.mismatch),1);
            body=`${hypothesisBoard(s)}<div class="hypothesis-meter"><span style="width:${Math.min(100,Math.abs(mismatch)/max*100)}%"></span></div><p>Real: ${escapeHtml(s.total)} · ipotetic: ${escapeHtml(s.assumed_total)}</p>${hypothesisFields(question,solved)}`;
        }else if(item.mode==="replacement_count"){
            body=`${hypothesisBoard(s,Number(question.answerValues.replacements??0))}<p class="interactive-instruction">Află cât schimbă o înlocuire și câte înlocuiri sunt necesare.</p>${hypothesisFields(question,solved)}`;
        }else if(["heads_legs","score_cards","containers","money_notes","bees_flowers","shares","vases"].includes(item.mode)){
            body=`${hypothesisBoard(s,Number(question.answerValues.high_count??0))}<div class="hypothesis-legend"><span>${escapeHtml(s.icons[0])} ${escapeHtml(s.low_name)} = ${escapeHtml(s.low)}</span><span>${escapeHtml(s.icons[1])} ${escapeHtml(s.high_name)} = ${escapeHtml(s.high)}</span></div>${hypothesisFields(question,solved)}`;
        }else if(item.mode==="hypothesis_error"){
            body=`${hypothesisBoard(s)}<p class="interactive-instruction">Apasă primul pas greșit.</p><div class="hypothesis-steps">${item.steps.map((step,index)=>`<button type="button" data-hypothesis-choice-key="step" data-hypothesis-choice="${index}" class="${String(question.answerValues.step)===String(index)?"is-selected":""}"${solved?" disabled":""}><b>${index+1}</b>${escapeHtml(step)}</button>`).join("")}</div>`;
        }else if(item.mode==="hypothesis_table"){
            body=`${hypothesisBoard(s)}<div class="hypothesis-table"><div><b>Ipoteză</b><span>${escapeHtml(s.count)} × ${escapeHtml(s.low)}</span></div><div><b>Nepotrivire</b><span>${escapeHtml(s.total)} − ipoteză</span></div><div><b>Înlocuiri</b><span>nepotrivire : ${escapeHtml(s.high-s.low)}</span></div></div>${hypothesisFields(question,solved)}`;
        }else if(item.mode==="full_hypothesis_puzzle"){
            body=`${hypothesisBoard(s,Number(question.answerValues.high_count??0))}<div class="hypothesis-flow"><span>Ipoteză</span><i>→</i><span>Nepotrivire</span><i>→</i><span>Înlocuiri</span><i>→</i><span>Soluție</span></div>${hypothesisFields(question,solved)}`;
        }else{
            body=`${hypothesisBoard(s,Number(question.answerValues.high_count??0))}<p class="interactive-instruction">Completează soluția și verifică totalul real.</p>${hypothesisFields(question,solved,["high_count","low_count","verified_total"])}${hypothesisChoices(question,"verified",[{value:"yes",label:"Verificarea este corectă"},{value:"no",label:"Verificarea este greșită"}],solved)}`;
        }
        return `<form class="training-hypothesis-form interactive-form">${body}${solved?"":'<button type="submit" class="btn btn-press">Verifică răspunsul</button>'}</form>`;
    }

    function operationSequenceHtml(question) {
        const solved = isSolved(question), item = question.interactive;
        if (!question.operationOrder) question.operationOrder = [];
        if (solved) question.operationOrder = [...item.correct_order];
        const chosen = new Set(question.operationOrder);
        const card = (index, placed) => `<button type="button" class="operation-sequence-card${placed ? " operation-sequence-card--placed" : ""}" data-operation-step="${index}"${solved ? " disabled" : ""}>${placed ? `<b>${question.operationOrder.indexOf(index) + 1}</b>` : ""}<span>${escapeHtml(item.steps[index])}</span></button>`;
        const pool = item.display_order.filter(index => !chosen.has(index)).map(index => card(index, false)).join("");
        const result = question.operationOrder.map((index, position) => `${position ? '<span class="operation-sequence-arrow">→</span>' : ""}${card(index, true)}`).join("");
        return `<form class="training-operation-sequence-form interactive-form"><p class="operation-main-expression">${escapeHtml(item.expression)}</p><p class="interactive-instruction">Apasă calculele în ordinea în care trebuie efectuate. Apasă un calcul așezat pentru a-l retrage.</p><div class="operation-sequence-pool">${pool || '<span class="operation-placeholder">Toate calculele au fost așezate.</span>'}</div><div class="operation-sequence-result">${result || '<span class="operation-placeholder">Ordinea construită va apărea aici.</span>'}</div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică ordinea</button>'}</form>`;
    }

    function operationWorkbenchHtml(question) {
        const solved = isSolved(question), item = question.interactive;
        if (!question.answerValues) question.answerValues = {};
        if (solved) item.stages.forEach((stage, index) => { question.answerValues[`stage:${index}`] = String(stage.answer); });
        const stages = item.stages.map((stage, index) => `<div class="operation-workbench-stage"><b>${index + 1}</b><span>${escapeHtml(stage.expression)}</span><span>=</span>${powerInput(`stage:${index}`, question.answerValues[`stage:${index}`], `Rezultatul etapei ${index + 1}`, solved)}</div>`).join("");
        return `<form class="training-operation-workbench-form interactive-form"><p class="operation-main-expression">${escapeHtml(item.expression)}</p><p class="interactive-instruction">Completează rezultatele intermediare în ordinea corectă.</p><div class="operation-workbench">${stages}</div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică rezultatele</button>'}</form>`;
    }

    function divisibilityInput(question, key, label, solved, wide = false) {
        return `<input class="divisibility-input${wide ? " divisibility-input--wide" : ""}" data-divisibility-key="${escapeHtml(key)}" inputmode="numeric" aria-label="${escapeHtml(label)}" value="${escapeHtml(question.answerValues[key] || "")}"${solved ? " disabled" : ""}>`;
    }

    function divisibilityValuesHtml(question) {
        const solved = isSolved(question), item = question.interactive;
        if (!question.answerValues) question.answerValues = {};
        if (solved) Object.entries(item.answers).forEach(([key, value]) => { question.answerValues[key] = String(value); });
        let body = "";
        if (item.mode === "relation") {
            const token = key => item.missing === key ? divisibilityInput(question, key, `${key} lipsă`, solved) : `<strong>${escapeHtml(item[key])}</strong>`;
            body = `<p class="interactive-instruction">Completează numărul lipsă astfel încât produsul să fie corect.</p><div class="divisibility-relation">${token("a")}<span>=</span>${token("b")}<span>·</span>${token("c")}</div>`;
        } else if (item.mode === "factor_pairs") {
            const pairs = item.pairs.map((pair, index) => `<div class="factor-pair-row">${divisibilityInput(question, `pair:${index}:left`, `Primul factor din perechea ${index + 1}`, solved)}<span>·</span>${divisibilityInput(question, `pair:${index}:right`, `Al doilea factor din perechea ${index + 1}`, solved)}<span>= ${escapeHtml(item.number)}</span></div>`).join("");
            body = `<p class="interactive-instruction">Scrie toate perechile de factori, în ordine crescătoare după primul număr.</p><div class="factor-pair-board">${pairs}</div>`;
        } else if (item.mode === "divisor_list") {
            body = `<div class="divisor-factory"><strong>${escapeHtml(item.number)}</strong><span>→</span>${divisibilityInput(question, "list", `Toți divizorii lui ${item.number}`, solved, true)}</div><p class="interactive-instruction">Scrie divizorii în ordine crescătoare, separați prin virgulă.</p>`;
        } else if (item.mode === "greatest_common") {
            body = `<div class="common-divisor-lists"><section><b>Divizorii lui ${escapeHtml(item.a)}</b><span>${escapeHtml(item.divisors_a.join(", "))}</span></section><section><b>Divizorii lui ${escapeHtml(item.b)}</b><span>${escapeHtml(item.divisors_b.join(", "))}</span></section></div><div class="greatest-common-answer"><span>Cel mai mare divizor comun:</span>${divisibilityInput(question, "greatest", "Cel mai mare divizor comun", solved)}</div>`;
        } else if (["sequence", "dual_sequence"].includes(item.mode)) {
            const rows = item.rows.map((row, rowIndex) => `<div class="multiple-sequence-row"><b>${escapeHtml(row.label)}</b>${row.items.map((value, index) => typeof value === "object" ? divisibilityInput(question, value.key, `Termenul lipsă ${index + 1} de pe rândul ${rowIndex + 1}`, solved) : `<span>${escapeHtml(value)}</span>`).join('<i>→</i>')}</div>`).join("");
            body = `<p class="interactive-instruction">Completează termenii lipsă din șirurile de multipli.</p><div class="multiple-sequences">${rows}</div>`;
        } else if (item.mode === "timeline") {
            const ticks = Array.from({length: item.count * 2}, (_, index) => `<span>${(index + 1) * Math.min(item.a, item.b)}</span>`).join("");
            body = `<div class="divisibility-timeline"><div class="timeline-track timeline-track--a"><b>din ${escapeHtml(item.a)} în ${escapeHtml(item.a)}</b></div><div class="timeline-track timeline-track--b"><b>din ${escapeHtml(item.b)} în ${escapeHtml(item.b)}</b></div><div class="timeline-ticks">${ticks}</div></div><label class="timeline-answer">Momente comune:${divisibilityInput(question, "moments", "Momentele comune", solved, true)}</label><p class="interactive-instruction">Scrie momentele în ordine, separate prin virgulă.</p>`;
        } else if (item.mode === "digit_sum") {
            const digits = String(item.number).split("").map(digit => `<span>${escapeHtml(digit)}</span>`).join('<i>+</i>');
            body = `<p class="interactive-instruction">Adună cifrele pentru a aplica criteriul de divizibilitate cu ${escapeHtml(item.criterion)}.</p><div class="digit-sum-strip">${digits}<i>=</i>${divisibilityInput(question, "sum", "Suma cifrelor", solved)}</div>`;
        } else {
            body = `<div class="first-common-board"><div><b>Multiplii lui ${escapeHtml(item.a)}</b><span>${escapeHtml(item.multiples_a.join(", "))}</span></div><div><b>Multiplii lui ${escapeHtml(item.b)}</b><span>${escapeHtml(item.multiples_b.join(", "))}</span></div></div><label class="greatest-common-answer"><span>Primul multiplu comun:</span>${divisibilityInput(question, "first", "Primul multiplu comun", solved)}</label>`;
        }
        return `<form class="training-divisibility-values-form interactive-form">${body}${solved ? "" : '<button type="submit" class="btn btn-press">Verifică răspunsul</button>'}</form>`;
    }

    function divisibilitySelectHtml(question) {
        const solved = isSolved(question), item = question.interactive;
        if (!question.selectedDivisibilityIds) question.selectedDivisibilityIds = [];
        if (solved) question.selectedDivisibilityIds = [...item.correct_ids];
        const selected = new Set(question.selectedDivisibilityIds);
        const cards = item.cards.map(card => `<button type="button" class="divisibility-choice-card${selected.has(card.id) ? " is-selected" : ""}" data-divisibility-card="${escapeHtml(card.id)}" aria-pressed="${selected.has(card.id)}"${solved ? " disabled" : ""}>${escapeHtml(card.label)}</button>`).join("");
        const instruction = item.mode === "role" ? "Alege toate denumirile corecte pentru numerele evidențiate." : item.mode === "bingo" ? "Găsește toate căsuțele care respectă condiția." : item.mode === "digits" ? "Selectează toate cifrele care fac numărul să respecte criteriul." : item.mode === "criteria" ? "Selectează toate numerele care respectă criteriul cerut." : `Selectează toți ${item.mode === "divisors" ? "divizorii" : "multiplii"}.`;
        return `<form class="training-divisibility-select-form interactive-form"><p class="interactive-instruction">${instruction}</p><div class="divisibility-card-grid${item.mode === "bingo" ? " divisibility-card-grid--bingo" : ""}">${cards}</div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică selecția</button>'}</form>`;
    }

    function divisibilitySortHtml(question) {
        const solved = isSolved(question), item = question.interactive;
        if (!question.divisibilityPlacements) question.divisibilityPlacements = {};
        if (solved) item.cards.forEach(card => { question.divisibilityPlacements[card.id] = card.zone; });
        const placed = question.divisibilityPlacements;
        const cardHtml = card => `<button type="button" draggable="${solved ? "false" : "true"}" class="divisibility-sort-card${question.activeDivisibilityCard === card.id ? " is-active" : ""}" data-sort-card="${escapeHtml(card.id)}"${solved ? " disabled" : ""}>${escapeHtml(card.label)}</button>`;
        const pool = item.cards.filter(card => !placed[card.id]).map(cardHtml).join("");
        const zones = item.zones.map(zone => `<section class="divisibility-zone${item.mode === "venn" ? " divisibility-zone--venn" : ""}" data-sort-zone="${escapeHtml(zone.id)}"><h3>${escapeHtml(zone.label)}</h3><div>${item.cards.filter(card => placed[card.id] === zone.id).map(cardHtml).join("") || '<span class="divisibility-zone-placeholder">Trage aici</span>'}</div></section>`).join("");
        return `<form class="training-divisibility-sort-form interactive-form"><p class="interactive-instruction">Trage cartonașele în zona corectă. Le poți și selecta, apoi apăsa zona.</p><div class="divisibility-sort-pool">${pool || '<span>Toate cartonașele sunt așezate.</span>'}</div><div class="divisibility-zones">${zones}</div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică sortarea</button>'}</form>`;
    }

    function criteriaTableHtml(question) {
        const solved = isSolved(question), item = question.interactive;
        if (!question.criteriaValues) question.criteriaValues = {};
        if (solved) Object.entries(item.answers).forEach(([key, value]) => { question.criteriaValues[key] = Boolean(value); });
        const rows = item.divisors.map((divisor, row) => `<tr><th>divizibil cu ${escapeHtml(divisor)}</th>${item.numbers.map((number, column) => { const key = `${row}:${column}`, checked = Boolean(question.criteriaValues[key]); return `<td><button type="button" class="criteria-check${checked ? " is-checked" : ""}" data-criteria-key="${key}" aria-pressed="${checked}" aria-label="${number} divizibil cu ${divisor}"${solved ? " disabled" : ""}>${checked ? "✓" : "×"}</button></td>`; }).join("")}</tr>`).join("");
        return `<form class="training-criteria-table-form interactive-form"><p class="interactive-instruction">Apasă fiecare căsuță pentru a alege ✓ sau ×.</p><div class="criteria-table-wrap"><table class="criteria-table"><thead><tr><th>Numărul</th>${item.numbers.map(number => `<th>${escapeHtml(number)}</th>`).join("")}</tr></thead><tbody>${rows}</tbody></table></div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică tabelul</button>'}</form>`;
    }

    function primeField(question, key, label, solved) {
        return `<input class="prime-input" data-prime-key="${escapeHtml(key)}" inputmode="numeric" aria-label="${escapeHtml(label)}" value="${escapeHtml(question.answerValues[key] || "")}"${solved ? " disabled" : ""}>`;
    }

    function primeWorkbenchHtml(question) {
        const item = question.interactive, solved = isSolved(question);
        if (!question.answerValues) question.answerValues = {};
        if (!question.primeSelectedIds) question.primeSelectedIds = [];
        if (solved) {
            Object.entries(item.answers).forEach(([key, value]) => { question.answerValues[key] = String(value); });
            if (item.correct_ids) question.primeSelectedIds = [...item.correct_ids];
        }
        let body = "";
        if (item.mode === "trial") {
            const rows = item.tests.map(row => `<tr><td>${item.number} : ${row.divisor}</td><td>${primeField(question, `remainder:${row.divisor}`, `Restul împărțirii la ${row.divisor}`, solved)}</td></tr>`).join("");
            const chosen = question.answerValues.classification || "";
            body = `<p class="interactive-instruction">Completează resturile, apoi clasifică numărul.</p><table class="prime-trial-table"><thead><tr><th>Împărțire</th><th>Rest</th></tr></thead><tbody>${rows}</tbody></table><div class="prime-classification"><button type="button" data-prime-class="prim" class="${chosen === "prim" ? "is-selected" : ""}"${solved ? " disabled" : ""}>Număr prim</button><button type="button" data-prime-class="compus" class="${chosen === "compus" ? "is-selected" : ""}"${solved ? " disabled" : ""}>Număr compus</button></div>`;
        } else if (item.mode === "factor_product") {
            const selected = new Set(question.primeSelectedIds);
            const card = entry => `<button type="button" draggable="${solved ? "false" : "true"}" data-prime-factor="${escapeHtml(entry.id)}" class="prime-factor-card${selected.has(entry.id) ? " is-selected" : ""}"${solved ? " disabled" : ""}>${entry.value}</button>`;
            const slots = Array.from({length: item.slot_count}, (_, index) => { const id = question.primeSelectedIds[index], entry = item.cards.find(cardItem => cardItem.id === id); return `<span>${entry ? entry.value : "?"}</span>`; }).join("<b>·</b>");
            body = `<p class="interactive-instruction">Trage factorii primi în construcție sau apasă-i în ordinea dorită.</p><div class="prime-factor-pool">${item.cards.map(card).join("")}</div><div class="prime-product-line"><strong>${item.target}</strong><b>=</b><div data-prime-factor-zone class="prime-factor-slots">${slots}</div></div>`;
        } else if (item.mode === "prime_pair") {
            body = `<p class="interactive-instruction">Ambele numere completate trebuie să fie prime.</p><div class="prime-equation-line">${primeField(question, "left", "Primul număr prim", solved)}<strong>${escapeHtml(item.operator)}</strong>${primeField(question, "right", "Al doilea număr prim", solved)}<strong>= ${item.target}</strong></div>`;
        } else if (item.mode === "prime_equation") {
            body = `<p class="interactive-instruction">Completează necunoscutele cu numere prime.</p><div class="prime-given-equation">${escapeHtml(item.equation)}</div><div class="prime-equation-fields">${item.fields.map(field => `<label>${escapeHtml(field.label)}${primeField(question, field.key, field.label, solved)}</label>`).join("")}</div>`;
        } else if (item.mode === "escape_code") {
            body = `<p class="interactive-instruction">Rezolvă indiciile; răspunsurile formează codul în ordinea dată.</p><div class="prime-code-clues">${item.clues.map((clue, index) => `<label><span>${index + 1}. ${escapeHtml(clue.text)}</span>${primeField(question, clue.key, `Cifra ${index + 1} a codului`, solved)}</label>`).join("")}</div>`;
        } else if (item.mode === "perfect_number") {
            const selected = new Set(question.primeSelectedIds);
            body = `<p class="interactive-instruction">Selectează divizorii mai mici decât ${item.number}, apoi calculează suma lor.</p><div class="prime-perfect-candidates">${item.candidates.map(value => `<button type="button" data-prime-perfect="${value}" class="${selected.has(String(value)) ? "is-selected" : ""}"${solved ? " disabled" : ""}>${value}</button>`).join("")}</div><div class="prime-perfect-sum"><span>Suma divizorilor selectați =</span>${primeField(question, "sum", "Suma divizorilor", solved)}</div>`;
        }
        return `<form class="training-prime-workbench-form interactive-form">${body}${solved ? "" : '<button type="submit" class="btn btn-press">Verifică răspunsul</button>'}</form>`;
    }

    function decimalField(question, key, label, solved) {
        return `<input class="decimal-input" data-decimal-key="${escapeHtml(key)}" inputmode="decimal" aria-label="${escapeHtml(label)}" value="${escapeHtml(question.answerValues[key] || "")}"${solved ? " disabled" : ""}>`;
    }

    function decimalWorkbenchHtml(question) {
        const item = question.interactive, solved = isSolved(question);
        if (!question.answerValues) question.answerValues = {};
        if (solved) Object.entries(item.answers).forEach(([key, value]) => { question.answerValues[key] = String(value); });
        let body = "";
        if (item.mode === "comma") {
            const places = Array.from({length: item.digits.length + 1}, (_, index) => `<button type="button" data-comma-place="${index}" class="decimal-comma-place${question.answerValues.position === String(index) ? " is-selected" : ""}"${solved ? " disabled" : ""}>${index === 0 ? "|" : item.digits[index - 1] + " |"}</button>`).join("");
            body = `<p class="interactive-instruction">Apasă spațiul în care trebuie așezată virgula.</p><div class="decimal-comma-board">${places}</div>`;
        } else if (item.mode === "conversion") {
            body = `<div class="decimal-conversion"><strong>${escapeHtml(item.source)}</strong><span>=</span>${item.target_kind === "decimal" ? decimalField(question, "decimal", "Fracția zecimală", solved) : `<span class="decimal-fraction">${decimalField(question, "numerator", "Numărător", solved)}<i></i>${decimalField(question, "denominator", "Numitor", solved)}</span>`}</div>`;
        } else if (item.mode === "build_fraction") {
            body = `<p class="interactive-instruction">Construiește fracția ordinară corespunzătoare.</p><div class="decimal-conversion"><strong>${escapeHtml(item.decimal)}</strong><span>=</span><span class="decimal-fraction">${decimalField(question, "numerator", "Numărător", solved)}<i></i>${decimalField(question, "denominator", "Numitor", solved)}</span></div>`;
        } else if (item.mode === "place_value") {
            body = `<p class="interactive-instruction">Completează cifrele în tabelul valorilor poziționale.</p><div class="decimal-place-table-wrap"><table class="decimal-place-table"><thead><tr>${item.columns.map(column => `<th>${escapeHtml(column.label)}</th>`).join("")}</tr></thead><tbody><tr>${item.columns.map(column => `<td>${decimalField(question, column.key, column.label, solved)}</td>`).join("")}</tr></tbody></table></div>`;
        } else if (item.mode === "words") {
            body = `<p class="interactive-instruction">Scrie cu cifre numărul rostit.</p><div class="decimal-words">„${escapeHtml(item.words)}”</div>${decimalField(question, "decimal", "Numărul zecimal", solved)}`;
        } else if (item.mode === "decompose") {
            body = `<p class="interactive-instruction">Completează descompunerea pe ordine zecimale.</p><div class="decimal-decomposition"><strong>${escapeHtml(item.decimal)} =</strong>${item.parts.map((part, index) => `<span>${decimalField(question, `part:${index}`, `Termenul ${index + 1}`, solved)}${index ? `<small>/${10 ** index}</small>` : ""}</span>`).join("+")}</div>`;
        } else if (item.mode === "amplify") {
            body = `<p class="interactive-instruction">Adu fracția la numitorul cerut, apoi scrie forma zecimală.</p><div class="decimal-amplify"><span class="decimal-fraction"><b>${item.numerator}</b><i></i><b>${item.denominator}</b></span><span>× ${decimalField(question, "factor", "Factor de amplificare", solved)}</span><span>=</span><span class="decimal-fraction">${decimalField(question, "new_numerator", "Numărător nou", solved)}<i></i><b>${item.target_denominator}</b></span><span>=</span>${decimalField(question, "decimal", "Forma zecimală", solved)}</div>`;
        } else if (["missing", "natural_n", "denominator"].includes(item.mode)) {
            body = `<div class="decimal-given">${escapeHtml(item.expression)}</div><div class="decimal-fields">${item.fields.map(field => `<label>${escapeHtml(field.label)}${decimalField(question, field.key, field.label, solved)}</label>`).join("")}</div>`;
        } else if (item.mode === "zeros") {
            body = `<p class="interactive-instruction">Completează formele echivalente adăugând zerouri după ultima zecimală.</p><div class="decimal-zero-chain"><strong>${escapeHtml(item.start)}</strong>${item.fields.map(field => `<span>=</span>${decimalField(question, field.key, field.label, solved)}`).join("")}</div>`;
        } else if (item.mode === "vessel") {
            const level = Number(question.answerValues.filled || 0), segments = Array.from({length:item.segments}, (_,i) => `<button type="button" data-vessel-level="${i + 1}" class="decimal-vessel-segment${i < level ? " is-filled" : ""}"${solved ? " disabled" : ""}></button>`).reverse().join("");
            body = `<p class="interactive-instruction">Apasă gradația care reprezintă cantitatea cerută.</p><div class="decimal-vessel"><div>${segments}</div><span>1</span><span>0</span></div><div class="decimal-vessel-target">Țintă: <strong>${escapeHtml(item.target_label)}</strong></div>`;
        }
        return `<form class="training-decimal-workbench-form interactive-form">${body}${solved ? "" : '<button type="submit" class="btn btn-press">Verifică răspunsul</button>'}</form>`;
    }

    function fractionShapeHtml(question, numerator, denominator, shape, selectable = false) {
        const selected = new Set(question.fractionSelected || []);
        const solved = isSolved(question);
        if (shape === "circle") {
            const sectors = Array.from({length: denominator}, (_, index) => {
                const start = (index / denominator) * Math.PI * 2 - Math.PI / 2;
                const end = ((index + 1) / denominator) * Math.PI * 2 - Math.PI / 2;
                const p1 = `${50 + 46 * Math.cos(start)} ${50 + 46 * Math.sin(start)}`;
                const p2 = `${50 + 46 * Math.cos(end)} ${50 + 46 * Math.sin(end)}`;
                const active = selectable ? selected.has(index) : index < numerator;
                return `<path d="M 50 50 L ${p1} A 46 46 0 ${end - start > Math.PI ? 1 : 0} 1 ${p2} Z" class="fraction-sector${active ? " is-filled" : ""}"${selectable ? ` data-fraction-segment="${index}"` : ""}></path>`;
            }).join("");
            return `<svg class="fraction-circle" viewBox="0 0 100 100" role="img" aria-label="${numerator} părți din ${denominator}">${sectors}</svg>`;
        }
        const cells = Array.from({length: denominator}, (_, index) => {
            const active = selectable ? selected.has(index) : index < numerator;
            return `<button type="button" class="fraction-cell${active ? " is-filled" : ""}"${selectable ? ` data-fraction-segment="${index}"` : " disabled"}${solved ? " disabled" : ""} aria-label="Partea ${index + 1}"></button>`;
        }).join("");
        return `<div class="fraction-shape fraction-shape--${shape}" style="--fraction-columns:${shape === "grid" ? Math.ceil(Math.sqrt(denominator)) : denominator}">${cells}</div>`;
    }

    function fractionField(question, key, label, solved, max = 100) {
        return `<input class="fraction-number-input" data-fraction-key="${key}" type="number" min="0" max="${max}" aria-label="${escapeHtml(label)}" value="${escapeHtml(question.answerValues?.[key] || "")}"${solved ? " disabled" : ""}>`;
    }

    function fractionVisualHtml(question) {
        const item = question.interactive, solved = isSolved(question);
        if (!question.answerValues) question.answerValues = {};
        if (!question.fractionSelected) question.fractionSelected = [];
        if (solved) {
            Object.entries(item.answers).forEach(([key, value]) => { question.answerValues[key] = String(value); });
            if (item.mode === "color") question.fractionSelected = String(item.answers.selected).split(",").filter(Boolean).map(Number);
        }
        let body = "";
        if (item.mode === "color") {
            body = `<p class="interactive-instruction">Apasă exact ${item.numerator} dintre cele ${item.denominator} părți egale.</p>${fractionShapeHtml(question, item.numerator, item.denominator, item.shape, true)}<div class="fraction-counter">Ai colorat <strong>${question.fractionSelected.length}</strong> din ${item.denominator} părți.</div>`;
        } else if (item.mode === "read") {
            body = `${fractionShapeHtml(question, item.numerator, item.denominator, item.shape)}<div class="fraction-equation">${fractionField(question, "numerator", "Numărător", solved, item.denominator)}<span class="fraction-line"></span>${fractionField(question, "denominator", "Numitor", solved, 100)}</div>`;
        } else if (item.mode === "construct") {
            const previewN = Number(question.answerValues.numerator || 0), previewD = Math.max(1, Number(question.answerValues.denominator || item.denominator));
            body = `<p class="interactive-instruction">Completează fracția, apoi urmărește reprezentarea.</p><div class="fraction-equation">${fractionField(question, "numerator", "Numărător", solved, 20)}<span class="fraction-line"></span>${fractionField(question, "denominator", "Numitor", solved, 20)}</div>${fractionShapeHtml(question, Math.min(previewN, previewD), previewD, item.shape)}`;
        } else if (item.mode === "repair") {
            const n = item.editable === "numerator" ? fractionField(question, "numerator", "Numărător nou", solved, 50) : `<strong>${item.numerator}</strong>`;
            const d = item.editable === "denominator" ? fractionField(question, "denominator", "Numitor nou", solved, 50) : `<strong>${item.denominator}</strong>`;
            body = `<p class="interactive-instruction">Modifică doar căsuța liberă.</p><div class="fraction-equation fraction-equation--large">${n}<span class="fraction-line"></span>${d}</div><div class="fraction-target">Țintă: <strong>${escapeHtml(item.target_label)}</strong></div>`;
        } else if (item.mode === "equivalent") {
            body = `<div class="fraction-equivalent-row"><span class="fraction-card"><b>${item.numerator}</b><i></i><b>${item.denominator}</b></span><span>×</span>${fractionField(question, "factor", "Factor", solved, 20)}<span>=</span><span class="fraction-card">${fractionField(question, "numerator", "Numărător echivalent", solved)}<i></i>${fractionField(question, "denominator", "Numitor echivalent", solved)}</span></div>`;
        } else if (item.mode === "mixed_to_fraction") {
            body = `<p class="interactive-instruction">Înmulțește întregul cu numitorul, apoi adună numărătorul.</p><div class="mixed-fraction-work"><span class="mixed-number"><b>${item.whole}</b>${fractionCardHtml([item.numerator, item.denominator])}</span><span>=</span><span class="fraction-card">${fractionField(question, "result", "Numărătorul fracției", solved)}<i></i><b>${item.denominator}</b></span></div><div class="mixed-formula-strip">${item.whole} · ${item.denominator} + ${item.numerator} = ?</div>`;
        } else if (item.mode === "fraction_to_mixed") {
            body = `<p class="interactive-instruction">Împarte numărătorul la numitor. Câtul este partea întreagă, iar restul devine numărător.</p><div class="mixed-division-strip"><b>${item.numerator} : ${item.denominator}</b><span>= cât și rest</span></div><div class="mixed-fraction-result"><span class="fraction-card"><b>${item.numerator}</b><i></i><b>${item.denominator}</b></span><span>=</span><span class="mixed-number">${fractionField(question, "whole", "Partea întreagă", solved)}<span class="fraction-card">${fractionField(question, "remainder", "Numărătorul părții fracționare", solved, item.denominator - 1)}<i></i><b>${item.denominator}</b></span></span></div>`;
        } else {
            body = `<div class="fraction-percent-row"><span class="fraction-card"><b>${item.numerator}</b><i></i><b>${item.denominator}</b></span><span>=</span><span class="fraction-card">${fractionField(question, "hundredths", "Numărător din 100", solved)}<i></i><b>100</b></span><span>=</span><label>${fractionField(question, "percent", "Procent", solved)}%</label></div>`;
        }
        return `<form class="training-fraction-visual-form interactive-form">${body}${solved ? "" : '<button type="submit" class="btn btn-press">Verifică răspunsul</button>'}</form>`;
    }

    function fractionDominoHtml(question) {
        const item = question.interactive, solved = isSolved(question);
        if (!question.dominoOrder) question.dominoOrder = [];
        if (solved) question.dominoOrder = [...item.correct_order];
        const tile = index => `<button type="button" class="fraction-domino" data-domino-tile="${index}"${solved ? " disabled" : ""}><span>${escapeHtml(item.tiles[index].left)}</span><span>${escapeHtml(item.tiles[index].right)}</span></button>`;
        const pool = item.display_order.filter(index => !question.dominoOrder.includes(index)).map(tile).join("");
        const chain = question.dominoOrder.map(tile).join("");
        return `<form class="training-fraction-domino-form interactive-form"><p class="interactive-instruction">Apasă piesele în ordinea corectă. Capetele care se ating trebuie să reprezinte aceeași valoare.</p><div class="fraction-domino-pool">${pool || "Toate piesele au fost așezate."}</div><div class="fraction-domino-chain">${chain || '<span class="domino-placeholder">Construiește lanțul aici</span>'}</div>${solved ? "" : '<button type="button" class="fraction-domino-clear">Reia aranjarea</button><button type="submit" class="btn btn-press">Verifică lanțul</button>'}</form>`;
    }

    function fractionCardHtml(pair) {
        return `<span class="fraction-card"><b>${escapeHtml(pair[0])}</b><i></i><b>${escapeHtml(pair[1])}</b></span>`;
    }

    function fractionCompareHtml(question) {
        const item = question.interactive, solved = isSolved(question);
        if (item.mode === "order") {
            if (!question.fractionOrder) question.fractionOrder = [];
            if (solved) question.fractionOrder = [...item.correct_order];
            const card = index => `<button type="button" class="fraction-order-card" data-fraction-order="${index}"${solved ? " disabled" : ""}>${escapeHtml(item.items[index].label)}</button>`;
            const pool = item.display_order.filter(index => !question.fractionOrder.includes(index)).map(card).join("");
            const ordered = question.fractionOrder.map(card).join('<span class="fraction-order-arrow">→</span>');
            return `<form class="training-fraction-compare-form interactive-form"><p class="interactive-instruction">Apasă fracțiile în ordine ${item.direction === "asc" ? "crescătoare" : "descrescătoare"}.</p><div class="fraction-order-pool">${pool || "Toate fracțiile sunt așezate."}</div><div class="fraction-order-line">${ordered || "Construiește ordinea aici"}</div>${solved ? "" : '<button type="button" class="fraction-order-clear">Reia</button><button type="submit" class="btn btn-press">Verifică ordinea</button>'}</form>`;
        }
        if (solved) question.fractionRelation = item.relation;
        let representations = "";
        if (item.mode === "visual") {
            representations = `<div class="fraction-visual-comparison"><div>${fractionShapeHtml(question, item.left[0], item.left[1], item.shape || "bar")}</div><div>${fractionShapeHtml(question, item.right[0], item.right[1], item.shape || "bar")}</div></div>`;
        }
        const signs = ["<", "=", ">"].map(sign => `<button type="button" class="fraction-relation${question.fractionRelation === sign ? " is-selected" : ""}" data-fraction-relation="${escapeHtml(sign)}"${solved ? " disabled" : ""}>${escapeHtml(sign)}</button>`).join("");
        const leftDisplay = item.left_label ? `<strong class="decimal-compare-value">${escapeHtml(item.left_label)}</strong>` : fractionCardHtml(item.left);
        const rightDisplay = item.right_label ? `<strong class="decimal-compare-value">${escapeHtml(item.right_label)}</strong>` : fractionCardHtml(item.right);
        return `<form class="training-fraction-compare-form interactive-form">${representations}<div class="fraction-comparison-row">${leftDisplay}<div class="fraction-relation-choices">${signs}</div>${rightDisplay}</div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică semnul</button>'}</form>`;
    }

    function fractionAxisHtml(question) {
        const item = question.interactive, solved = isSolved(question), total = item.denominator * item.maximum;
        if (solved) question.selectedAxisTick = item.answer_tick;
        const ticks = Array.from({length: total + 1}, (_, index) => {
            const label = index % item.denominator === 0 ? String(index / item.denominator) : "";
            const selected = question.selectedAxisTick === index;
            return `<button type="button" class="fraction-axis-tick${selected ? " is-selected" : ""}" data-axis-tick="${index}" aria-label="Poziția ${index}/${item.denominator}"${solved ? " disabled" : ""}><i></i><span>${label}</span></button>`;
        }).join("");
        return `<form class="training-fraction-axis-form interactive-form"><p class="interactive-instruction">Unitatea este împărțită în ${item.denominator} părți egale. Apasă gradația corectă pentru ${item.target_numerator}/${item.denominator}.</p><div class="fraction-axis"><div class="fraction-axis-line"></div>${ticks}</div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică poziția</button>'}</form>`;
    }

    function lessonField(question, key, label, solved, wide = false) {
        return `<input class="lesson-number-field${wide ? " is-wide" : ""}" data-lesson-key="${escapeHtml(key)}" inputmode="numeric" aria-label="${escapeHtml(label)}" value="${escapeHtml(question.answerValues?.[key] || "")}"${solved ? " disabled" : ""}>`;
    }

    function gcdWorkbenchHtml(question) {
        const item = question.interactive, solved = isSolved(question);
        if (!question.answerValues) question.answerValues = {};
        if (solved) Object.entries(item.answers).forEach(([key,value]) => question.answerValues[key] = String(value));
        let body = "";
        if (item.mode === "select") {
            const selected = new Set(String(question.answerValues.common || "").split(",").filter(Boolean));
            body = `<p class="interactive-instruction">Selectează toți divizorii comuni.</p><div class="gcd-candidates">${item.candidates.map(value => `<button type="button" data-gcd-choice="${value}" class="${selected.has(String(value)) ? "is-selected" : ""}"${solved ? " disabled" : ""}>${value}</button>`).join("")}</div><label class="gcd-result">c.m.m.d.c. = ${lessonField(question,"gcd","Cel mai mare divizor comun",solved)}</label>`;
        } else if (item.mode === "packing") {
            body = `<div class="gcd-packing"><section><b>${item.a}</b><span>obiecte de primul tip</span></section><section><b>${item.b}</b><span>obiecte de al doilea tip</span></section></div><div class="gcd-packing-fields"><label>Număr maxim de grupe${lessonField(question,"groups","Număr de grupe",solved)}</label><label>Primul tip/grup${lessonField(question,"per_a","Primul tip în grup",solved)}</label><label>Al doilea tip/grup${lessonField(question,"per_b","Al doilea tip în grup",solved)}</label></div>`;
        } else {
            body = `<div class="gcd-table"><label>Divizorii lui ${item.a}${lessonField(question,"divisors_a",`Divizorii lui ${item.a}`,solved,true)}</label><label>Divizorii lui ${item.b}${lessonField(question,"divisors_b",`Divizorii lui ${item.b}`,solved,true)}</label><label>Divizorii comuni${lessonField(question,"common","Divizorii comuni",solved,true)}</label><label>c.m.m.d.c.${lessonField(question,"gcd","Cel mai mare divizor comun",solved)}</label></div>`;
        }
        return `<form class="training-gcd-workbench-form interactive-form">${body}${solved ? "" : '<button type="submit" class="btn btn-press">Verifică răspunsul</button>'}</form>`;
    }

    function fractionScaleHtml(question) {
        const item = question.interactive, solved = isSolved(question);
        if (!question.answerValues) question.answerValues = {};
        if (solved) Object.entries(item.answers).forEach(([key,value]) => question.answerValues[key] = String(value));
        const op = ["amplify","missing_factor"].includes(item.mode) ? "×" : ":";
        let leftN = item.numerator, leftD = item.denominator;
        if (item.mode === "restore") { leftN = item.result_numerator; leftD = item.result_denominator; }
        const resultN = item.mode === "restore" ? lessonField(question,"numerator","Numărător inițial",solved) : lessonField(question,"result_numerator","Numărător rezultat",solved);
        const resultD = item.mode === "restore" ? lessonField(question,"denominator","Numitor inițial",solved) : lessonField(question,"result_denominator","Numitor rezultat",solved);
        return `<form class="training-fraction-scale-form interactive-form"><div class="fraction-scale-board"><span class="fraction-card"><b>${leftN}</b><i></i><b>${leftD}</b></span><span class="fraction-scale-operation">${op}</span>${lessonField(question,"factor","Factor",solved)}<span>=</span><span class="fraction-card">${resultN}<i></i>${resultD}</span></div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică transformarea</button>'}</form>`;
    }

    function fractionReducePathHtml(question) {
        const item = question.interactive, solved = isSolved(question);
        if (!question.answerValues) question.answerValues = {};
        if (solved) item.steps.forEach((step,index) => ["factor","numerator","denominator"].forEach(key => question.answerValues[`${index}:${key}`] = String(step[key])));
        let previous = `<span class="fraction-card"><b>${item.numerator}</b><i></i><b>${item.denominator}</b></span>`;
        const steps = item.steps.map((step,index) => { const html = `<div class="reduce-path-step">${previous}<span>:</span>${lessonField(question,`${index}:factor`,`Factorul etapei ${index+1}`,solved)}<span>=</span><span class="fraction-card">${lessonField(question,`${index}:numerator`,`Numărătorul etapei ${index+1}`,solved)}<i></i>${lessonField(question,`${index}:denominator`,`Numitorul etapei ${index+1}`,solved)}</span></div>`; previous = `<span class="fraction-card"><b>${step.numerator}</b><i></i><b>${step.denominator}</b></span>`; return html; }).join("");
        return `<form class="training-fraction-reduce-form interactive-form"><p class="interactive-instruction">Completează fiecare simplificare până obții o fracție ireductibilă.</p><div class="reduce-path">${steps}</div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică traseul</button>'}</form>`;
    }

    function lcmWorkbenchHtml(question) {
        const item = question.interactive, solved = isSolved(question);
        if (!question.answerValues) question.answerValues = {};
        if (solved) Object.entries(item.answers).forEach(([key,value]) => question.answerValues[key] = String(value));
        let body = "";
        if (item.mode === "select") {
            const selected = new Set(String(question.answerValues.common || "").split(",").filter(Boolean));
            body = `<p class="interactive-instruction">Selectează multiplii comuni, apoi scrie cel mai mic.</p><div class="gcd-candidates">${item.candidates.map(value => `<button type="button" data-lcm-choice="${value}" class="${selected.has(String(value)) ? "is-selected" : ""}"${solved ? " disabled" : ""}>${value}</button>`).join("")}</div><label class="gcd-result">c.m.m.m.c. = ${lessonField(question,"lcm","Cel mai mic multiplu comun",solved)}</label>`;
        } else if (item.mode === "sync") {
            body = `<div class="lcm-sync"><section><b>din ${item.a} în ${item.a}</b><span>${escapeHtml(item.multiples_a.join(" → "))}</span></section><section><b>din ${item.b} în ${item.b}</b><span>${escapeHtml(item.multiples_b.join(" → "))}</span></section></div><label class="gcd-result">Prima întâlnire: ${lessonField(question,"lcm","Primul moment comun",solved)}</label>`;
        } else {
            body = `<div class="gcd-table"><label>Multiplii lui ${item.a}${lessonField(question,"multiples_a",`Multiplii lui ${item.a}`,solved,true)}</label><label>Multiplii lui ${item.b}${lessonField(question,"multiples_b",`Multiplii lui ${item.b}`,solved,true)}</label><label>Multiplii comuni${lessonField(question,"common","Multiplii comuni",solved,true)}</label><label>c.m.m.m.c.${lessonField(question,"lcm","Cel mai mic multiplu comun",solved)}</label></div>`;
        }
        return `<form class="training-lcm-workbench-form interactive-form">${body}${solved ? "" : '<button type="submit" class="btn btn-press">Verifică răspunsul</button>'}</form>`;
    }

    function commonDenominatorHtml(question) {
        const item = question.interactive, solved = isSolved(question);
        if (!question.answerValues) question.answerValues = {};
        if (solved) Object.entries(item.answers).forEach(([key,value]) => question.answerValues[key] = String(value));
        const transformed = (side, label) => `<div class="common-denominator-side"><span class="fraction-card"><b>${item[side][0]}</b><i></i><b>${item[side][1]}</b></span><span>×</span>${lessonField(question,`${side}_factor`,`Factor pentru ${label}`,solved)}<span>=</span><span class="fraction-card">${lessonField(question,`${side}_numerator`,`Numărător ${label}`,solved)}<i></i>${lessonField(question,"common_denominator",`Numitor comun`,solved)}</span></div>`;
        return `<form class="training-common-denominator-form interactive-form"><p class="interactive-instruction">Găsește cel mai mic numitor comun și amplifică fiecare fracție cu factorul potrivit.</p><div class="common-denominator-board">${transformed("left","prima fracție")}${transformed("right","a doua fracție")}</div>${item.mode === "compare" ? `<label class="common-relation-label">Semnul dintre fracțiile transformate${lessonField(question,"relation","Semnul corect",solved)}</label>` : ""}${solved ? "" : '<button type="submit" class="btn btn-press">Verifică transformările</button>'}</form>`;
    }

    function answerHtml(question, selectedOptionId, showWrongSelection) {
        switch (question.type) {
            case "parentheses_drag":
            case "parentheses_target":
                return parenthesesHtml(question);
            case "column_addition":
            case "column_multiplication":
            case "column_subtraction":
                return columnCalculationHtml(question);
            case "missing_digits":
                return missingDigitsHtml(question);
            case "error_spotting":
                return errorSpottingHtml(question);
            case "input_output":
                return inputOutputHtml(question);
            case "column_division":
                return columnDivisionHtml(question);
            case "division_relation":
                return divisionRelationHtml(question);
            case "operation_chain":
                return operationChainHtml(question);
            case "division_table":
                return divisionTableHtml(question);
            case "numeric_input":
                return numericInputHtml(question);
            case "factor_builder":
                return factorBuilderHtml(question);
            case "factor_error":
                return factorErrorHtml(question);
            case "factor_match":
            case "power_match":
                return factorMatchHtml(question);
            case "power_builder":
                return powerBuilderHtml(question);
            case "power_table":
                return powerTableHtml(question);
            case "power_cycle":
                return powerCycleHtml(question);
            case "power_square":
                return powerSquareHtml(question);
            case "power_rule_chain":
                return powerRuleChainHtml(question);
            case "power_compare":
                return powerCompareHtml(question);
            case "power_order":
                return powerOrderHtml(question);
            case "base_values":
                return baseValuesHtml(question);
            case "base_match":
                return baseMatchHtml(question);
            case "binary_toggle":
                return binaryToggleHtml(question);
            case "base_error":
                return factorErrorHtml(question);
            case "unit_reduction":
                return unitReductionHtml(question);
            case "comparison_method":
                return comparisonMethodHtml(question);
            case "figurative_method":
                return figurativeMethodHtml(question);
            case "reverse_method":
                return reverseMethodHtml(question);
            case "false_hypothesis_method":
                return falseHypothesisHtml(question);
            case "operation_sequence":
                return operationSequenceHtml(question);
            case "operation_workbench":
                return operationWorkbenchHtml(question);
            case "divisibility_values":
                return divisibilityValuesHtml(question);
            case "divisibility_select":
                return divisibilitySelectHtml(question);
            case "divisibility_sort":
                return divisibilitySortHtml(question);
            case "divisibility_error":
                return factorErrorHtml(question);
            case "criteria_table":
                return criteriaTableHtml(question);
            case "prime_workbench":
                return primeWorkbenchHtml(question);
            case "decimal_workbench":
                return decimalWorkbenchHtml(question);
            case "fraction_visual":
                return fractionVisualHtml(question);
            case "fraction_domino":
                return fractionDominoHtml(question);
            case "fraction_compare":
                return fractionCompareHtml(question);
            case "fraction_axis":
                return fractionAxisHtml(question);
            case "gcd_workbench":
                return gcdWorkbenchHtml(question);
            case "fraction_scale":
                return fractionScaleHtml(question);
            case "fraction_reduce_path":
                return fractionReducePathHtml(question);
            case "lcm_workbench":
                return lcmWorkbenchHtml(question);
            case "common_denominator":
                return commonDenominatorHtml(question);
            default:
                return optionsHtml(question, selectedOptionId, showWrongSelection);
        }
    }

    function renderQuestion(selectedOptionId, showWrongSelection) {
        const question = data.questions[currentIndex];
        if (!cardEl || !question) {
            return;
        }

        const formatLabels = {
            grid: "Grilă",
            true_false: "Adevărat sau fals",
            interactive: "Interactiv",
        };
        const formatTag = question.format || (question.type === "multiple_choice" ? "grid" : "interactive");
        cardEl.innerHTML =
            `<span class="question-format-badge question-format-badge--${escapeHtml(formatTag)}">${escapeHtml(formatLabels[formatTag] || "Exercițiu")}</span>` +
            `<h2 style="margin:0 0 1rem;">${escapeHtml(question.text)}</h2>` +
            (showWrongSelection
                ? question.status === "wrong"
                    ? '<p class="training-feedback" style="margin:0 0 0.75rem;"><span class="training-feedback--wrong">Greșit. Încearcă alt răspuns.</span></p>'
                    : ""
                : feedbackHtml(question)) +
            explanationHtml(question) +
            answerHtml(question, selectedOptionId, showWrongSelection);

        bindForm();
        updateProgress();
        updateArrows();
        updateGridCurrent();
    }

    function updateProgress() {
        if (progressEl) {
            progressEl.textContent = `Întrebarea ${currentIndex + 1} din ${data.questions.length}`;
        }
    }

    function updateArrows() {
        const hasPrev = currentIndex > 0;
        const hasNext = currentIndex < data.questions.length - 1;

        if (prevArrow) {
            if (hasPrev) {
                prevArrow.href = trainingUrl(currentIndex - 1);
                prevArrow.classList.remove("training-arrow--placeholder");
                prevArrow.removeAttribute("aria-hidden");
            } else {
                prevArrow.href = trainingUrl(currentIndex);
                prevArrow.classList.add("training-arrow--placeholder");
                prevArrow.setAttribute("aria-hidden", "true");
            }
        }

        if (nextArrow) {
            if (hasNext) {
                nextArrow.href = trainingUrl(currentIndex + 1);
                nextArrow.classList.remove("training-arrow--placeholder");
                nextArrow.removeAttribute("aria-hidden");
            } else {
                nextArrow.href = trainingUrl(currentIndex);
                nextArrow.classList.add("training-arrow--placeholder");
                nextArrow.setAttribute("aria-hidden", "true");
            }
        }
    }

    function updateGridCell(index, status) {
        if (!gridEl) {
            return;
        }
        const cell = gridEl.querySelector(`[data-training-index="${index}"]`);
        if (!cell) {
            return;
        }
        cell.classList.remove(
            "training-cell--unanswered",
            "training-cell--correct",
            "training-cell--wrong"
        );
        cell.classList.add(`training-cell--${status}`);
    }

    function updateGridCurrent() {
        if (!gridEl) {
            return;
        }
        gridEl.querySelectorAll(".training-cell").forEach((cell) => {
            const cellIndex = parseInt(cell.dataset.trainingIndex, 10);
            if (cellIndex === currentIndex) {
                cell.setAttribute("aria-current", "true");
            } else {
                cell.removeAttribute("aria-current");
            }
        });
    }

    function showSaveError(message) {
        if (!saveErrorEl) {
            return;
        }
        const reportHref = `/feedback/raporteaza/?from=${encodeURIComponent(window.location.pathname)}`;
        saveErrorEl.innerHTML =
            `${escapeHtml(message || "Nu am putut salva progresul. Încearcă din nou.")} ` +
            `<a href="${reportHref}" class="training-report-link">Raportează problema</a>`;
        saveErrorEl.hidden = false;
    }

    function hideSaveError() {
        if (saveErrorEl) {
            saveErrorEl.hidden = true;
            saveErrorEl.textContent = "";
        }
    }

    async function persistAnswer(question, answer) {
        const body = new FormData();
        body.append("question_id", String(question.id));
        if (["parentheses_drag", "parentheses_target"].includes(question.type)) {
            body.append("open_index", String(answer.open));
            body.append("close_index", String(answer.close));
        } else if (["column_addition", "column_multiplication", "column_subtraction"].includes(question.type)) {
            body.append("result_digits", answer.resultDigits);
            body.append("borrow_columns", JSON.stringify(answer.borrowColumns));
        } else if (["missing_digits", "input_output", "factor_builder", "factor_match", "power_builder", "power_match", "power_table", "power_cycle", "power_square", "power_rule_chain", "base_values", "base_match", "binary_toggle", "unit_reduction", "comparison_method", "figurative_method", "reverse_method", "false_hypothesis_method", "operation_workbench", "divisibility_values", "prime_workbench", "decimal_workbench", "fraction_visual", "gcd_workbench", "fraction_scale", "fraction_reduce_path", "lcm_workbench", "common_denominator"].includes(question.type)) {
            body.append("values", JSON.stringify(answer.values));
        } else if (question.type === "divisibility_select") {
            body.append("selected_ids", JSON.stringify(answer.selectedIds));
        } else if (question.type === "divisibility_sort") {
            body.append("placements", JSON.stringify(answer.placements));
        } else if (question.type === "criteria_table") {
            body.append("values", JSON.stringify(answer.values));
        } else if (question.type === "power_compare") {
            body.append("relation", answer.relation);
        } else if (["power_order", "operation_sequence", "fraction_domino"].includes(question.type)) {
            body.append("order", JSON.stringify(answer.order));
        } else if (question.type === "fraction_compare") {
            body.append("relation", answer.relation || "");
            body.append("order", JSON.stringify(answer.order || []));
        } else if (question.type === "fraction_axis") {
            body.append("selected_tick", String(answer.selectedTick));
        } else if (question.type === "error_spotting") {
            body.append("selected_column", String(answer.selectedColumn));
        } else if (question.type === "column_division") {
            body.append("quotient", answer.quotient);
            body.append("remainders", JSON.stringify(answer.remainders));
        } else if (question.type === "operation_chain") {
            body.append("values", JSON.stringify(answer.values));
        } else if (question.type === "division_table") {
            body.append("values", JSON.stringify(answer.values));
        } else if (["division_relation", "numeric_input"].includes(question.type)) {
            body.append("value", answer.value);
        } else if (["factor_error", "base_error", "divisibility_error"].includes(question.type)) {
            body.append("selected_step", String(answer.selectedStep));
        } else {
            body.append("option_id", String(answer.optionId));
        }

        const response = await fetch(data.submitUrl, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCsrfToken(),
            },
            body,
            credentials: "same-origin",
        });

        if (!response.ok) {
            let message = "Nu am putut salva progresul.";
            try {
                const payload = await response.json();
                if (payload.error) {
                    message = payload.error;
                }
            } catch (_err) {
                /* ignore */
            }
            throw new Error(message);
        }

        return response.json();
    }

    function bindForm() {
        const parenthesesForm = cardEl?.querySelector(".training-parentheses-form");
        if (parenthesesForm) {
            bindParenthesesForm(parenthesesForm);
            return;
        }
        const columnForm = cardEl?.querySelector(".training-column-form");
        if (columnForm) {
            bindColumnForm(columnForm);
            return;
        }
        const missingForm = cardEl?.querySelector(".training-missing-form");
        if (missingForm) {
            bindMissingForm(missingForm);
            return;
        }
        const errorForm = cardEl?.querySelector(".training-error-form");
        if (errorForm) {
            bindErrorForm(errorForm);
            return;
        }
        const machineForm = cardEl?.querySelector(".training-machine-form");
        if (machineForm) {
            bindMachineForm(machineForm);
            return;
        }
        const divisionColumnForm = cardEl?.querySelector(".training-division-column-form");
        if (divisionColumnForm) { bindDivisionColumnForm(divisionColumnForm); return; }
        const chainForm = cardEl?.querySelector(".training-chain-form");
        if (chainForm) { bindChainForm(chainForm); return; }
        const tableForm = cardEl?.querySelector(".training-table-form");
        if (tableForm) { bindStructuredValuesForm(tableForm); return; }
        const singleValueForm = cardEl?.querySelector(".training-single-value-form");
        if (singleValueForm) { bindSingleValueForm(singleValueForm); return; }
        const factorBuilderForm = cardEl?.querySelector(".training-factor-builder-form");
        if (factorBuilderForm) {
            bindFactorBuilderForm(factorBuilderForm);
            return;
        }
        const factorErrorForm = cardEl?.querySelector(".training-factor-error-form");
        if (factorErrorForm) {
            bindFactorErrorForm(factorErrorForm);
            return;
        }
        const factorMatchForm = cardEl?.querySelector(".training-factor-match-form");
        if (factorMatchForm) {
            bindFactorMatchForm(factorMatchForm);
            return;
        }
        const powerValuesForm = cardEl?.querySelector(".training-power-values-form");
        if (powerValuesForm) {
            bindStructuredValuesForm(powerValuesForm);
            return;
        }
        const powerCompareForm = cardEl?.querySelector(".training-power-compare-form");
        if (powerCompareForm) { bindPowerCompareForm(powerCompareForm); return; }
        const powerOrderForm = cardEl?.querySelector(".training-power-order-form");
        if (powerOrderForm) { bindPowerOrderForm(powerOrderForm); return; }
        const baseValuesForm = cardEl?.querySelector(".training-base-values-form");
        if (baseValuesForm) { bindBaseValuesForm(baseValuesForm); return; }
        const binaryToggleForm = cardEl?.querySelector(".training-binary-toggle-form");
        if (binaryToggleForm) { bindBinaryToggleForm(binaryToggleForm); return; }
        const unitReductionForm = cardEl?.querySelector(".training-unit-reduction-form");
        if (unitReductionForm) { bindUnitReductionForm(unitReductionForm); return; }
        const comparisonForm = cardEl?.querySelector(".training-comparison-form");
        if (comparisonForm) { bindComparisonForm(comparisonForm); return; }
        const figurativeForm = cardEl?.querySelector(".training-figurative-form");
        if (figurativeForm) { bindFigurativeForm(figurativeForm); return; }
        const reverseForm = cardEl?.querySelector(".training-reverse-form");
        if (reverseForm) { bindReverseForm(reverseForm); return; }
        const hypothesisForm = cardEl?.querySelector(".training-hypothesis-form");
        if (hypothesisForm) { bindHypothesisForm(hypothesisForm); return; }
        const operationSequenceForm = cardEl?.querySelector(".training-operation-sequence-form");
        if (operationSequenceForm) { bindOperationSequenceForm(operationSequenceForm); return; }
        const operationWorkbenchForm = cardEl?.querySelector(".training-operation-workbench-form");
        if (operationWorkbenchForm) { bindStructuredValuesForm(operationWorkbenchForm); return; }
        const divisibilityValuesForm = cardEl?.querySelector(".training-divisibility-values-form");
        if (divisibilityValuesForm) { bindDivisibilityValuesForm(divisibilityValuesForm); return; }
        const divisibilitySelectForm = cardEl?.querySelector(".training-divisibility-select-form");
        if (divisibilitySelectForm) { bindDivisibilitySelectForm(divisibilitySelectForm); return; }
        const divisibilitySortForm = cardEl?.querySelector(".training-divisibility-sort-form");
        if (divisibilitySortForm) { bindDivisibilitySortForm(divisibilitySortForm); return; }
        const criteriaTableForm = cardEl?.querySelector(".training-criteria-table-form");
        if (criteriaTableForm) { bindCriteriaTableForm(criteriaTableForm); return; }
        const primeWorkbenchForm = cardEl?.querySelector(".training-prime-workbench-form");
        if (primeWorkbenchForm) { bindPrimeWorkbenchForm(primeWorkbenchForm); return; }
        const decimalWorkbenchForm = cardEl?.querySelector(".training-decimal-workbench-form");
        if (decimalWorkbenchForm) { bindDecimalWorkbenchForm(decimalWorkbenchForm); return; }
        const fractionVisualForm = cardEl?.querySelector(".training-fraction-visual-form");
        if (fractionVisualForm) { bindFractionVisualForm(fractionVisualForm); return; }
        const fractionDominoForm = cardEl?.querySelector(".training-fraction-domino-form");
        if (fractionDominoForm) { bindFractionDominoForm(fractionDominoForm); return; }
        const fractionCompareForm = cardEl?.querySelector(".training-fraction-compare-form");
        if (fractionCompareForm) { bindFractionCompareForm(fractionCompareForm); return; }
        const fractionAxisForm = cardEl?.querySelector(".training-fraction-axis-form");
        if (fractionAxisForm) { bindFractionAxisForm(fractionAxisForm); return; }
        const gcdForm = cardEl?.querySelector(".training-gcd-workbench-form");
        if (gcdForm) { bindLessonValuesForm(gcdForm); return; }
        const fractionScaleForm = cardEl?.querySelector(".training-fraction-scale-form");
        if (fractionScaleForm) { bindLessonValuesForm(fractionScaleForm); return; }
        const fractionReduceForm = cardEl?.querySelector(".training-fraction-reduce-form");
        if (fractionReduceForm) { bindLessonValuesForm(fractionReduceForm); return; }
        const lcmForm = cardEl?.querySelector(".training-lcm-workbench-form");
        if (lcmForm) { bindLessonValuesForm(lcmForm); return; }
        const commonDenominatorForm = cardEl?.querySelector(".training-common-denominator-form");
        if (commonDenominatorForm) { bindLessonValuesForm(commonDenominatorForm); return; }
        const form = cardEl?.querySelector(".training-options-form");
        if (!form) {
            return;
        }

        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            hideSaveError();

            const question = data.questions[currentIndex];
            if (isSolved(question)) {
                return;
            }

            const selected = form.querySelector('input[name="option_id"]:checked');
            if (!selected) {
                return;
            }

            const optionId = parseInt(selected.value, 10);
            const isCorrect = optionId === question.correctOptionId;

            question.status = isCorrect ? "correct" : "wrong";
            updateGridCell(currentIndex, question.status);
            renderQuestion(optionId, !isCorrect);

            try {
                const result = await persistAnswer(question, { optionId });
                question.status = result.status;
                if (result.is_correct && result.explanation) {
                    question.explanation = result.explanation;
                }
                if (result.is_correct) {
                    renderQuestion(optionId, false);
                }
            } catch (err) {
                showSaveError(err.message);
            }
        });
    }

    async function submitInteractiveAnswer(question, answer) {
        hideSaveError();
        try {
            const result = await persistAnswer(question, answer);
            question.status = result.status;
            updateGridCell(currentIndex, question.status);
            if (result.is_correct && result.explanation) {
                question.explanation = result.explanation;
            }
            renderQuestion(null, !result.is_correct);
        } catch (err) {
            showSaveError(err.message);
        }
    }

    function keepOnlyDigits(input, maxLength = null) {
        input.value = input.value.replace(/\D/g, "");
        if (maxLength !== null) input.value = input.value.slice(0, maxLength);
    }

    function bindColumnForm(form) {
        const question = data.questions[currentIndex];
        if (isSolved(question)) return;
        form.querySelectorAll("[data-borrow-index]").forEach((button) => {
            button.addEventListener("click", () => {
                const index = Number(button.dataset.borrowIndex);
                question.columnAnswer.borrows[index] = !question.columnAnswer.borrows[index];
                const active = question.columnAnswer.borrows[index];
                button.classList.toggle("column-borrow--active", active);
                button.setAttribute("aria-pressed", String(active));
                button.textContent = active ? "1" : "";
            });
        });
        const inputs = [...form.querySelectorAll("[data-result-index]")];
        inputs.forEach((input, position) => {
            input.addEventListener("input", () => {
                keepOnlyDigits(input, 1);
                question.columnAnswer.digits[Number(input.dataset.resultIndex)] = input.value;
                if (input.value && inputs[position + 1]) inputs[position + 1].focus();
            });
        });
        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            if (question.columnAnswer.digits.some((digit) => !digit)) {
                inputs.find((input) => !input.value)?.focus();
                return;
            }
            await submitInteractiveAnswer(question, {
                resultDigits: question.columnAnswer.digits.join(""),
                borrowColumns: question.columnAnswer.borrows,
            });
        });
    }

    function bindMissingForm(form) {
        const question = data.questions[currentIndex];
        if (isSolved(question)) return;
        const inputs = [...form.querySelectorAll("[data-answer-key]")];
        inputs.forEach((input, position) => {
            input.addEventListener("input", () => {
                keepOnlyDigits(input, 1);
                question.answerValues[input.dataset.answerKey] = input.value;
                if (input.value && inputs[position + 1]) inputs[position + 1].focus();
            });
        });
        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            if (inputs.some((input) => !input.value)) {
                inputs.find((input) => !input.value)?.focus();
                return;
            }
            await submitInteractiveAnswer(question, { values: question.answerValues });
        });
    }

    function bindErrorForm(form) {
        const question = data.questions[currentIndex];
        if (isSolved(question)) return;
        form.querySelectorAll("[data-error-column]").forEach((button) => {
            button.addEventListener("click", () => {
                question.selectedColumn = Number(button.dataset.errorColumn);
                form.querySelectorAll("[data-error-column]").forEach((item) => {
                    item.classList.toggle("error-column--selected", item === button);
                    item.classList.remove("error-column--wrong");
                });
            });
        });
        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            if (!Number.isInteger(question.selectedColumn)) return;
            await submitInteractiveAnswer(question, {
                selectedColumn: question.selectedColumn,
            });
        });
    }

    function bindMachineForm(form) {
        const question = data.questions[currentIndex];
        if (isSolved(question)) return;
        const inputs = [...form.querySelectorAll("[data-answer-key]")];
        inputs.forEach((input) => {
            input.addEventListener("input", () => {
                keepOnlyDigits(input);
                question.answerValues[input.dataset.answerKey] = input.value;
            });
        });
        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            if (inputs.some((input) => !input.value)) {
                inputs.find((input) => !input.value)?.focus();
                return;
            }
            await submitInteractiveAnswer(question, { values: question.answerValues });
        });
    }

    function bindDivisionColumnForm(form) {
        const question = data.questions[currentIndex];
        if (isSolved(question)) return;
        const quotient = form.querySelector(".division-quotient-input");
        const remainderInputs = [...form.querySelectorAll("[data-remainder-index]")];
        quotient.addEventListener("input", () => { keepOnlyDigits(quotient); question.divisionAnswer.quotient = quotient.value; });
        remainderInputs.forEach(input => input.addEventListener("input", () => { keepOnlyDigits(input); question.divisionAnswer.remainders[Number(input.dataset.remainderIndex)] = input.value; }));
        form.addEventListener("submit", async event => { event.preventDefault(); if (!quotient.value || remainderInputs.some(input => !input.value)) return; await submitInteractiveAnswer(question, question.divisionAnswer); });
    }

    function bindChainForm(form) {
        const question = data.questions[currentIndex];
        if (isSolved(question)) return;
        const inputs = [...form.querySelectorAll("[data-chain-index]")];
        inputs.forEach(input => input.addEventListener("input", () => { keepOnlyDigits(input); question.chainValues[Number(input.dataset.chainIndex)] = input.value; }));
        form.addEventListener("submit", async event => { event.preventDefault(); if (inputs.some(input => !input.value)) return; await submitInteractiveAnswer(question, { values: question.chainValues }); });
    }

    function bindStructuredValuesForm(form) {
        const question = data.questions[currentIndex];
        if (isSolved(question)) return;
        const inputs = [...form.querySelectorAll("[data-answer-key]")];
        inputs.forEach(input => input.addEventListener("input", () => { keepOnlyDigits(input); question.answerValues[input.dataset.answerKey] = input.value; }));
        form.addEventListener("submit", async event => { event.preventDefault(); if (inputs.some(input => !input.value)) return; await submitInteractiveAnswer(question, { values: question.answerValues }); });
    }

    function bindBaseValuesForm(form) {
        const question = data.questions[currentIndex];
        if (isSolved(question)) return;
        const inputs = [...form.querySelectorAll("[data-answer-key]")];
        inputs.forEach(input => input.addEventListener("input", () => {
            if (input.dataset.inputKind === "binary") input.value = input.value.replace(/[^01]/g, "");
            else if (input.dataset.inputKind === "text") input.value = input.value.replace(/[^A-Za-zĂÂÎȘȚăâîșț]/g, "").toUpperCase();
            else keepOnlyDigits(input, input.maxLength > 0 ? input.maxLength : null);
            question.answerValues[input.dataset.answerKey] = input.value;
        }));
        form.addEventListener("submit", async event => { event.preventDefault(); if (inputs.some(input => !input.value)) return; await submitInteractiveAnswer(question, {values: question.answerValues}); });
    }

    function bindBinaryToggleForm(form) {
        const question = data.questions[currentIndex];
        if (isSolved(question)) return;
        form.querySelectorAll("[data-bit-index]").forEach(button => button.addEventListener("click", () => {
            const bits = question.answerValues.bits.split("");
            const index = Number(button.dataset.bitIndex);
            bits[index] = bits[index] === "1" ? "0" : "1";
            question.answerValues.bits = bits.join("");
            renderQuestion(null, false);
        }));
        form.addEventListener("submit", async event => { event.preventDefault(); await submitInteractiveAnswer(question, {values: question.answerValues}); });
    }

    function bindUnitReductionForm(form) {
        const question = data.questions[currentIndex];
        if (isSolved(question)) return;

        form.querySelectorAll("[data-unit-key]").forEach(input => input.addEventListener("input", () => {
            keepOnlyDigits(input);
            question.answerValues[input.dataset.unitKey] = input.value;
        }));

        form.querySelectorAll("[data-unit-range]").forEach(input => {
            input.addEventListener("input", () => {
                const key = input.dataset.unitRange;
                question.answerValues[key] = input.value;
                form.querySelector(`[data-range-output="${key}"]`)?.replaceChildren(document.createTextNode(input.value));
                if (question.interactive.mode === "speed_simulator") {
                    const distance = Math.min(Number(input.value) * question.interactive.speed, question.interactive.target_distance);
                    form.querySelector("[data-speed-distance]")?.replaceChildren(document.createTextNode(String(distance)));
                    const marker = form.querySelector(".unit-speed-track span");
                    if (marker) marker.style.left = `${(distance / question.interactive.target_distance) * 100}%`;
                }
            });
            input.addEventListener("change", () => renderQuestion(null, false));
        });

        form.querySelectorAll("[data-unit-counter]").forEach(button => button.addEventListener("click", () => {
            const current = Number(question.answerValues.count || 0);
            const maximum = Number(button.dataset.unitMax || 30);
            question.answerValues.count = String(Math.max(0, Math.min(maximum, current + Number(button.dataset.unitCounter))));
            renderQuestion(null, false);
        }));

        form.querySelectorAll("[data-unit-choice-key]").forEach(button => button.addEventListener("click", () => {
            question.answerValues[button.dataset.unitChoiceKey] = button.dataset.unitChoice;
            renderQuestion(null, false);
        }));

        form.querySelectorAll("[data-unit-select]").forEach(select => select.addEventListener("change", () => {
            question.answerValues[select.dataset.unitSelect] = select.value;
        }));

        const placeOperation = (slotIndex, operation) => {
            question.answerValues[`operation:${slotIndex}`] = operation;
            question.activeUnitOperation = null;
            renderQuestion(null, false);
        };
        form.querySelectorAll("[data-operation-choice]").forEach(button => {
            button.addEventListener("click", () => {
                question.activeUnitOperation = button.dataset.operationChoice;
                renderQuestion(null, false);
            });
            button.addEventListener("dragstart", event => {
                event.dataTransfer.setData("text/plain", button.dataset.operationChoice);
                event.dataTransfer.effectAllowed = "copy";
            });
        });
        form.querySelectorAll("[data-operation-slot]").forEach(slot => {
            slot.addEventListener("click", () => {
                if (question.activeUnitOperation) placeOperation(Number(slot.dataset.operationSlot), question.activeUnitOperation);
            });
            slot.addEventListener("dragover", event => { event.preventDefault(); slot.classList.add("unit-operation-slot--over"); });
            slot.addEventListener("dragleave", () => slot.classList.remove("unit-operation-slot--over"));
            slot.addEventListener("drop", event => {
                event.preventDefault();
                placeOperation(Number(slot.dataset.operationSlot), event.dataTransfer.getData("text/plain"));
            });
        });

        form.addEventListener("submit", async event => {
            event.preventDefault();
            const required = Object.keys(question.interactive.answers);
            if (required.some(key => question.answerValues[key] === undefined || question.answerValues[key] === "")) return;
            await submitInteractiveAnswer(question, {values: question.answerValues});
        });
    }

    function bindComparisonForm(form) {
        const question = data.questions[currentIndex];
        if (isSolved(question)) return;
        form.querySelectorAll("[data-comparison-key]").forEach(input => input.addEventListener("input", () => {
            keepOnlyDigits(input);
            question.answerValues[input.dataset.comparisonKey] = input.value;
        }));
        form.querySelectorAll("[data-comparison-choice-key]").forEach(button => button.addEventListener("click", () => {
            question.answerValues[button.dataset.comparisonChoiceKey] = button.dataset.comparisonChoice;
            renderQuestion(null, false);
        }));
        form.querySelectorAll("[data-comparison-select]").forEach(select => select.addEventListener("change", () => {
            question.answerValues[select.dataset.comparisonSelect] = select.value;
        }));
        form.addEventListener("submit", async event => {
            event.preventDefault();
            const required = Object.keys(question.interactive.answers);
            if (required.some(key => question.answerValues[key] === undefined || question.answerValues[key] === "")) return;
            await submitInteractiveAnswer(question, {values: question.answerValues});
        });
    }

    function bindFigurativeForm(form) {
        const question = data.questions[currentIndex];
        if (isSolved(question)) return;
        form.querySelectorAll("[data-figurative-key]").forEach(input => input.addEventListener("input", () => {
            keepOnlyDigits(input); question.answerValues[input.dataset.figurativeKey] = input.value;
        }));
        form.querySelectorAll("[data-figurative-choice-key]").forEach(button => button.addEventListener("click", () => {
            question.answerValues[button.dataset.figurativeChoiceKey] = button.dataset.figurativeChoice; renderQuestion(null,false);
        }));
        form.querySelectorAll("[data-figurative-range]").forEach(input => input.addEventListener("input", () => {
            question.answerValues[input.dataset.figurativeRange] = input.value; renderQuestion(null,false);
        }));
        form.querySelectorAll("[data-figurative-select]").forEach(select => select.addEventListener("change", () => { question.answerValues[select.dataset.figurativeSelect] = select.value; }));
        form.querySelectorAll("[data-figurative-scheme]").forEach(button => button.addEventListener("click", () => {
            const value = button.dataset.figurativeScheme;
            if (question.interactive.mode === "choose_scheme") question.answerValues.scheme = value;
            else if (question.answerValues.first === undefined || question.answerValues.first === value || question.answerValues.second !== undefined) { question.answerValues = {first:value}; }
            else question.answerValues.second = value;
            renderQuestion(null,false);
        }));
        form.addEventListener("submit", async event => {
            event.preventDefault(); const required = Object.keys(question.interactive.answers);
            if (required.some(key => question.answerValues[key] === undefined || question.answerValues[key] === "")) return;
            await submitInteractiveAnswer(question,{values:question.answerValues});
        });
    }

    function bindReverseForm(form) {
        const question=data.questions[currentIndex]; if(isSolved(question))return;
        form.querySelectorAll("[data-reverse-key]").forEach(input=>input.addEventListener("input",()=>{ if(!input.dataset.reverseKey.startsWith("op:"))keepOnlyDigits(input); question.answerValues[input.dataset.reverseKey]=input.value; }));
        form.querySelectorAll("[data-reverse-select]").forEach(select=>select.addEventListener("change",()=>{question.answerValues[select.dataset.reverseSelect]=select.value;}));
        form.querySelectorAll("[data-reverse-choice-key]").forEach(button=>button.addEventListener("click",()=>{question.answerValues[button.dataset.reverseChoiceKey]=button.dataset.reverseChoice;renderQuestion(null,false);}));
        form.querySelectorAll("[data-reverse-range]").forEach(input=>input.addEventListener("input",()=>{question.answerValues[input.dataset.reverseRange]=input.value;renderQuestion(null,false);}));
        let dragged=null, selected=null;
        form.querySelectorAll("[data-reverse-drag-card]").forEach(card=>{
            card.addEventListener("dragstart",()=>{dragged=card.dataset.reverseDragCard;});
            card.addEventListener("click",()=>{selected=card.dataset.reverseDragCard; card.classList.add("is-selected");});
        });
        form.querySelectorAll("[data-reverse-drop]").forEach(zone=>{
            zone.addEventListener("dragover",event=>event.preventDefault());
            zone.addEventListener("drop",event=>{event.preventDefault();if(dragged){question.answerValues[zone.dataset.reverseDrop]=dragged;renderQuestion(null,false);}});
            zone.addEventListener("click",()=>{if(selected){question.answerValues[zone.dataset.reverseDrop]=selected;selected=null;}else delete question.answerValues[zone.dataset.reverseDrop];renderQuestion(null,false);});
        });
        form.addEventListener("submit",async event=>{event.preventDefault();const required=Object.keys(question.interactive.answers);if(required.some(key=>question.answerValues[key]===undefined||question.answerValues[key]===""))return;await submitInteractiveAnswer(question,{values:question.answerValues});});
    }

    function bindHypothesisForm(form){
        const question=data.questions[currentIndex];if(isSolved(question))return;
        form.querySelectorAll("[data-hypothesis-key]").forEach(input=>input.addEventListener("input",()=>{input.value=input.value.replace(/[^\d-]/g,"");question.answerValues[input.dataset.hypothesisKey]=input.value;}));
        form.querySelectorAll("[data-hypothesis-choice-key]").forEach(button=>button.addEventListener("click",()=>{question.answerValues[button.dataset.hypothesisChoiceKey]=button.dataset.hypothesisChoice;renderQuestion(null,false);}));
        form.addEventListener("submit",async event=>{event.preventDefault();const required=Object.keys(question.interactive.answers);if(required.some(key=>question.answerValues[key]===undefined||question.answerValues[key]===""))return;await submitInteractiveAnswer(question,{values:question.answerValues});});
    }

    function bindSingleValueForm(form) {
        const question = data.questions[currentIndex];
        if (isSolved(question)) return;
        const input = form.querySelector("[data-numeric-value]");
        input.addEventListener("input", () => { keepOnlyDigits(input); question.numericValue = input.value; });
        form.addEventListener("submit", async event => { event.preventDefault(); if (!input.value) return; await submitInteractiveAnswer(question, { value: question.numericValue }); });
    }

    function bindFactorBuilderForm(form) {
        const question = data.questions[currentIndex];
        if (isSolved(question)) return;
        const inputs = [...form.querySelectorAll("[data-answer-key]")];
        inputs.forEach((input) => {
            input.addEventListener("input", () => {
                keepOnlyDigits(input);
                question.answerValues[input.dataset.answerKey] = input.value;
            });
        });
        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            if (inputs.some((input) => !input.value)) {
                inputs.find((input) => !input.value)?.focus();
                return;
            }
            await submitInteractiveAnswer(question, {values: question.answerValues});
        });
    }

    function bindFactorErrorForm(form) {
        const question = data.questions[currentIndex];
        if (isSolved(question)) return;
        form.querySelectorAll("[data-factor-step]").forEach((button) => {
            button.addEventListener("click", () => {
                question.selectedStep = Number(button.dataset.factorStep);
                form.querySelectorAll("[data-factor-step]").forEach((item) => {
                    item.classList.toggle("factor-step--selected", item === button);
                    item.classList.remove("factor-step--wrong");
                });
            });
        });
        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            if (!Number.isInteger(question.selectedStep)) return;
            await submitInteractiveAnswer(question, {selectedStep: question.selectedStep});
        });
    }

    function bindFactorMatchForm(form) {
        const question = data.questions[currentIndex];
        if (isSolved(question)) return;
        form.querySelectorAll("[data-match-left]").forEach((button) => {
            button.addEventListener("click", () => {
                question.activeMatchLeft = Number(button.dataset.matchLeft);
                renderQuestion(null, false);
            });
            button.addEventListener("dragstart", event => {
                event.dataTransfer.setData("text/plain", button.dataset.matchLeft);
                event.dataTransfer.effectAllowed = "move";
                button.classList.add("base-match-card--dragging");
            });
            button.addEventListener("dragend", () => button.classList.remove("base-match-card--dragging"));
        });
        form.querySelectorAll("[data-match-right]").forEach((button) => {
            button.addEventListener("click", () => {
                if (!Number.isInteger(question.activeMatchLeft)) return;
                const rightIndex = Number(button.dataset.matchRight);
                Object.keys(question.matchValues).forEach((key) => {
                    if (Number(question.matchValues[key]) === rightIndex) delete question.matchValues[key];
                });
                question.matchValues[question.activeMatchLeft] = rightIndex;
                question.activeMatchLeft = null;
                renderQuestion(null, false);
            });
            button.addEventListener("dragover", event => { event.preventDefault(); button.classList.add("base-match-drop--over"); });
            button.addEventListener("dragleave", () => button.classList.remove("base-match-drop--over"));
            button.addEventListener("drop", event => {
                event.preventDefault();
                button.classList.remove("base-match-drop--over");
                const leftIndex = Number(event.dataTransfer.getData("text/plain"));
                if (!Number.isInteger(leftIndex)) return;
                const rightIndex = Number(button.dataset.matchRight);
                Object.keys(question.matchValues).forEach(key => { if (Number(question.matchValues[key]) === rightIndex) delete question.matchValues[key]; });
                question.matchValues[leftIndex] = rightIndex;
                question.activeMatchLeft = null;
                renderQuestion(null, false);
            });
        });
        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            if (Object.keys(question.matchValues).length !== question.interactive.pairs.length) return;
            await submitInteractiveAnswer(question, {values: question.matchValues});
        });
    }

    function bindPowerCompareForm(form) {
        const question = data.questions[currentIndex];
        if (isSolved(question)) return;
        form.querySelectorAll("[data-power-relation]").forEach(button => button.addEventListener("click", () => {
            question.selectedRelation = button.dataset.powerRelation;
            form.querySelectorAll("[data-power-relation]").forEach(item => {
                item.classList.toggle("power-relation-button--selected", item === button);
                item.classList.remove("power-relation-button--wrong");
            });
        }));
        form.addEventListener("submit", async event => {
            event.preventDefault();
            if (!question.selectedRelation) return;
            await submitInteractiveAnswer(question, {relation: question.selectedRelation});
        });
    }

    function bindPowerOrderForm(form) {
        const question = data.questions[currentIndex];
        if (isSolved(question)) return;
        form.querySelectorAll("[data-power-order-index]").forEach(button => button.addEventListener("click", () => {
            const index = Number(button.dataset.powerOrderIndex);
            const position = question.orderValues.indexOf(index);
            if (position === -1) question.orderValues.push(index);
            else question.orderValues.splice(position, 1);
            renderQuestion(null, false);
        }));
        form.addEventListener("submit", async event => {
            event.preventDefault();
            if (question.orderValues.length !== question.interactive.items.length) return;
            await submitInteractiveAnswer(question, {order: question.orderValues});
        });
    }

    function bindOperationSequenceForm(form) {
        const question = data.questions[currentIndex];
        if (isSolved(question)) return;
        form.querySelectorAll("[data-operation-step]").forEach(button => button.addEventListener("click", () => {
            const index = Number(button.dataset.operationStep);
            const position = question.operationOrder.indexOf(index);
            if (position === -1) question.operationOrder.push(index);
            else question.operationOrder.splice(position, 1);
            renderQuestion(null, false);
        }));
        form.addEventListener("submit", async event => {
            event.preventDefault();
            if (question.operationOrder.length !== question.interactive.steps.length) return;
            await submitInteractiveAnswer(question, {order: question.operationOrder});
        });
    }

    function bindDivisibilityValuesForm(form) {
        const question = data.questions[currentIndex];
        if (isSolved(question)) return;
        const inputs = [...form.querySelectorAll("[data-divisibility-key]")];
        inputs.forEach(input => input.addEventListener("input", () => {
            input.value = input.value.replace(/[^0-9, ]/g, "");
            question.answerValues[input.dataset.divisibilityKey] = input.value;
        }));
        form.addEventListener("submit", async event => {
            event.preventDefault();
            if (inputs.some(input => !input.value.trim())) return;
            await submitInteractiveAnswer(question, {values: question.answerValues});
        });
    }

    function bindDivisibilitySelectForm(form) {
        const question = data.questions[currentIndex];
        if (isSolved(question)) return;
        form.querySelectorAll("[data-divisibility-card]").forEach(button => button.addEventListener("click", () => {
            const id = button.dataset.divisibilityCard;
            const index = question.selectedDivisibilityIds.indexOf(id);
            if (index === -1) question.selectedDivisibilityIds.push(id);
            else question.selectedDivisibilityIds.splice(index, 1);
            button.classList.toggle("is-selected", index === -1);
            button.setAttribute("aria-pressed", String(index === -1));
        }));
        form.addEventListener("submit", async event => {
            event.preventDefault();
            if (!question.selectedDivisibilityIds.length) return;
            await submitInteractiveAnswer(question, {selectedIds: question.selectedDivisibilityIds});
        });
    }

    function bindDivisibilitySortForm(form) {
        const question = data.questions[currentIndex];
        if (isSolved(question)) return;
        const place = (cardId, zoneId) => {
            question.divisibilityPlacements[cardId] = zoneId;
            question.activeDivisibilityCard = null;
            renderQuestion(null, false);
        };
        form.querySelectorAll("[data-sort-card]").forEach(button => {
            button.addEventListener("click", event => {
                event.stopPropagation();
                question.activeDivisibilityCard = button.dataset.sortCard;
                renderQuestion(null, false);
            });
            button.addEventListener("dragstart", event => {
                event.dataTransfer.setData("text/plain", button.dataset.sortCard);
                event.dataTransfer.effectAllowed = "move";
            });
        });
        form.querySelectorAll("[data-sort-zone]").forEach(zone => {
            zone.addEventListener("click", () => { if (question.activeDivisibilityCard) place(question.activeDivisibilityCard, zone.dataset.sortZone); });
            zone.addEventListener("dragover", event => { event.preventDefault(); zone.classList.add("is-over"); });
            zone.addEventListener("dragleave", () => zone.classList.remove("is-over"));
            zone.addEventListener("drop", event => {
                event.preventDefault();
                zone.classList.remove("is-over");
                const cardId = event.dataTransfer.getData("text/plain");
                if (cardId) place(cardId, zone.dataset.sortZone);
            });
        });
        form.addEventListener("submit", async event => {
            event.preventDefault();
            if (Object.keys(question.divisibilityPlacements).length !== question.interactive.cards.length) return;
            await submitInteractiveAnswer(question, {placements: question.divisibilityPlacements});
        });
    }

    function bindCriteriaTableForm(form) {
        const question = data.questions[currentIndex];
        if (isSolved(question)) return;
        form.querySelectorAll("[data-criteria-key]").forEach(button => button.addEventListener("click", () => {
            const key = button.dataset.criteriaKey;
            question.criteriaValues[key] = !Boolean(question.criteriaValues[key]);
            button.classList.toggle("is-checked", question.criteriaValues[key]);
            button.setAttribute("aria-pressed", String(question.criteriaValues[key]));
            button.textContent = question.criteriaValues[key] ? "✓" : "×";
        }));
        form.addEventListener("submit", async event => {
            event.preventDefault();
            const values = {};
            Object.keys(question.interactive.answers).forEach(key => { values[key] = Boolean(question.criteriaValues[key]); });
            await submitInteractiveAnswer(question, {values});
        });
    }

    function bindPrimeWorkbenchForm(form) {
        const question = data.questions[currentIndex], item = question.interactive;
        if (isSolved(question)) return;
        form.querySelectorAll("[data-prime-key]").forEach(input => input.addEventListener("input", () => {
            input.value = input.value.replace(/\D/g, "");
            question.answerValues[input.dataset.primeKey] = input.value;
        }));
        form.querySelectorAll("[data-prime-class]").forEach(button => button.addEventListener("click", () => {
            question.answerValues.classification = button.dataset.primeClass;
            form.querySelectorAll("[data-prime-class]").forEach(choice => choice.classList.toggle("is-selected", choice === button));
        }));
        const toggleFactor = id => {
            const index = question.primeSelectedIds.indexOf(id);
            if (index >= 0) question.primeSelectedIds.splice(index, 1);
            else if (question.primeSelectedIds.length < item.slot_count) question.primeSelectedIds.push(id);
            renderQuestion(null, false);
        };
        form.querySelectorAll("[data-prime-factor]").forEach(button => {
            button.addEventListener("click", () => toggleFactor(button.dataset.primeFactor));
            button.addEventListener("dragstart", event => event.dataTransfer.setData("text/plain", button.dataset.primeFactor));
        });
        const factorZone = form.querySelector("[data-prime-factor-zone]");
        if (factorZone) {
            factorZone.addEventListener("dragover", event => event.preventDefault());
            factorZone.addEventListener("drop", event => { event.preventDefault(); const id = event.dataTransfer.getData("text/plain"); if (id) toggleFactor(id); });
        }
        form.querySelectorAll("[data-prime-perfect]").forEach(button => button.addEventListener("click", () => {
            const id = button.dataset.primePerfect, index = question.primeSelectedIds.indexOf(id);
            if (index >= 0) question.primeSelectedIds.splice(index, 1); else question.primeSelectedIds.push(id);
            button.classList.toggle("is-selected", index < 0);
        }));
        form.addEventListener("submit", async event => {
            event.preventDefault();
            const values = {...question.answerValues};
            if (item.mode === "factor_product") {
                if (question.primeSelectedIds.length !== item.slot_count) return;
                values.factors = question.primeSelectedIds.map(id => item.cards.find(card => card.id === id).value).sort((a, b) => a - b).join(",");
            }
            if (item.mode === "perfect_number") {
                values.divisors = question.primeSelectedIds.map(Number).sort((a, b) => a - b).join(",");
            }
            if (Object.keys(item.answers).some(key => values[key] === undefined || String(values[key]).trim() === "")) return;
            await submitInteractiveAnswer(question, {values});
        });
    }

    function bindDecimalWorkbenchForm(form) {
        const question = data.questions[currentIndex], item = question.interactive;
        if (isSolved(question)) return;
        form.querySelectorAll("[data-decimal-key]").forEach(input => input.addEventListener("input", () => {
            input.value = input.value.replace(/[^0-9,.]/g, "");
            question.answerValues[input.dataset.decimalKey] = input.value;
        }));
        form.querySelectorAll("[data-comma-place]").forEach(button => button.addEventListener("click", () => {
            question.answerValues.position = button.dataset.commaPlace;
            form.querySelectorAll("[data-comma-place]").forEach(choice => choice.classList.toggle("is-selected", choice === button));
        }));
        form.querySelectorAll("[data-vessel-level]").forEach(button => button.addEventListener("click", () => {
            question.answerValues.filled = button.dataset.vesselLevel;
            renderQuestion(null, false);
        }));
        form.addEventListener("submit", async event => {
            event.preventDefault();
            if (Object.keys(item.answers).some(key => question.answerValues[key] === undefined || String(question.answerValues[key]).trim() === "")) return;
            await submitInteractiveAnswer(question, {values: question.answerValues});
        });
    }

    function bindFractionVisualForm(form) {
        const question = data.questions[currentIndex];
        if (isSolved(question)) return;
        form.querySelectorAll("[data-fraction-segment]").forEach(segment => segment.addEventListener("click", () => {
            const index = Number(segment.dataset.fractionSegment);
            const position = question.fractionSelected.indexOf(index);
            if (position >= 0) question.fractionSelected.splice(position, 1);
            else question.fractionSelected.push(index);
            question.fractionSelected.sort((a, b) => a - b);
            renderQuestion(null, false);
        }));
        form.querySelectorAll("[data-fraction-key]").forEach(input => input.addEventListener("input", () => {
            keepOnlyDigits(input);
            question.answerValues[input.dataset.fractionKey] = input.value;
        }));
        form.querySelectorAll("[data-fraction-key]").forEach(input => input.addEventListener("change", () => {
            if (question.interactive.mode === "construct") renderQuestion(null, false);
        }));
        form.addEventListener("submit", async event => {
            event.preventDefault();
            const values = question.interactive.mode === "color"
                ? {selected: question.fractionSelected.join(",")}
                : question.answerValues;
            if (question.interactive.mode !== "color" && form.querySelectorAll("[data-fraction-key]").length && [...form.querySelectorAll("[data-fraction-key]")].some(input => !input.value)) return;
            await submitInteractiveAnswer(question, {values});
        });
    }

    function bindFractionDominoForm(form) {
        const question = data.questions[currentIndex];
        if (isSolved(question)) return;
        form.querySelectorAll("[data-domino-tile]").forEach(button => button.addEventListener("click", () => {
            const index = Number(button.dataset.dominoTile);
            const position = question.dominoOrder.indexOf(index);
            if (position >= 0) question.dominoOrder.splice(position, 1);
            else question.dominoOrder.push(index);
            renderQuestion(null, false);
        }));
        form.querySelector(".fraction-domino-clear")?.addEventListener("click", () => {
            question.dominoOrder = [];
            renderQuestion(null, false);
        });
        form.addEventListener("submit", async event => {
            event.preventDefault();
            if (question.dominoOrder.length !== question.interactive.tiles.length) return;
            await submitInteractiveAnswer(question, {order: question.dominoOrder});
        });
    }

    function bindFractionCompareForm(form) {
        const question = data.questions[currentIndex];
        if (isSolved(question)) return;
        form.querySelectorAll("[data-fraction-relation]").forEach(button => button.addEventListener("click", () => {
            question.fractionRelation = button.dataset.fractionRelation;
            renderQuestion(null, false);
        }));
        form.querySelectorAll("[data-fraction-order]").forEach(button => button.addEventListener("click", () => {
            const index = Number(button.dataset.fractionOrder);
            const position = question.fractionOrder.indexOf(index);
            if (position >= 0) question.fractionOrder.splice(position, 1);
            else question.fractionOrder.push(index);
            renderQuestion(null, false);
        }));
        form.querySelector(".fraction-order-clear")?.addEventListener("click", () => {
            question.fractionOrder = [];
            renderQuestion(null, false);
        });
        form.addEventListener("submit", async event => {
            event.preventDefault();
            if (question.interactive.mode === "order") {
                if (question.fractionOrder.length !== question.interactive.items.length) return;
                await submitInteractiveAnswer(question, {order: question.fractionOrder});
            } else {
                if (!question.fractionRelation) return;
                await submitInteractiveAnswer(question, {relation: question.fractionRelation});
            }
        });
    }

    function bindFractionAxisForm(form) {
        const question = data.questions[currentIndex];
        if (isSolved(question)) return;
        form.querySelectorAll("[data-axis-tick]").forEach(button => button.addEventListener("click", () => {
            question.selectedAxisTick = Number(button.dataset.axisTick);
            renderQuestion(null, false);
        }));
        form.addEventListener("submit", async event => {
            event.preventDefault();
            if (!Number.isInteger(question.selectedAxisTick)) return;
            await submitInteractiveAnswer(question, {selectedTick: question.selectedAxisTick});
        });
    }

    function bindLessonValuesForm(form) {
        const question = data.questions[currentIndex];
        if (isSolved(question)) return;
        form.querySelectorAll("[data-lesson-key]").forEach(input => input.addEventListener("input", () => {
            input.value = input.value.replace(/[^0-9, ]/g, "");
            question.answerValues[input.dataset.lessonKey] = input.value;
        }));
        form.querySelectorAll("[data-gcd-choice]").forEach(button => button.addEventListener("click", () => {
            const selected = new Set(String(question.answerValues.common || "").split(",").filter(Boolean));
            const value = button.dataset.gcdChoice;
            if (selected.has(value)) selected.delete(value); else selected.add(value);
            question.answerValues.common = [...selected].map(Number).sort((a,b) => a-b).join(",");
            renderQuestion(null, false);
        }));
        form.querySelectorAll("[data-lcm-choice]").forEach(button => button.addEventListener("click", () => {
            const selected = new Set(String(question.answerValues.common || "").split(",").filter(Boolean));
            const value = button.dataset.lcmChoice;
            if (selected.has(value)) selected.delete(value); else selected.add(value);
            question.answerValues.common = [...selected].map(Number).sort((a,b) => a-b).join(",");
            renderQuestion(null, false);
        }));
        form.addEventListener("submit", async event => {
            event.preventDefault();
            if ([...form.querySelectorAll("[data-lesson-key]")].some(input => !input.value)) return;
            await submitInteractiveAnswer(question, {values: question.answerValues});
        });
    }

    function bindParenthesesForm(form) {
        const question = data.questions[currentIndex];
        if (isSolved(question)) return;

        let activeSymbol = null;
        let draggedSymbol = null;
        const localError = form.querySelector(".paren-local-error");

        const clearDropHighlights = () => {
            form.querySelectorAll(".paren-slot--over").forEach((slot) => {
                slot.classList.remove("paren-slot--over");
            });
        };

        const placeSymbol = (symbol, index) => {
            question.placement[symbol] = index;
            activeSymbol = null;
            renderQuestion(null, false);
        };

        form.querySelectorAll("[data-symbol]").forEach((tile) => {
            tile.addEventListener("dragstart", (event) => {
                const symbol = tile.dataset.symbol;
                draggedSymbol = symbol;
                event.dataTransfer.setData("text/plain", symbol);
                event.dataTransfer.effectAllowed = "move";
            });
            tile.addEventListener("dragend", () => {
                draggedSymbol = null;
                clearDropHighlights();
            });
            tile.addEventListener("click", (event) => {
                event.stopPropagation();
                activeSymbol = tile.dataset.symbol;
                form.querySelectorAll("[data-symbol]").forEach((item) =>
                    item.classList.toggle("paren-tile--active", item.dataset.symbol === activeSymbol)
                );
            });
            tile.addEventListener("pointerdown", (event) => {
                if (event.button !== 0) return;
                const symbol = tile.dataset.symbol;
                const startX = event.clientX;
                const startY = event.clientY;
                tile.classList.add("paren-tile--dragging");

                const finishPointerDrag = (upEvent) => {
                    tile.classList.remove("paren-tile--dragging");
                    document.removeEventListener("pointerup", finishPointerDrag);
                    clearDropHighlights();
                    const moved =
                        Math.abs(upEvent.clientX - startX) > 8 ||
                        Math.abs(upEvent.clientY - startY) > 8;
                    if (!moved) return;
                    const target = document
                        .elementFromPoint(upEvent.clientX, upEvent.clientY)
                        ?.closest(".paren-slot");
                    if (
                        target &&
                        form.contains(target) &&
                        target.dataset.accepts === symbol
                    ) {
                        placeSymbol(symbol, Number(target.dataset.slotIndex));
                    }
                };

                document.addEventListener("pointerup", finishPointerDrag);
            });
        });

        form.querySelectorAll(".paren-slot").forEach((slot) => {
            slot.addEventListener("dragover", (event) => {
                if (draggedSymbol === slot.dataset.accepts) {
                    event.preventDefault();
                    clearDropHighlights();
                    slot.classList.add("paren-slot--over");
                } else {
                    slot.classList.remove("paren-slot--over");
                }
            });
            slot.addEventListener("dragleave", () => slot.classList.remove("paren-slot--over"));
            slot.addEventListener("drop", (event) => {
                event.preventDefault();
                const symbol = event.dataTransfer.getData("text/plain");
                clearDropHighlights();
                draggedSymbol = null;
                if (
                    (symbol === "open" || symbol === "close") &&
                    slot.dataset.accepts === symbol
                ) {
                    placeSymbol(symbol, Number(slot.dataset.slotIndex));
                }
            });
            slot.addEventListener("click", () => {
                if (activeSymbol && slot.dataset.accepts === activeSymbol) {
                    placeSymbol(activeSymbol, Number(slot.dataset.slotIndex));
                }
            });
        });

        form.querySelector(".paren-clear")?.addEventListener("click", () => {
            clearDropHighlights();
            question.placement = { open: null, close: null };
            renderQuestion(null, false);
        });

        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            hideSaveError();
            const placement = question.placement;
            if (
                !Number.isInteger(placement.open) ||
                !Number.isInteger(placement.close) ||
                placement.open >= placement.close
            ) {
                if (localError) localError.hidden = false;
                return;
            }

            try {
                await submitInteractiveAnswer(question, placement);
            } catch (err) {
                showSaveError(err.message);
            }
        });
    }

    function navigateTo(index, pushState) {
        if (index < 0 || index >= data.questions.length || index === currentIndex) {
            return;
        }
        currentIndex = index;
        hideSaveError();
        renderQuestion(null, false);
        if (pushState) {
            history.pushState({ index }, "", trainingUrl(index));
        }
    }

    if (prevArrow) {
        prevArrow.addEventListener("click", (event) => {
            if (prevArrow.classList.contains("training-arrow--placeholder")) {
                return;
            }
            event.preventDefault();
            navigateTo(currentIndex - 1, true);
        });
    }

    if (nextArrow) {
        nextArrow.addEventListener("click", (event) => {
            if (nextArrow.classList.contains("training-arrow--placeholder")) {
                return;
            }
            event.preventDefault();
            navigateTo(currentIndex + 1, true);
        });
    }

    if (gridEl) {
        gridEl.addEventListener("click", (event) => {
            const cell = event.target.closest("[data-training-index]");
            if (!cell) {
                return;
            }
            event.preventDefault();
            navigateTo(parseInt(cell.dataset.trainingIndex, 10), true);
        });
    }

    window.addEventListener("popstate", (event) => {
        const index =
            event.state && typeof event.state.index === "number"
                ? event.state.index
                : parseIndexFromUrl();
        if (index !== currentIndex) {
            currentIndex = index;
            hideSaveError();
            renderQuestion(null, false);
        }
    });

    try {
        validatePayload(data);
        currentIndex = parseIndexFromUrl();
        buildGrid();
        renderQuestion(null, false);
        history.replaceState({ index: currentIndex }, "", trainingUrl(currentIndex));
        revealPage();
    } catch (err) {
        showBootError(err.message || "Nu am putut încărca antrenarea.");
    }
})();
