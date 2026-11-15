const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const math = require(path.join(root, 'static/core/js/math-rendering.js'));
const katex = require(path.join(root, 'static/vendor/katex-0.19.0/katex.min.js'));
const dir = path.join(root, 'data/quizzes/clasa_9');
let questions = 0, fragments = 0;
for (const name of fs.readdirSync(dir).filter(name => /^clasa_9_u04_l\d+_.*\.json$/.test(name))) {
    const data = JSON.parse(fs.readFileSync(path.join(dir, name), 'utf8'));
    for (const q of data.questions) {
        if (q.practice_scope?.bank !== 'gradul_ii_a4_v1') continue;
        questions++;
        for (const value of [q.text, q.explanation, ...q.options.map(o => o.text)]) {
            for (const segment of math.segments(value)) {
                if (!segment.tex) continue;
                katex.renderToString('\\displaystyle ' + segment.tex,
                    {throwOnError: true, strict: 'error', trust: false, maxExpand: 1000});
                fragments++;
            }
        }
    }
}
assert.equal(questions, 480);
console.log(`${questions} quadratic grids; ${fragments} strict KaTeX fragments passed.`);
