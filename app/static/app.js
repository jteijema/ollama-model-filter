const slider = document.getElementById('slider');
const minInput = document.getElementById('minInput');
const maxInput = document.getElementById('maxInput');
const modelsContainer = document.getElementById('modelsContainer');

// Initialize noUiSlider
noUiSlider.create(slider, {
    start: [0, 406],
    connect: true,
    range: {
        'min': 0,
        'max': 406
    },
    step: 1
});

const API_BASE_URL = window.location.origin; 

async function fetchModels(min, max) {
    const response = await fetch(`${API_BASE_URL}/models?over=${min}&under=${max}`);
    if (!response.ok) {
        console.error('Failed to fetch models:', response.status, response.statusText);
        return;
    }
    const models = await response.json();
    renderModels(models);
}

// Render models on the page
function renderModels(models) {
    modelsContainer.innerHTML = '';
    models.forEach(model => {
        const modelElement = document.createElement('div');
        modelElement.classList.add('model');
        const modelUrl = `https://ollama.com/library/${model.name}`;
        modelElement.innerHTML = `
            <h3><a href="${modelUrl}" target="_blank" rel="noopener noreferrer">${model.name}</a></h3>
            <p>Sizes: ${model.sizes.join(', ')}</p>
            <p class="latest-update">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="update-icon">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"></path>
                </svg>
                Updated ${model.latest_update}
            </p>
        `;
        modelsContainer.appendChild(modelElement);
    });
}


// Update slider when input fields change
minInput.addEventListener('change', () => {
    let min = parseInt(minInput.value, 10);
    let max = parseInt(maxInput.value, 10);
    if (min < 0) min = 0;
    if (min > max) min = max;
    slider.noUiSlider.set([min, null]);
    fetchModels(min, max);
});

maxInput.addEventListener('change', () => {
    let min = parseInt(minInput.value, 10);
    let max = parseInt(maxInput.value, 10);
    if (max > 406) max = 406;
    if (max < min) max = min;
    slider.noUiSlider.set([null, max]);
    fetchModels(min, max);
});

// Update input fields and fetch models when the slider changes
slider.noUiSlider.on('update', function (values) {
    const [min, max] = values.map(value => Math.round(value));
    minInput.value = min;
    maxInput.value = max;
});

slider.noUiSlider.on('change', function (values) {
    const [min, max] = values.map(value => Math.round(value));
    fetchModels(min, max);
});

// Initial fetch
fetchModels(0, 406);
