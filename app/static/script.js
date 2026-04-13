let currentStep = 1;
let applianceEnergy = 0;
let seasonData = null;
let energyChart = null;

document.addEventListener('DOMContentLoaded', function() {
    updateApplianceEnergy();
    setupEventListeners();
    detectSeason();
    initializeModelSelection();
});

function initializeModelSelection() {
    const selectedModel = document.querySelector('input[name="model_type"]:checked');
    if (!selectedModel) {
        const availableModel = document.querySelector('input[name="model_type"]:not([disabled])');
        if (availableModel) {
            availableModel.checked = true;
            handleModelSelection({ target: availableModel });
        }
    } else {
        handleModelSelection({ target: selectedModel });
    }
}

function setupEventListeners() {
    const applianceInputs = document.querySelectorAll('#step1 input[type="number"], #step1 input[type="checkbox"]');
    applianceInputs.forEach(input => {
        input.addEventListener('input', updateApplianceEnergy);
        input.addEventListener('change', updateApplianceEnergy);
    });

    const tempInput = document.getElementById('avg_temp');
    if (tempInput) {
        tempInput.addEventListener('input', detectSeason);
    }
    
    const modelInputs = document.querySelectorAll('input[name="model_type"]');
    modelInputs.forEach(input => {
        input.addEventListener('change', handleModelSelection);
    });
}

function handleModelSelection(event) {
    const selectedModel = event.target.value;
    
    const modelCards = document.querySelectorAll('.model-card');
    modelCards.forEach(card => {
        card.classList.remove('selected');
    });
    
    event.target.closest('.model-card').classList.add('selected');
}

function goToStep(stepNumber) {
    if (stepNumber < 1 || stepNumber > 4) return;
    
    if (!validateCurrentStep()) {
        return;
    }
    
    const currentStepElement = document.querySelector('.step-content.active');
    if (currentStepElement) {
        currentStepElement.classList.remove('active');
    }
    
    const newStepElement = document.getElementById(`step${stepNumber}`);
    if (newStepElement) {
        newStepElement.classList.add('active');
    }
    
    updateProgressBar(stepNumber);
    
    currentStep = stepNumber;
    
    if (stepNumber === 2) {
        detectSeason();
    } else if (stepNumber === 3) {
    }
}

function validateCurrentStep() {
    if (currentStep === 1) {
        const hasAppliances = getApplianceData();
        const totalEnergy = Object.values(hasAppliances).reduce((sum, hours) => sum + hours, 0);
        
        if (totalEnergy === 0) {
            alert('Please select at least one appliance or specify usage hours.');
            return false;
        }
    } else if (currentStep === 2) {
        const weatherInputs = document.querySelectorAll('#step2 input[required]');
        for (let input of weatherInputs) {
            if (!input.value || input.value === '') {
                alert('Please fill in all weather fields.');
                input.focus();
                return false;
            }
        }
    } else if (currentStep === 3) {
        const selectedModel = getSelectedModel();
        if (!selectedModel) {
            alert('Please select a prediction model.');
            return false;
        }
    }
    return true;
}

function updateProgressBar(stepNumber) {
    const steps = document.querySelectorAll('.progress-step');
    steps.forEach((step, index) => {
        if (index + 1 <= stepNumber) {
            step.classList.add('active');
        } else {
            step.classList.remove('active');
        }
    });
}

function getApplianceData() {
    const appliances = {};
    
    appliances.ac = parseFloat(document.getElementById('ac_hours').value) || 0;
    appliances.fan = parseFloat(document.getElementById('fan_hours').value) || 0;
    appliances.lights = parseFloat(document.getElementById('lights_hours').value) || 0;
    appliances.television = parseFloat(document.getElementById('television_hours').value) || 0;
    appliances.washing_machine = parseFloat(document.getElementById('washing_machine_hours').value) || 0;
    
    const refrigeratorCheck = document.getElementById('refrigerator_check');
    appliances.refrigerator = refrigeratorCheck.checked ? 24 : 0;
    
    return appliances;
}

function updateApplianceEnergy() {
    const appliances = getApplianceData();
    
    fetch('/api/calculate-appliance-energy', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ appliances: appliances })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            applianceEnergy = data.total_energy_kwh;
            document.getElementById('appliance_energy').textContent = applianceEnergy.toFixed(2);
        }
    })
    .catch(error => {
        console.error('Error calculating appliance energy:', error);
    });
}

function detectSeason() {
    const avgTemp = parseFloat(document.getElementById('avg_temp').value);
    
    if (isNaN(avgTemp)) return;
    
    fetch('/api/detect-season', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ temperature: avgTemp })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            seasonData = data;
            updateSeasonDisplay(data);
        }
    })
    .catch(error => {
        console.error('Error detecting season:', error);
    });
}

function updateSeasonDisplay(data) {
    const seasonDisplay = document.getElementById('season_display');
    if (seasonDisplay) {
        const seasonText = data.season.toUpperCase();
        seasonDisplay.innerHTML = `
            <span class="season-icon">${seasonText}</span>
            <span class="season-name">${data.season}</span>
        `;
        seasonDisplay.style.color = data.color;
    }
}

function getWeatherData() {
    return {
        avg_temp: parseFloat(document.getElementById('avg_temp').value),
        avg_rel_humidity: parseFloat(document.getElementById('avg_rel_humidity').value),
        avg_wind_speed: parseFloat(document.getElementById('avg_wind_speed').value),
        inst_temp: parseFloat(document.getElementById('inst_temp').value),
        total_global_rad: parseFloat(document.getElementById('total_global_rad').value)
    };
}

function getSelectedModel() {
    const modelRadios = document.querySelectorAll('input[name="model_type"]');
    for (let radio of modelRadios) {
        if (radio.checked && !radio.disabled) {
            return radio.value;
        }
    }
    
    const fallbackRadio = document.querySelector('input[name="model_type"][value="fallback"]');
    if (fallbackRadio && !fallbackRadio.disabled) {
        fallbackRadio.checked = true;
        return 'fallback';
    }
    
    return null;
}

function makePrediction() {
    if (!validateCurrentStep()) {
        return;
    }
    
    const weatherData = getWeatherData();
    const modelType = getSelectedModel();
    
    const predictionData = {
        ...weatherData,
        lag_1: applianceEnergy,
        model_type: modelType
    };
    
    const predictButton = document.querySelector('.btn-predict');
    const originalText = predictButton.textContent;
    predictButton.textContent = '🔄 Predicting...';
    predictButton.disabled = true;
    
    fetch('/api/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(predictionData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayResults(data);
            goToStep(4);
        } else {
            alert('Prediction failed: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error making prediction:', error);
        alert('Error making prediction. Please try again.');
    })
    .finally(() => {
        predictButton.textContent = originalText;
        predictButton.disabled = false;
    });
}

function displayResults(predictionData) {
    document.getElementById('result_appliance_energy').textContent = applianceEnergy.toFixed(2);
    document.getElementById('result_prediction').textContent = predictionData.prediction.toFixed(2);
    document.getElementById('result_model').textContent = predictionData.model;
    
    if (seasonData) {
        document.getElementById('result_season_icon').textContent = seasonData.icon;
        document.getElementById('result_season').textContent = seasonData.season;
    }
    
    if (predictionData.analysis) {
        displayEnergyAnalysis(predictionData.analysis);
    }
    
    createEnergyChart(applianceEnergy, predictionData.prediction);
}

function displayEnergyAnalysis(analysis) {
    let analysisSection = document.getElementById('energy-analysis');
    if (!analysisSection) {
        analysisSection = document.createElement('div');
        analysisSection.id = 'energy-analysis';
        analysisSection.className = 'energy-analysis-section';
        
        const resultsGrid = document.querySelector('.results-grid');
        resultsGrid.parentNode.insertBefore(analysisSection, resultsGrid.nextSibling);
    }
    
    const statusColors = {
        'efficient': '#10b981',
        'moderate': '#f59e0b', 
        'wasteful': '#ef4444'
    };
    
    const statusColor = statusColors[analysis.status] || '#6b7280';
    
    analysisSection.innerHTML = `
        <div class="analysis-header">
            <h3>Energy Efficiency Analysis</h3>
            <div class="efficiency-status" style="background-color: ${statusColor}20; border-left: 4px solid ${statusColor};">
                <div class="status-message">${analysis.message}</div>
                <div class="waste-percentage">
                    ${analysis.energy_difference > 0 ? 
                        `Energy Overhead: ${analysis.waste_percentage}% (${analysis.energy_difference} kWh above appliances)` : 
                        `Excellent Efficiency: Prediction ${Math.abs(analysis.energy_difference)} kWh below appliance usage`
                    }
                </div>
            </div>
        </div>
        
        <div class="savings-summary">
            <div class="savings-card">
                <div class="savings-icon">SAVE</div>
                <div class="savings-content">
                    <h4>Potential Daily Savings</h4>
                    <div class="savings-value">${analysis.potential_savings.daily_kwh} kWh</div>
                    <div class="savings-cost">₹${analysis.potential_savings.daily_cost}</div>
                </div>
            </div>
            <div class="savings-card">
                <div class="savings-icon">MONTH</div>
                <div class="savings-content">
                    <h4>Monthly Savings</h4>
                    <div class="savings-value">${analysis.potential_savings.monthly_kwh} kWh</div>
                    <div class="savings-cost">₹${analysis.potential_savings.monthly_cost}</div>
                </div>
            </div>
            <div class="savings-card">
                <div class="savings-icon">YEAR</div>
                <div class="savings-content">
                    <h4>Yearly Savings</h4>
                    <div class="savings-value">${analysis.potential_savings.yearly_kwh} kWh</div>
                    <div class="savings-cost">₹${analysis.potential_savings.yearly_cost}</div>
                </div>
            </div>
        </div>
        
        <div class="recommendations-section">
            <h4>Personalized Recommendations</h4>
            <div class="recommendations-grid">
                ${analysis.recommendations.map(rec => `
                    <div class="recommendation-card priority-${rec.priority}">
                        <div class="rec-header">
                            <span class="rec-icon">${rec.icon}</span>
                            <span class="rec-title">${rec.title}</span>
                            <span class="rec-saving">${rec.potential_saving}</span>
                        </div>
                        <div class="rec-description">${rec.description}</div>
                        <div class="rec-category">${rec.category}</div>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

function createEnergyChart(applianceEnergy, predictedEnergy) {
    const ctx = document.getElementById('energyChart').getContext('2d');
    
    if (energyChart) {
        energyChart.destroy();
    }
    
    energyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Appliance Energy', 'Predicted Total'],
            datasets: [{
                label: 'Energy Consumption (kWh)',
                data: [applianceEnergy, predictedEnergy],
                backgroundColor: [
                    'rgba(59, 130, 246, 0.8)',
                    'rgba(16, 185, 129, 0.8)'
                ],
                borderColor: [
                    'rgba(59, 130, 246, 1)',
                    'rgba(16, 185, 129, 1)'
                ],
                borderWidth: 2,
                borderRadius: 8,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: 'white',
                    bodyColor: 'white',
                    borderColor: 'rgba(255, 255, 255, 0.2)',
                    borderWidth: 1,
                    cornerRadius: 8,
                    callbacks: {
                        label: function(context) {
                            return `${context.parsed.y.toFixed(2)} kWh`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.8)',
                        callback: function(value) {
                            return value.toFixed(1) + ' kWh';
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: 'rgba(255, 255, 255, 0.8)'
                    }
                }
            }
        }
    });
}

function restartPrediction() {
    document.querySelectorAll('input[type="number"]').forEach(input => {
        input.value = input.defaultValue || 0;
    });
    
    document.querySelectorAll('input[type="checkbox"]').forEach(input => {
        input.checked = false;
    });
    
    applianceEnergy = 0;
    seasonData = null;
    
    document.getElementById('appliance_energy').textContent = '0.00';
    
    goToStep(1);
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        border-radius: 8px;
        color: white;
        font-weight: 500;
        z-index: 1000;
        opacity: 0;
        transform: translateX(100%);
        transition: all 0.3s ease;
    `;
    
    switch(type) {
        case 'success':
            notification.style.backgroundColor = '#10b981';
            break;
        case 'error':
            notification.style.backgroundColor = '#ef4444';
            break;
        case 'warning':
            notification.style.backgroundColor = '#f59e0b';
            break;
        default:
            notification.style.backgroundColor = '#3b82f6';
    }
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.opacity = '1';
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}