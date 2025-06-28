// farm_shop_project/static/users/js/admin_farmer_search.js

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('farmerSearchInput');
    const searchResults = document.getElementById('searchResults');
    const noResultsMessage = document.getElementById('noResultsMessage');
    const selectedFarmersContainer = document.getElementById('selectedFarmersContainer');
    const noSelectedMessage = document.getElementById('noSelectedMessage');
    const selectedCountSpan = document.getElementById('selectedCount');
    const selectedFarmerIdsHiddenInput = document.getElementById('id_selected_farmer_ids');

    let searchTimeout = null;
    const selectedFarmers = new Map(); // Map to store selected farmers: id -> {id, username, full_name, email}

    // Function to update the hidden input and selected count
    function updateSelectedState() {
        const ids = Array.from(selectedFarmers.keys()).join(',');
        selectedFarmerIdsHiddenInput.value = ids;
        selectedCountSpan.textContent = selectedFarmers.size;

        if (selectedFarmers.size > 0) {
            noSelectedMessage.style.display = 'none';
            selectedFarmersContainer.innerHTML = ''; // Clear previous
            selectedFarmers.forEach((farmer, id) => {
                const badge = document.createElement('span');
                badge.className = 'badge bg-primary me-2 mb-2 d-inline-flex align-items-center';
                badge.innerHTML = `${farmer.full_name} <button type="button" class="btn-close btn-close-white ms-1" aria-label="Remove" data-farmer-id="${id}"></button>`;
                selectedFarmersContainer.appendChild(badge);

                badge.querySelector('.btn-close').addEventListener('click', function() {
                    removeSelectedFarmer(id);
                });
            });
        } else {
            noSelectedMessage.style.display = 'block';
            selectedFarmersContainer.innerHTML = ''; // Clear badges
            selectedFarmersContainer.appendChild(noSelectedMessage);
        }
    }

    // Function to add a farmer to selected list
    function addSelectedFarmer(farmer) {
        if (!selectedFarmers.has(farmer.id)) {
            selectedFarmers.set(farmer.id, farmer);
            updateSelectedState();
            // Deselect checkbox in search results if it exists
            const checkbox = document.getElementById(`farmer_checkbox_${farmer.id}`);
            if (checkbox) {
                checkbox.checked = true;
            }
        }
    }

    // Function to remove a farmer from selected list
    function removeSelectedFarmer(farmerId) {
        if (selectedFarmers.has(farmerId)) {
            selectedFarmers.delete(farmerId);
            updateSelectedState();
            // Uncheck checkbox in search results if it exists
            const checkbox = document.getElementById(`farmer_checkbox_${farmerId}`);
            if (checkbox) {
                checkbox.checked = false;
            }
        }
    }

    // Handle search input changes
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        const query = this.value.trim();

        if (query.length < 3 && query.length !== 0) {
            searchResults.innerHTML = '<p class="text-center text-muted p-3">Type at least 3 characters to search.</p>';
            noResultsMessage.style.display = 'none';
            return;
        }

        if (query.length === 0) {
            searchResults.innerHTML = '';
            noResultsMessage.style.display = 'block';
            searchResults.appendChild(noResultsMessage);
            return;
        }

        searchTimeout = setTimeout(() => {
            fetch(`/accounts/admin/search-farmers/?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    searchResults.innerHTML = ''; // Clear previous results
                    if (data.status === 'success' && data.farmers.length > 0) {
                        noResultsMessage.style.display = 'none';
                        data.farmers.forEach(farmer => {
                            const item = document.createElement('div');
                            item.className = 'list-group-item list-group-item-action d-flex align-items-center';
                            item.innerHTML = `
                                <input type="checkbox" class="form-check-input me-2" id="farmer_checkbox_${farmer.id}" ${selectedFarmers.has(farmer.id) ? 'checked' : ''}>
                                <label class="form-check-label flex-grow-1" for="farmer_checkbox_${farmer.id}">
                                    <strong>${farmer.full_name}</strong> (${farmer.username})<br>
                                    <small class="text-muted">${farmer.email}</small>
                                </label>
                            `;
                            searchResults.appendChild(item);

                            item.querySelector(`#farmer_checkbox_${farmer.id}`).addEventListener('change', function() {
                                if (this.checked) {
                                    addSelectedFarmer(farmer);
                                } else {
                                    removeSelectedFarmer(farmer.id);
                                }
                            });
                        });
                    } else {
                        noResultsMessage.style.display = 'block';
                        searchResults.appendChild(noResultsMessage);
                        searchResults.innerHTML = '<p class="text-center text-muted p-3">No farmers found matching your search.</p>';
                    }
                })
                .catch(error => {
                    console.error('Error fetching farmer search results:', error);
                    searchResults.innerHTML = '<p class="text-center text-danger p-3">Error fetching search results.</p>';
                });
        }, 300); // Debounce search for 300ms
    });

    // Initial state update for selected farmers
    updateSelectedState();

    // Handle form submission to ensure the hidden input is correctly populated
    const notificationForm = document.getElementById('notificationForm');
    if (notificationForm) {
        notificationForm.addEventListener('submit', function() {
            updateSelectedState(); // Final update before submission
        });
    }
});