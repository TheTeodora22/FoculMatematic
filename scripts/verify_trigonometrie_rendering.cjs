// Strict rendering check using exactly the production parser and pinned KaTeX.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const renderer = require(path.join(root, 'static/core/js/math-rendering.js'));
const katex = require(path.join(root, 'static/vendor/katex-0.19.0/katex.min.js'));
const dir = path.join(root, 'data/quizzes/clasa_9');
const partial = process.argv.includes('--partial');
const files = fs.readdirSync(dir).filter(name => /^clasa_9_u07_l\d+_.*\.json$/.test(name));
assert.equal(files.length, 9);
let questions = 0, fragments = 0;
for (const name of files) {
    const data = JSON.parse(fs.readFileSync(path.join(dir, name), 'utf8'));
    for (const q of data.questions.filter(q => q.practice_scope?.bank === 'g3_trigo_v1')) {
        questions++;
        for (const text of [q.text, q.explanation, ...q.options.map(option => option.text)]) {
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
        assert(q.options.every(option => option.text.length <= 255));
    }
}
assert(partial ? questions > 0 && questions <= 585 : questions === 585);
console.log(`OK: ${questions} trigonometrie questions, ${fragments} strict KaTeX fragments.`);
