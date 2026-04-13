import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from energy_prediction_models import EnergyPredictionModels

def create_visualizations():
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")
    
    energy_models = EnergyPredictionModels("data/loureiro_energy.csv")
    energy_models.run_complete_pipeline()
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Household Energy Consumption Prediction - Model Analysis', fontsize=16, fontweight='bold')
    
    metrics_df = pd.DataFrame(energy_models.metrics).T
    
    ax1 = axes[0, 0]
    metrics_df[['MAE', 'RMSE']].plot(kind='bar', ax=ax1)
    ax1.set_title('Error Metrics Comparison (Lower is Better)')
    ax1.set_ylabel('Error Value')
    ax1.tick_params(axis='x', rotation=45)
    ax1.legend(title='Metrics')
    
    ax2 = axes[0, 1]
    r2_scores = metrics_df['R²']
    colors = ['gold' if score == r2_scores.max() else 'lightblue' for score in r2_scores]
    r2_scores.plot(kind='bar', ax=ax2, color=colors)
    ax2.set_title('R² Score Comparison (Higher is Better)')
    ax2.set_ylabel('R² Score')
    ax2.tick_params(axis='x', rotation=45)
    ax2.axhline(y=r2_scores.max(), color='red', linestyle='--', alpha=0.7)
    
    ax3 = axes[1, 0]
    colors_list = ['blue', 'green', 'orange']
    for i, (name, predictions) in enumerate(energy_models.predictions.items()):
        ax3.scatter(energy_models.y_test, predictions, alpha=0.5, label=name, s=10, color=colors_list[i])
    
    all_values = [energy_models.y_test.min()] + [pred.min() for pred in energy_models.predictions.values()]
    min_val = min(all_values)
    all_values_max = [energy_models.y_test.max()] + [pred.max() for pred in energy_models.predictions.values()]
    max_val = max(all_values_max)
    ax3.plot([min_val, max_val], [min_val, max_val], 'r--', alpha=0.8, label='Perfect Prediction')
    
    ax3.set_xlabel('Actual Energy Consumption')
    ax3.set_ylabel('Predicted Energy Consumption')
    ax3.set_title('Actual vs Predicted Values')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    ax4 = axes[1, 1]
    for i, (name, predictions) in enumerate(energy_models.predictions.items()):
        residuals = energy_models.y_test - predictions
        ax4.scatter(predictions, residuals, alpha=0.5, label=name, s=10, color=colors_list[i])
    
    ax4.axhline(y=0, color='red', linestyle='--', alpha=0.8)
    ax4.set_xlabel('Predicted Values')
    ax4.set_ylabel('Residuals (Actual - Predicted)')
    ax4.set_title('Residual Analysis')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('energy_prediction_results.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    plt.figure(figsize=(15, 8))
    
    sample_size = min(500, len(energy_models.y_test))
    sample_indices = np.random.choice(len(energy_models.y_test), sample_size, replace=False)
    sample_indices.sort()
    
    plt.plot(sample_indices, energy_models.y_test.iloc[sample_indices], 
             label='Actual', alpha=0.7, linewidth=2, color='black')
    
    for i, (name, predictions) in enumerate(energy_models.predictions.items()):
        plt.plot(sample_indices, predictions[sample_indices], 
                label=f'{name} (Predicted)', alpha=0.8, linewidth=1.5)
    
    plt.title('Energy Consumption: Actual vs Predicted (Sample)', fontsize=14, fontweight='bold')
    plt.xlabel('Sample Index')
    plt.ylabel('Energy Consumption')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('energy_timeseries_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    create_visualizations()
