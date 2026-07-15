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
            if (!question.text || !Array.isArray(question.options) || question.options.length === 0) {
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

    function renderQuestion(selectedOptionId, showWrongSelection) {
        const question = data.questions[currentIndex];
        if (!cardEl || !question) {
            return;
        }

        cardEl.innerHTML =
            `<h2 style="margin:0 0 1rem;">${escapeHtml(question.text)}</h2>` +
            (showWrongSelection && selectedOptionId
                ? question.status === "wrong"
                    ? '<p class="training-feedback" style="margin:0 0 0.75rem;"><span class="training-feedback--wrong">Greșit. Încearcă alt răspuns.</span></p>'
                    : ""
                : feedbackHtml(question)) +
            explanationHtml(question) +
            optionsHtml(question, selectedOptionId, showWrongSelection);

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

    async function persistAnswer(question, optionId) {
        const body = new FormData();
        body.append("question_id", String(question.id));
        body.append("option_id", String(optionId));

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
                const result = await persistAnswer(question, optionId);
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
