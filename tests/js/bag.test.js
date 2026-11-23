/**
 * Tests for shopping bag JavaScript functionality.
 */

describe("Shopping Bag", () => {

    beforeEach(() => {
        jest.resetModules();

        document.body.innerHTML = `
            <span id="bag-count">1</span>
            <div id="site-feedback"></div>

            <div id="bag-content">
                <div class="bag-item">
                    <form class="bag-update-form" action="/bag/update/1/">
                        <input name="quantity" value="1">
                        <button type="submit">Update</button>
                    </form>

                    <form class="bag-remove-form" action="/bag/remove/1/">
                        <button type="submit">Remove</button>
                    </form>

                    <span class="bag-item-subtotal">500.00</span>
                </div>

                <p>Total: £<span id="bag-total">500.00</span></p>
            </div>
        `;

        global.fetch = jest.fn();
    });

    test("Add updates header bag count", async () => {
        document.body.innerHTML = `
            <span id="bag-count">0</span>
            <div id="site-feedback"></div>

            <form id="add-to-bag-form" action="/bag/add/1/">
                <button type="submit">Add to Bag</button>
            </form>
        `;

        fetch.mockResolvedValue({
            ok: true,
            json: async () => ({
                success: true,
                quantity: 1,
                bag_count: 1,
            }),
        });

        require("../../static/js/bag.js");
        document.dispatchEvent(new Event("DOMContentLoaded"));

        document.querySelector("#add-to-bag-form").dispatchEvent(
            new Event("submit", { cancelable: true })
        );

        await new Promise(resolve => setTimeout(resolve, 0));

        expect(document.querySelector("#bag-count").textContent)
            .toBe("1");
    });

    test("Update changes subtotal, total and header count", async () => {
        fetch.mockResolvedValue({
            ok: true,
            json: async () => ({
                success: true,
                subtotal: "1000.00",
                total: "1000.00",
                bag_count: 2,
            }),
        });

        require("../../static/js/bag.js");
        document.dispatchEvent(new Event("DOMContentLoaded"));

        document.querySelector(".bag-update-form").dispatchEvent(
            new Event("submit", { cancelable: true })
        );

        await new Promise(resolve => setTimeout(resolve, 0));

        expect(document.querySelector(".bag-item-subtotal").textContent)
            .toBe("1000.00");

        expect(document.querySelector("#bag-total").textContent)
            .toBe("1000.00");

        expect(document.querySelector("#bag-count").textContent)
            .toBe("2");
    });

    test("Remove deletes product and updates header count", async () => {
        fetch.mockResolvedValue({
            ok: true,
            json: async () => ({
                success: true,
                total: "0.00",
                bag_count: 0,
            }),
        });

        require("../../static/js/bag.js");
        document.dispatchEvent(new Event("DOMContentLoaded"));

        document.querySelector(".bag-remove-form").dispatchEvent(
            new Event("submit", { cancelable: true })
        );

        await new Promise(resolve => setTimeout(resolve, 0));

        expect(document.querySelector(".bag-item")).toBeNull();

        expect(document.querySelector("#bag-count").textContent)
            .toBe("0");
    });

    test("Removing last product displays empty bag message", async () => {
        fetch.mockResolvedValue({
            ok: true,
            json: async () => ({
                success: true,
                total: "0.00",
                bag_count: 0,
            }),
        });

        require("../../static/js/bag.js");
        document.dispatchEvent(new Event("DOMContentLoaded"));

        document.querySelector(".bag-remove-form").dispatchEvent(
            new Event("submit", { cancelable: true })
        );

        await new Promise(resolve => setTimeout(resolve, 0));

        expect(document.querySelector("#bag-content").textContent)
            .toContain("Your shopping bag is empty.");
    });
}); 