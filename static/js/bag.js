/**
 * Handle adding products to the shopping bag asynchronously.
 * Display success or error feedback without reloading the page.
 */
document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("#add-to-bag-form");
    const feedback = document.querySelector("#site-feedback");

    if (!form || !feedback) return;

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const button = form.querySelector('button[type="submit"]');
        button.disabled = true;

        try {
            const response = await fetch(form.action, {
                method: "POST",
                body: new FormData(form),
            });

            const data = await response.json();

            if (!response.ok || !data.success) {
                throw new Error(data.error || "Unable to add product.");
            }

            feedback.textContent = "Product added to your bag.";
            feedback.className = "container alert alert-success mt-3";

        } catch (error) {
            feedback.textContent = error.message;
            feedback.className = "container alert alert-danger mt-3";

        } finally {
            button.disabled = false;
        }
    });
});

/**
 * Handle shopping bag quantity updates asynchronously.
 * Refresh item subtotals and the bag total without reloading the page.
 */
document.addEventListener("DOMContentLoaded", () => {
    const updateForms = document.querySelectorAll(".bag-update-form");
    const feedback = document.querySelector("#site-feedback");
    const bagTotal = document.querySelector("#bag-total");

    updateForms.forEach((form) => {
        form.addEventListener("submit", async (event) => {
            event.preventDefault();

            const button = form.querySelector('button[type="submit"]');
            const subtotal = form.closest(".bag-item")
                .querySelector(".bag-item-subtotal");

            button.disabled = true;

            try {
                const response = await fetch(form.action, {
                    method: "POST",
                    body: new FormData(form),
                });

                const data = await response.json();

                if (!response.ok || !data.success) {
                    throw new Error(data.error || "Unable to update quantity.");
                }

                subtotal.textContent = data.subtotal;
                bagTotal.textContent = data.total;

                feedback.textContent = "Shopping bag updated.";
                feedback.className = "container alert alert-success mt-3";

            } catch (error) {
                feedback.textContent = error.message;
                feedback.className = "container alert alert-danger mt-3";

            } finally {
                button.disabled = false;
            }
        });
    });
});

/**
 * Remove products from the shopping bag asynchronously.
 * Update the total and display the empty bag state when necessary.
 */
document.addEventListener("DOMContentLoaded", () => {
    const removeForms = document.querySelectorAll(".bag-remove-form");
    const feedback = document.querySelector("#site-feedback");
    const bagTotal = document.querySelector("#bag-total");
    const bagContent = document.querySelector("#bag-content");

    if (!feedback || !bagContent) return;

    removeForms.forEach((form) => {
        form.addEventListener("submit", async (event) => {
            event.preventDefault();

            const button = form.querySelector('button[type="submit"]');
            const bagItem = form.closest(".bag-item");

            button.disabled = true;

            try {
                const response = await fetch(form.action, {
                    method: "POST",
                    body: new FormData(form),
                });

                const data = await response.json();

                if (!response.ok || !data.success) {
                    throw new Error(data.error || "Unable to remove product.");
                }

                bagItem.remove();

                if (bagContent.querySelectorAll(".bag-item").length === 0) {
                    bagContent.innerHTML = "<p>Your shopping bag is empty.</p>";
                } else if (bagTotal) {
                    bagTotal.textContent = data.total;
                }

                feedback.textContent = "Product removed from your bag.";
                feedback.className = "container alert alert-success mt-3";

            } catch (error) {
                feedback.textContent = error.message;
                feedback.className = "container alert alert-danger mt-3";

            } finally {
                button.disabled = false;
            }
        });
    });
});