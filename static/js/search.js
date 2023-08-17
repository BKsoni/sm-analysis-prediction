const stockInput = document.getElementById('stock-input');
const autocompleteResults = document.getElementById('autocomplete-results');

stockInput.addEventListener('input', () => {
    const inputText = stockInput.value.trim().toUpperCase();
    if (inputText.length >= 3) {
        fetch(`/autocomplete?search=${inputText}`)
            .then(response => response.json())
            .then(data => {
                const suggestions = data.suggestions;
                if (suggestions.length > 0) {
                    autocompleteResults.innerHTML = suggestions
                        .map(item => `<div class="autocomplete-item">${item}</div>`)
                        .join('');
                    autocompleteResults.style.display = 'block';
                } else {
                    autocompleteResults.style.display = 'none';
                }
            })
            .catch(error => {
                console.error('Error fetching autocomplete data:', error);
            });
    } else {
        autocompleteResults.style.display = 'none';
    }
});

autocompleteResults.addEventListener('click', event => {
    if (event.target.classList.contains('autocomplete-item')) {
        stockInput.value = event.target.textContent;
        autocompleteResults.style.display = 'none';
    }
});