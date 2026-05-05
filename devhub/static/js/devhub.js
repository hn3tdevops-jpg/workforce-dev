/* Workforce Dev Hub - Vanilla JS */

(function () {
    "use strict";

    // Auto-dismiss alerts after 5 seconds
    document.addEventListener("DOMContentLoaded", function () {
        const alerts = document.querySelectorAll(".alert.alert-dismissible");
        alerts.forEach(function (alert) {
            setTimeout(function () {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
                if (bsAlert) bsAlert.close();
            }, 5000);
        });
    });

    // Confirm dangerous form submissions
    document.addEventListener("DOMContentLoaded", function () {
        const dangerForms = document.querySelectorAll("form[data-confirm]");
        dangerForms.forEach(function (form) {
            form.addEventListener("submit", function (e) {
                const msg = form.getAttribute("data-confirm") || "Are you sure?";
                if (!window.confirm(msg)) {
                    e.preventDefault();
                }
            });
        });
    });

    // Slug auto-fill from name field
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
