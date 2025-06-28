// farm_shop_project/static/users/js/pincode_lookup.js
document.addEventListener('DOMContentLoaded', function() {
    const pincodeFieldReg = document.getElementById('id_pincode_reg');
    const cityFieldReg = document.getElementById('id_city_reg');
    const stateFieldReg = document.getElementById('id_state_reg');

    // For admin create employee form
    const pincodeFieldEmp = document.getElementById('id_pincode');
    const cityFieldEmp = document.getElementById('id_city');
    const stateFieldEmp = document.getElementById('id_state');

    function setupPincodeLookup(pincodeInput, cityInput, stateInput) {
        if (!pincodeInput || !cityInput || !stateInput) {
            return; // Fields not present on this page
        }

        let timeout = null;
        pincodeInput.addEventListener('input', function() {
            clearTimeout(timeout);
            const pincode = this.value.trim();

            cityInput.value = ''; // Clear previous value immediately
            stateInput.value = ''; // Clear previous value immediately
            cityInput.placeholder = 'Fetching...';
            stateInput.placeholder = 'Fetching...';

            if (pincode.length !== 6 || !/^\d+$/.test(pincode)) {
                // Pincode is not 6 digits or contains non-digits, clear fields and placeholders
                cityInput.placeholder = 'Auto-filled by Pincode';
                stateInput.placeholder = 'Auto-filled by Pincode';
                return;
            }

            timeout = setTimeout(() => {
                fetch(`/accounts/pincode-lookup/?pincode=${pincode}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            cityInput.value = data.city || '';
                            stateInput.value = data.state || '';
                            cityInput.placeholder = data.city ? '' : 'City not found';
                            stateInput.placeholder = data.state ? '' : 'State not found';
                        } else {
                            cityInput.value = '';
                            stateInput.value = '';
                            cityInput.placeholder = data.message || 'Invalid Pincode';
                            stateInput.placeholder = 'Invalid Pincode';
                        }
                    })
                    .catch(error => {
                        console.error('Pincode lookup error:', error);
                        cityInput.value = '';
                        stateInput.value = '';
                        cityInput.placeholder = 'Error fetching data';
                        stateInput.placeholder = 'Error fetching data';
                    });
            }, 500); // Debounce for 500ms
        });

        // Handle clearing if pincode field is emptied
        pincodeInput.addEventListener('blur', function() {
            if (!this.value.trim()) {
                cityInput.value = '';
                stateInput.value = '';
                cityInput.placeholder = 'Auto-filled by Pincode';
                stateInput.placeholder = 'Auto-filled by Pincode';
            }
        });
    }

    // Apply setup to both forms if their fields exist
    setupPincodeLookup(pincodeFieldReg, cityFieldReg, stateFieldReg);
    setupPincodeLookup(pincodeFieldEmp, cityFieldEmp, stateFieldEmp);
});