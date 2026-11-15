// Uses the same parser and pinned KaTeX build as the live training page.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const renderer = require(path.join(root, 'static/core/js/math-rendering.js'));
const katex = require(path.join(root, 'static/vendor/katex-0.19.0/katex.min.js'));
const dir = path.join(root, 'data/quizzes/clasa_9');
let questions = 0, fragments = 0;
const files = fs.readdirSync(dir).filter(name => /^clasa_9_u06_l\d+_.*\.json$/.test(name));
assert.equal(files.length, 5);
for (const name of files) {
    const bank = JSON.parse(fs.readFileSync(path.join(dir, name), 'utf8'));
    for (const q of bank.questions) {
        questions++;
        for (const text of [q.text, q.explanation, ...(q.options || []).map(o => o.text)]) {
            assert.equal(typeof text, 'string');
            for (const part of renderer.segments(text)) {
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
assert.equal(questions, 425);
console.log(`${questions} questions, ${fragments} fragments: strict KaTeX passed.`);
