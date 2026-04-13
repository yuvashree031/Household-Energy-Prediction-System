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

## Screenshots

<p align="center">
  <img src="project_screenshots/Dashboard.png" width="700"/>
</p>

<p align="center"><b>Dashboard View</b></p>

<p align="center">
  <img src="project_screenshots/Graph.png" width="700"/>
</p>

<p align="center"><b>Graph Visualization</b></p>

<p align="center">
  <img src="project_screenshots/Step1.png" width="700"/>
</p>

<p align="center"><b>Step 1 - Appliance Selection</b></p>

<p align="center">
  <img src="project_screenshots/Step2.png" width="700"/>
</p>

<p align="center"><b>Step 2 - Weather Inputs</b></p>

<p align="center">
  <img src="project_screenshots/Step3.png" width="700"/>
</p>

<p align="center"><b>Step 3 - Model Selection</b></p>

<p align="center">
  <img src="project_screenshots/Step4.png" width="700"/>
</p>

<p align="center"><b>Step 4 - Prediction Results</b></p>

<p align="center">
  <img src="project_screenshots/energy_prediction_results.png" width="700"/>
</p>

<p align="center"><b>Energy Prediction Results</b></p>

<p align="center">
  <img src="project_screenshots/energy_timeseries_comparison.png" width="700"/>
</p>

<p align="center"><b>Energy Time Series Comparison</b></p>

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
A simple and interpretable baseline model that establishes a linear relationship between input features and energy consumption.

### Random Forest
An ensemble learning method that builds multiple decision trees and merges their results for better accuracy.

### Gradient Boosting
A sequential ensemble technique that improves prediction performance by correcting previous errors.

### LSTM (Long Short-Term Memory)
A deep learning model designed for time-series forecasting and sequential data.

---

## Project Structure

```
Household-energy-prediction/
|
├── app/
├── models/
├── data/
├── notebooks/
├── project_screenshots/
├── README.md
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/calculate-appliance-energy` | Calculate energy |
| POST | `/api/detect-season` | Detect season |
| POST | `/api/predict` | Predict energy |
| GET | `/health` | Health check |

---

## Dependencies

```
pandas
numpy
scikit-learn
tensorflow
keras
flask
```

---

## Usage

1. Run the application  
2. Enter appliance usage  
3. Provide weather inputs  
4. Select model  
5. View predictions  

---

## Development

```bash
cd app
python app.py
```

---
