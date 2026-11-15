/* Independent recovery path: still works when training.js cannot execute. */
(function () {
    let ready = false;
    document.documentElement.classList.add("fm-js");

    function fail(message) {
        if (ready) return;
        document.querySelector(".training-page")?.classList.remove("training-page--loading");
        const loader = document.getElementById("training-loader");
        if (!loader) return;
        loader.hidden = false;
        loader.classList.add("training-loader--error");
        loader.style.display = "flex";
        loader.setAttribute("role", "alert");
        loader.replaceChildren();
        const text = document.createElement("p");
        text.textContent = message || "Antrenarea nu s-a încărcat complet. Reîncarcă pagina pentru a încerca din nou.";
        const retry = document.createElement("button");
        retry.type = "button";
        retry.className = "btn btn-press";
        retry.textContent = "Reîncarcă pagina";
        retry.addEventListener("click", () => window.location.reload());
        loader.append(text, retry);
    }

    const timeout = window.setTimeout(() => fail(), 15000);
    window.fmTrainingBoot = {
        fail,
        ready() { ready = true; window.clearTimeout(timeout); },
    };
    window.addEventListener("error", event => {
        const script = event.target;
        if ((script?.tagName === "SCRIPT" && script.hasAttribute("data-training-script")) ||
            (event.filename && event.filename.includes("/core/js/training.js"))) {
            window.clearTimeout(timeout);
            fail();
        }
    }, true);
})();
