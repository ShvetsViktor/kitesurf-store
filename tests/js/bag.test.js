/**
 * Tests for shopping bag JavaScript functionality.
 */

describe("Shopping Bag", () => {

    beforeEach(() => {
        jest.resetModules();
    
        document.body.innerHTML = `
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

    test("Update changes subtotal and total", async () => {
        fetch.mockResolvedValue({
            ok: true,
            json: async () => ({
                success: true,
                subtotal: "1000.00",
                total: "1000.00",
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
    });

    test("Remove deletes product", async () => {
        fetch.mockResolvedValue({
            ok: true,
            json: async () => ({
                success: true,
                total: "0.00",
            }),
        });

        require("../../static/js/bag.js");
        document.dispatchEvent(new Event("DOMContentLoaded"));

        document.querySelector(".bag-remove-form").dispatchEvent(
            new Event("submit", { cancelable: true })
        );

        await new Promise(resolve => setTimeout(resolve, 0));

        expect(document.querySelector(".bag-item")).toBeNull();
    });

    test("Removing last product displays empty bag message", async () => {
        fetch.mockResolvedValue({
            ok: true,
            json: async () => ({
                success: true,
                total: "0.00",
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