/**
 * Handle adding products to the shopping bag asynchronously.
 * Display success or error feedback without reloading the page.
 */
document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("#add-to-bag-form");
    const feedback = document.querySelector("#site-feedback");
    const bagCount = document.querySelector("#bag-count");

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

            if (bagCount) {
                bagCount.textContent = data.bag_count;
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
 * Refresh item subtotals, bag total and header count without reloading.
 */
document.addEventListener("DOMContentLoaded", () => {
    const updateForms = document.querySelectorAll(".bag-update-form");
    const feedback = document.querySelector("#site-feedback");
    const bagTotal = document.querySelector("#bag-total");
    const bagCount = document.querySelector("#bag-count");

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

                if (bagCount) {
                    bagCount.textContent = data.bag_count;
                }

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
 * Update the total, header count and empty bag state without reloading.
 */
document.addEventListener("DOMContentLoaded", () => {
    const removeForms = document.querySelectorAll(".bag-remove-form");
    const feedback = document.querySelector("#site-feedback");
    const bagTotal = document.querySelector("#bag-total");
    const bagContent = document.querySelector("#bag-content");
    const bagCount = document.querySelector("#bag-count");

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

                if (bagCount) {
                    bagCount.textContent = data.bag_count;
                }

                if (bagContent.querySelectorAll(".bag-item").length === 0) {
                    bagContent.innerHTML = `
                        <div class="card bag-empty-state">
                            <div class="card-body text-center py-5">
                                <h2 class="h5 mb-3">Your shopping bag is empty.</h2>
                                <p class="text-muted mb-0">
                                    Explore our kitesurfing equipment
                                    and add something to your bag.
                                </p>
                            </div>
                        </div>
                    `;
                } else if (bagTotal) {
                    if (data.total === null) {
                        window.location.reload();
                        return;
                    }
                
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