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
                "geometry_canvas",
                "operation_sequence",
                "operation_workbench",
                "divisibility_values",
                "divisibility_select",
                "divisibility_sort",
                "divisibility_error",
                "criteria_table",
                "prime_workbench",
                "decimal_workbench",
                "statistics_chart",
                "algebra_workbench",
                "fraction_visual",
                "fraction_domino",
                "fraction_compare",
                "fraction_axis",
                "gcd_workbench",
                "fraction_scale",
                "fraction_reduce_path",
                "lcm_workbench",
                "common_denominator",
                "fraction_product",
                "fraction_division",
                "fraction_power",
                "fraction_percent",
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
            `<label class="division-step"><span>${escapeHtml(item.step_labels?.[index] || (index === item.remainders.length - 1 ? "Rest final" : `Rest după cifra ${index + 1}`))}</span><input data-remainder-index="${index}" inputmode="numeric" value="${escapeHtml(question.divisionAnswer.remainders[index])}"${solved ? " disabled" : ""}></label>`
        ).join("");
        return `<form class="training-division-column-form interactive-form">` +
            `<div class="division-equation"><strong>${escapeHtml(item.display_dividend ?? item.dividend)}</strong><span>:</span><strong>${escapeHtml(item.display_divisor ?? item.divisor)}</strong><span>=</span><input class="division-quotient-input" inputmode="decimal" aria-label="Câtul împărțirii" value="${escapeHtml(question.divisionAnswer.quotient)}"${solved ? " disabled" : ""}></div>` +
            `<p class="interactive-instruction">${escapeHtml(item.instruction || "Completează câtul și restul obținut după coborârea fiecărei cifre. Restul final trebuie să fie mai mic decât împărțitorul.")}</p>` +
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

    function geometryRomanianLabel(value){
        const labels={point:"punct",line:"dreaptă",segment:"segment",segments:"segmente",ray:"semidreaptă",plane:"plan",halfplane:"semiplan",plain_line:"linie",notation:"notație",on:"aparține",off:"nu aparține",cap:"capăt",origine:"origine",arrow:"săgeată",remove_arrows:"elimină săgețile",keep_one_arrow:"păstrează o singură săgeată",add_two_arrows:"adaugă două săgeți",horizontal:"orizontală",vertical:"verticală",diagonal:"oblică",upper:"deasupra",lower:"dedesubt",collinear:"coliniare",noncollinear:"necoliniare",parallel:"paralele",concurrent:"concurente",identical:"identice",same:"de aceeași parte",opposite:"de părți diferite",all_collinear:"toate coliniare",no_three_collinear:"nici trei coliniare",three_collinear:"trei coliniare",general:"poziție generală",two_rows:"două rânduri",all_parallel:"toate paralele",all_concurrent:"toate concurente",pairwise:"intersecții distincte",two_parallel_one_secant:"două paralele și o secantă",three_lines:"trei drepte",two_point_lines:"două drepte cu puncte",free:"poziție liberă"};
        return labels[String(value)]||String(value).replaceAll("_"," ");
    }

    function geometryFigureSvg(figure, compact=false) {
        const kind=figure.kind, label=figure.label||figure.notation||"",angle=Number(figure.angle)||0;
        let shape="";
        if(kind==="point") shape=`<circle cx="${220+(Number(figure.variant)||0)*18}" cy="80" r="7" class="geo-point"></circle>${label?`<text x="${236+(Number(figure.variant)||0)*18}" y="70" class="geo-notation">${escapeHtml(label)}</text>`:""}`;
        else if(kind==="line"){
            const namedPoints=/^[A-ZĂÂÎȘȚ]{2}$/.test(label)?`<circle cx="150" cy="80" r="6" class="geo-point"></circle><circle cx="290" cy="80" r="6" class="geo-point"></circle><text x="140" y="60" class="geo-notation">${escapeHtml(label[0])}</text><text x="286" y="60" class="geo-notation">${escapeHtml(label[1])}</text>`:"";
            shape=`<g transform="rotate(${angle} 220 80)"><line x1="55" y1="80" x2="385" y2="80" class="geo-line"></line><path d="M55 80l14-8v16zM385 80l-14-8v16z" class="geo-arrow"></path>${namedPoints}</g>${label&&!namedPoints?`<text x="350" y="62" class="geo-notation">${escapeHtml(label)}</text>`:""}`;
        }
        else if(kind==="point_line") shape='<line x1="45" y1="90" x2="395" y2="90" class="geo-line geo-boundary"></line><path d="M45 90l14-8v16zM395 90l-14-8v16z" class="geo-arrow"></path>';
        else if(kind==="line_pair"||kind==="parallel"){
            const relation=kind==="parallel"?"parallel":figure.relation;
            if(relation==="concurrent")shape='<line x1="65" y1="125" x2="375" y2="35" class="geo-line"></line><line x1="65" y1="35" x2="375" y2="125" class="geo-line geo-line--accent"></line>';
            else if(relation==="identical")shape='<line x1="55" y1="80" x2="385" y2="80" class="geo-line geo-line--wide"></line><line x1="55" y1="80" x2="385" y2="80" class="geo-line geo-line--accent"></line>';
            else shape='<line x1="55" y1="55" x2="385" y2="55" class="geo-line"></line><line x1="55" y1="110" x2="385" y2="110" class="geo-line geo-line--accent"></line>';
        }
        else if(kind==="spokes"){
            const count=Math.max(1,Number(figure.count)||3);
            shape=Array.from({length:count},(_,index)=>{const angle=index*Math.PI/count,x=Math.cos(angle)*180,y=Math.sin(angle)*70;return `<line x1="${220-x}" y1="${80-y}" x2="${220+x}" y2="${80+y}" class="geo-line${index%2?' geo-line--accent':''}"></line>`;}).join("")+ '<circle cx="220" cy="80" r="6" class="geo-point"></circle>';
        }
        else if(kind==="points"){
            const count=Math.max(1,Number(figure.count)||4);
            shape=Array.from({length:count},(_,index)=>{const x=75+(index%4)*95,y=55+Math.floor(index/4)*65+(index%2)*18;return `<circle cx="${x}" cy="${y}" r="6" class="geo-point"></circle><text x="${x+10}" y="${y-8}">${String.fromCharCode(65+index)}</text>`;}).join("");
        }
        else if(kind==="two_point_lines") shape='<line x1="45" y1="55" x2="395" y2="55" class="geo-line"></line><line x1="45" y1="115" x2="395" y2="115" class="geo-line geo-line--accent"></line>';
        else if(kind==="three_lines"){
            const lineCase=figure.case||"all_parallel";
            if(lineCase==="all_concurrent")shape='<line x1="45" y1="80" x2="395" y2="80" class="geo-line"></line><line x1="70" y1="135" x2="370" y2="25" class="geo-line geo-line--accent"></line><line x1="70" y1="25" x2="370" y2="135" class="geo-line"></line><circle cx="220" cy="80" r="6" class="geo-point"></circle>';
            else if(lineCase==="pairwise")shape='<line x1="55" y1="125" x2="385" y2="45" class="geo-line"></line><line x1="55" y1="35" x2="385" y2="115" class="geo-line geo-line--accent"></line><line x1="95" y1="140" x2="335" y2="20" class="geo-line"></line>';
            else if(lineCase==="two_parallel_one_secant")shape='<line x1="45" y1="50" x2="395" y2="50" class="geo-line"></line><line x1="45" y1="115" x2="395" y2="115" class="geo-line geo-line--accent"></line><line x1="130" y1="145" x2="310" y2="20" class="geo-line"></line>';
            else shape='<line x1="45" y1="40" x2="395" y2="40" class="geo-line"></line><line x1="45" y1="80" x2="395" y2="80" class="geo-line geo-line--accent"></line><line x1="45" y1="120" x2="395" y2="120" class="geo-line"></line>';
        }
        else if(kind==="segment") shape=`<g transform="rotate(${angle} 220 80)"><line x1="90" y1="80" x2="350" y2="80" class="geo-line"></line><line x1="90" y1="66" x2="90" y2="94" class="geo-cap"></line><line x1="350" y1="66" x2="350" y2="94" class="geo-cap"></line><circle cx="90" cy="80" r="6" class="geo-point"></circle><circle cx="350" cy="80" r="6" class="geo-point"></circle>${label.length>=2?`<text x="78" y="58" class="geo-notation">${escapeHtml(label[0])}</text><text x="350" y="58" class="geo-notation">${escapeHtml(label[1])}</text>`:""}</g>`;
        else if(kind==="ray") shape=`<g transform="rotate(${angle} 220 80)"><line x1="90" y1="80" x2="375" y2="80" class="geo-line"></line><line x1="90" y1="66" x2="90" y2="94" class="geo-cap"></line><path d="M385 80l-16-9v18z" class="geo-arrow"></path><circle cx="90" cy="80" r="6" class="geo-point"></circle><circle cx="270" cy="80" r="6" class="geo-point"></circle>${label.length>=2?`<text x="78" y="58" class="geo-notation">${escapeHtml(label[0])}</text><text x="265" y="60" class="geo-notation">${escapeHtml(label[1])}</text>`:""}</g>`;
        else if(kind==="plane") shape=`<polygon points="105,35 355,35 320,125 70,125" class="geo-plane"></polygon><text x="105" y="112" class="geo-plane-label">${escapeHtml(label||"α")}</text>`;
        else if(kind==="halfplane") shape=`<polygon points="55,25 385,25 350,80 75,80" class="geo-half"></polygon><polygon points="75,80 350,80 320,140 35,140" class="geo-plane"></polygon><line x1="65" y1="80" x2="360" y2="80" class="geo-line geo-boundary"></line><text x="115" y="59" class="geo-plane-label">ρ</text><text x="295" y="122" class="geo-plane-label">π</text><text x="344" y="72" class="geo-boundary-label">${escapeHtml(figure.boundary_label||"d")}</text>`;
        else shape='<line x1="90" y1="80" x2="350" y2="80" class="geo-line"></line>';
        const extra=(figure.points||[]).map(point=>`<g><circle cx="${point.x}" cy="${point.y}" r="5" class="geo-point"></circle><text x="${point.x+9}" y="${point.y-9}">${escapeHtml(point.name)}</text></g>`).join("");
        return `<svg class="geometry-figure${compact?" is-compact":""}" viewBox="0 0 440 160" role="img" aria-label="${escapeHtml(geometryRomanianLabel(kind))}">${shape}${extra}</svg>`;
    }

    function geometryPointCanvas(question, solved) {
        const item=question.interactive, exact=["place_points","reconstruct_model","full_geometry_puzzle"].includes(item.mode);
        if(!question.geometryInitialized){
            (item.points||[]).forEach((point,index)=>{
                if(question.answerValues[point.name]!==undefined)return;
                if(item.mode==="full_geometry_puzzle")question.answerValues[point.name]=`${45+index*65},155`;
                else question.answerValues[point.name]=`${Math.max(25,Math.min(415,point.x+(exact?(index%2?70:-70):0)))},${Math.max(25,Math.min(160,point.y+(exact?45:0)))}`;
            });
            question.geometryInitialized=true;
        }
        const targets=exact?(item.points||[]).map(point=>`<g class="geo-target"><circle cx="${point.x}" cy="${point.y}" r="16"></circle><text x="${point.x}" y="${point.y+4}" text-anchor="middle">${escapeHtml(point.name)}</text></g>`).join(""):"";
        const points=(item.points||[]).map(point=>{const [x,y]=String(question.answerValues[point.name]).split(",").map(Number);return `<g class="geo-draggable" data-geometry-point="${escapeHtml(point.name)}" transform="translate(${x} ${y})"${solved?" aria-disabled=\"true\"":""}><circle r="9"></circle><text x="12" y="-10">${escapeHtml(point.name)}</text></g>`;}).join("");
        return `<svg class="geometry-canvas" viewBox="0 0 440 180"><defs><pattern id="geometry-grid" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0H0V20" fill="none" stroke="rgba(255,255,255,.09)" stroke-width="1"></path></pattern></defs><rect width="440" height="180" fill="url(#geometry-grid)"></rect>${item.figures?.map(fig=>geometryEmbeddedShape(fig)).join("")||""}${targets}${points}</svg>`;
    }

    function geometryEmbeddedShape(figure){
        if(figure.kind==="plane")return `<polygon points="85,30 365,30 335,145 55,145" class="geo-plane"></polygon><text x="90" y="132" class="geo-plane-label">${escapeHtml(figure.label||"α")}</text>`;
        if(figure.kind==="line")return `<line x1="35" y1="90" x2="405" y2="90" class="geo-line"></line>${figure.label?`<text x="382" y="76" class="geo-boundary-label">${escapeHtml(figure.label)}</text>`:""}`;
        if(figure.kind==="ray")return `<line x1="90" y1="90" x2="395" y2="90" class="geo-line"></line><line x1="90" y1="73" x2="90" y2="107" class="geo-cap"></line><path d="M405 90l-16-9v18z" class="geo-arrow"></path><circle cx="90" cy="90" r="6" class="geo-point"></circle><text x="76" y="68" class="geo-notation">${escapeHtml((figure.label||"M")[0])}</text>`;
        if(figure.kind==="line_pair"){
            if(figure.relation==="concurrent")return '<line x1="35" y1="145" x2="405" y2="35" class="geo-line"></line><line x1="35" y1="35" x2="405" y2="145" class="geo-line geo-line--accent"></line>';
            if(figure.relation==="identical")return '<line x1="35" y1="90" x2="405" y2="90" class="geo-line geo-line--wide"></line><line x1="35" y1="90" x2="405" y2="90" class="geo-line geo-line--accent"></line>';
            return '<line x1="35" y1="60" x2="405" y2="60" class="geo-line"></line><line x1="35" y1="120" x2="405" y2="120" class="geo-line geo-line--accent"></line>';
        }
        return "";
    }

    function geometryChoices(question,key,choices,solved,labels=null){
        return `<div class="geometry-choices">${choices.map((value,index)=>`<button type="button" data-geometry-choice-key="${escapeHtml(key)}" data-geometry-choice="${escapeHtml(value)}" class="${String(question.answerValues[key])===String(value)?"is-selected":""}"${solved?" disabled":""}>${escapeHtml(labels?.[index]||geometryRomanianLabel(value))}</button>`).join("")}</div>`;
    }

    function geometryRelationManipulator(question,solved){
        const item=question.interactive,values=question.answerValues,start=item.figures?.[0]?.relation||"parallel",target=item.answers.relation;
        if(!question.geometryRelationInitialized){
            const relation=solved?target:start;
            values.line_angle=String(relation==="concurrent"?40:0);
            values.line_y=String(relation==="identical"?70:120);
            question.geometryRelationInitialized=true;
        }
        const angle=Number(values.line_angle||0),lineY=Number(values.line_y||120),parallelAngle=Math.min(Math.abs(angle%180),Math.abs(180-(angle%180)))<=5;
        const relation=parallelAngle?(Math.abs(lineY-70)<=8?"identical":"parallel"):"concurrent";
        values.relation=relation;
        return `<div class="geometry-relation-workbench"><svg class="geometry-canvas" viewBox="0 0 440 180"><defs><pattern id="geometry-relation-grid" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0H0V20" fill="none" stroke="rgba(255,255,255,.08)" stroke-width="1"></path></pattern></defs><rect width="440" height="180" fill="url(#geometry-relation-grid)"></rect><line x1="35" y1="70" x2="405" y2="70" class="geo-line"></line><text x="388" y="57" class="geo-notation">a</text><g transform="rotate(${angle} 220 ${lineY})"><line x1="35" y1="${lineY}" x2="405" y2="${lineY}" class="geo-line geo-line--accent"></line></g><text x="388" y="${Math.min(165,lineY+22)}" class="geo-notation">b</text></svg><p class="geometry-relation-result">Poziția obținută: <b>${escapeHtml(geometryRomanianLabel(relation))}</b></p><div class="geometry-tool-controls"><label><span>înclinarea dreptei b: <b data-geometry-output="line_angle">${angle}</b>°</span><input type="range" min="0" max="90" step="5" value="${angle}" data-geometry-range="line_angle"${solved?" disabled":""}></label><label><span>poziția dreptei b: <b data-geometry-output="line_y">${lineY}</b></span><input type="range" min="45" max="135" step="5" value="${lineY}" data-geometry-range="line_y"${solved?" disabled":""}></label></div></div>`;
    }

    function geometryConstructionCanvas(question,solved){
        const item=question.interactive,points=item.points||[],first=question.answerValues.first,second=question.answerValues.second,tool=question.answerValues.tool;
        const a=points.find(point=>point.name===first),b=points.find(point=>point.name===second);
        let drawing="";
        if(a&&b&&tool){
            const vx=b.x-a.x,vy=b.y-a.y,length=Math.hypot(vx,vy)||1,ux=vx/length,uy=vy/length;
            if(tool==="segment")drawing=`<line x1="${a.x}" y1="${a.y}" x2="${b.x}" y2="${b.y}" class="geometry-drawn-line"></line>`;
            else if(tool==="ray")drawing=`<line x1="${a.x}" y1="${a.y}" x2="${a.x+ux*300}" y2="${a.y+uy*300}" class="geometry-drawn-line"></line><path d="M${a.x+ux*310} ${a.y+uy*310}l-16-9v18z" class="geo-arrow" transform="rotate(${Math.atan2(vy,vx)*180/Math.PI} ${a.x+ux*310} ${a.y+uy*310})"></path>`;
            else if(tool==="line")drawing=`<line x1="${a.x-ux*260}" y1="${a.y-uy*260}" x2="${a.x+ux*360}" y2="${a.y+uy*360}" class="geometry-drawn-line"></line>`;
        }
        const pointSvg=points.map(point=>`<button></button><g class="geo-pickable${point.name===first||point.name===second?" is-selected":""}" data-geometry-pick-point="${escapeHtml(point.name)}"><circle cx="${point.x}" cy="${point.y}" r="10"></circle><text x="${point.x+14}" y="${point.y-10}">${escapeHtml(point.name)}</text></g>`).join("").replaceAll("<button></button>","");
        return `<p class="interactive-instruction">Alege instrumentul, apoi apasă pe cele două puncte în ordinea cerută. Figura se desenează imediat.</p>${geometryChoices(question,"tool",item.tools,solved)}<svg class="geometry-canvas" viewBox="0 0 440 180"><defs><pattern id="geometry-construction-grid" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0H0V20" fill="none" stroke="rgba(255,255,255,.09)" stroke-width="1"></path></pattern></defs><rect width="440" height="180" fill="url(#geometry-construction-grid)"></rect>${drawing}${pointSvg}</svg>`;
    }

    function geometryBoundaryCanvas(question,solved){
        const item=question.interactive,side=question.answerValues.side||"",boundary=question.answerValues.boundary||item.initial_boundary||"";
        let fills='<polygon points="70,25 370,25 340,90 55,90" class="geo-plane"></polygon><polygon points="55,90 340,90 310,155 35,155" class="geo-plane"></polygon>';
        if(side==="upper")fills='<polygon points="70,25 370,25 340,90 55,90" class="geo-half geo-half--active"></polygon><polygon points="55,90 340,90 310,155 35,155" class="geo-plane"></polygon>';
        if(side==="lower")fills='<polygon points="70,25 370,25 340,90 55,90" class="geo-plane"></polygon><polygon points="55,90 340,90 310,155 35,155" class="geo-half geo-half--active"></polygon>';
        const angle=boundary==="vertical"?90:boundary==="diagonal"?-22:0;
        const line=(boundary||item.mode==="choose_halfplane")?`<line x1="55" y1="90" x2="370" y2="90" class="geo-line geo-boundary" transform="rotate(${angle} 220 90)"></line><text x="355" y="78" class="geo-boundary-label">d</text>`:"";
        const choices=item.mode==="choose_halfplane"?geometryChoices(question,"side",item.choices,solved):geometryChoices(question,"boundary",item.choices,solved);
        return `<p class="interactive-instruction">Alege poziția, iar desenul se modifică imediat.</p><svg class="geometry-canvas geometry-boundary-canvas" viewBox="0 0 440 180">${fills}${line}<text x="90" y="145" class="geo-plane-label">α</text></svg>${choices}`;
    }

    function geometryDragSlots(question,solved){
        const item=question.interactive,palette=item.labels||item.choices||[],left=question.answerValues.left||"",right=question.answerValues.right||"";
        const marker=(value,side)=>{
            const x=side==="left"?90:350;
            if(value==="arrow")return `<path d="M${x} 80l${side==="left"?16:-16}-10v20z" class="geo-arrow"></path>`;
            if(value==="cap"||value==="origine")return `<line x1="${x}" y1="63" x2="${x}" y2="97" class="geo-cap"></line><circle cx="${x}" cy="80" r="6" class="geo-point"></circle>`;
            if(value)return `<circle cx="${x}" cy="80" r="7" class="geo-point"></circle><text x="${x+(side==="left"?-15:10)}" y="58" class="geo-notation">${escapeHtml(value)}</text>`;
            return "";
        };
        const tiles=palette.map(value=>`<button type="button" draggable="true" data-geometry-drag-value="${escapeHtml(value)}" class="geometry-drag-tile${question.geometryPalette===String(value)?" is-selected":""}"${solved?" disabled":""}>${escapeHtml(geometryRomanianLabel(value))}</button>`).join("");
        const slot=(side,value)=>`<button type="button" data-geometry-drop-slot="${side}" class="geometry-drop-slot"${solved?" disabled":""}><b>${side==="left"?"stânga":"dreapta"}</b><span>${value?escapeHtml(geometryRomanianLabel(value)):"trage aici"}</span></button>`;
        return `<p class="interactive-instruction">Trage etichetele sau marcajele în cele două locuri. Pe telefon le poți apăsa pe rând.</p><div class="geometry-drag-palette">${tiles}</div><svg class="geometry-canvas" viewBox="0 0 440 160"><line x1="90" y1="80" x2="350" y2="80" class="geo-line"></line>${marker(left,"left")}${marker(right,"right")}</svg><div class="geometry-drop-row">${slot("left",left)}${slot("right",right)}</div>`;
    }

    function geometryEdgeBuilder(question,solved){
        const item=question.interactive,points=item.points||[],selected=new Set(String(question.answerValues.edges||"").split(",").filter(Boolean));
        const byName=Object.fromEntries(points.map(point=>[point.name,point]));
        const lines=[...selected].map(edge=>{const a=byName[edge[0]],b=byName[edge[1]];return a&&b?`<line x1="${a.x}" y1="${a.y}" x2="${b.x}" y2="${b.y}" class="geometry-drawn-line"></line>`:"";}).join("");
        const nodes=points.map(point=>`<g class="geo-pickable${question.geometryEdgeStart===point.name?" is-selected":""}" data-geometry-edge-point="${escapeHtml(point.name)}"><circle cx="${point.x}" cy="${point.y}" r="10"></circle><text x="${point.x+14}" y="${point.y-10}">${escapeHtml(point.name)}</text></g>`).join("");
        return `<p class="interactive-instruction">Unește punctele două câte două apăsând pe capetele fiecărui segment.</p><svg class="geometry-canvas" viewBox="0 0 440 180"><defs><pattern id="geometry-edge-grid" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0H0V20" fill="none" stroke="rgba(255,255,255,.09)" stroke-width="1"></path></pattern></defs><rect width="440" height="180" fill="url(#geometry-edge-grid)"></rect>${lines}${nodes}</svg>`;
    }

    function geometryStaticPointCanvas(question){
        const item=question.interactive;
        return `<svg class="geometry-canvas" viewBox="0 0 440 180"><line x1="35" y1="90" x2="405" y2="90" class="geo-line"></line>${(item.points||[]).map(point=>`<circle cx="${point.x}" cy="90" r="7" class="geo-point"></circle><text x="${point.x-5}" y="68" class="geo-notation">${escapeHtml(point.name)}</text>`).join("")}</svg>`;
    }

    function geometryFields(question,solved,keys=null){
        const reserved=new Set(["figure","kind","tool","target","origin","membership","side","boundary","answer","error","repair","selected","edges","conditions","first","second","left","right"]);
        const selected=keys||Object.keys(question.interactive.answers).filter(key=>!reserved.has(key)&&!key.startsWith("match:")&&!key.startsWith("position:"));
        return `<div class="geometry-fields">${selected.map(key=>`<label>${escapeHtml(geometryRomanianLabel(key))}<input data-geometry-key="${escapeHtml(key)}" value="${escapeHtml(question.answerValues[key]??"")}"${solved?" disabled":""}></label>`).join("")}</div>`;
    }

    function geometryToolWorkbench(question,solved){
        const item=question.interactive, expected=item.answers||{}, limits=item.tool_limits||{}, values=question.answerValues;
        Object.keys(expected).forEach(key=>{if(key!=="through"&&values[key]===undefined)values[key]=String(key.includes("angle")?90:key.endsWith("_x")?160:50);});
        const current=(key,fallback)=>Number(values[key]??fallback);
        const rulerAngle=current("ruler_angle",90),rulerX=current("ruler_x",160),rulerY=current("ruler_y",45);
        const squareAngle=current("square_angle",90),squareX=current("square_x",290),squareY=current("square_y",120);
        const lineAngle=current("line_angle",90),rad=lineAngle*Math.PI/180,dx=Math.cos(rad)*210,dy=Math.sin(rad)*90;
        const ruler=item.show_ruler?`<g class="geometry-ruler" transform="translate(${rulerX} ${rulerY}) rotate(${rulerAngle})"><rect x="-145" y="-14" width="290" height="28" rx="4"></rect>${Array.from({length:29},(_,i)=>`<line x1="${-140+i*10}" y1="-14" x2="${-140+i*10}" y2="${i%5===0?2:-5}"></line>`).join("")}<text x="0" y="7" text-anchor="middle">RIGLĂ</text></g>`:"";
        const square=item.show_square?`<g class="geometry-set-square" transform="translate(${squareX} ${squareY}) rotate(${squareAngle})"><path d="M-72 48H72L-72-48Z M-43 27H24L-43-17Z" fill-rule="evenodd"></path><text x="-34" y="39">ECHER</text></g>`:"";
        const points=(item.points||[]).map(point=>`<circle cx="${point.x}" cy="${point.y}" r="6" class="geo-point"></circle><text x="${point.x+10}" y="${point.y-9}">${escapeHtml(point.name)}</text>`).join("");
        const drawn=expected.line_angle!==undefined?`<line x1="${220-dx}" y1="${90-dy}" x2="${220+dx}" y2="${90+dy}" class="geometry-drawn-line"></line>`:"";
        const controls=Object.keys(expected).filter(key=>key!=="through").map(key=>{
            const type=key.includes("angle")?"angle":key.endsWith("_x")?"x":"y",range=limits[type]||[type==="angle"?0:30,type==="angle"?175:360,type==="angle"?5:10],fallback=type==="angle"?90:type==="x"?160:50;
            const labels={ruler_angle:"unghiul riglei",ruler_x:"poziția riglei stânga–dreapta",ruler_y:"poziția riglei sus–jos",square_angle:"unghiul echerului",square_x:"poziția echerului stânga–dreapta",square_y:"poziția echerului sus–jos",line_angle:"unghiul dreptei trasate"};
            return `<label><span>${escapeHtml(labels[key]||key.replaceAll("_"," "))}: <b data-geometry-output="${key}">${current(key,fallback)}</b></span><input type="range" min="${range[0]}" max="${range[1]}" step="${range[2]}" value="${current(key,fallback)}" data-geometry-range="${key}"${solved?" disabled":""}></label>`;
        }).join("");
        const through=expected.through!==undefined?geometryChoices(question,"through",[...(item.points||[]).map(point=>point.name),"free"].filter((value,index,array)=>array.indexOf(value)===index),solved,[...(item.points||[]).map(point=>`prin ${point.name}`),"poziție liberă"]):"";
        return `<div class="geometry-tool-workbench"><svg class="geometry-canvas" viewBox="0 0 440 180"><defs><pattern id="geometry-tool-grid" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0H0V20" fill="none" stroke="rgba(255,255,255,.08)" stroke-width="1"></path></pattern></defs><rect width="440" height="180" fill="url(#geometry-tool-grid)"></rect>${(item.figures||[]).map(geometryEmbeddedShape).join("")}${drawn}${points}${ruler}${square}</svg><div class="geometry-tool-controls">${controls}</div>${through}</div>`;
    }

    function geometryCanvasHtml(question){
        const solved=isSolved(question),item=question.interactive,mode=item.mode;
        if(!question.answerValues)question.answerValues={};
        if(solved)Object.entries(item.answers).forEach(([key,value])=>{question.answerValues[key]=String(value);});
        let body="";
        if(mode==="choose_figure"){
            body=`<div class="geometry-card-grid">${item.figures.map((figure,index)=>`<button type="button" data-geometry-choice-key="figure" data-geometry-choice="${index}" class="${String(question.answerValues.figure)===String(index)?"is-selected":""}"${solved?" disabled":""}><b>${String.fromCharCode(65+index)}</b>${geometryFigureSvg(figure,true)}</button>`).join("")}</div>`;
        }else if(mode==="construct_figure"){
            body=geometryConstructionCanvas(question,solved);
        }else if(["transform_figure","label_endpoints","complete_markers"].includes(mode)){
            body=geometryDragSlots(question,solved);
        }else if(["place_points","coincidence","place_noncollinear","place_collinear","reconstruct_model","point_on_line","repair_membership","move_to_collinear"].includes(mode)){
            body=`<p class="interactive-instruction">Trage punctele.</p>${geometryPointCanvas(question,solved)}`;
        }else if(mode==="plane_points"){
            body=`<p class="interactive-instruction">Trage punctele: primul în plan, al doilea în afara lui.</p>${geometryPointCanvas(question,solved)}`;
        }else if(["split_plane","move_boundary","choose_halfplane"].includes(mode)){
            body=geometryBoundaryCanvas(question,solved);
        }else if(mode==="build_triangle"){
            body=geometryEdgeBuilder(question,solved);
        }else if(mode==="line_counter"){
            body=geometryEdgeBuilder(question,solved);
        }else if(["min_lines","max_lines","arrange_line_count"].includes(mode)){
            body=`<p class="interactive-instruction">Trage punctele.</p>${geometryPointCanvas(question,solved)}`;
        }else if(["enumerate_segments","containing_segments"].includes(mode)){
            body=`${geometryStaticPointCanvas(question)}${geometryFields(question,solved,["segments"])}`;
        }else if(mode==="full_geometry_puzzle"){
            body=`${geometryPointCanvas(question,solved)}${geometryChoices(question,"tool",item.tools,solved)}${geometryFields(question,solved,["notation"])}`;
        }else if(["match_figure","match_notation","match_relation_notation","sort_relations"].includes(mode)){
            const options=mode==="match_figure"?item.labels:mode==="sort_relations"?item.labels:item.notations;
            body=`<div class="geometry-match">${item.figures.map((figure,index)=>`<section>${geometryFigureSvg(figure,true)}<select data-geometry-select="match:${index}"${solved?" disabled":""}><option value="">Alege</option>${options.map(value=>`<option value="${escapeHtml(value)}"${question.answerValues[`match:${index}`]===value?" selected":""}>${escapeHtml(geometryRomanianLabel(value))}</option>`).join("")}</select></section>`).join("")}</div>`;
        }else if(mode==="select_figures"){
            const selected=new Set(String(question.answerValues.selected||"").split(",").filter(Boolean));
            body=`<div class="geometry-card-grid">${item.figures.map((figure,index)=>`<button type="button" data-geometry-multi="selected" data-geometry-value="${index}" class="${selected.has(String(index))?"is-selected":""}"${solved?" disabled":""}>${geometryFigureSvg(figure,true)}</button>`).join("")}</div>`;
        }else if(mode==="instruction_sequence"||mode==="order_tool_steps"){
            body=`<div class="geometry-sequence">${item.steps.map((_,position)=>`<label><b>${position+1}</b><select data-geometry-select="position:${position}"${solved?" disabled":""}><option value="">Alege</option>${item.steps.map((step,index)=>`<option value="${index}"${String(question.answerValues[`position:${position}`])===String(index)?" selected":""}>${escapeHtml(step)}</option>`).join("")}</select></label>`).join("")}</div>`;
        }else if(mode==="visual_true_false"){
            body=`${geometryFigureSvg(item.figures[0])}<p class="geometry-statement">${escapeHtml(item.statement)}</p>${geometryChoices(question,"answer",["true","false"],solved,["Adevărat","Fals"])}`;
        }else if(mode==="notation_detective"){
            body=`<div class="geometry-notation-list">${item.notations.map((value,index)=>`<button type="button" data-geometry-choice-key="error" data-geometry-choice="${index}" class="${String(question.answerValues.error)===String(index)?"is-selected":""}"${solved?" disabled":""}>${escapeHtml(value)}</button>`).join("")}</div>`;
        }else if(mode==="construction_checker"&&item.validation){
            body=`<p class="interactive-instruction">Trage punctele, apoi alege figura construită.</p>${geometryPointCanvas(question,solved)}${geometryChoices(question,"tool",item.tools,solved)}`;
        }else if(mode==="construction_checker"||mode==="multi_condition"){
            const active=new Set(String(question.geometryConditions||"").split(",").filter(Boolean));
            body=`${geometryPointCanvas(question,solved)}<div class="geometry-checklist">${item.conditions.map((condition,index)=>`<button type="button" data-geometry-condition="${index}" class="${active.has(String(index))?"is-selected":""}"${solved?" disabled":""}>✓ ${escapeHtml(condition)}</button>`).join("")}</div>`;
        }else if(["make_concurrent","make_parallel","make_identical","transform_relation","repair_relation"].includes(mode)){
            body=geometryRelationManipulator(question,solved);
        }else if(["ruler_line","position_ruler","ruler_set_square_parallel","place_set_square","slide_set_square","parallel_through_point","continue_construction","repair_tools","draw_concurrent","draw_parallel","draw_identical"].includes(mode)){
            body=geometryToolWorkbench(question,solved);
        }else{
            body=(item.figures||[]).map(figure=>geometryFigureSvg(figure)).join("");
            const choiceMap={construct_figure:["tool",item.tools],identify_figure:["kind",item.choices],repair_drawing:["repair",item.choices],transform_figure:["target",item.choices],choose_origin:["origin",item.choices],complete_markers:null,point_membership:["membership",item.choices],split_plane:["boundary",item.choices],choose_halfplane:["side",item.choices],move_boundary:["boundary",item.choices]};
            if(item.choice_key)body+=item.multi?geometryMultiText(question,item.choice_key,item.choices,solved,item.labels):geometryChoices(question,item.choice_key,item.choices,solved,item.labels);
            else if(choiceMap[mode])body+=geometryChoices(question,choiceMap[mode][0],choiceMap[mode][1],solved);
            if(mode==="construct_figure")body+=geometryChoices(question,"first",item.points.map(p=>p.name),solved)+geometryChoices(question,"second",item.points.map(p=>p.name),solved);
            else if(mode==="label_endpoints")body+=geometryChoices(question,"left",item.labels,solved)+geometryChoices(question,"right",item.labels,solved);
            else if(mode==="complete_markers")body+=geometryChoices(question,"left",item.choices,solved)+geometryChoices(question,"right",item.choices,solved);
            else if(mode==="build_triangle")body+=geometryMultiText(question,"edges",["AB","AC","BC","MN","MP","NP"],solved);
            else if(mode==="plane_points")body+=geometryChoices(question,"inside",item.points.map(p=>p.name),solved)+geometryChoices(question,"outside",item.points.map(p=>p.name),solved);
            else if(mode==="containing_segments"||mode==="enumerate_segments")body+=geometryFields(question,solved,["segments"]);
            else if(mode==="reverse_ray"||mode==="complete_notation")body+=geometryFields(question,solved,["notation"]);
            else if(!item.choice_key)body+=geometryFields(question,solved);
        }
        return `<form class="training-geometry-form interactive-form">${body}${solved?"":'<button type="submit" class="btn btn-press">Verifică răspunsul</button>'}</form>`;
    }

    function geometryMultiText(question,key,choices,solved,labels=null){
        const selected=new Set(String(question.answerValues[key]||"").split(",").filter(Boolean));
        return `<div class="geometry-choices">${choices.map((value,index)=>`<button type="button" data-geometry-multi="${key}" data-geometry-value="${value}" class="${selected.has(String(value))?"is-selected":""}"${solved?" disabled":""}>${escapeHtml(labels?.[index]??geometryRomanianLabel(value))}</button>`).join("")}</div>`;
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
        const acceptsFraction = String(key).includes("fraction");
        return `<input class="decimal-input" data-decimal-key="${escapeHtml(key)}" inputmode="${acceptsFraction ? "text" : "decimal"}" aria-label="${escapeHtml(label)}" value="${escapeHtml(question.answerValues[key] || "")}"${solved ? " disabled" : ""}>`;
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
        } else if (item.mode === "classification") {
            body = `<p class="interactive-instruction">${escapeHtml(item.instruction || "Pentru fiecare fracție, alege tipul formei zecimale.")}</p><div class="decimal-classification">${item.items.map(entry => `<section><strong>${escapeHtml(entry.label)}</strong><div>${item.categories.map(category => `<button type="button" data-decimal-class-key="class:${escapeHtml(entry.id)}" data-decimal-class-value="${escapeHtml(category.value)}" class="${question.answerValues[`class:${entry.id}`] === category.value ? "is-selected" : ""}"${solved ? " disabled" : ""}>${escapeHtml(category.label)}</button>`).join("")}</div></section>`).join("")}</div>`;
        } else if (item.mode === "period_select") {
            body = `<div class="decimal-period-display">${escapeHtml(item.display)}</div><p class="interactive-instruction">Apasă grupul de cifre care reprezintă perioada.</p><div class="decimal-period-choices">${item.choices.map(choice => `<button type="button" data-decimal-choice-key="period" data-decimal-choice-value="${escapeHtml(choice)}" class="${question.answerValues.period === String(choice) ? "is-selected" : ""}"${solved ? " disabled" : ""}>${escapeHtml(choice)}</button>`).join("")}</div>`;
        } else if (item.mode === "period_notation") {
            body = `<div class="decimal-period-notation"><span>${escapeHtml(item.prefix)}(</span>${decimalField(question, "period", "Perioada", solved)}<span>)</span></div><p class="interactive-instruction">Completează cifrele care trebuie scrise între paranteze.</p>`;
        } else if (item.mode === "average_balance") {
            const value = question.answerValues.missing ?? item.initial;
            body = `<p class="interactive-instruction">Mută cursorul până când media ajunge la valoarea cerută.</p><div class="decimal-average-balance"><section><span>Numere cunoscute</span><strong>${item.known_values.map(escapeHtml).join(" · ")}</strong></section><div class="decimal-average-beam"><span>media ${escapeHtml(item.target)}</span></div><section><label>Numărul lipsă: <b data-average-value>${escapeHtml(value)}</b></label><input type="range" min="${item.min}" max="${item.max}" step="${item.step}" value="${escapeHtml(value)}" data-average-range${solved ? " disabled" : ""}></section></div>`;
        }
        return `<form class="training-decimal-workbench-form interactive-form">${body}${solved ? "" : '<button type="submit" class="btn btn-press">Verifică răspunsul</button>'}</form>`;
    }

    function statisticsInput(question, key, label, solved) {
        return `<input class="decimal-input" data-stat-key="${escapeHtml(key)}" inputmode="decimal" aria-label="${escapeHtml(label)}" value="${escapeHtml(question.answerValues[key] || "")}"${solved ? " disabled" : ""}>`;
    }

    function statisticsChartSvg(question, line = false) {
        const item = question.interactive, solved = isSolved(question), W = 620, H = 300, L = 52, T = 18, B = 46;
        const ph = H - T - B, pw = W - L - 18, max = item.max_value, step = item.step || Math.max(1, Math.ceil(max / 5));
        const current = item.values.map((value, i) => solved ? value : Number(question.answerValues?.[`value:${i}`] ?? (item.mode === "repair_bar" ? item.shown_values[i] : (["build_bar","build_line"].includes(item.mode) ? 0 : value))));
        const grid = Array.from({length: Math.floor(max / step) + 1}, (_, i) => { const v=i*step,y=T+ph-v/max*ph; return `<g><line x1="${L}" y1="${y}" x2="${L+pw}" y2="${y}" class="stat-grid-line"/><text x="${L-8}" y="${y+4}" text-anchor="end">${v}</text></g>`; }).join("");
        const gap = pw / item.labels.length;
        const labels = item.labels.map((label,i)=>`<text x="${L+gap*(i+.5)}" y="${H-18}" text-anchor="middle">${escapeHtml(label)}</text>`).join("");
        let marks;
        if (line) {
            const pts=current.map((v,i)=>[L+gap*(i+.5),T+ph-v/max*ph]);
            marks=`<path d="${pts.map((p,i)=>`${i?'L':'M'}${p[0]},${p[1]}`).join(' ')}" class="stat-line-path"/>`+pts.map((p,i)=>`<circle cx="${p[0]}" cy="${p[1]}" r="9" role="button" tabindex="0" aria-label="${escapeHtml(item.labels[i])}: ${current[i]}" data-stat-choice="${i}" class="stat-point${String(question.answerValues?.selected)===String(i)?' is-selected':''}"/>`).join("");
        } else {
            marks=current.map((v,i)=>{const h=v/max*ph,x=L+gap*i+gap*.18;return `<rect x="${x}" y="${T+ph-h}" width="${gap*.64}" height="${h}" rx="5" role="button" tabindex="0" aria-label="${escapeHtml(item.labels[i])}: ${v}" data-stat-choice="${i}" class="stat-bar${String(question.answerValues?.selected)===String(i)?' is-selected':''}"/>`;}).join("");
        }
        return `<svg class="statistics-chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="${line?'Grafic cu linii':'Grafic cu bare'}">${grid}<line x1="${L}" y1="${T}" x2="${L}" y2="${T+ph}" class="stat-axis"/><line x1="${L}" y1="${T+ph}" x2="${L+pw}" y2="${T+ph}" class="stat-axis"/>${marks}${labels}</svg>`;
    }

    function statisticsChartHtml(question) {
        const item=question.interactive, solved=isSolved(question); if(!question.answerValues)question.answerValues={};
        if(solved)Object.entries(item.answers).forEach(([k,v])=>question.answerValues[k]=String(v));
        let body="";
        if(["read_bar","build_bar","repair_bar","read_line","build_line"].includes(item.mode)){
            if(["build_bar","repair_bar","build_line"].includes(item.mode)){
                body=`<div class="statistics-table-wrap"><table class="statistics-table statistics-source-table"><caption>Date de reprezentat</caption><thead><tr>${item.labels.map(label=>`<th>${escapeHtml(label)}</th>`).join("")}</tr></thead><tbody><tr>${item.values.map(value=>`<td>${escapeHtml(value)}</td>`).join("")}</tr></tbody></table></div>`;
            }
            body+=statisticsChartSvg(question,item.mode.includes("line"));
            if(["build_bar","repair_bar","build_line"].includes(item.mode)) body+=`<div class="statistics-sliders">${item.labels.map((label,i)=>{const v=question.answerValues[`value:${i}`]??(item.mode==="repair_bar"?item.shown_values[i]:0);return `<label><span>${escapeHtml(label)}: <b>${v}</b></span><input type="range" min="0" max="${item.max_value}" step="${item.step||1}" value="${v}" data-stat-range="value:${i}"${solved?' disabled':''}></label>`;}).join("")}</div>`;
            else body+=`<p class="interactive-instruction">Apasă direct bara sau punctul cerut.</p>`;
        } else if(["frequency_table","relative_frequency"].includes(item.mode)){
            body=`<div class="statistics-raw">${(item.raw_values||[]).map(v=>`<span>${escapeHtml(v)}</span>`).join("")}</div><div class="statistics-table-wrap"><table class="statistics-table"><thead><tr><th>Categorie</th><th>Frecvență</th>${item.mode==="relative_frequency"?'<th>Procent</th>':''}</tr></thead><tbody>${item.categories.map((c,i)=>`<tr><th>${escapeHtml(c)}</th><td>${statisticsInput(question,`frequency:${i}`,`Frecvența pentru ${c}`,solved)}</td>${item.mode==="relative_frequency"?`<td>${statisticsInput(question,`percent:${i}`,`Procentul pentru ${c}`,solved)}%</td>`:''}</tr>`).join("")}</tbody></table></div>`;
        } else {
            body=`<div class="statistics-dataset">${item.dataset.map(v=>`<span>${escapeHtml(v)}</span>`).join("")}</div><div class="decimal-fields">${item.fields.map(f=>`<label>${escapeHtml(f.label)}${statisticsInput(question,f.key,f.label,solved)}</label>`).join("")}</div>`;
        }
        return `<form class="training-statistics-form interactive-form">${body}${solved?'':'<button type="submit" class="btn btn-press">Verifică răspunsul</button>'}</form>`;
    }

    function algebraField(question, field, solved) {
        const value = question.answerValues?.[field.key] ?? "";
        return `<label class="algebra-field"><span>${escapeHtml(field.label)}</span><input data-algebra-key="${escapeHtml(field.key)}" type="text" inputmode="text" autocomplete="off" autocapitalize="off" spellcheck="false" value="${escapeHtml(value)}" aria-label="${escapeHtml(field.label)}"${solved ? " disabled" : ""}></label>`;
    }

    function algebraKeyboardHtml(item, solved) {
        if (solved || !(item.fields || []).length) return "";
        const source = [item.expression, item.identity, item.target, ...(item.stages || [])].filter(Boolean).join(" ");
        const letters = [...new Set((source.match(/[a-zA-Z]/g) || []).map(letter => letter.toLowerCase()))].slice(0, 8);
        const numericOnly = ["average", "verify_identity"].includes(item.mode);
        const symbols = numericOnly
            ? ["7", "8", "9", "4", "5", "6", "1", "2", "3", "0", ",", "/", "+", "−", "·", "(", ")"]
            : ["7", "8", "9", "4", "5", "6", "1", "2", "3", "0", ...letters, "+", "−", "·", "/", "(", ")", "=", "√", "²", "³", "ⁿ"];
        const unique = [...new Set(symbols)];
        return `<section class="algebra-keyboard" aria-label="Tastatură matematică"><div class="algebra-keyboard-head"><strong>Tastatură matematică</strong><span>Apasă întâi căsuța în care vrei să scrii.</span></div><div class="algebra-keyboard-keys">${unique.map(symbol => `<button type="button" data-math-key="${escapeHtml(symbol)}" aria-label="Inserează ${escapeHtml(symbol)}">${escapeHtml(symbol)}</button>`).join("")}<button type="button" data-math-action="left" aria-label="Mută cursorul la stânga">←</button><button type="button" data-math-action="right" aria-label="Mută cursorul la dreapta">→</button><button type="button" data-math-action="backspace" aria-label="Șterge ultimul simbol">⌫</button><button type="button" data-math-action="clear" class="is-clear" aria-label="Golește căsuța">C</button></div></section>`;
    }

    function algebraWorkbenchHtml(question) {
        const item = question.interactive, solved = isSolved(question);
        if (!question.answerValues) question.answerValues = {};
        if (solved) Object.entries(item.answers).forEach(([key, value]) => { question.answerValues[key] = String(value); });
        const form = body => `<form class="training-algebra-form interactive-form"><div class="algebra-board">${body}${algebraKeyboardHtml(item, solved)}</div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică răspunsul</button>'}</form>`;
        const fields = () => `<div class="algebra-fields">${(item.fields || []).map(field => algebraField(question, field, solved)).join("")}</div>`;

        if (["simplify", "complete_rule", "radical_steps", "unknown", "average"].includes(item.mode)) {
            const stages = (item.stages || []).map((stage, index) => `<div class="algebra-stage"><b>${index + 1}</b><span>${escapeHtml(stage)}</span></div>`).join("");
            return form(`${item.expression ? `<div class="algebra-expression">${escapeHtml(item.expression)}</div>` : ""}${stages ? `<div class="algebra-stages">${stages}</div>` : ""}${fields()}`);
        }
        if (["true_false", "compare", "parentheses"].includes(item.mode)) {
            const selected = String(question.answerValues.choice ?? "");
            return form(`${item.expression ? `<div class="algebra-expression">${escapeHtml(item.expression)}</div>` : ""}<div class="algebra-choice-row">${item.choices.map((choice, index) => `<button type="button" data-algebra-choice="${index}" class="${selected === String(index) ? "is-selected" : ""}"${solved ? " disabled" : ""}>${escapeHtml(choice)}</button>`).join("")}</div>`);
        }
        if (["match", "classify"].includes(item.mode)) {
            const options = item.options || item.pairs.map(pair => pair.right);
            return form(`<div class="algebra-match-board">${item.pairs.map((pair, index) => `<label><strong>${escapeHtml(pair.left)}</strong><span>→</span><select data-algebra-key="match:${index}"${solved ? " disabled" : ""}><option value="">Alege</option>${options.map((option, optionIndex) => `<option value="${optionIndex}"${String(question.answerValues[`match:${index}`] ?? "") === String(optionIndex) ? " selected" : ""}>${escapeHtml(option)}</option>`).join("")}</select></label>`).join("")}</div>`);
        }
        if (item.mode === "error") {
            const selected = String(question.answerValues.error ?? "");
            return form(`<p class="interactive-instruction">Apasă primul pas greșit.</p><div class="algebra-error-steps">${item.steps.map((step, index) => `<button type="button" data-algebra-error="${index}" class="${selected === String(index) ? "is-selected" : ""}"${solved ? " disabled" : ""}><b>${index + 1}</b><span>${escapeHtml(step)}</span></button>`).join("")}</div>`);
        }
        if (item.mode === "identity_builder") {
            const selected = String(question.answerValues.pieces ?? "").split(",").filter(Boolean).map(Number);
            return form(`<div class="algebra-expression">${escapeHtml(item.target)}</div><p class="interactive-instruction">Apasă piesele în ordinea în care apar în membrul drept.</p><div class="algebra-piece-pool">${item.pieces.map((piece, index) => `<button type="button" data-algebra-piece="${index}" class="${selected.includes(index) ? "is-selected" : ""}"${solved ? " disabled" : ""}>${escapeHtml(piece)}</button>`).join("")}</div><div class="algebra-built-expression">${selected.map(index => `<span>${escapeHtml(item.pieces[index])}</span>`).join("") || "Construcția ta apare aici"}</div>`);
        }
        if (item.mode === "verify_identity") {
            const selected = String(question.answerValues.verdict ?? "");
            return form(`<div class="algebra-expression">${escapeHtml(item.identity)}</div><div class="algebra-values">${item.values.map(value => `<span>${escapeHtml(value)}</span>`).join("")}</div>${fields()}<div class="algebra-choice-row">${["Identitatea se verifică", "Identitatea nu se verifică"].map((choice, index) => `<button type="button" data-algebra-verdict="${index}" class="${selected === String(index) ? "is-selected" : ""}"${solved ? " disabled" : ""}>${choice}</button>`).join("")}</div>`);
        }
        if (item.mode === "transform_chain") {
            return form(`<div class="algebra-expression">${escapeHtml(item.expression)}</div><div class="algebra-chain">${item.steps.map((step, index) => `<label><span>Pasul ${index + 1}</span><select data-algebra-key="step:${index}"${solved ? " disabled" : ""}><option value="">Alege transformarea</option>${step.options.map((option, optionIndex) => `<option value="${optionIndex}"${String(question.answerValues[`step:${index}`] ?? "") === String(optionIndex) ? " selected" : ""}>${escapeHtml(option)}</option>`).join("")}</select></label>`).join("")}</div>`);
        }
        return form(fields());
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
        const fractionInputs = (prefix, numeratorLabel = "Numărător", denominatorLabel = "Numitor") => `<span class="fraction-card">${lessonField(question,`${prefix}_numerator`,numeratorLabel,solved)}<i></i>${lessonField(question,`${prefix}_denominator`,denominatorLabel,solved)}</span>`;
        const operationChoices = () => `<div class="fraction-operation-choices">${["+", "-"].map(operation => `<button type="button" data-fraction-operation="${operation}" class="fraction-operation-choice${String(question.answerValues.operator || "") === operation ? " is-selected" : ""}"${solved ? " disabled" : ""}>${operation}</button>`).join("")}</div>`;
        if (item.mode === "calculate") {
            const transformed = side => `<span class="fraction-card">${lessonField(question,`${side}_numerator`,`Numărătorul ${side === "left" ? "primei" : "celei de-a doua"} fracții`,solved)}<i></i>${lessonField(question,"common_denominator","Numitor comun",solved)}</span>`;
            return `<form class="training-common-denominator-form interactive-form"><p class="interactive-instruction">Adu fracțiile la același numitor, efectuează operația și scrie rezultatul ireductibil.</p><div class="fraction-operation-row">${fractionCardHtml(item.left)}<b>${item.operation}</b>${fractionCardHtml(item.right)}</div><div class="fraction-workflow"><div>${transformed("left")}<b>${item.operation}</b>${transformed("right")}</div><span>→</span>${fractionInputs("result","Numărător rezultat","Numitor rezultat")}</div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică rezolvarea</button>'}</form>`;
        }
        if (item.mode === "missing_term" || item.mode === "inverse") {
            const missing = fractionInputs("missing","Numărător lipsă","Numitor lipsă");
            const left = item.missing_side === "left" ? missing : fractionCardHtml(item.left);
            const right = item.missing_side === "right" ? missing : fractionCardHtml(item.right);
            return `<form class="training-common-denominator-form interactive-form"><p class="interactive-instruction">Completează fracția lipsă astfel încât egalitatea să fie adevărată.</p><div class="fraction-operation-row">${left}<b>${item.operation}</b>${right}<b>=</b>${fractionCardHtml(item.result)}</div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică fracția</button>'}</form>`;
        }
        if (item.mode === "operator") {
            return `<form class="training-common-denominator-form interactive-form"><p class="interactive-instruction">Alege operația care face egalitatea adevărată.</p><div class="fraction-operation-row">${fractionCardHtml(item.left)}${operationChoices()}${fractionCardHtml(item.right)}<b>=</b>${fractionCardHtml(item.result)}</div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică operația</button>'}</form>`;
        }
        if (item.mode === "problem") {
            return `<form class="training-common-denominator-form interactive-form"><p class="interactive-instruction">Alege operația sugerată de problemă și completează rezultatul ireductibil.</p><div class="fraction-operation-row">${fractionCardHtml(item.left)}${operationChoices()}${fractionCardHtml(item.right)}<b>=</b>${fractionInputs("result","Numărător rezultat","Numitor rezultat")}</div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică răspunsul</button>'}</form>`;
        }
        if (item.mode === "mixed") {
            return `<form class="training-common-denominator-form interactive-form"><p class="interactive-instruction">Calculează și scrie rezultatul ca număr mixt ireductibil.</p><div class="fraction-operation-row">${fractionCardHtml(item.left)}<b>${item.operation}</b>${fractionCardHtml(item.right)}<b>=</b><span class="mixed-number">${lessonField(question,"whole","Partea întreagă",solved)}${fractionInputs("mixed","Numărătorul părții fracționare","Numitorul părții fracționare")}</span></div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică numărul mixt</button>'}</form>`;
        }
        if (item.mode === "order_steps") {
            const chosen = String(question.answerValues.order || "").split(",").filter(value => value !== "").map(Number);
            const card = (index, placed) => `<button type="button" data-fraction-step="${index}" class="fraction-step-card${placed ? " is-placed" : ""}"${solved ? " disabled" : ""}><b>${placed ? chosen.indexOf(index) + 1 : "•"}</b><span>${escapeHtml(item.steps[index])}</span></button>`;
            const pool = item.display_order.filter(index => !chosen.includes(index)).map(index => card(index,false)).join("");
            const result = chosen.map(index => card(index,true)).join("");
            return `<form class="training-common-denominator-form interactive-form"><p class="interactive-instruction">Apasă pașii în ordinea în care trebuie efectuat calculul. Un pas așezat poate fi retras.</p><div class="fraction-step-pool">${pool || "Toți pașii au fost așezați."}</div><div class="fraction-step-result">${result || "Ordinea construită va apărea aici."}</div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică ordinea</button>'}</form>`;
        }
        if (item.mode === "match") {
            const options = item.result_order.map(index => `<option value="${index}">${escapeHtml(item.pairs[index].result)}</option>`).join("");
            const rows = item.pairs.map((pair,index) => `<label class="fraction-match-row"><strong>${escapeHtml(pair.operation)}</strong><span>→</span><select data-lesson-key="match_${index}" aria-label="Rezultatul calculului ${index + 1}"${solved ? " disabled" : ""}><option value="">Alege rezultatul</option>${item.result_order.map(resultIndex => `<option value="${resultIndex}"${String(question.answerValues[`match_${index}`] ?? "") === String(resultIndex) ? " selected" : ""}>${escapeHtml(item.pairs[resultIndex].result)}</option>`).join("")}</select></label>`).join("");
            return `<form class="training-common-denominator-form interactive-form"><p class="interactive-instruction">Potrivește fiecare calcul cu rezultatul lui ireductibil.</p><div class="fraction-match-board">${rows}</div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică potrivirile</button>'}</form>`;
        }
        if (item.mode === "missing") {
            const missing = lessonField(question, "missing", item.missing_position === "numerator" ? "Numărător lipsă" : "Numitor lipsă", solved);
            const result = item.missing_position === "numerator"
                ? `<span class="fraction-card">${missing}<i></i><b>${item.known_value}</b></span>`
                : `<span class="fraction-card"><b>${item.known_value}</b><i></i>${missing}</span>`;
            return `<form class="training-common-denominator-form interactive-form"><p class="interactive-instruction">Completează valoarea lipsă astfel încât fracțiile să fie echivalente.</p><div class="common-denominator-side">${fractionCardHtml(item.left)}<span>=</span>${result}</div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică valoarea</button>'}</form>`;
        }
        if (item.mode === "error") {
            const selected = String(question.answerValues.error_index ?? "");
            const steps = item.steps.map((step,index) => `<button type="button" data-common-error="${index}" class="common-error-step${selected === String(index) ? " is-selected" : ""}"${solved ? " disabled" : ""}><b>${index + 1}</b><span>${escapeHtml(step)}</span></button>`).join("");
            return `<form class="training-common-denominator-form interactive-form"><p class="interactive-instruction">Apasă primul pas greșit.</p><div class="common-error-steps">${steps}</div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică pasul</button>'}</form>`;
        }
        const transformed = (side, label) => `<div class="common-denominator-side"><span class="fraction-card"><b>${item[side][0]}</b><i></i><b>${item[side][1]}</b></span><span>×</span>${lessonField(question,`${side}_factor`,`Factor pentru ${label}`,solved)}<span>=</span><span class="fraction-card">${lessonField(question,`${side}_numerator`,`Numărător ${label}`,solved)}<i></i>${lessonField(question,"common_denominator",`Numitor comun`,solved)}</span></div>`;
        return `<form class="training-common-denominator-form interactive-form"><p class="interactive-instruction">Găsește cel mai mic numitor comun și amplifică fiecare fracție cu factorul potrivit.</p><div class="common-denominator-board">${transformed("left","prima fracție")}${transformed("right","a doua fracție")}</div>${item.mode === "compare" ? `<label class="common-relation-label">Semnul dintre fracțiile transformate${lessonField(question,"relation","Semnul corect",solved)}</label>` : ""}${solved ? "" : '<button type="submit" class="btn btn-press">Verifică transformările</button>'}</form>`;
    }

    function fractionProductHtml(question) {
        const item = question.interactive, solved = isSolved(question);
        if (!question.answerValues) question.answerValues = {};
        if (solved) Object.entries(item.answers).forEach(([key,value]) => question.answerValues[key] = String(value));
        const inputs = (prefix, numeratorLabel = "Numărător", denominatorLabel = "Numitor") => `<span class="fraction-card">${lessonField(question,`${prefix}_numerator`,numeratorLabel,solved)}<i></i>${lessonField(question,`${prefix}_denominator`,denominatorLabel,solved)}</span>`;
        const product = `${fractionCardHtml(item.left)}<b>·</b>${fractionCardHtml(item.right)}`;
        if (item.mode === "build") {
            return `<form class="training-fraction-product-form interactive-form"><p class="interactive-instruction">Înmulțește numărătorii și numitorii, apoi simplifică produsul.</p><div class="fraction-product-row">${product}<b>=</b>${inputs("raw","Numărător înainte de simplificare","Numitor înainte de simplificare")}<b>=</b>${inputs("result","Numărător final","Numitor final")}</div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică produsul</button>'}</form>`;
        }
        if (item.mode === "cross_cancel") {
            const rows = item.cancellations.map((entry,index) => `<div class="product-cancel-row"><span>${entry.first}</span><span>și</span><span>${entry.second}</span><span>se simplifică prin</span>${lessonField(question,`${index}:factor`,`Factorul simplificării ${index + 1}`,solved)}<span>→</span>${lessonField(question,`${index}:first_result`,`Primul număr simplificat`,solved)}<span>și</span>${lessonField(question,`${index}:second_result`,`Al doilea număr simplificat`,solved)}</div>`).join("");
            return `<form class="training-fraction-product-form interactive-form"><p class="interactive-instruction">Simplifică în cruce înainte să înmulțești.</p><div class="fraction-product-row">${product}</div><div class="product-cancel-board">${rows}</div><div class="fraction-product-row"><span>Produsul ireductibil:</span>${inputs("result","Numărător final","Numitor final")}</div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică simplificările</button>'}</form>`;
        }
        if (item.mode === "visual") {
            const selected = new Set(String(question.answerValues.selected || "").split(",").filter(Boolean).map(Number));
            const cells = Array.from({length:item.rows * item.columns}, (_,index) => {
                const row = Math.floor(index / item.columns), column = index % item.columns;
                const first = column < item.first_columns, second = row < item.second_rows;
                return `<button type="button" data-product-cell="${index}" class="product-visual-cell${first ? " is-first" : ""}${second ? " is-second" : ""}${selected.has(index) ? " is-selected" : ""}" aria-label="Căsuța ${index + 1}"${solved ? " disabled" : ""}></button>`;
            }).join("");
            return `<form class="training-fraction-product-form interactive-form"><p class="interactive-instruction">Zonele hașurate arată cei doi factori. Apasă căsuțele din suprapunerea lor.</p><div class="product-visual-grid" style="--product-columns:${item.columns}">${cells}</div><div class="product-visual-legend"><span>Primul factor</span><span>Al doilea factor</span><span>Produsul</span></div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică suprapunerea</button>'}</form>`;
        }
        if (item.mode === "missing" || item.mode === "inverse") {
            const missingNumerator = item.editable === "denominator" ? `<b>${item.missing[0]}</b>` : lessonField(question,"missing_numerator","Numărător lipsă",solved);
            const missingDenominator = item.editable === "numerator" ? `<b>${item.missing[1]}</b>` : lessonField(question,"missing_denominator","Numitor lipsă",solved);
            const missing = `<span class="fraction-card">${missingNumerator}<i></i>${missingDenominator}</span>`;
            const left = item.missing_side === "left" ? missing : fractionCardHtml(item.left), right = item.missing_side === "right" ? missing : fractionCardHtml(item.right);
            return `<form class="training-fraction-product-form interactive-form"><p class="interactive-instruction">Completează factorul lipsă.</p><div class="fraction-product-row">${left}<b>·</b>${right}<b>=</b>${fractionCardHtml(item.result)}</div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică factorul</button>'}</form>`;
        }
        if (item.mode === "cancel_select") {
            const selected = new Set(String(question.answerValues.selected || "").split(",").filter(Boolean));
            const choices = item.candidates.map(candidate => `<button type="button" data-product-cancel="${escapeHtml(candidate.id)}" class="product-cancel-choice${selected.has(candidate.id) ? " is-selected" : ""}"${solved ? " disabled" : ""}>${escapeHtml(candidate.label)}</button>`).join("");
            return `<form class="training-fraction-product-form interactive-form"><p class="interactive-instruction">Selectează toate simplificările în cruce permise înainte de înmulțire.</p><div class="fraction-product-row">${product}</div><div class="product-cancel-choices">${choices}</div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică alegerile</button>'}</form>`;
        }
        if (item.mode === "error") {
            const selected = String(question.answerValues.error_index ?? "");
            const steps = item.steps.map((step,index) => `<button type="button" data-product-error="${index}" class="common-error-step${selected === String(index) ? " is-selected" : ""}"${solved ? " disabled" : ""}><b>${index + 1}</b><span>${escapeHtml(step)}</span></button>`).join("");
            return `<form class="training-fraction-product-form interactive-form"><p class="interactive-instruction">Apasă primul pas greșit.</p><div class="common-error-steps">${steps}</div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică pasul</button>'}</form>`;
        }
        if (item.mode === "order_steps") {
            const chosen = String(question.answerValues.order || "").split(",").filter(value => value !== "").map(Number);
            const card = (index, placed) => `<button type="button" data-product-step="${index}" class="fraction-step-card${placed ? " is-placed" : ""}"${solved ? " disabled" : ""}><b>${placed ? chosen.indexOf(index) + 1 : "•"}</b><span>${escapeHtml(item.steps[index])}</span></button>`;
            const pool = item.display_order.filter(index => !chosen.includes(index)).map(index => card(index,false)).join("");
            return `<form class="training-fraction-product-form interactive-form"><p class="interactive-instruction">Apasă pașii în ordinea corectă.</p><div class="fraction-step-pool">${pool || "Toți pașii au fost așezați."}</div><div class="fraction-step-result">${chosen.map(index => card(index,true)).join("") || "Ordinea construită va apărea aici."}</div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică ordinea</button>'}</form>`;
        }
        if (item.mode === "match") {
            const rows = item.pairs.map((pair,index) => `<label class="fraction-match-row"><strong>${escapeHtml(pair.operation)}</strong><span>→</span><select data-lesson-key="match_${index}" aria-label="Rezultatul produsului ${index + 1}"${solved ? " disabled" : ""}><option value="">Alege rezultatul</option>${item.result_order.map(resultIndex => `<option value="${resultIndex}"${String(question.answerValues[`match_${index}`] ?? "") === String(resultIndex) ? " selected" : ""}>${escapeHtml(item.pairs[resultIndex].result)}</option>`).join("")}</select></label>`).join("");
            return `<form class="training-fraction-product-form interactive-form"><p class="interactive-instruction">Potrivește fiecare înmulțire cu rezultatul ei ireductibil.</p><div class="fraction-match-board">${rows}</div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică potrivirile</button>'}</form>`;
        }
        if (item.mode === "mixed") {
            return `<form class="training-fraction-product-form interactive-form"><p class="interactive-instruction">Transformă numerele mixte, înmulțește și scrie rezultatul ca număr mixt ireductibil.</p><div class="fraction-product-row"><strong>${escapeHtml(item.left_label)}</strong><b>·</b><strong>${escapeHtml(item.right_label)}</strong><b>=</b><span class="mixed-number">${lessonField(question,"whole","Partea întreagă",solved)}${inputs("mixed","Numărător fracționar","Numitor fracționar")}</span></div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică rezultatul</button>'}</form>`;
        }
        return `<form class="training-fraction-product-form interactive-form"><p class="interactive-instruction">Calculează fracția cerută de problemă și simplifică rezultatul.</p><div class="fraction-product-row">${product}<b>=</b>${inputs("result","Numărător rezultat","Numitor rezultat")}</div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică răspunsul</button>'}</form>`;
    }

    function fractionDivisionHtml(question) {
        const item = question.interactive, solved = isSolved(question);
        if (!question.answerValues) question.answerValues = {};
        if (solved) Object.entries(item.answers).forEach(([key,value]) => question.answerValues[key] = String(value));
        const inputs = (prefix, numeratorLabel = "Numărător", denominatorLabel = "Numitor") => `<span class="fraction-card">${lessonField(question,`${prefix}_numerator`,numeratorLabel,solved)}<i></i>${lessonField(question,`${prefix}_denominator`,denominatorLabel,solved)}</span>`;
        const division = `${fractionCardHtml(item.left)}<b>:</b>${fractionCardHtml(item.right)}`;
        if (item.mode === "reciprocal") {
            return `<form class="training-fraction-division-form interactive-form"><p class="interactive-instruction">Schimbă între ele numărătorul și numitorul.</p><div class="fraction-product-row"><span>Inversa lui</span>${fractionCardHtml(item.right)}<b>este</b>${inputs("inverse","Numărătorul inversei","Numitorul inversei")}</div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică inversa</button>'}</form>`;
        }
        if (item.mode === "build") {
            return `<form class="training-fraction-division-form interactive-form"><p class="interactive-instruction">Înlocuiește împărțirea cu înmulțirea prin inversa celei de-a doua fracții, apoi calculează.</p><div class="fraction-product-row">${division}<b>=</b>${fractionCardHtml(item.left)}<b>·</b>${inputs("inverse","Numărătorul inversei","Numitorul inversei")}<b>=</b>${inputs("result","Numărător final","Numitor final")}</div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică împărțirea</button>'}</form>`;
        }
        if (item.mode === "cross_cancel") {
            const rows = item.cancellations.map((entry,index) => `<div class="product-cancel-row"><span>${entry.first}</span><span>și</span><span>${entry.second}</span><span>se simplifică prin</span>${lessonField(question,`${index}:factor`,`Factorul simplificării ${index + 1}`,solved)}<span>→</span>${lessonField(question,`${index}:first_result`,`Primul număr simplificat`,solved)}<span>și</span>${lessonField(question,`${index}:second_result`,`Al doilea număr simplificat`,solved)}</div>`).join("");
            return `<form class="training-fraction-division-form interactive-form"><p class="interactive-instruction">Inversează a doua fracție, apoi simplifică în cruce.</p><div class="fraction-product-row">${division}<b>=</b>${fractionCardHtml(item.left)}<b>·</b>${fractionCardHtml(item.multiplier)}</div><div class="product-cancel-board">${rows}</div><div class="fraction-product-row"><span>Câtul ireductibil:</span>${inputs("result","Numărător final","Numitor final")}</div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică simplificările</button>'}</form>`;
        }
        if (item.mode === "visual") {
            const selected = String(question.answerValues.groups ?? "");
            const groups = item.candidates.map(value => `<button type="button" data-division-groups="${value}" class="division-group-choice${selected === String(value) ? " is-selected" : ""}"${solved ? " disabled" : ""}>${value}</button>`).join("");
            const pieces = Array.from({length:item.piece_count}, (_,index) => `<span${index < item.filled_pieces ? ' class="is-filled"' : ""}></span>`).join("");
            return `<form class="training-fraction-division-form interactive-form"><p class="interactive-instruction">Privește bara și alege câte grupuri complete de mărimea indicată încap.</p><div class="division-visual-info"><strong>${escapeHtml(item.dividend_label)}</strong><span>împărțit în grupuri de</span><strong>${escapeHtml(item.divisor_label)}</strong></div><div class="division-visual-strip">${pieces}</div><div class="division-group-choices">${groups}</div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică numărul de grupuri</button>'}</form>`;
        }
        if (item.mode === "missing" || item.mode === "inverse") {
            const missingNumerator = item.editable === "denominator" ? `<b>${item.missing[0]}</b>` : lessonField(question,"missing_numerator","Numărător lipsă",solved);
            const missingDenominator = item.editable === "numerator" ? `<b>${item.missing[1]}</b>` : lessonField(question,"missing_denominator","Numitor lipsă",solved);
            const missing = `<span class="fraction-card">${missingNumerator}<i></i>${missingDenominator}</span>`;
            const left = item.missing_side === "left" ? missing : fractionCardHtml(item.left), right = item.missing_side === "right" ? missing : fractionCardHtml(item.right);
            return `<form class="training-fraction-division-form interactive-form"><p class="interactive-instruction">Completează fracția lipsă.</p><div class="fraction-product-row">${left}<b>:</b>${right}<b>=</b>${fractionCardHtml(item.result)}</div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică fracția</button>'}</form>`;
        }
        if (item.mode === "cancel_select") {
            const selected = new Set(String(question.answerValues.selected || "").split(",").filter(Boolean));
            const choices = item.candidates.map(candidate => `<button type="button" data-product-cancel="${escapeHtml(candidate.id)}" class="product-cancel-choice${selected.has(candidate.id) ? " is-selected" : ""}"${solved ? " disabled" : ""}>${escapeHtml(candidate.label)}</button>`).join("");
            return `<form class="training-fraction-division-form interactive-form"><p class="interactive-instruction">După inversarea celei de-a doua fracții, selectează simplificările permise.</p><div class="fraction-product-row">${fractionCardHtml(item.left)}<b>·</b>${fractionCardHtml(item.multiplier)}</div><div class="product-cancel-choices">${choices}</div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică alegerile</button>'}</form>`;
        }
        if (item.mode === "error") {
            const selected = String(question.answerValues.error_index ?? "");
            const steps = item.steps.map((step,index) => `<button type="button" data-product-error="${index}" class="common-error-step${selected === String(index) ? " is-selected" : ""}"${solved ? " disabled" : ""}><b>${index + 1}</b><span>${escapeHtml(step)}</span></button>`).join("");
            return `<form class="training-fraction-division-form interactive-form"><p class="interactive-instruction">Apasă primul pas greșit.</p><div class="common-error-steps">${steps}</div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică pasul</button>'}</form>`;
        }
        if (item.mode === "order_steps") {
            const chosen = String(question.answerValues.order || "").split(",").filter(value => value !== "").map(Number);
            const card = (index, placed) => `<button type="button" data-product-step="${index}" class="fraction-step-card${placed ? " is-placed" : ""}"${solved ? " disabled" : ""}><b>${placed ? chosen.indexOf(index) + 1 : "•"}</b><span>${escapeHtml(item.steps[index])}</span></button>`;
            const pool = item.display_order.filter(index => !chosen.includes(index)).map(index => card(index,false)).join("");
            return `<form class="training-fraction-division-form interactive-form"><p class="interactive-instruction">Apasă pașii în ordinea corectă.</p><div class="fraction-step-pool">${pool || "Toți pașii au fost așezați."}</div><div class="fraction-step-result">${chosen.map(index => card(index,true)).join("") || "Ordinea construită va apărea aici."}</div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică ordinea</button>'}</form>`;
        }
        if (item.mode === "match") {
            const rows = item.pairs.map((pair,index) => `<label class="fraction-match-row"><strong>${escapeHtml(pair.operation)}</strong><span>→</span><select data-lesson-key="match_${index}" aria-label="Rezultatul împărțirii ${index + 1}"${solved ? " disabled" : ""}><option value="">Alege rezultatul</option>${item.result_order.map(resultIndex => `<option value="${resultIndex}"${String(question.answerValues[`match_${index}`] ?? "") === String(resultIndex) ? " selected" : ""}>${escapeHtml(item.pairs[resultIndex].result)}</option>`).join("")}</select></label>`).join("");
            return `<form class="training-fraction-division-form interactive-form"><p class="interactive-instruction">Potrivește fiecare împărțire cu rezultatul ei ireductibil.</p><div class="fraction-match-board">${rows}</div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică potrivirile</button>'}</form>`;
        }
        if (item.mode === "mixed") {
            return `<form class="training-fraction-division-form interactive-form"><p class="interactive-instruction">Transformă numerele mixte în fracții, calculează și scrie rezultatul ca număr mixt.</p><div class="fraction-product-row"><strong>${escapeHtml(item.left_label)}</strong><b>:</b><strong>${escapeHtml(item.right_label)}</strong><b>=</b><span class="mixed-number">${lessonField(question,"whole","Partea întreagă",solved)}${inputs("mixed","Numărător fracționar","Numitor fracționar")}</span></div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică rezultatul</button>'}</form>`;
        }
        return `<form class="training-fraction-division-form interactive-form"><p class="interactive-instruction">Transformă împărțirea în înmulțire și scrie rezultatul ireductibil.</p><div class="fraction-product-row">${division}<b>=</b>${inputs("result","Numărător rezultat","Numitor rezultat")}</div>${solved ? "" : '<button type="submit" class="btn btn-press">Verifică răspunsul</button>'}</form>`;
    }

    function fractionPowerHtml(question) {
        const item = question.interactive, solved = isSolved(question);
        if (!question.answerValues) question.answerValues = {};
        if (solved) Object.entries(item.answers).forEach(([key,value]) => question.answerValues[key] = String(value));
        const field = (key,label) => lessonField(question,key,label,solved);
        const fraction = value => fractionCardHtml(value);
        const power = (value, exponent) => `<span class="fraction-power-expression">${fraction(value)}<sup>${escapeHtml(exponent)}</sup></span>`;
        const form = body => `<form class="training-fraction-power-form interactive-form">${body}${solved ? "" : '<button type="submit" class="btn btn-press">Verifică răspunsul</button>'}</form>`;
        if (item.mode === "build") {
            return form(`<p class="interactive-instruction">Ridică separat numărătorul și numitorul la putere, apoi calculează.</p><div class="fraction-power-line">${power(item.base,item.exponent)}<b>=</b><span class="fraction-card"><span>${item.base[0]}<sup>${item.exponent}</sup> = ${field("numerator_power","Puterea numărătorului")}</span><i></i><span>${item.base[1]}<sup>${item.exponent}</sup> = ${field("denominator_power","Puterea numitorului")}</span></span><b>=</b><span class="fraction-card">${field("result_numerator","Numărător rezultat")}<i></i>${field("result_denominator","Numitor rezultat")}</span></div>`);
        }
        if (item.mode === "expand") {
            return form(`<p class="interactive-instruction">Scrie factorii identici care formează puterea.</p><div class="fraction-power-line">${power(item.base,item.exponent)}<b>=</b><span class="power-factor-slots">${Array.from({length:item.exponent},(_,i)=>field(`factor_${i+1}`,`Factorul ${i+1}`)).join(" · ")}</span></div><small>Scrie fiecare factor ca fracție, de exemplu 2/3.</small>`);
        }
        if (item.mode === "compress") {
            return form(`<p class="interactive-instruction">Transformă produsul de factori identici într-o singură putere.</p><div class="fraction-power-line"><strong>${escapeHtml(item.product)}</strong><b>=</b><span>(</span>${field("base","Baza puterii")}<span>)</span><sup>${field("exponent","Exponentul puterii")}</sup></div><small>Scrie baza ca fracție, de exemplu 3/5.</small>`);
        }
        if (item.mode === "missing" || item.mode === "given_base" || item.mode === "given_exponent") {
            return form(`<p class="interactive-instruction">Completează valoarea lipsă.</p><div class="fraction-power-given">${escapeHtml(item.expression)}</div><div class="fraction-power-fields">${item.fields.map(entry=>`<label><span>${escapeHtml(entry.label)}</span>${field(entry.key,entry.label)}</label>`).join("")}</div>`);
        }
        if (item.mode === "rule" || item.mode === "exponent_rule") {
            const selected = String(question.answerValues[item.answer_key] || "");
            const choices = item.choices.map(choice=>`<button type="button" data-power-choice-key="${escapeHtml(item.answer_key)}" data-power-choice-value="${escapeHtml(choice.value)}" class="fraction-power-choice${selected === String(choice.value) ? " is-selected" : ""}"${solved ? " disabled" : ""}>${escapeHtml(choice.label)}</button>`).join("");
            const extra = (item.fields || []).map(entry=>`<label><span>${escapeHtml(entry.label)}</span>${field(entry.key,entry.label)}</label>`).join("");
            return form(`<p class="interactive-instruction">${escapeHtml(item.instruction)}</p><div class="fraction-power-given">${escapeHtml(item.expression)}</div><div class="fraction-power-choices">${choices}</div><div class="fraction-power-fields">${extra}</div>`);
        }
        if (item.mode === "error") {
            const selected = String(question.answerValues.error_index ?? "");
            return form(`<p class="interactive-instruction">Apasă primul pas greșit.</p><div class="common-error-steps">${item.steps.map((step,index)=>`<button type="button" data-fraction-power-error="${index}" class="common-error-step${selected === String(index) ? " is-selected" : ""}"${solved ? " disabled" : ""}><b>${index+1}</b><span>${escapeHtml(step)}</span></button>`).join("")}</div>`);
        }
        if (item.mode === "order_steps") {
            const chosen = String(question.answerValues.order || "").split(",").filter(Boolean).map(Number);
            const card = (index,placed)=>`<button type="button" data-fraction-power-step="${index}" class="fraction-step-card${placed ? " is-placed" : ""}"${solved ? " disabled" : ""}><b>${placed ? chosen.indexOf(index)+1 : "•"}</b><span>${escapeHtml(item.steps[index])}</span></button>`;
            return form(`<p class="interactive-instruction">Apasă pașii în ordinea corectă.</p><div class="fraction-step-pool">${item.display_order.filter(index=>!chosen.includes(index)).map(index=>card(index,false)).join("") || "Toți pașii au fost așezați."}</div><div class="fraction-step-result">${chosen.map(index=>card(index,true)).join("") || "Ordinea construită va apărea aici."}</div>`);
        }
        if (item.mode === "match") {
            return form(`<p class="interactive-instruction">Potrivește fiecare expresie cu forma ei echivalentă.</p><div class="fraction-match-board">${item.pairs.map((pair,index)=>`<label class="fraction-match-row"><strong>${escapeHtml(pair.left)}</strong><span>→</span><select data-lesson-key="match_${index}" aria-label="Potrivirea ${index+1}"${solved ? " disabled" : ""}><option value="">Alege</option>${item.result_order.map(resultIndex=>`<option value="${resultIndex}"${String(question.answerValues[`match_${index}`] ?? "") === String(resultIndex) ? " selected" : ""}>${escapeHtml(item.pairs[resultIndex].right)}</option>`).join("")}</select></label>`).join("")}</div>`);
        }
        if (item.mode === "visual") {
            const selected = String(question.answerValues.selected || "");
            return form(`<p class="interactive-instruction">Fiecare etapă împarte din nou partea aleasă. Selectează fracția finală.</p><div class="fraction-power-visual"><div class="fraction-power-grid" style="--power-cells:${item.cell_count}">${Array.from({length:item.cell_count},(_,i)=>`<span${i < item.filled_cells ? ' class="is-filled"' : ""}></span>`).join("")}</div><strong>${escapeHtml(item.caption)}</strong></div><div class="fraction-power-choices">${item.choices.map(choice=>`<button type="button" data-power-choice-key="selected" data-power-choice-value="${escapeHtml(choice)}" class="fraction-power-choice${selected === String(choice) ? " is-selected" : ""}"${solved ? " disabled" : ""}>${escapeHtml(choice)}</button>`).join("")}</div>`);
        }
        return form(`<p class="interactive-instruction">Rezolvă problema și scrie fracția ireductibilă.</p><div class="fraction-power-line">${power(item.base,item.exponent)}<b>=</b><span class="fraction-card">${field("result_numerator","Numărător rezultat")}<i></i>${field("result_denominator","Numitor rezultat")}</span></div>`);
    }

    function fractionPercentHtml(question) {
        const item = question.interactive, solved = isSolved(question);
        if (!question.answerValues) question.answerValues = {};
        if (solved) Object.entries(item.answers).forEach(([key,value]) => question.answerValues[key] = String(value));
        const field = entry => `<label><span>${escapeHtml(entry.label)}</span>${lessonField(question,entry.key,entry.label,solved,true)}</label>`;
        const form = body => `<form class="training-fraction-percent-form interactive-form">${body}${solved ? "" : '<button type="submit" class="btn btn-press">Verifică răspunsul</button>'}</form>`;
        if (["natural","fraction","unit_path","missing","convert","price","problem"].includes(item.mode)) {
            const path = item.path ? `<div class="percent-unit-path">${item.path.map((node,index)=>`<span><b>${escapeHtml(node.top)}</b><small>${escapeHtml(node.bottom)}</small></span>${index < item.path.length-1 ? "<i>→</i>" : ""}`).join("")}</div>` : "";
            const machine = item.mode === "price" ? `<div class="percent-price-machine"><span>Preț inițial<strong>${escapeHtml(item.initial)}</strong></span><i>→</i><span>${escapeHtml(item.change_label)}</span><i>→</i><span>Preț final</span></div>` : "";
            return form(`<p class="interactive-instruction">${escapeHtml(item.instruction)}</p><div class="fraction-power-given">${escapeHtml(item.expression)}</div>${path}${machine}<div class="fraction-power-fields">${item.fields.map(field).join("")}</div>`);
        }
        if (item.mode === "grid") {
            const selected = Number(question.answerValues.selected || 0);
            const cells = Array.from({length:100},(_,index)=>`<button type="button" data-percent-grid="${index+1}" class="percent-hundred-cell${index < selected ? " is-filled" : ""}" aria-label="${index+1}%"${solved ? " disabled" : ""}></button>`).join("");
            return form(`<p class="interactive-instruction">Apasă pătrățelul corespunzător procentului; vor fi colorate toate pătrățelele până la el.</p><div class="percent-hundred-grid">${cells}</div><div class="percent-grid-readout"><strong>${selected}%</strong><span>= ${selected}/100</span></div>`);
        }
        if (item.mode === "slider") {
            const value = Number(question.answerValues.percent ?? item.initial ?? 0);
            return form(`<p class="interactive-instruction">Mută cursorul la procentul cerut.</p><div class="percent-slider-card"><strong data-percent-value>${value}%</strong><input type="range" min="0" max="100" step="${item.step || 1}" value="${value}" data-percent-slider${solved ? " disabled" : ""}><div><span>0%</span><span>50%</span><span>100%</span></div></div>`);
        }
        if (item.mode === "table") {
            return form(`<p class="interactive-instruction">Completează valorile; suma lor trebuie să refacă totalul.</p><div class="percent-table-wrap"><table class="percent-table"><thead><tr><th>Categorie</th><th>Procent</th><th>Valoare</th></tr></thead><tbody>${item.rows.map((row,index)=>`<tr><th>${escapeHtml(row.label)}</th><td>${row.percent}%</td><td>${lessonField(question,`value_${index}`,`Valoarea pentru ${row.label}`,solved,true)}</td></tr>`).join("")}</tbody><tfoot><tr><th>Total</th><td>100%</td><td>${escapeHtml(item.total)}</td></tr></tfoot></table></div>`);
        }
        if (item.mode === "error") {
            const selected = String(question.answerValues.error_index ?? "");
            return form(`<p class="interactive-instruction">Apasă primul pas greșit.</p><div class="common-error-steps">${item.steps.map((step,index)=>`<button type="button" data-percent-error="${index}" class="common-error-step${selected === String(index) ? " is-selected" : ""}"${solved ? " disabled" : ""}><b>${index+1}</b><span>${escapeHtml(step)}</span></button>`).join("")}</div>`);
        }
        if (item.mode === "order_steps") {
            const chosen = String(question.answerValues.order || "").split(",").filter(Boolean).map(Number);
            const card = (index,placed)=>`<button type="button" data-percent-step="${index}" class="fraction-step-card${placed ? " is-placed" : ""}"${solved ? " disabled" : ""}><b>${placed ? chosen.indexOf(index)+1 : "•"}</b><span>${escapeHtml(item.steps[index])}</span></button>`;
            return form(`<p class="interactive-instruction">Apasă pașii în ordinea corectă.</p><div class="fraction-step-pool">${item.display_order.filter(index=>!chosen.includes(index)).map(index=>card(index,false)).join("") || "Toți pașii au fost așezați."}</div><div class="fraction-step-result">${chosen.map(index=>card(index,true)).join("") || "Ordinea construită va apărea aici."}</div>`);
        }
        if (item.mode === "match") {
            return form(`<p class="interactive-instruction">Potrivește fiecare situație cu schema sau răspunsul corect.</p><div class="fraction-match-board">${item.pairs.map((pair,index)=>`<label class="fraction-match-row"><strong>${escapeHtml(pair.left)}</strong><span>→</span><select data-lesson-key="match_${index}" aria-label="Potrivirea ${index+1}"${solved ? " disabled" : ""}><option value="">Alege</option>${item.result_order.map(resultIndex=>`<option value="${resultIndex}"${String(question.answerValues[`match_${index}`] ?? "") === String(resultIndex) ? " selected" : ""}>${escapeHtml(item.pairs[resultIndex].right)}</option>`).join("")}</select></label>`).join("")}</div>`);
        }
        return form("");
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
            case "geometry_canvas":
                return geometryCanvasHtml(question);
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
            case "statistics_chart":
                return statisticsChartHtml(question);
            case "algebra_workbench":
                return algebraWorkbenchHtml(question);
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
            case "fraction_product":
                return fractionProductHtml(question);
            case "fraction_division":
                return fractionDivisionHtml(question);
            case "fraction_power":
                return fractionPowerHtml(question);
            case "fraction_percent":
                return fractionPercentHtml(question);
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
        } else if (["missing_digits", "input_output", "factor_builder", "factor_match", "power_builder", "power_match", "power_table", "power_cycle", "power_square", "power_rule_chain", "base_values", "base_match", "binary_toggle", "unit_reduction", "comparison_method", "figurative_method", "reverse_method", "false_hypothesis_method", "geometry_canvas", "operation_workbench", "divisibility_values", "prime_workbench", "decimal_workbench", "statistics_chart", "algebra_workbench", "fraction_visual", "gcd_workbench", "fraction_scale", "fraction_reduce_path", "lcm_workbench", "common_denominator", "fraction_product", "fraction_division", "fraction_power", "fraction_percent"].includes(question.type)) {
            const values = answer.values ?? question.answerValues ?? {};
            body.append("values", JSON.stringify(values));
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
        const geometryForm = cardEl?.querySelector(".training-geometry-form");
        if (geometryForm) { bindGeometryForm(geometryForm); return; }
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
        const statisticsForm = cardEl?.querySelector(".training-statistics-form");
        if (statisticsForm) { bindStatisticsForm(statisticsForm); return; }
        const algebraForm = cardEl?.querySelector(".training-algebra-form");
        if (algebraForm) { bindAlgebraForm(algebraForm); return; }
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
        const fractionProductForm = cardEl?.querySelector(".training-fraction-product-form");
        if (fractionProductForm) { bindFractionProductForm(fractionProductForm); return; }
        const fractionDivisionForm = cardEl?.querySelector(".training-fraction-division-form");
        if (fractionDivisionForm) { bindFractionProductForm(fractionDivisionForm); return; }
        const fractionPowerForm = cardEl?.querySelector(".training-fraction-power-form");
        if (fractionPowerForm) { bindFractionPowerForm(fractionPowerForm); return; }
        const fractionPercentForm = cardEl?.querySelector(".training-fraction-percent-form");
        if (fractionPercentForm) { bindFractionPercentForm(fractionPercentForm); return; }
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
        quotient.addEventListener("input", () => { quotient.value = quotient.value.replace(/[^0-9,.]/g, ""); question.divisionAnswer.quotient = quotient.value; });
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

    function bindGeometryForm(form){
        const question=data.questions[currentIndex];if(isSolved(question))return;
        form.querySelectorAll("[data-geometry-key]").forEach(input=>input.addEventListener("input",()=>{question.answerValues[input.dataset.geometryKey]=input.value.trim();}));
        form.querySelectorAll("[data-geometry-range]").forEach(input=>{
            input.addEventListener("input",()=>{question.answerValues[input.dataset.geometryRange]=input.value;const output=form.querySelector(`[data-geometry-output="${input.dataset.geometryRange}"]`);if(output)output.textContent=input.value;});
            input.addEventListener("change",()=>renderQuestion(null,false));
        });
        form.querySelectorAll("[data-geometry-choice-key]").forEach(button=>button.addEventListener("click",()=>{question.answerValues[button.dataset.geometryChoiceKey]=button.dataset.geometryChoice;renderQuestion(null,false);}));
        form.querySelectorAll("[data-geometry-select]").forEach(select=>select.addEventListener("change",()=>{question.answerValues[select.dataset.geometrySelect]=select.value;}));
        form.querySelectorAll("[data-geometry-multi]").forEach(button=>button.addEventListener("click",()=>{
            const key=button.dataset.geometryMulti,value=button.dataset.geometryValue,current=new Set(String(question.answerValues[key]||"").split(",").filter(Boolean));
            if(current.has(value))current.delete(value);else current.add(value);
            question.answerValues[key]=[...current].sort((a,b)=>a.localeCompare(b,undefined,{numeric:true})).join(",");renderQuestion(null,false);
        }));
        form.querySelectorAll("[data-geometry-condition]").forEach(button=>button.addEventListener("click",()=>{
            const current=new Set(String(question.geometryConditions||"").split(",").filter(Boolean)),value=button.dataset.geometryCondition;
            if(current.has(value))current.delete(value);else current.add(value);question.geometryConditions=[...current].sort().join(",");
            if(current.size===question.interactive.conditions.length)question.answerValues.conditions=question.interactive.answers.conditions;else delete question.answerValues.conditions;renderQuestion(null,false);
        }));
        form.querySelectorAll("[data-geometry-pick-point]").forEach(point=>point.addEventListener("click",()=>{
            const name=point.dataset.geometryPickPoint;
            if(!question.answerValues.first||question.answerValues.second){question.answerValues.first=name;delete question.answerValues.second;}
            else if(question.answerValues.first!==name)question.answerValues.second=name;
            renderQuestion(null,false);
        }));
        form.querySelectorAll("[data-geometry-drag-value]").forEach(tile=>{
            tile.addEventListener("click",()=>{question.geometryPalette=tile.dataset.geometryDragValue;renderQuestion(null,false);});
            tile.addEventListener("dragstart",event=>{event.dataTransfer.setData("text/plain",tile.dataset.geometryDragValue);});
        });
        form.querySelectorAll("[data-geometry-drop-slot]").forEach(slot=>{
            const place=value=>{if(!value)return;question.answerValues[slot.dataset.geometryDropSlot]=value;question.geometryPalette="";renderQuestion(null,false);};
            slot.addEventListener("dragover",event=>event.preventDefault());
            slot.addEventListener("drop",event=>{event.preventDefault();place(event.dataTransfer.getData("text/plain"));});
            slot.addEventListener("click",()=>place(question.geometryPalette));
        });
        form.querySelectorAll("[data-geometry-edge-point]").forEach(point=>point.addEventListener("click",()=>{
            const name=point.dataset.geometryEdgePoint;
            if(!question.geometryEdgeStart){question.geometryEdgeStart=name;renderQuestion(null,false);return;}
            if(question.geometryEdgeStart===name){question.geometryEdgeStart="";renderQuestion(null,false);return;}
            const edge=[question.geometryEdgeStart,name].sort().join(""),edges=new Set(String(question.answerValues.edges||"").split(",").filter(Boolean));
            if(edges.has(edge))edges.delete(edge);else edges.add(edge);
            question.answerValues.edges=[...edges].sort().join(",");question.geometryEdgeStart="";renderQuestion(null,false);
        }));
        form.querySelectorAll("[data-geometry-point]").forEach(point=>{
            point.addEventListener("pointerdown",event=>{
                event.preventDefault();point.setPointerCapture(event.pointerId);point.classList.add("is-dragging");
                const svg=point.closest("svg");
                const move=moveEvent=>{const svgPoint=svg.createSVGPoint();svgPoint.x=moveEvent.clientX;svgPoint.y=moveEvent.clientY;const local=svgPoint.matrixTransform(svg.getScreenCTM().inverse()),cx=Math.max(15,Math.min(425,Math.round(local.x))),cy=Math.max(15,Math.min(165,Math.round(local.y)));point.setAttribute("transform",`translate(${cx} ${cy})`);question.answerValues[point.dataset.geometryPoint]=`${cx},${cy}`;};
                const up=()=>{
                    const mode=question.interactive.mode,target=(question.interactive.points||[]).find(candidate=>candidate.name===point.dataset.geometryPoint);
                    if(["place_points","reconstruct_model","full_geometry_puzzle"].includes(mode)&&target){
                        const [x,y]=String(question.answerValues[point.dataset.geometryPoint]).split(",").map(Number);
                        if(Math.hypot(x-target.x,y-target.y)<=62){
                            question.answerValues[point.dataset.geometryPoint]=`${target.x},${target.y}`;
                            point.setAttribute("transform",`translate(${target.x} ${target.y})`);
                            point.classList.add("is-snapped");
                            setTimeout(()=>point.classList.remove("is-snapped"),350);
                        }
                    }else if(["point_on_line","repair_membership","move_to_collinear"].includes(mode)&&question.interactive.answers.membership==="on"){
                        const [x,y]=String(question.answerValues[point.dataset.geometryPoint]).split(",").map(Number),line=question.interactive.line||{a:0,b:1,c:-90};
                        const a=Number(line.a)||0,b=Number(line.b)||0,c=Number(line.c)||0,denominator=a*a+b*b||1,signed=(a*x+b*y+c)/denominator;
                        if(Math.abs(a*x+b*y+c)/Math.sqrt(denominator)<=48){
                            const px=Math.round(x-a*signed),py=Math.round(y-b*signed);
                            question.answerValues[point.dataset.geometryPoint]=`${px},${py}`;
                            point.setAttribute("transform",`translate(${px} ${py})`);
                            point.classList.add("is-snapped");
                            setTimeout(()=>point.classList.remove("is-snapped"),350);
                        }
                    }
                    point.classList.remove("is-dragging");point.removeEventListener("pointermove",move);point.removeEventListener("pointerup",up);
                };
                point.addEventListener("pointermove",move);point.addEventListener("pointerup",up);
            });
        });
        form.addEventListener("submit",async event=>{event.preventDefault();const required=Object.keys(question.interactive.answers);if(["place_noncollinear","place_collinear","coincidence","point_on_line","repair_membership","move_to_collinear","plane_points","min_lines","max_lines","arrange_line_count"].includes(question.interactive.mode)){const names=(question.interactive.points||[]).map(point=>point.name);if(names.some(key=>question.answerValues[key]===undefined))return;}else if(required.some(key=>question.answerValues[key]===undefined||question.answerValues[key]===""))return;await submitInteractiveAnswer(question,{values:question.answerValues});});
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
            input.value = input.value.replace(/[^0-9,./]/g, "");
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
        form.querySelectorAll("[data-decimal-class-key]").forEach(button => button.addEventListener("click", () => {
            question.answerValues[button.dataset.decimalClassKey] = button.dataset.decimalClassValue;
            form.querySelectorAll(`[data-decimal-class-key="${button.dataset.decimalClassKey}"]`).forEach(choice => choice.classList.toggle("is-selected", choice === button));
        }));
        form.querySelectorAll("[data-decimal-choice-key]").forEach(button => button.addEventListener("click", () => {
            question.answerValues[button.dataset.decimalChoiceKey] = button.dataset.decimalChoiceValue;
            form.querySelectorAll(`[data-decimal-choice-key="${button.dataset.decimalChoiceKey}"]`).forEach(choice => choice.classList.toggle("is-selected", choice === button));
        }));
        const averageRange = form.querySelector("[data-average-range]");
        if (averageRange) averageRange.addEventListener("input", () => {
            question.answerValues.missing = averageRange.value.replace(".", ",");
            form.querySelector("[data-average-value]").textContent = question.answerValues.missing;
        });
        form.addEventListener("submit", async event => {
            event.preventDefault();
            if (Object.keys(item.answers).some(key => question.answerValues[key] === undefined || String(question.answerValues[key]).trim() === "")) return;
            await submitInteractiveAnswer(question, {values: question.answerValues});
        });
    }

    function bindStatisticsForm(form) {
        const question=data.questions[currentIndex], item=question.interactive; if(isSolved(question))return;
        form.querySelectorAll("[data-stat-key]").forEach(input=>input.addEventListener("input",()=>{input.value=input.value.replace(/[^0-9,.]/g,"");question.answerValues[input.dataset.statKey]=input.value;}));
        form.querySelectorAll("[data-stat-choice]").forEach(mark=>{const choose=()=>{question.answerValues.selected=mark.dataset.statChoice;renderQuestion(null,false);};mark.addEventListener("click",choose);mark.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();choose();}});});
        form.querySelectorAll("[data-stat-range]").forEach(input=>input.addEventListener("input",()=>{question.answerValues[input.dataset.statRange]=input.value;renderQuestion(null,false);}));
        form.addEventListener("submit",async event=>{event.preventDefault();const required=Object.keys(item.answers);if(required.some(key=>question.answerValues[key]===undefined||String(question.answerValues[key]).trim()===""))return;await submitInteractiveAnswer(question,{values:question.answerValues});});
    }

    function bindAlgebraForm(form) {
        const question = data.questions[currentIndex], item = question.interactive;
        if (isSolved(question)) return;
        const controls = [...form.querySelectorAll("[data-algebra-key]")];
        const rememberActive = control => {
            question.algebraActiveKey = control.dataset.algebraKey;
        };
        controls.forEach(control => {
            const update = () => { question.answerValues[control.dataset.algebraKey] = control.value; };
            control.addEventListener(control.tagName === "SELECT" ? "change" : "input", update);
            if (control.tagName === "INPUT") {
                control.addEventListener("focus", () => rememberActive(control));
                control.addEventListener("click", () => rememberActive(control));
            }
        });
        const textControls = controls.filter(control => control.tagName === "INPUT");
        const activeInput = () => textControls.find(control => control.dataset.algebraKey === question.algebraActiveKey) || textControls[0];
        const updateFromKeyboard = (input, value, cursor) => {
            input.value = value;
            question.answerValues[input.dataset.algebraKey] = value;
            question.algebraActiveKey = input.dataset.algebraKey;
            input.focus({preventScroll: true});
            input.setSelectionRange(cursor, cursor);
        };
        form.querySelectorAll("[data-math-key]").forEach(button => button.addEventListener("click", () => {
            const input = activeInput();
            if (!input) return;
            const start = input.selectionStart ?? input.value.length, end = input.selectionEnd ?? start;
            const symbol = button.dataset.mathKey;
            updateFromKeyboard(input, input.value.slice(0, start) + symbol + input.value.slice(end), start + symbol.length);
        }));
        form.querySelectorAll("[data-math-action]").forEach(button => button.addEventListener("click", () => {
            const input = activeInput();
            if (!input) return;
            const start = input.selectionStart ?? input.value.length, end = input.selectionEnd ?? start;
            if (button.dataset.mathAction === "clear") return updateFromKeyboard(input, "", 0);
            if (button.dataset.mathAction === "left") return updateFromKeyboard(input, input.value, Math.max(0, start - 1));
            if (button.dataset.mathAction === "right") return updateFromKeyboard(input, input.value, Math.min(input.value.length, end + 1));
            const from = start === end ? Math.max(0, start - 1) : start;
            updateFromKeyboard(input, input.value.slice(0, from) + input.value.slice(end), from);
        }));
        form.querySelectorAll("[data-algebra-choice]").forEach(button => button.addEventListener("click", () => {
            question.answerValues.choice = button.dataset.algebraChoice;
            renderQuestion(null, false);
        }));
        form.querySelectorAll("[data-algebra-error]").forEach(button => button.addEventListener("click", () => {
            question.answerValues.error = button.dataset.algebraError;
            renderQuestion(null, false);
        }));
        form.querySelectorAll("[data-algebra-verdict]").forEach(button => button.addEventListener("click", () => {
            question.answerValues.verdict = button.dataset.algebraVerdict;
            renderQuestion(null, false);
        }));
        form.querySelectorAll("[data-algebra-piece]").forEach(button => button.addEventListener("click", () => {
            const selected = String(question.answerValues.pieces || "").split(",").filter(Boolean).map(Number);
            const index = Number(button.dataset.algebraPiece), position = selected.indexOf(index);
            if (position >= 0) selected.splice(position, 1); else selected.push(index);
            question.answerValues.pieces = selected.join(",");
            renderQuestion(null, false);
        }));
        form.addEventListener("submit", async event => {
            event.preventDefault();
            const required = Object.keys(item.answers);
            if (required.some(key => question.answerValues[key] === undefined || String(question.answerValues[key]).trim() === "")) return;
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
        form.querySelectorAll("select[data-lesson-key]").forEach(select => select.addEventListener("change", () => {
            question.answerValues[select.dataset.lessonKey] = select.value;
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
        form.querySelectorAll("[data-common-error]").forEach(button => button.addEventListener("click", () => {
            question.answerValues.error_index = button.dataset.commonError;
            renderQuestion(null, false);
        }));
        form.querySelectorAll("[data-fraction-operation]").forEach(button => button.addEventListener("click", () => {
            question.answerValues.operator = button.dataset.fractionOperation;
            renderQuestion(null, false);
        }));
        form.querySelectorAll("[data-fraction-step]").forEach(button => button.addEventListener("click", () => {
            const index = Number(button.dataset.fractionStep);
            const order = String(question.answerValues.order || "").split(",").filter(value => value !== "").map(Number);
            const position = order.indexOf(index);
            if (position >= 0) order.splice(position, 1); else order.push(index);
            question.answerValues.order = order.join(",");
            renderQuestion(null, false);
        }));
        form.addEventListener("submit", async event => {
            event.preventDefault();
            if ([...form.querySelectorAll("[data-lesson-key]")].some(input => !input.value)) return;
            if (Object.keys(question.interactive.answers).some(key => question.answerValues[key] === undefined || String(question.answerValues[key]).trim() === "")) return;
            await submitInteractiveAnswer(question, {values: question.answerValues});
        });
    }

    function bindFractionProductForm(form) {
        const question = data.questions[currentIndex];
        if (isSolved(question)) return;
        form.querySelectorAll("[data-lesson-key]").forEach(input => {
            const save = () => {
                input.value = input.value.replace(/[^0-9, ]/g, "");
                question.answerValues[input.dataset.lessonKey] = input.value;
            };
            input.addEventListener("input", save);
            input.addEventListener("change", save);
        });
        form.querySelectorAll("[data-product-cell]").forEach(button => button.addEventListener("click", () => {
            const index = Number(button.dataset.productCell);
            const selected = String(question.answerValues.selected || "").split(",").filter(Boolean).map(Number);
            const position = selected.indexOf(index);
            if (position >= 0) selected.splice(position, 1); else selected.push(index);
            question.answerValues.selected = selected.sort((a,b) => a-b).join(",");
            renderQuestion(null, false);
        }));
        form.querySelectorAll("[data-product-cancel]").forEach(button => button.addEventListener("click", () => {
            const id = button.dataset.productCancel;
            const selected = String(question.answerValues.selected || "").split(",").filter(Boolean);
            const position = selected.indexOf(id);
            if (position >= 0) selected.splice(position, 1); else selected.push(id);
            question.answerValues.selected = selected.sort().join(",");
            renderQuestion(null, false);
        }));
        form.querySelectorAll("[data-division-groups]").forEach(button => button.addEventListener("click", () => {
            question.answerValues.groups = button.dataset.divisionGroups;
            renderQuestion(null, false);
        }));
        form.querySelectorAll("[data-product-error]").forEach(button => button.addEventListener("click", () => {
            question.answerValues.error_index = button.dataset.productError;
            renderQuestion(null, false);
        }));
        form.querySelectorAll("[data-product-step]").forEach(button => button.addEventListener("click", () => {
            const index = Number(button.dataset.productStep);
            const order = String(question.answerValues.order || "").split(",").filter(value => value !== "").map(Number);
            const position = order.indexOf(index);
            if (position >= 0) order.splice(position, 1); else order.push(index);
            question.answerValues.order = order.join(",");
            renderQuestion(null, false);
        }));
        form.addEventListener("submit", async event => {
            event.preventDefault();
            if ([...form.querySelectorAll("[data-lesson-key]")].some(input => !input.value)) return;
            if (Object.keys(question.interactive.answers).some(key => question.answerValues[key] === undefined || String(question.answerValues[key]).trim() === "")) return;
            await submitInteractiveAnswer(question, {values: question.answerValues});
        });
    }

    function bindFractionPowerForm(form) {
        const question = data.questions[currentIndex];
        if (isSolved(question)) return;
        form.querySelectorAll("[data-lesson-key]").forEach(input => {
            const save = () => { question.answerValues[input.dataset.lessonKey] = input.value.trim(); };
            input.addEventListener("input", save);
            input.addEventListener("change", save);
        });
        form.querySelectorAll("[data-power-choice-key]").forEach(button => button.addEventListener("click", () => {
            question.answerValues[button.dataset.powerChoiceKey] = button.dataset.powerChoiceValue;
            renderQuestion(null, false);
        }));
        form.querySelectorAll("[data-fraction-power-error]").forEach(button => button.addEventListener("click", () => {
            question.answerValues.error_index = button.dataset.fractionPowerError;
            renderQuestion(null, false);
        }));
        form.querySelectorAll("[data-fraction-power-step]").forEach(button => button.addEventListener("click", () => {
            const index = Number(button.dataset.fractionPowerStep);
            const order = String(question.answerValues.order || "").split(",").filter(Boolean).map(Number);
            const position = order.indexOf(index);
            if (position >= 0) order.splice(position,1); else order.push(index);
            question.answerValues.order = order.join(",");
            renderQuestion(null,false);
        }));
        form.addEventListener("submit", async event => {
            event.preventDefault();
            if ([...form.querySelectorAll("[data-lesson-key]")].some(input => !input.value.trim())) return;
            if (Object.keys(question.interactive.answers).some(key => question.answerValues[key] === undefined || String(question.answerValues[key]).trim() === "")) return;
            await submitInteractiveAnswer(question,{values:question.answerValues});
        });
    }

    function bindFractionPercentForm(form) {
        const question = data.questions[currentIndex];
        if (isSolved(question)) return;
        form.querySelectorAll("[data-lesson-key]").forEach(input => {
            const save = () => { question.answerValues[input.dataset.lessonKey] = input.value.trim(); };
            input.addEventListener("input",save); input.addEventListener("change",save);
        });
        form.querySelectorAll("[data-percent-grid]").forEach(button => button.addEventListener("click",()=>{
            question.answerValues.selected = button.dataset.percentGrid;
            renderQuestion(null,false);
        }));
        const slider = form.querySelector("[data-percent-slider]");
        if (slider) slider.addEventListener("input",()=>{
            question.answerValues.percent = slider.value;
            const display = form.querySelector("[data-percent-value]");
            if (display) display.textContent = `${slider.value}%`;
        });
        form.querySelectorAll("[data-percent-error]").forEach(button=>button.addEventListener("click",()=>{
            question.answerValues.error_index = button.dataset.percentError; renderQuestion(null,false);
        }));
        form.querySelectorAll("[data-percent-step]").forEach(button=>button.addEventListener("click",()=>{
            const index=Number(button.dataset.percentStep), order=String(question.answerValues.order||"").split(",").filter(Boolean).map(Number), position=order.indexOf(index);
            if(position>=0) order.splice(position,1); else order.push(index);
            question.answerValues.order=order.join(","); renderQuestion(null,false);
        }));
        form.addEventListener("submit",async event=>{
            event.preventDefault();
            if([...form.querySelectorAll("[data-lesson-key]")].some(input=>!input.value.trim())) return;
            if(Object.keys(question.interactive.answers).some(key=>question.answerValues[key]===undefined||String(question.answerValues[key]).trim()==="")) return;
            await submitInteractiveAnswer(question,{values:question.answerValues});
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
