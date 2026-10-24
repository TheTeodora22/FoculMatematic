/* Run with: node scripts/verify_math_rendering.cjs */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const root = path.resolve(__dirname, "..");
const math = require(path.join(root, "static/core/js/math-rendering.js"));
const katex = require(path.join(root, "static/vendor/katex-0.19.0/katex.min.js"));

// These verify grouping/meaning, not only whether KaTeX accepts the syntax.
const fixtures = new Map([
    ["∑ₖ₌₁^4 1/[k(k+1)]", "\\sum_{k=1}^{4} \\frac{1}{k \\left( k + 1 \\right)}"],
    ["∑ₖ₌₁ⁿ k²", "\\sum_{k=1}^{n} k^{2}"],
    ["∏ₖ₌₂^7 (1−1/k²)", "\\prod_{k=2}^{7} \\left( 1 - \\frac{1}{k^{2}} \\right)"],
    ["n(n+1)(2n+1)/6", "\\frac{n \\left( n + 1 \\right) \\left( 2 n + 1 \\right)}{6}"],
    ["x⁴+1/x⁴", "x^{4} + \\frac{1}{x^{4}}"],
    ["aₙ₊₁=2aₙ+1", "a_{n+1} = 2 a_{n} + 1"],
    ["(−1)^(n+1)n(n+1)/2", "\\frac{\\left( -1 \\right)^{n + 1} n \\left( n + 1 \\right)}{2}"],
    ["√(2+uₙ)", "\\sqrt{2 + u_{n}}"],
    ["a/(b+c)", "\\frac{a}{b + c}"],
    ["a/b+c", "\\frac{a}{b} + c"],
]);
for (const [input, expected] of fixtures) assert.equal(math.toTex(input), expected, input);
assert.deepEqual(math.segments("O sumă de 2 lei și o monedă."), [{ text: "O sumă de 2 lei și o monedă." }]);
assert.equal(math.segments("Calculați \\(\\frac{1}{2}\\).")[1].tex, "\\frac{1}{2}");

const payload = JSON.parse(fs.readFileSync(path.join(root,
    "data/quizzes/clasa_9/clasa_9_u01_l05_rationamente_logice_inductia_matematica_si_probleme_de_numarare.json"), "utf8"));
let expressions = 0;
for (const question of payload.questions) {
    for (const text of [question.text, question.explanation, ...question.options.map(o => o.text)]) {
        const parts = math.segments(text);
        assert.equal(parts.map(p => p.text).join(""), text, "Source text must not be lost");
        for (const part of parts) {
            if (part.tex) {
                const html = katex.renderToString("\\displaystyle " + part.tex,
                    { throwOnError: true, strict: "error", trust: false, output: "htmlAndMathml" });
                assert.ok(html.includes("katex-mathml"));
                expressions++;
            } else assert.ok(!/[∑∏]/.test(part.text), "An unformatted sum/product remains: " + part.text);
        }
    }
}
console.log(`${fixtures.size} grouping fixtures passed; ${payload.questions.length} questions; ${expressions} mathematical fragments rendered without errors.`);
