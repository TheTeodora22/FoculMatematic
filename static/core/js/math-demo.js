(function () {
    "use strict";
    const error = document.getElementById("boards-error");
    if (!window.JXG) { window.fmMathBoardsBoot?.fail(); error.hidden = false; return; }
    try {
        const options = {boundingbox: [-6, 8, 8, -6], axis: true, keepaspectratio: true, showCopyright: true,
            showNavigation: false, resize: {enabled: true}, keyboard: {enabled: true}};
        const graph = JXG.JSXGraph.initBoard("function-board", options);
        const inputs = ["a", "b", "c"].map(key => document.getElementById("coef-" + key));
        let coefficients = [1, -4, 3];
        graph.create("functiongraph", [x => coefficients[0] * x * x + coefficients[1] * x + coefficients[2]],
            {strokeColor: "#315bd6", strokeWidth: 3});
        function update() {
            const valid = inputs.every(input => input.value !== "" && input.checkValidity() && Number.isFinite(input.valueAsNumber));
            if (!valid) {
                document.getElementById("graph-description").textContent = "Introdu coeficienți între −10 și 10, cu cel mult o zecimală.";
                return;
            }
            coefficients = inputs.map(input => input.valueAsNumber);
            document.getElementById("graph-description").textContent =
                `f(x) = (${coefficients[0]})x² + (${coefficients[1]})x + (${coefficients[2]})` +
                (coefficients[0] === 0 ? " — funcția nu mai este de gradul al doilea." : "");
            graph.update();
        }
        inputs.forEach(input => input.addEventListener("input", update));
        update();
        const triangle = JXG.JSXGraph.initBoard("triangle-board", options);
        const vertices = [[-2, -1], [4, -1], [1, 4]].map((coords, index) =>
            triangle.create("point", coords, {name: "ABC"[index], size: 4, fixed: false}));
        triangle.create("polygon", vertices, {fillColor: "#6a9de6", fillOpacity: .18,
            borders: {strokeColor: "#315bd6", strokeWidth: 2}});
        window.fmMathBoardsBoot?.ready();
    } catch (exception) {
        window.fmMathBoardsBoot?.fail();
        error.hidden = false;
        console.error("Inițializarea laboratorului matematic a eșuat", exception);
    }
}());
