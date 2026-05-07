/* Workforce Dev Hub - Vanilla JS */

(function () {
    "use strict";

    // Auto-dismiss alerts after 5 seconds
    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll(".alert.alert-dismissible").forEach(function (alert) {
            setTimeout(function () {
                var bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
                if (bsAlert) bsAlert.close();
            }, 5000);
        });
    });

    // Confirm dangerous form submissions
    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll("form[data-confirm]").forEach(function (form) {
            form.addEventListener("submit", function (e) {
                var msg = form.getAttribute("data-confirm") || "Are you sure?";
                if (!window.confirm(msg)) {
                    e.preventDefault();
                }
            });
        });
    });

    // Submit loading state: show spinner on submit buttons in any form
    // (except forms with data-no-loading attribute)
    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll("form:not([data-no-loading])").forEach(function (form) {
            form.addEventListener("submit", function () {
                var btn = form.querySelector("[type=submit]");
                if (!btn || btn.disabled) return;
                // Store original text so we can restore it if needed
                var label = btn.querySelector(".btn-label");
                var loading = btn.querySelector(".btn-loading");
                if (label && loading) {
                    // Already has dual-state markup (e.g. login page handles its own)
                    return;
                }
                var original = btn.innerHTML;
                btn.innerHTML =
                    '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>' +
                    "Please wait\u2026";
                btn.disabled = true;
                // Re-enable after 8 s in case form validation rejects
                setTimeout(function () {
                    btn.disabled = false;
                    btn.innerHTML = original;
                }, 8000);
            });
        });
    });

    // Slug auto-fill from name field
    document.addEventListener("DOMContentLoaded", function () {
        var nameField = document.getElementById("name");
        var slugField = document.getElementById("slug");
        if (nameField && slugField && slugField.value === "") {
            nameField.addEventListener("input", function () {
                slugField.value = nameField.value
                    .toLowerCase()
                    .replace(/[^a-z0-9]+/g, "-")
                    .replace(/^-+|-+$/g, "");
            });
        }
    });

    // Copy-to-clipboard for elements with data-copy attribute
    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll("[data-copy]").forEach(function (btn) {
            btn.addEventListener("click", function () {
                var text = btn.getAttribute("data-copy");
                if (!text) return;
                navigator.clipboard.writeText(text).then(function () {
                    var original = btn.innerHTML;
                    btn.innerHTML = '<i class="bi bi-check2"></i>';
                    setTimeout(function () { btn.innerHTML = original; }, 1500);
                }).catch(function () {
                    // Fallback for browsers without clipboard API
                    var ta = document.createElement("textarea");
                    ta.value = text;
                    ta.style.position = "fixed";
                    ta.style.opacity = "0";
                    document.body.appendChild(ta);
                    ta.focus();
                    ta.select();
                    document.execCommand("copy");
                    document.body.removeChild(ta);
                });
            });
        });
    });

})();
