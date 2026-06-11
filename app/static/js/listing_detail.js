document.addEventListener("DOMContentLoaded", async () => {
  const container = document.getElementById("detailContainer");

  try {
    const response = await fetch(`/api/listings/${LISTING_ID}`);
    if (!response.ok) throw new Error("Item not found");

    const item = await response.json();

    // 1. Authorization Logic (Mocked for Week 8)
    // We assume User ID 1 is the 'Logged In' user until Shamreen merges Auth
    const isOwner = item.seller_id === 1;

    // 2. Prepare the Edit button only if the user is the owner
    let editButtonHtml = "";
    if (isOwner) {
      editButtonHtml = `<a href="/edit-listing/${item.id}" class="btn btn-outline-secondary">Edit My Listing</a>`;
    }

    // 3. Build the UI
    container.innerHTML = `
            <div class="col-md-6">
                <img src="${item.image_url}" class="img-fluid rounded shadow" alt="${item.title}">
            </div>
            <div class="col-md-6">
                <nav aria-label="breadcrumb">
                    <ol class="breadcrumb">
                        <li class="breadcrumb-item"><a href="/marketplace">Marketplace</a></li>
                        <li class="breadcrumb-item active">${item.category}</li>
                    </ol>
                </nav>
                <h1 class="display-5 fw-bold">${item.title}</h1>
                <p class="text-muted">Listed on: ${new Date(item.listing_date).toLocaleDateString()}</p>
                <h3 class="text-success mb-4">$${item.price}</h3>
                
                <div class="mb-4">
                    <h5>Description</h5>
                    <p>${item.description}</p>
                    <span class="badge bg-secondary p-2">Condition: ${item.condition}</span>
                </div>

                <div class="card border-primary">
                    <div class="card-body">
                        <h5 class="card-title text-primary">Contact Seller</h5>
                        <hr>
                        <p class="mb-1"><strong>Name:</strong> ${item.seller_info ? item.seller_info.display_name : "Anonymous"}</p>
                        <p class="mb-1"><strong>Email:</strong> <a href="mailto:${item.seller_info ? item.seller_info.email : ""}">${item.seller_info ? item.seller_info.email : "N/A"}</a></p>
                        <p class="mb-0"><strong>Phone:</strong> ${item.seller_info ? item.seller_info.contact_number : "N/A"}</p>
                    </div>
                </div>
                
                <div class="mt-4 d-grid gap-2">
                    <button class="btn btn-primary btn-lg">Make an Offer</button>
                    ${editButtonHtml} <!-- This will be empty if not owner -->
                </div>
            </div>
        `;
  } catch (error) {
    container.innerHTML = `
            <div class="alert alert-danger w-100">
                <h4>Error 404</h4>
                <p>Sorry, the listing you are looking for does not exist or has been deleted.</p>
                <a href="/marketplace" class="btn btn-outline-danger">Back to Marketplace</a>
            </div>`;
  }
});
