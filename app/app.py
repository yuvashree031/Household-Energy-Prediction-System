from flask import Flask, render_template, request, jsonify # type: ignore
import numpy as np
import pandas as pd
import joblib
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
import os
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)

MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')

rf_model = None
rf_available = False
try:
    import numpy
    import joblib
    from sklearn.ensemble import RandomForestRegressor
    
    rf_model = joblib.load(os.path.join(MODEL_DIR, 'random_forest_energy_model_new.pkl'))
    rf_available = True
        
except Exception as e:
    rf_available = False

lstm_model = None
lstm_available = False

try:
    import os
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    
    import tensorflow as tf # type: ignore
    
    lstm_model = tf.keras.models.load_model(os.path.join(MODEL_DIR, 'lstm_energy_model.h5'))
    lstm_available = True
except Exception as e:
    lstm_available = False

linear_model = None
gb_model = None
new_models_available = False

try:
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    
    from energy_prediction_models import EnergyPredictionModels
    
    energy_predictor = EnergyPredictionModels("data/loureiro_energy.csv")
    
    energy_predictor.load_data()
    energy_predictor.preprocess_data()
    X, y, feature_columns = energy_predictor.prepare_features_and_target()
    energy_predictor.split_data(X, y)
    energy_predictor.train_models()
    
    linear_model = energy_predictor.models.get('Linear Regression')
    gb_model = energy_predictor.models.get('Gradient Boosting')
    rf_new_model = energy_predictor.models.get('Random Forest')
    
    if linear_model and gb_model and rf_new_model:
        new_models_available = True
    
except Exception as e:
    new_models_available = False

scaler_X = MinMaxScaler()
scaler_y = MinMaxScaler()
X_dummy = np.array([
    [15, 40, 0, 0, 0, 15, 0, 0, 0, 0],
    [35, 100, 360, 15, 20, 35, 50, 10, 1000, 50]
])
y_dummy = np.array([[0], [50]])
scaler_X.fit(X_dummy)
scaler_y.fit(y_dummy)

def fallback_prediction(features):
    avg_temp, avg_rel_humidity, _, avg_wind_speed, _, inst_temp, _, _, total_global_rad, lag_1 = features
    
    base_energy = lag_1
    
    temp_factor = 1.0
    if avg_temp > 30:
        temp_factor = 1.3
    elif avg_temp > 25:
        temp_factor = 1.15
    elif avg_temp < 15:
        temp_factor = 1.2
    
    humidity_factor = 1.0 + (max(0, avg_rel_humidity - 60) / 1000)
    
    solar_factor = 1.0 + (total_global_rad / 10000)
    
    prediction = base_energy * temp_factor * humidity_factor * solar_factor
    
    return max(0, prediction)

APPLIANCE_POWER = {
    'ac': 1500,
    'fan': 75,
    'lights': 60,
    'refrigerator': 150,
    'television': 120,
    'washing_machine': 500
}

@app.route('/')
def index():
    return render_template('index.html', lstm_available=lstm_available, rf_available=rf_available)

@app.route('/api/calculate-appliance-energy', methods=['POST'])
def calculate_appliance_energy():
    try:
        data = request.json
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data received'
            }), 400
            
        appliances = data.get('appliances', {})
        
        total_energy = 0
        appliance_breakdown = {}
        
        for appliance, hours in appliances.items():
            if appliance in APPLIANCE_POWER:
                power = APPLIANCE_POWER[appliance]
                if appliance == 'refrigerator':
                    hours = 24
                energy_kwh = (power * hours) / 1000
                total_energy += energy_kwh
                appliance_breakdown[appliance] = {
                    'power_watts': power,
                    'hours': hours,
                    'energy_kwh': round(energy_kwh, 4)
                }
        
        result = {
            'success': True,
            'total_energy_kwh': round(total_energy, 4),
            'breakdown': appliance_breakdown
        }
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/detect-season', methods=['POST'])
def detect_season():
    try:
        data = request.json
        temp = float(data.get('temperature', 25))
        
        if temp > 30:
            season = 'Hot'
            icon = 'HOT'
            color = '#ef4444'
        elif temp >= 20:
            season = 'Moderate'
            icon = 'MODERATE'
            color = '#f59e0b'
        else:
            season = 'Cold'
            icon = 'COLD'
            color = '#3b82f6'
        
        return jsonify({
            'success': True,
            'season': season,
            'icon': icon,
            'color': color,
            'temperature': temp
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

def convert_features_for_new_models(old_features, data):
    from datetime import datetime
    import calendar
    
    current_time = datetime.now()
    hour = current_time.hour
    day = current_time.day
    month = current_time.month
    day_of_week = current_time.weekday()
    quarter = (month - 1) // 3 + 1
    week_of_year = current_time.isocalendar()[1]
    
    appliance_energy = float(data.get('lag_1', 0))
    
    features = [
        hour, day, month, day_of_week, quarter, week_of_year,
        appliance_energy,
        0.5, 0.3, 0.8, 0.2, 0.6, 0.4, 0.7, 0.1, 0.9, 0.3,
        0.5, 0.2, 0.8, 0.4, 0.6, 0.3, 0.7, 0.1, 0.9
    ]
    
    return features

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        
        avg_temp = float(data.get('avg_temp'))
        avg_rel_humidity = float(data.get('avg_rel_humidity'))
        avg_wind_speed = float(data.get('avg_wind_speed'))
        inst_temp = float(data.get('inst_temp'))
        total_global_rad = float(data.get('total_global_rad'))
        lag_1 = float(data.get('lag_1'))
        model_type = data.get('model_type', 'random_forest')
        
        features = [
            avg_temp,
            avg_rel_humidity,
            0,
            avg_wind_speed,
            avg_wind_speed * 1.5,
            inst_temp,
            0,
            0,
            total_global_rad,
            lag_1
        ]
        
        X_input = np.array([features])
        
        if model_type == 'lstm' and lstm_available:
            X_scaled = scaler_X.transform(X_input)
            X_reshaped = X_scaled.reshape((1, 1, 10))
            prediction_scaled = lstm_model.predict(X_reshaped, verbose=0)
            prediction = scaler_y.inverse_transform(prediction_scaled)[0][0]
            model_name = 'LSTM Neural Network'
        elif model_type == 'random_forest' and rf_available:
            prediction = rf_model.predict(X_input)[0]
            model_name = 'Random Forest (Original)'
        elif model_type == 'random_forest_new' and new_models_available:
            features_new = convert_features_for_new_models(features, data)
            prediction = rf_new_model.predict([features_new])[0]
            model_name = 'Random Forest (New)'
        elif model_type == 'linear_regression' and new_models_available:
            features_new = convert_features_for_new_models(features, data)
            prediction = linear_model.predict([features_new])[0]
            model_name = 'Linear Regression'
        elif model_type == 'gradient_boosting' and new_models_available:
            features_new = convert_features_for_new_models(features, data)
            prediction = gb_model.predict([features_new])[0]
            model_name = 'Gradient Boosting'
        else:
            prediction = fallback_prediction(features)
            model_name = 'Fallback Model (Weather-based)'
        
        prediction = max(0, float(prediction))
        
        if prediction < lag_1 * 0.9:
            prediction = lag_1 * 1.05
            model_name += " (Adjusted)"
        
        analysis = calculate_energy_analysis(lag_1, prediction, avg_temp, avg_rel_humidity)
        
        return jsonify({
            'success': True,
            'prediction': round(prediction, 4),
            'model': model_name,
            'analysis': analysis
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

def calculate_energy_analysis(appliance_energy, predicted_energy, temperature, humidity):
    difference = predicted_energy - appliance_energy
    
    waste_percentage = (difference / appliance_energy) * 100 if appliance_energy > 0 else 0
    
    if difference <= 0:
        status = "efficient"
        message = "Excellent! Your total consumption is very close to appliance usage."
        potential_savings = 0
    elif waste_percentage <= 10:
        status = "efficient"
        message = "Great! You're using energy very efficiently with minimal overhead."
        potential_savings = 0
    elif waste_percentage <= 25:
        status = "moderate"
        message = "Your energy usage is moderate. Some optimization opportunities exist."
        potential_savings = difference * 0.3
    else:
        status = "wasteful"
        message = "High energy consumption detected. Significant savings possible."
        potential_savings = difference * 0.5
    
    recommendations = generate_recommendations(
        appliance_energy, predicted_energy, temperature, humidity, waste_percentage
    )
    
    monthly_savings = potential_savings * 30
    yearly_savings = potential_savings * 365
    
    cost_per_kwh = 9.60
    daily_cost_savings = potential_savings * cost_per_kwh
    monthly_cost_savings = monthly_savings * cost_per_kwh
    yearly_cost_savings = yearly_savings * cost_per_kwh
    
    baseline_efficient = appliance_energy + (appliance_energy * 0.15)
    
    return {
        'status': status,
        'message': message,
        'appliance_energy': round(appliance_energy, 2),
        'predicted_energy': round(predicted_energy, 2),
        'baseline_efficient': round(baseline_efficient, 2),
        'energy_difference': round(difference, 2),
        'waste_percentage': round(waste_percentage, 1),
        'potential_savings': {
            'daily_kwh': round(potential_savings, 2),
            'monthly_kwh': round(monthly_savings, 2),
            'yearly_kwh': round(yearly_savings, 2),
            'daily_cost': round(daily_cost_savings, 2),
            'monthly_cost': round(monthly_cost_savings, 2),
            'yearly_cost': round(yearly_cost_savings, 2)
        },
        'recommendations': recommendations
    }

def generate_recommendations(appliance_energy, predicted_energy, temperature, humidity, waste_percentage):
    recommendations = []
    
    overhead = predicted_energy - appliance_energy
    overhead_percentage = (overhead / appliance_energy) * 100 if appliance_energy > 0 else 0
    
    if temperature > 28 and overhead_percentage > 15:
        recommendations.append({
            'category': 'Cooling',
            'icon': '',
            'title': 'Optimize Air Conditioning',
            'description': 'Set AC to 24-26°C instead of lower temperatures to reduce energy overhead',
            'potential_saving': '15-20%',
            'priority': 'high'
        })
        recommendations.append({
            'category': 'Cooling',
            'icon': '',
            'title': 'Use Fans Efficiently',
            'description': 'Use ceiling fans to feel 2-3°C cooler, allowing higher AC settings',
            'potential_saving': '10-15%',
            'priority': 'medium'
        })
    elif temperature < 18 and overhead_percentage > 15:
        recommendations.append({
            'category': 'Heating',
            'icon': '',
            'title': 'Optimize Heating',
            'description': 'Set heating to 20-22°C and use layers for comfort',
            'potential_saving': '10-15%',
            'priority': 'high'
        })
    
    if humidity > 70 and overhead_percentage > 10:
        recommendations.append({
            'category': 'Humidity',
            'icon': '',
            'title': 'Reduce Humidity Load',
            'description': 'Use exhaust fans in kitchen/bathroom to reduce AC workload',
            'potential_saving': '5-10%',
            'priority': 'medium'
        })
    
    if overhead_percentage > 30:
        recommendations.append({
            'category': 'Appliances',
            'icon': '',
            'title': 'Switch to LED Lighting',
            'description': 'Replace incandescent bulbs with LED for 75% less energy',
            'potential_saving': '75%',
            'priority': 'high'
        })
        recommendations.append({
            'category': 'Appliances',
            'icon': '',
            'title': 'Unplug Standby Devices',
            'description': 'Unplug electronics when not in use to eliminate phantom loads',
            'potential_saving': '5-10%',
            'priority': 'high'
        })
    
    if overhead_percentage > 20:
        recommendations.append({
            'category': 'Efficiency',
            'icon': '',
            'title': 'Use Timer Controls',
            'description': 'Set timers for AC, water heater, and other appliances',
            'potential_saving': '10-20%',
            'priority': 'medium'
        })
    
    if overhead_percentage > 5:
        recommendations.extend([
            {
                'category': 'Maintenance',
                'icon': '',
                'title': 'Regular AC Maintenance',
                'description': 'Clean AC filters monthly for optimal efficiency',
                'potential_saving': '5-15%',
                'priority': 'medium'
            },
            {
                'category': 'Insulation',
                'icon': '',
                'title': 'Improve Insulation',
                'description': 'Seal gaps around doors/windows to reduce energy loss',
                'potential_saving': '10-25%',
                'priority': 'low'
            }
        ])
    else:
        recommendations.extend([
            {
                'category': 'Maintenance',
                'icon': '',
                'title': 'Maintain Efficiency',
                'description': 'Continue regular maintenance to keep optimal performance',
                'potential_saving': '5%',
                'priority': 'low'
            },
            {
                'category': 'Monitoring',
                'icon': '',
                'title': 'Monitor Usage',
                'description': 'Keep tracking energy usage to maintain efficiency',
                'potential_saving': '2-5%',
                'priority': 'low'
            }
        ])
    
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    recommendations.sort(key=lambda x: priority_order[x['priority']])
    
    return recommendations[:6]

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy', 
        'random_forest_loaded': rf_available,
        'lstm_loaded': lstm_available,
        'fallback_available': True
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
