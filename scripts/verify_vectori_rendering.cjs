// Verify exactly the mathematical fragments parsed by the production renderer.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const math = require(path.join(root, 'static/core/js/math-rendering.js'));
const katex = require(path.join(root, 'static/vendor/katex-0.19.0/katex.min.js'));
const dir = path.join(root, 'data/quizzes/clasa_9');
let fragments = 0, questions = 0;
for (const name of fs.readdirSync(dir).filter(name => /^clasa_9_u05_l\d+_.*\.json$/.test(name))) {
    const bank = JSON.parse(fs.readFileSync(path.join(dir, name), 'utf8'));
    for (const q of bank.questions) {
        questions++;
        for (const text of [q.text, q.explanation, ...(q.options || []).map(o => o.text)]) {
            assert.equal(typeof text, 'string');
            for (const part of math.segments(text)) {
                if (!part.tex) continue;
                try {
                    katex.renderToString('\\displaystyle ' + part.tex,
                        {throwOnError: true, strict: 'error', trust: false, maxExpand: 1000});
                    fragments++;
                } catch (error) {
                    throw new Error(`${name}: ${q.text}\n${part.tex}\n${error.message}`);
                }
            }
        }
    }
}
assert.equal(questions, 337);
console.log(`${questions} questions; ${fragments} mathematical fragments passed strict KaTeX rendering.`);
