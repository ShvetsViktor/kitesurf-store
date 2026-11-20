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