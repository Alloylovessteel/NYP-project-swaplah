document.addEventListener('DOMContentLoaded', () => {
    // 1. UI Elements
    const container = document.getElementById('listingsContainer');
    const paginationContainer = document.getElementById('paginationContainer'); // Added this
    const searchBtn = document.getElementById('searchBtn');
    const searchInput = document.getElementById('searchInput');
    const categoryFilter = document.getElementById('categoryFilter');
    const clearBtn = document.getElementById('clearFilters');

    // 2. Fetch function - now accepts a 'page' argument (default is 1)
    async function fetchListings(page = 1) {
        const search = searchInput.value;
        const category = categoryFilter.value;

        // Added &page= to the URL
        let url = `/api/listings?search=${encodeURIComponent(search)}&category=${encodeURIComponent(category)}&page=${page}`;

        try {
            const response = await fetch(url);
            const data = await response.json();

            renderListings(data.listings);
            renderPagination(data); // Call the new pagination renderer
        } catch (error) {
            console.error("Error fetching listings:", error);
            container.innerHTML = `<div class="alert alert-danger w-100">Failed to load items.</div>`;
        }
    }

    // 3. Render Listings (Your existing logic)
    function renderListings(listings) {
        container.innerHTML = ''; 

        if (listings.length === 0) {
            container.innerHTML = `<div class="text-center w-100 py-5"><h5>No items found matching your criteria.</h5></div>`;
            return;
        }

        listings.forEach(item => {
            const card = `
                <div class="col">
                    <div class="card h-100 shadow-sm">
                        <img src="${item.image_url}" class="card-img-top" alt="${item.title}" style="height: 200px; object-fit: cover;">
                        <div class="card-body">
                            <h5 class="card-title">${item.title}</h5>
                            <p class="card-text text-muted small">${item.description.substring(0, 60)}...</p>
                            <div class="d-flex justify-content-between align-items-center">
                                <span class="badge bg-success">$${item.price}</span>
                                <span class="badge bg-secondary">${item.condition}</span>
                            </div>
                        </div>
                        <div class="card-footer bg-white border-top-0">
                            <a href="/api/listings/${item.id}" class="btn btn-outline-primary btn-sm w-100">View Details</a>
                        </div>
                    </div>
                </div>
            `;
            container.innerHTML += card;
        });
    }

    // 4. NEW: Render Pagination Buttons
    function renderPagination(data) {
        paginationContainer.innerHTML = '';

        // Don't show pagination if there's only 1 page
        if (data.pages <= 1) return;

        // Create the buttons
        for (let i = 1; i <= data.pages; i++) {
            const activeClass = i === data.current_page ? 'active' : '';
            const pageItem = `
                <li class="page-item ${activeClass}">
                    <a class="page-link" href="#" data-page="${i}">${i}</a>
                </li>
            `;
            paginationContainer.innerHTML += pageItem;
        }

        // Add click events to the new buttons
        document.querySelectorAll('.page-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetPage = e.target.getAttribute('data-page');
                fetchListings(targetPage);
                window.scrollTo(0, 0); // Scroll to top for better UX
            });
        });
    }

    // 5. Event Listeners
    // When searching or filtering, always reset to page 1
    searchBtn.addEventListener('click', () => fetchListings(1));
    categoryFilter.addEventListener('change', () => fetchListings(1));

    clearBtn.addEventListener('click', () => {
        searchInput.value = '';
        categoryFilter.value = '';
        fetchListings(1);
    });

    // Initial load
    fetchListings(1);
});
