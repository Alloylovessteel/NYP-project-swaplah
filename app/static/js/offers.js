document.addEventListener("DOMContentLoaded", () => {
    const submitButton = document.getElementById("submitOfferBtn");

    if (!submitButton) {
        return;
    }

    submitButton.addEventListener("click", async () => {
        const offerPrice = document.getElementById("offerPrice").value;

        const response = await fetch("/api/offers", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                listing_id: LISTING_ID,
                offer_price: offerPrice
            })
        });

        const result = await response.json();

        alert(result.message || result.error);
    });
});