#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
#==============================================================================
#                    AnthroHPK v4.0 - KEJAR TUMBUH MODULE
#           Kalkulator Target Kejar Tumbuh (Growth Velocity)
#==============================================================================
"""

import os
import math
from typing import Dict, List, Optional, Tuple
from datetime import date, datetime
import traceback

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import UI_THEMES, OUTPUTS_DIR

# ==============================================================================
# REFERENCE DATA - GROWTH VELOCITY STANDARDS
# ==============================================================================

# WHO Growth Velocity Standards (median, approximate values)
# Format: {age_range: {"weight": (min_normal, max_normal), "height": (min_normal, max_normal)}}
GROWTH_VELOCITY_REFERENCE = {
    "0_3": {
        "weight_male": (0.8, 1.3),      # kg/bulan
        "weight_female": (0.7, 1.2),
        "height_male": (3.0, 4.0),      # cm/bulan
        "height_female": (2.8, 3.8)
    },
    "3_6": {
        "weight_male": (0.5, 0.9),
        "weight_female": (0.4, 0.8),
        "height_male": (2.0, 2.8),
        "height_female": (1.8, 2.6)
    },
    "6_9": {
        "weight_male": (0.3, 0.6),
        "weight_female": (0.3, 0.5),
        "height_male": (1.3, 1.8),
        "height_female": (1.2, 1.7)
    },
    "9_12": {
        "weight_male": (0.2, 0.5),
        "weight_female": (0.2, 0.4),
        "height_male": (1.0, 1.5),
        "height_female": (0.9, 1.4)
    },
    "12_24": {
        "weight_male": (0.15, 0.35),
        "weight_female": (0.15, 0.30),
        "height_male": (0.8, 1.2),
        "height_female": (0.7, 1.1)
    },
    "24_60": {
        "weight_male": (0.1, 0.25),
        "weight_female": (0.1, 0.20),
        "height_male": (0.5, 0.8),
        "height_female": (0.5, 0.7)
    }
}


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def get_velocity_reference(age_months: float, sex: str) -> Dict:
    """
    Get velocity reference values for specific age and sex
    
    Args:
        age_months: Age in months
        sex: 'M' or 'Laki-laki' or 'F' or 'Perempuan'
        
    Returns:
        Dictionary with weight and height velocity ranges
    """
    # Normalize sex
    sex_key = "male" if str(sex).upper().startswith(("M", "L")) else "female"
    
    # Determine age range
    if age_months < 3:
        range_key = "0_3"
    elif age_months < 6:
        range_key = "3_6"
    elif age_months < 9:
        range_key = "6_9"
    elif age_months < 12:
        range_key = "9_12"
    elif age_months < 24:
        range_key = "12_24"
    else:
        range_key = "24_60"
    
    ref = GROWTH_VELOCITY_REFERENCE.get(range_key, GROWTH_VELOCITY_REFERENCE["24_60"])
    
    return {
        "weight_range": ref.get(f"weight_{sex_key}", (0.1, 0.5)),
        "height_range": ref.get(f"height_{sex_key}", (0.5, 1.0)),
        "age_range": range_key
    }


def evaluate_velocity(velocity: float, reference_range: Tuple[float, float], measure_type: str) -> Dict:
    """
    Evaluate velocity against reference range
    
    Args:
        velocity: Calculated velocity (per month)
        reference_range: (min_normal, max_normal)
        measure_type: "weight" or "height"
        
    Returns:
        Evaluation result dictionary
    """
    min_normal, max_normal = reference_range
    
    if velocity < 0:
        return {
            "status": "Penurunan",
            "color": "#d32f2f",
            "emoji": "🚨",
            "message": f"Terjadi PENURUNAN {measure_type}! Segera konsultasi ke dokter.",
            "severity": "critical"
        }
    elif velocity < min_normal * 0.5:
        return {
            "status": "Sangat Lambat",
            "color": "#e65100",
            "emoji": "⚠️",
            "message": f"Pertumbuhan {measure_type} sangat lambat. Perlu evaluasi segera.",
            "severity": "warning"
        }
    elif velocity < min_normal:
        return {
            "status": "Lambat",
            "color": "#f57c00",
            "emoji": "📊",
            "message": f"Pertumbuhan {measure_type} di bawah rata-rata. Perlu perhatian.",
            "severity": "attention"
        }
    elif velocity <= max_normal:
        return {
            "status": "Normal",
            "color": "#388e3c",
            "emoji": "✅",
            "message": f"Pertumbuhan {measure_type} dalam rentang normal.",
            "severity": "normal"
        }
    else:
        return {
            "status": "Cepat",
            "color": "#1976d2",
            "emoji": "📈",
            "message": f"Pertumbuhan {measure_type} di atas rata-rata.",
            "severity": "good"
        }


def calculate_velocity(data1: Dict, data2: Dict) -> Dict:
    """
    Calculate growth velocity between two measurements
    
    Args:
        data1: First measurement {"usia_bulan": float, "bb": float, "tb": float}
        data2: Second measurement {"usia_bulan": float, "bb": float, "tb": float}
        
    Returns:
        Velocity calculation results
    """
    delta_months = data2['usia_bulan'] - data1['usia_bulan']
    
    if delta_months <= 0:
        return None
    
    delta_bb = data2['bb'] - data1['bb']
    delta_tb = data2['tb'] - data1['tb']
    
    velocity_bb = delta_bb / delta_months
    velocity_tb = delta_tb / delta_months
    
    return {
        'periode': f"{data1['usia_bulan']:.1f} → {data2['usia_bulan']:.1f} bulan",
        'delta_months': round(delta_months, 1),
        'delta_bb': round(delta_bb, 2),
        'delta_tb': round(delta_tb, 1),
        'velocity_bb': round(velocity_bb, 3),
        'velocity_tb': round(velocity_tb, 2),
        'mid_age': (data1['usia_bulan'] + data2['usia_bulan']) / 2
    }


# ==============================================================================
# MAIN ANALYSIS FUNCTION
# ==============================================================================

def analyze_growth_velocity(data_list: List[Dict], gender: str) -> Dict:
    """
    Perform comprehensive growth velocity analysis
    
    Args:
        data_list: List of measurements [{"usia_bulan": float, "bb": float, "tb": float}, ...]
        gender: "Laki-laki" or "Perempuan"
        
    Returns:
        Complete analysis results
    """
    if len(data_list) < 2:
        return {
            "success": False,
            "error": "Minimal 2 pengukuran diperlukan untuk analisis"
        }
    
    # Sort by age
    sorted_data = sorted(data_list, key=lambda x: x['usia_bulan'])
    
    # Calculate velocities for each interval
    velocities = []
    for i in range(len(sorted_data) - 1):
        vel = calculate_velocity(sorted_data[i], sorted_data[i + 1])
        if vel:
            velocities.append(vel)
    
    if not velocities:
        return {
            "success": False,
            "error": "Tidak dapat menghitung velocity (periksa urutan usia)"
        }
    
    # Evaluate each velocity
    evaluations = []
    for vel in velocities:
        ref = get_velocity_reference(vel['mid_age'], gender)
        
        bb_eval = evaluate_velocity(vel['velocity_bb'], ref['weight_range'], "berat badan")
        tb_eval = evaluate_velocity(vel['velocity_tb'], ref['height_range'], "tinggi badan")
        
        evaluations.append({
            **vel,
            'reference': ref,
            'bb_evaluation': bb_eval,
            'tb_evaluation': tb_eval
        })
    
    # Calculate overall averages
    avg_velocity_bb = sum(v['velocity_bb'] for v in velocities) / len(velocities)
    avg_velocity_tb = sum(v['velocity_tb'] for v in velocities) / len(velocities)
    
    total_delta_bb = sorted_data[-1]['bb'] - sorted_data[0]['bb']
    total_delta_tb = sorted_data[-1]['tb'] - sorted_data[0]['tb']
    total_months = sorted_data[-1]['usia_bulan'] - sorted_data[0]['usia_bulan']
    
    # Overall assessment
    critical_count = sum(1 for e in evaluations if e['bb_evaluation']['severity'] == 'critical' or e['tb_evaluation']['severity'] == 'critical')
    warning_count = sum(1 for e in evaluations if e['bb_evaluation']['severity'] == 'warning' or e['tb_evaluation']['severity'] == 'warning')
    
    if critical_count > 0:
        overall_status = "critical"
        overall_message = "⚠️ PERHATIAN: Terdeteksi penurunan atau pertumbuhan sangat lambat. Segera konsultasi ke dokter!"
    elif warning_count > 0:
        overall_status = "warning"
        overall_message = "📊 Perlu perhatian: Beberapa periode menunjukkan pertumbuhan di bawah rata-rata."
    else:
        overall_status = "normal"
        overall_message = "✅ Pertumbuhan keseluruhan dalam rentang normal. Pertahankan pola makan dan stimulasi."
    
    return {
        "success": True,
        "data": sorted_data,
        "velocities": velocities,
        "evaluations": evaluations,
        "summary": {
            "total_measurements": len(sorted_data),
            "total_periods": len(velocities),
            "total_months": round(total_months, 1),
            "total_delta_bb": round(total_delta_bb, 2),
            "total_delta_tb": round(total_delta_tb, 1),
            "avg_velocity_bb": round(avg_velocity_bb, 3),
            "avg_velocity_tb": round(avg_velocity_tb, 2),
            "overall_status": overall_status,
            "overall_message": overall_message
        },
        "gender": gender
    }


# ==============================================================================
# PLOTTING FUNCTIONS
# ==============================================================================

def plot_kejar_tumbuh_trajectory(data_list: List[Dict], gender: str, 
                                  theme_name: str = "pink_pastel") -> str:
    """
    Plot growth trajectory with velocity indicators
    
    Args:
        data_list: List of measurements
        gender: "Laki-laki" or "Perempuan"
        theme_name: UI theme name
        
    Returns:
        Path to saved plot file
    """
    if len(data_list) < 2:
        return None
    
    theme = UI_THEMES.get(theme_name, UI_THEMES["pink_pastel"])
    
    # Sort data
    sorted_data = sorted(data_list, key=lambda x: x['usia_bulan'])
    
    ages = [d['usia_bulan'] for d in sorted_data]
    weights = [d['bb'] for d in sorted_data]
    heights = [d['tb'] for d in sorted_data]
    
    # Create figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    fig.patch.set_facecolor(theme['bg'])
    
    # Style settings
    line_color = theme['primary']
    point_color = theme['secondary']
    
    # Plot Weight trajectory
    ax1.set_facecolor(theme['card'])
    ax1.plot(ages, weights, 'o-', color=line_color, linewidth=2.5, 
             markersize=10, markerfacecolor=point_color, 
             markeredgecolor='white', markeredgewidth=2)
    
    # Add annotations
    for i, (age, weight) in enumerate(zip(ages, weights)):
        ax1.annotate(f'{weight:.1f} kg',
                    (age, weight),
                    textcoords="offset points",
                    xytext=(0, 10),
                    ha='center',
                    fontsize=9,
                    fontweight='bold',
                    color=theme['text'])
    
    ax1.set_xlabel('Usia (bulan)', fontsize=11, fontweight='bold', color=theme['text'])
    ax1.set_ylabel('Berat Badan (kg)', fontsize=11, fontweight='bold', color=theme['text'])
    ax1.set_title(f'📈 Trajectory Berat Badan\n{"Laki-laki" if gender.upper().startswith(("L", "M")) else "Perempuan"}',
                  fontsize=12, fontweight='bold', color=theme['text'], pad=10)
    ax1.grid(True, alpha=0.3, linestyle='--', color=theme['border'])
    ax1.tick_params(colors=theme['text'])
    
    # Plot Height trajectory
    ax2.set_facecolor(theme['card'])
    ax2.plot(ages, heights, 's-', color='#4CAF50', linewidth=2.5,
             markersize=10, markerfacecolor='#81C784',
             markeredgecolor='white', markeredgewidth=2)
    
    for i, (age, height) in enumerate(zip(ages, heights)):
        ax2.annotate(f'{height:.1f} cm',
                    (age, height),
                    textcoords="offset points",
                    xytext=(0, 10),
                    ha='center',
                    fontsize=9,
                    fontweight='bold',
                    color=theme['text'])
    
    ax2.set_xlabel('Usia (bulan)', fontsize=11, fontweight='bold', color=theme['text'])
    ax2.set_ylabel('Tinggi Badan (cm)', fontsize=11, fontweight='bold', color=theme['text'])
    ax2.set_title(f'📏 Trajectory Tinggi Badan\n{"Laki-laki" if gender.upper().startswith(("L", "M")) else "Perempuan"}',
                  fontsize=12, fontweight='bold', color=theme['text'], pad=10)
    ax2.grid(True, alpha=0.3, linestyle='--', color=theme['border'])
    ax2.tick_params(colors=theme['text'])
    
    plt.tight_layout()
    
    # Save plot
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"kejar_tumbuh_{timestamp}.png"
    filepath = os.path.join(OUTPUTS_DIR, filename)
    
    fig.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=theme['bg'])
    plt.close(fig)
    
    return filepath


# ==============================================================================
# HTML GENERATION
# ==============================================================================

def generate_kejar_tumbuh_html(analysis: Dict) -> str:
    """
    Generate comprehensive HTML report from analysis
    
    Args:
        analysis: Result from analyze_growth_velocity()
        
    Returns:
        HTML string
    """
    if not analysis.get('success'):
        return f"""
        <div style='padding: 20px; background: #ffebee; border-radius: 10px; text-align: center;'>
            <h3 style='color: #c62828;'>⚠️ Tidak Dapat Menganalisis</h3>
            <p style='color: #b71c1c;'>{analysis.get('error', 'Error tidak diketahui')}</p>
        </div>
        """
    
    summary = analysis['summary']
    evaluations = analysis['evaluations']
    
    # Status colors
    status_colors = {
        'critical': '#d32f2f',
        'warning': '#f57c00',
        'normal': '#388e3c'
    }
    
    status_color = status_colors.get(summary['overall_status'], '#666')
    
    html = f"""
    <!-- Overall Summary -->
    <div style='background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
                padding: 20px; border-radius: 15px; margin-bottom: 20px;'>
        <h2 style='color: #1565c0; margin: 0 0 15px 0;'>📈 Hasil Analisis Growth Velocity</h2>
        <div style='background: white; padding: 15px; border-radius: 10px; 
                    border-left: 4px solid {status_color};'>
            <p style='margin: 0; font-size: 1.1em; color: {status_color}; font-weight: bold;'>
                {summary['overall_message']}
            </p>
        </div>
    </div>
    
    <!-- Summary Stats -->
    <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); 
                gap: 15px; margin-bottom: 20px;'>
        <div style='background: #e8f5e9; padding: 15px; border-radius: 10px; text-align: center;'>
            <div style='font-size: 1.5em; font-weight: bold; color: #2e7d32;'>{summary['total_measurements']}</div>
            <div style='color: #666; font-size: 0.9em;'>Pengukuran</div>
        </div>
        <div style='background: #e3f2fd; padding: 15px; border-radius: 10px; text-align: center;'>
            <div style='font-size: 1.5em; font-weight: bold; color: #1565c0;'>{summary['total_months']}</div>
            <div style='color: #666; font-size: 0.9em;'>Bulan Dipantau</div>
        </div>
        <div style='background: #fff3e0; padding: 15px; border-radius: 10px; text-align: center;'>
            <div style='font-size: 1.5em; font-weight: bold; color: #e65100;'>+{summary['total_delta_bb']} kg</div>
            <div style='color: #666; font-size: 0.9em;'>Kenaikan BB</div>
        </div>
        <div style='background: #fce4ec; padding: 15px; border-radius: 10px; text-align: center;'>
            <div style='font-size: 1.5em; font-weight: bold; color: #c2185b;'>+{summary['total_delta_tb']} cm</div>
            <div style='color: #666; font-size: 0.9em;'>Kenaikan TB</div>
        </div>
    </div>
    
    <!-- Detailed Results Table -->
    <div style='background: white; padding: 20px; border-radius: 15px; 
                box-shadow: 0 2px 10px rgba(0,0,0,0.1); overflow-x: auto;'>
        <h3 style='color: #333; margin: 0 0 15px 0;'>📊 Detail per Periode</h3>
        <table style='width: 100%; border-collapse: collapse; min-width: 600px;'>
            <thead>
                <tr style='background: #f5f5f5;'>
                    <th style='padding: 12px; text-align: left; border-bottom: 2px solid #ddd;'>Periode</th>
                    <th style='padding: 12px; text-align: center; border-bottom: 2px solid #ddd;'>Durasi</th>
                    <th style='padding: 12px; text-align: center; border-bottom: 2px solid #ddd;'>Δ BB</th>
                    <th style='padding: 12px; text-align: center; border-bottom: 2px solid #ddd;'>Velocity BB</th>
                    <th style='padding: 12px; text-align: center; border-bottom: 2px solid #ddd;'>Status BB</th>
                    <th style='padding: 12px; text-align: center; border-bottom: 2px solid #ddd;'>Δ TB</th>
                    <th style='padding: 12px; text-align: center; border-bottom: 2px solid #ddd;'>Velocity TB</th>
                    <th style='padding: 12px; text-align: center; border-bottom: 2px solid #ddd;'>Status TB</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for i, eval_data in enumerate(evaluations):
        row_bg = '#fafafa' if i % 2 == 0 else '#ffffff'
        bb_eval = eval_data['bb_evaluation']
        tb_eval = eval_data['tb_evaluation']
        
        html += f"""
            <tr style='background: {row_bg};'>
                <td style='padding: 10px; border-bottom: 1px solid #eee;'>{eval_data['periode']}</td>
                <td style='padding: 10px; border-bottom: 1px solid #eee; text-align: center;'>{eval_data['delta_months']} bln</td>
                <td style='padding: 10px; border-bottom: 1px solid #eee; text-align: center;'>{eval_data['delta_bb']:+.2f} kg</td>
                <td style='padding: 10px; border-bottom: 1px solid #eee; text-align: center; font-weight: bold;'>
                    {eval_data['velocity_bb']:.3f} kg/bln
                </td>
                <td style='padding: 10px; border-bottom: 1px solid #eee; text-align: center;'>
                    <span style='background: {bb_eval["color"]}22; color: {bb_eval["color"]}; 
                                 padding: 4px 8px; border-radius: 4px; font-weight: bold;'>
                        {bb_eval["emoji"]} {bb_eval["status"]}
                    </span>
                </td>
                <td style='padding: 10px; border-bottom: 1px solid #eee; text-align: center;'>{eval_data['delta_tb']:+.1f} cm</td>
                <td style='padding: 10px; border-bottom: 1px solid #eee; text-align: center; font-weight: bold;'>
                    {eval_data['velocity_tb']:.2f} cm/bln
                </td>
                <td style='padding: 10px; border-bottom: 1px solid #eee; text-align: center;'>
                    <span style='background: {tb_eval["color"]}22; color: {tb_eval["color"]}; 
                                 padding: 4px 8px; border-radius: 4px; font-weight: bold;'>
                        {tb_eval["emoji"]} {tb_eval["status"]}
                    </span>
                </td>
            </tr>
        """
    
    html += """
            </tbody>
        </table>
    </div>
    
    <!-- Recommendations -->
    <div style='background: #fff8e1; padding: 20px; border-radius: 15px; margin-top: 20px;'>
        <h3 style='color: #f57f17; margin: 0 0 15px 0;'>💡 Rekomendasi</h3>
        <ul style='margin: 0; padding-left: 25px;'>
            <li style='margin: 8px 0;'>Lakukan pengukuran rutin setiap bulan</li>
            <li style='margin: 8px 0;'>Pastikan asupan protein hewani di setiap makan</li>
            <li style='margin: 8px 0;'>Tambahkan lemak sehat (EVOO, santan) untuk kalori ekstra</li>
            <li style='margin: 8px 0;'>Konsultasi ke dokter jika ada penurunan atau stagnasi pertumbuhan</li>
        </ul>
    </div>
    """
    
    return html


# ==============================================================================
# HANDLER FUNCTION (untuk Gradio)
# ==============================================================================

def kalkulator_kejar_tumbuh_handler(data_list: List[Dict], gender: str) -> Tuple[str, Optional[str]]:
    """
    Handler for Kejar Tumbuh calculator
    
    Args:
        data_list: List of measurements
        gender: Gender string
        
    Returns:
        Tuple of (html_report, plot_path)
    """
    try:
        if not data_list or len(data_list) < 2:
            return (
                "<p style='color: #e74c3c; padding: 20px;'>"
                "⚠️ Minimal 2 data pengukuran diperlukan untuk analisis.</p>",
                None
            )
        
        # Run analysis
        analysis = analyze_growth_velocity(data_list, gender)
        
        # Generate HTML report
        html_report = generate_kejar_tumbuh_html(analysis)
        
        # Generate plot
        plot_path = None
        if analysis.get('success'):
            plot_path = plot_kejar_tumbuh_trajectory(data_list, gender)
        
        return html_report, plot_path
        
    except Exception as e:
        print(f"❌ Error in kejar_tumbuh_handler: {e}")
        traceback.print_exc()
        return f"<p style='color: #e74c3c; padding: 20px;'>Error: {str(e)}</p>", None


print("✅ Kejar Tumbuh module loaded")
