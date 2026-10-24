/* LaTeX rendering and conservative typography for the existing plain-text bank.
 * Source strings stay unchanged: only explicitly marked display elements render.
 */
(function (global) {
    "use strict";
    const subChars = "₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₕᵢⱼₖₗₘₙₒₚᵣₛₜᵤᵥₓ";
    const subValues = "0123456789+-=()aehijklmnoprstuvx";
    const supChars = "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿⁱ";
    const supValues = "0123456789+-=()ni";
    const translate = (value, from, to) => Array.from(value, c => to[from.indexOf(c)] || c).join("");
    const isLetter = c => Boolean(c && /\p{L}/u.test(c));
    const ignoredWords = new Set(["a", "cu", "un", "la", "de", "din", "in", "si", "sau", "iar"]);
    const symbols = {
        "−": "-", "·": "\\cdot", "×": "\\times", "≤": "\\le", "≥": "\\ge", "≠": "\\ne",
        "∈": "\\in", "∉": "\\notin", "⊆": "\\subseteq", "∪": "\\cup", "∩": "\\cap", "∖": "\\setminus",
        "⇒": "\\Rightarrow", "⇔": "\\Leftrightarrow", "±": "\\pm", "…": "\\ldots", "⋯": "\\cdots",
        "ℕ": "\\mathbb{N}", "ℤ": "\\mathbb{Z}", "ℚ": "\\mathbb{Q}", "ℝ": "\\mathbb{R}",
        "∅": "\\varnothing", "∞": "\\infty", "α": "\\alpha", "β": "\\beta", "γ": "\\gamma",
        "δ": "\\delta", "π": "\\pi", "∀": "\\forall", "∃": "\\exists", "¬": "\\neg",
        "∧": "\\land", "∨": "\\lor", "°": "{}^\\circ",
    };
    const operators = new Set(["+", "-", "−", "·", "×", "*", "/", "^", "_", "=", "<", ">", ":", ",", ";",
        "≤", "≥", "≠", "∈", "∉", "⊆", "∪", "∩", "∖", "⇒", "⇔", "±", "∧", "∨"]);
    const opens = new Set(["(", "[", "{", "⌊"]);
    const closes = new Set([")", "]", "}", "⌋"]);

    function readScript(text, start, chars, values) {
        let end = start;
        while (end < text.length && chars.includes(text[end])) end++;
        return { value: translate(text.slice(start, end), chars, values), end };
    }

    function tokenAt(text, start) {
        const c = text[start];
        if (!c) return null;
        if (c === "∑" || c === "∏") {
            const lower = readScript(text, start + 1, subChars, subValues);
            let upper = readScript(text, lower.end, supChars, supValues);
            if (text[lower.end] === "^") {
                const match = /^(?:\^([A-Za-z0-9]+)|\^\(([^()]*)\))/.exec(text.slice(lower.end));
                if (match) upper = { value: match[1] || match[2], end: lower.end + match[0].length };
            }
            const command = c === "∑" ? "\\sum" : "\\prod";
            return { kind: "sum", tex: command + (lower.value ? `_{${lower.value}}` : "") + (upper.value ? `^{${upper.value}}` : ""),
                end: upper.end, math: true };
        }
        if (subChars.includes(c)) return null;
        if (supChars.includes(c)) {
            const script = readScript(text, start, supChars, supValues);
            return { kind: "sup", tex: script.value, end: script.end, math: true };
        }
        if (c === "√") return { kind: "sqrt", end: start + 1, math: true };
        if (opens.has(c) || closes.has(c)) return { kind: c, tex: c, end: start + 1, math: c === "⌊" || c === "⌋" };
        if (operators.has(c)) return { kind: c, tex: symbols[c] || c, end: start + 1, math: ![",", ";", ":"].includes(c) };
        if (c === "!") return { kind: "!", tex: "!", end: start + 1, math: true };
        if (symbols[c]) return { kind: "atom", tex: symbols[c], end: start + 1, math: true };
        const numeric = /^\d+(?:[.,]\d+)?/.exec(text.slice(start));
        if (numeric) return { kind: "atom", tex: numeric[0].replace(",", "{,}"), end: start + numeric[0].length };
        const word = /^[A-Za-z]+/.exec(text.slice(start));
        if (word) {
            const value = word[0];
            if (isLetter(text[start + value.length]) && !subChars.includes(text[start + value.length]) && !supChars.includes(text[start + value.length])) return null;
            // Single variables and conventional products (ab, nm, ...) only.
            if (value.length > 1 && (ignoredWords.has(value.toLowerCase()) || value.length > 3 || !/^[abcdkmnpqrstuvxyzABCDKMNPQRSTUVXYZ]+$/.test(value))) return null;
            let end = start + value.length;
            const script = readScript(text, end, subChars, subValues);
            let tex = value;
            if (script.value) { tex += `_{${script.value}}`; end = script.end; }
            return { kind: "atom", tex, end, math: Boolean(script.value) };
        }
        return null;
    }

    function collect(text, start) {
        const tokens = [];
        let cursor = start;
        while (cursor < text.length) {
            let next = cursor;
            while (text[next] === " " || text[next] === "\u00a0") next++;
            const token = tokenAt(text, next);
            if (!token) break;
            tokens.push(token);
            cursor = token.end;
        }
        while (tokens.length && [",", ";", ":"].includes(tokens[tokens.length - 1].kind)) tokens.pop();
        return { tokens, end: tokens.length ? tokens[tokens.length - 1].end : start };
    }

    function toTex(tokens) {
        let index = 0;
        const peek = () => tokens[index];
        const bare = node => node.body === undefined ? node.tex : node.body;
        const atomStart = token => token && ["atom", "sqrt", "sum", "(", "[", "{", "⌊"].includes(token.kind);
        function base() {
            const token = tokens[index++];
            if (!token) throw new Error("Missing operand");
            let node;
            if (["+", "-", "−", "±"].includes(token.kind)) {
                node = { tex: token.tex + base().tex };
            } else if (token.kind === "sqrt") {
                node = { tex: `\\sqrt{${bare(base())}}` };
            } else if (token.kind === "sum") {
                node = { tex: token.tex + " " + multiply().tex };
            } else if (opens.has(token.kind)) {
                const body = sequence();
                const closing = tokens[index++];
                if (!closing || !closes.has(closing.kind)) throw new Error("Unclosed group");
                const left = { "{": "\\{", "⌊": "\\lfloor" }[token.kind] || token.kind;
                const right = { "}": "\\}", "⌋": "\\rfloor" }[closing.kind] || closing.kind;
                node = { tex: `\\left${left} ${body} \\right${right}`, body };
            } else if (token.kind === "atom") {
                node = { tex: token.tex };
            } else throw new Error("Unexpected token");
            while (peek() && ["^", "_", "sup", "!"].includes(peek().kind)) {
                const op = tokens[index++];
                if (op.kind === "!") node = { tex: node.tex + "!" };
                else if (op.kind === "sup") node = { tex: node.tex + `^{${op.tex}}` };
                else node = { tex: node.tex + `${op.kind}{${bare(base())}}` };
            }
            return node;
        }
        function multiply() {
            let node = base();
            while (peek()) {
                const op = peek();
                if (op.kind === "/") {
                    index++;
                    node = { tex: `\\frac{${bare(node)}}{${bare(base())}}` };
                } else if (["·", "×", "*"].includes(op.kind)) {
                    index++;
                    node = { tex: node.tex + "\\cdot " + base().tex };
                } else if (atomStart(op)) node = { tex: node.tex + " " + base().tex };
                else break;
            }
            return node;
        }
        function sequence() {
            let tex = multiply().tex;
            while (peek() && !closes.has(peek().kind)) {
                const op = tokens[index++];
                if (!operators.has(op.kind)) throw new Error("Unexpected sequence");
                tex += " " + op.tex + " " + multiply().tex;
            }
            return tex;
        }
        const tex = sequence();
        if (index !== tokens.length) throw new Error("Trailing tokens");
        return tex;
    }

    function segments(text) {
        const result = [];
        let cursor = 0, plain = "";
        const flush = () => { if (plain) result.push({ text: plain }); plain = ""; };
        while (cursor < text.length) {
            const explicit = /^(\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\])/.exec(text.slice(cursor));
            if (explicit) {
                flush();
                result.push({ text: explicit[0], tex: explicit[0].slice(2,-2), display: explicit[0][1] === "[" });
                cursor += explicit[0].length;
                continue;
            }
            const canStart = !isLetter(text[cursor-1]) && !/[0-9]/.test(text[cursor-1] || "");
            const found = canStart ? collect(text, cursor) : { tokens: [] };
            if (found.tokens.length && found.tokens.some(t => t.math)) {
                try {
                    const tex = toTex(found.tokens);
                    flush();
                    result.push({ text: text.slice(cursor, found.end), tex });
                    cursor = found.end;
                    continue;
                } catch (_) { /* Incomplete/ambiguous legacy fragments remain readable text. */ }
            }
            plain += text[cursor++];
        }
        flush();
        return result;
    }

    function render(root) {
        if (!global.katex || !root) return;
        const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
            acceptNode(node) {
                return node.parentElement.closest(".fm-formula, .katex, script, style, textarea, pre, code, input, select")
                    ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT;
            },
        });
        const nodes = [];
        while (walker.nextNode()) nodes.push(walker.currentNode);
        for (const node of nodes) {
            const parts = segments(node.textContent);
            if (!parts.some(p => p.tex)) continue;
            const fragment = document.createDocumentFragment();
            for (const part of parts) {
                if (!part.tex) { fragment.appendChild(document.createTextNode(part.text)); continue; }
                const span = document.createElement("span");
                span.className = "fm-formula";
                try {
                    global.katex.render("\\displaystyle " + part.tex, span, {
                        displayMode: Boolean(part.display), throwOnError: true, trust: false,
                        strict: "error", maxExpand: 1000, output: "htmlAndMathml",
                    });
                    fragment.appendChild(span);
                } catch (_) { fragment.appendChild(document.createTextNode(part.text)); }
            }
            node.replaceWith(fragment);
        }
    }

    global.FMMath = { segments, toTex: text => toTex(collect(text, 0).tokens), render };
    if (typeof module !== "undefined" && module.exports) module.exports = global.FMMath;
    if (typeof document === "undefined") return;
    function start() {
        const container = document.querySelector(".container");
        if (!container) return;
        let scheduled = false;
        const observer = new MutationObserver(() => {
            if (scheduled) return;
            scheduled = true;
            requestAnimationFrame(update);
        });
        function update() {
            scheduled = false;
            observer.disconnect();
            container.querySelectorAll("[data-math-content]").forEach(render);
            observer.observe(container, { childList: true, subtree: true, characterData: true });
        }
        update();
    }
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start);
    else start();
})(typeof window === "undefined" ? globalThis : window);
