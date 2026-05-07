/* Workforce Dev Hub - Vanilla JS */
(function () {
    "use strict";
    const ALERT_DISMISS_DELAY_MS = 6000;
    const COPY_FEEDBACK_DURATION_MS = 1200;

    document.addEventListener("DOMContentLoaded", function () {
        const alerts = document.querySelectorAll(".alert.alert-dismissible");
        alerts.forEach(function (alert) {
            setTimeout(function () {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
                if (bsAlert) bsAlert.close();
            }, ALERT_DISMISS_DELAY_MS);
        });
    });

    document.addEventListener("DOMContentLoaded", function () {
        const forms = document.querySelectorAll("form[data-confirm]");
        forms.forEach(function (form) {
            form.addEventListener("submit", function (event) {
                const message = form.getAttribute("data-confirm") || "Are you sure?";
                if (!window.confirm(message)) {
                    event.preventDefault();
                }
            });
        });
    });

    document.addEventListener("DOMContentLoaded", function () {
        const forms = document.querySelectorAll("form[data-submit-loading]");
        forms.forEach(function (form) {
            form.addEventListener("submit", function () {
                const submit = form.querySelector('[type="submit"]');
                if (!submit || submit.disabled) return;
                submit.dataset.originalText = submit.innerHTML;
                submit.disabled = true;
                submit.innerHTML = `<span class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>${submit.dataset.loadingText || "Saving..."}`;
            });
        });
    });

    document.addEventListener("DOMContentLoaded", function () {
        const buttons = document.querySelectorAll("[data-copy-target]");
        buttons.forEach(function (button) {
            button.addEventListener("click", async function () {
                const selector = button.getAttribute("data-copy-target");
                const source = selector ? document.querySelector(selector) : null;
                if (!source) return;
                const value = source.textContent || source.value || "";
                try {
                    await navigator.clipboard.writeText(value.trim());
                    button.dataset.originalLabel = button.textContent;
                    button.textContent = "Copied";
                    setTimeout(function () {
                        button.textContent = button.dataset.originalLabel || "Copy";
                    }, COPY_FEEDBACK_DURATION_MS);
                } catch (err) {
                    console.error("Copy failed", err);
                }
            });
        });
    });

    document.addEventListener("DOMContentLoaded", function () {
        const queryInputs = document.querySelectorAll('input[name="q"]');
        queryInputs.forEach(function (input) {
            if (!input.form || !input.value) return;
            const clear = document.createElement("button");
            clear.type = "button";
            clear.className = "btn btn-outline-secondary";
            clear.textContent = "Clear";
            clear.addEventListener("click", function () {
                input.value = "";
                input.form.submit();
            });
            const submitButton = input.form.querySelector(
                ".btn-outline-primary, .btn-primary, button[type='submit']"
            );
            if (submitButton) {
                submitButton.after(clear);
            } else {
                input.insertAdjacentElement("afterend", clear);
            }
        });
    });

    document.addEventListener("DOMContentLoaded", function () {
        const nameField = document.getElementById("name");
        const slugField = document.getElementById("slug");
        if (nameField && slugField && slugField.value === "") {
            nameField.addEventListener("input", function () {
                slugField.value = nameField.value
                    .toLowerCase()
                    .replace(/[^a-z0-9]+/g, "-")
                    .replace(/^-+|-+$/g, "");
            });
        }
    });
})();
