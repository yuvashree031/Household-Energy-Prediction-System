# Household Energy Consumption Prediction System

An intelligent web-based application for predicting household energy consumption using machine learning and deep learning models with a structured multi-step workflow. The system allows users to input appliance usage details and weather conditions to get accurate energy consumption predictions using multiple ML models.

---

## Features

- Multi-step guided workflow for easy data input
- Support for multiple machine learning and deep learning models
- Real-time appliance energy calculation based on power ratings
- Automatic season detection from temperature input
- Interactive visualizations and appliance-wise energy breakdown
- REST API for integration with other systems
- Comparison of predicted vs calculated energy consumption

---

## Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Steps

1. Clone the repository

```bash
git clone <repository-url>
cd Household-energy-prediction
```

2. Install dependencies

```bash
pip install -r app/requirements.txt
```

3. Run the application

```bash
python app/app.py
```

4. Open in browser

```
http://localhost:5000
```

---

## Workflow

### Step 1 - Appliance Selection

Select household appliances from a predefined list and enter the usage duration for each. The system automatically calculates energy consumption using built-in power ratings and provides a real-time energy estimate before proceeding.

### Step 2 - Weather Inputs

Enter the current environmental parameters including temperature, humidity, wind speed, and solar radiation. The system automatically classifies the season based on the temperature value provided.

### Step 3 - Model Selection

Choose from available prediction models. Each model has different characteristics in terms of accuracy, speed, and interpretability. The system automatically detects which models are available based on saved model files.

### Step 4 - Prediction Results

View the predicted energy consumption along with an appliance-wise breakdown. Results are displayed with interactive visualizations and compared against the calculated appliance energy total.

---

## Appliance Power Ratings

| Appliance | Power (W) | Usage Type |
|-----------|-----------|------------|
| Air Conditioner | 1500 | Variable |
| Refrigerator | 150 | Always On |
| Washing Machine | 500 | Variable |
| Television | 120 | Variable |
| Fan | 75 | Variable |
| Lights | 60 | Variable |

---

## Season Classification

| Season | Temperature Condition |
|--------|----------------------|
| Hot | Greater than 30°C |
| Moderate | Between 20°C and 30°C |
| Cold | Less than 20°C |

---

## Machine Learning Models

### Linear Regression

A simple and interpretable baseline model that establishes a linear relationship between input features and energy consumption. Best suited for understanding feature importance and quick predictions.

### Random Forest

An ensemble learning method that builds multiple decision trees and merges their results. It handles non-linear relationships effectively and provides stable, accurate predictions with resistance to overfitting.

### Gradient Boosting

A sequential ensemble technique that builds trees one at a time, where each new tree corrects errors made by the previous ones. It delivers high prediction accuracy and performs well on structured data.

### LSTM (Long Short-Term Memory)

A deep learning model designed for sequential and time-series data. It captures temporal dependencies in energy consumption patterns and is suitable for advanced forecasting scenarios.

---

## Project Structure

```
Household-energy-prediction/
|
├── app/
│   ├── app.py
│   ├── requirements.txt
│   ├── templates/
│   │   ├── index.html
│   │   └── index_realtime.html
│   └── static/
│       ├── style.css
│       ├── script.js
│       ├── style_realtime.css
│       └── script_realtime.js
|
├── models/
│   ├── random_forest_energy_model.pkl
│   └── lstm_energy_model.h5
|
├── data/
│   ├── energy_data.csv
│   └── weather_data.csv
|
├── notebooks/
│   └── model_training.ipynb
|
├── install.bat
├── run.bat
└── README.md
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/calculate-appliance-energy` | Calculate energy based on appliance usage |
| POST | `/api/detect-season` | Detect season from temperature input |
| POST | `/api/predict` | Predict total energy consumption |
| GET | `/health` | Application health check |

---

## Dependencies

```
pandas==2.0.3
numpy==1.24.3
scikit-learn==1.3.0
tensorflow==2.13.0
keras==2.13.1
protobuf==3.20.3
joblib==1.3.2
flask==2.3.3
werkzeug==2.3.7
h5py==3.9.0
```

---

## Customization

### Modify Appliance Power Ratings

Edit the `APPLIANCE_POWER` dictionary in `app/app.py` to update wattage values or add new appliances:

```python
APPLIANCE_POWER = {
    'ac': 1500,
    'fan': 75,
    'lights': 60,
    'refrigerator': 150,
    'television': 120,
    'washing_machine': 500
}
```

### Modify Season Logic

Update the temperature thresholds in `app/app.py` to adjust season boundaries:

```python
if temp > 30:
    season = 'Hot'
elif temp >= 20:
    season = 'Moderate'
else:
    season = 'Cold'
```

---

## Usage

1. Launch the application and open it in your browser
2. Select the appliances used in your household and enter their daily usage hours
3. Enter the current weather conditions for your location
4. Select the machine learning model you want to use for prediction
5. View the predicted energy consumption, breakdown chart, and comparison with calculated values

---

## Development

To run the application in development mode with debug enabled:

```bash
cd app
python app.py
```

The application will reload automatically on code changes when running in development mode.