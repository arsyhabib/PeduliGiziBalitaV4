#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
#==============================================================================
#                    AnthroHPK v4.0 - GROWTH CHARTS MODULE
#               Matplotlib Visualization for WHO Growth Standards
#==============================================================================
"""

import os
import math
import numpy as np
from typing import Dict, Tuple, List, Optional, Union
from functools import lru_cache
from datetime import datetime

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

plt.ioff()  # Disable interactive mode
plt.rcParams.update({
    'figure.max_open_warning': 0,
    'figure.dpi': 100,
    'savefig.dpi': 150,
    'savefig.bbox': 'tight',
})

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import UI_THEMES, BOUNDS, OUTPUTS_DIR

# Age grid for smooth curve generation (0-60 months, step 0.25)
AGE_GRID = np.arange(0.0, 60.25, 0.25)


# ==============================================================================
# ROOT FINDING FOR CURVE GENERATION
# ==============================================================================

def brentq_rootfind(f, a: float, b: float, xtol: float = 1e-6, maxiter: int = 100) -> float:
    """
    Brent's method for root finding (scipy-free implementation)
    """
    fa = f(a)
    fb = f(b)
    
    if fa is None or fb is None:
        return (a + b) / 2.0
    
    if abs(fa) < 1e-10:
        return a
    if abs(fb) < 1e-10:
        return b
    
    if fa * fb > 0:
        return (a + b) / 2.0
    
    for iteration in range(maxiter):
        m = 0.5 * (a + b)
        fm = f(m)
        
        if fm is None:
            return m
        
        if abs(fm) < 1e-10 or (b - a) / 2 < xtol:
            return m
        
        if fa * fm < 0:
            b, fb = m, fm
        else:
            a, fa = m, fm
    
    return 0.5 * (a + b)


def invert_zscore_function(z_func, target_z: float, lo: float, hi: float, samples: int = 150) -> float:
    """
    Invert z-score function to find measurement value that produces target z-score
    """
    xs = np.linspace(lo, hi, samples)
    last_x, last_f = None, None
    best_x, best_abs = None, float('inf')
    
    for x in xs:
        z = z_func(x)
        f = None if z is None else (z - target_z)
        
        if f is not None:
            af = abs(f)
            if af < best_abs:
                best_x, best_abs = x, af
            
            if last_f is not None and f * last_f < 0:
                try:
                    root = brentq_rootfind(
                        lambda t: (z_func(t) or 0.0) - target_z,
                        last_x,
                        x,
                        xtol=1e-5
                    )
                    return float(root)
                except Exception:
                    pass
            
            last_x, last_f = x, f
    
    return float(best_x if best_x is not None else (lo + hi) / 2.0)


# ==============================================================================
# CURVE GENERATION
# ==============================================================================

@lru_cache(maxsize=128)
def generate_wfa_curve(sex: str, z_score: float) -> Tuple[np.ndarray, np.ndarray]:
    """Generate Weight-for-Age WHO curve for given z-score"""
    from .who_calculator import get_calculator, _safe_z_calc
    
    calc = get_calculator()
    if calc is None:
        return AGE_GRID.copy(), np.zeros_like(AGE_GRID)
    
    lo, hi = BOUNDS['wfa']
    
    def z_func(weight, age):
        return _safe_z_calc(calc.wfa, weight, age, sex)
    
    weights = []
    for age in AGE_GRID:
        weight = invert_zscore_function(
            lambda w: z_func(w, age),
            z_score,
            lo,
            hi
        )
        weights.append(weight)
    
    return AGE_GRID.copy(), np.array(weights)


@lru_cache(maxsize=128)
def generate_hfa_curve(sex: str, z_score: float) -> Tuple[np.ndarray, np.ndarray]:
    """Generate Height-for-Age WHO curve for given z-score"""
    from .who_calculator import get_calculator, _safe_z_calc
    
    calc = get_calculator()
    if calc is None:
        return AGE_GRID.copy(), np.zeros_like(AGE_GRID)
    
    lo, hi = BOUNDS['hfa']
    
    def z_func(height, age):
        return _safe_z_calc(calc.lhfa, height, age, sex)
    
    heights = []
    for age in AGE_GRID:
        height = invert_zscore_function(
            lambda h: z_func(h, age),
            z_score,
            lo,
            hi
        )
        heights.append(height)
    
    return AGE_GRID.copy(), np.array(heights)


@lru_cache(maxsize=128)
def generate_hcfa_curve(sex: str, z_score: float) -> Tuple[np.ndarray, np.ndarray]:
    """Generate Head Circumference-for-Age WHO curve for given z-score"""
    from .who_calculator import get_calculator, _safe_z_calc
    
    calc = get_calculator()
    if calc is None:
        return AGE_GRID.copy(), np.zeros_like(AGE_GRID)
    
    lo, hi = BOUNDS['hcfa']
    
    def z_func(hc, age):
        return _safe_z_calc(calc.hcfa, hc, age, sex)
    
    head_circs = []
    for age in AGE_GRID:
        hc = invert_zscore_function(
            lambda h: z_func(h, age),
            z_score,
            lo,
            hi
        )
        head_circs.append(hc)
    
    return AGE_GRID.copy(), np.array(head_circs)


@lru_cache(maxsize=128)
def generate_wfl_curve(sex: str, age_months: float, z_score: float) -> Tuple[np.ndarray, np.ndarray]:
    """Generate Weight-for-Length WHO curve for given z-score"""
    from .who_calculator import get_calculator, _safe_z_calc
    
    calc = get_calculator()
    if calc is None:
        lengths = np.arange(BOUNDS['wfl_l'][0], BOUNDS['wfl_l'][1] + 0.5, 0.5)
        return lengths, np.zeros_like(lengths)
    
    lengths = np.arange(BOUNDS['wfl_l'][0], BOUNDS['wfl_l'][1] + 0.5, 0.5)
    lo_w, hi_w = BOUNDS['wfl_w']
    
    def z_func(weight, length):
        return _safe_z_calc(calc.wfl, weight, age_months, sex, length)
    
    weights = []
    for length in lengths:
        weight = invert_zscore_function(
            lambda w: z_func(w, length),
            z_score,
            lo_w,
            hi_w
        )
        weights.append(weight)
    
    return lengths, np.array(weights)


# ==============================================================================
# THEME APPLICATION
# ==============================================================================

def apply_matplotlib_theme(theme_name: str = "pink_pastel") -> Dict[str, str]:
    """Apply custom theme to matplotlib"""
    theme = UI_THEMES.get(theme_name, UI_THEMES["pink_pastel"])
    
    plt.style.use('default')
    plt.rcParams.update({
        "axes.facecolor": theme["card"],
        "figure.facecolor": theme["bg"],
        "savefig.facecolor": theme["bg"],
        "text.color": theme["text"],
        "axes.labelcolor": theme["text"],
        "axes.edgecolor": theme["border"],
        "xtick.color": theme["text"],
        "ytick.color": theme["text"],
        "grid.color": theme["border"],
        "grid.alpha": 0.35,
        "grid.linestyle": "--",
        "grid.linewidth": 0.8,
        "legend.framealpha": 1.0,
        "legend.fancybox": True,
        "legend.edgecolor": theme["border"],
        "legend.shadow": True,
        "font.size": 10,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.labelsize": 11,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 9,
        "axes.linewidth": 1.5,
    })
    
    return theme


def _fill_zone_between_curves(ax, x: np.ndarray, lower: np.ndarray, upper: np.ndarray, 
                              color: str, alpha: float, label: str):
    """Helper to fill colored zones between SD curves"""
    try:
        ax.fill_between(
            x, lower, upper,
            color=color,
            alpha=alpha,
            zorder=1,
            label=label,
            linewidth=0,
            edgecolor='none'
        )
    except Exception as e:
        print(f"Fill zone warning: {e}")


# ==============================================================================
# PLOTTING FUNCTIONS
# ==============================================================================

def plot_weight_for_age(payload: Dict, theme_name: str = "pink_pastel") -> Figure:
    """Plot Weight-for-Age growth chart with child's data point"""
    from .utilities import format_zscore
    
    theme = apply_matplotlib_theme(theme_name)
    
    sex = payload['sex']
    age = payload['age_mo']
    weight = payload.get('w')
    
    sd_lines = {
        -3: ('#DC143C', '-', 2.0),
        -2: ('#FF6347', '-', 2.5),
        -1: (theme['primary'], '--', 1.5),
        0: (theme['secondary'], '-', 2.5),
        1: (theme['primary'], '--', 1.5),
        2: ('#FF6347', '-', 2.5),
        3: ('#DC143C', '-', 2.0)
    }
    
    curves = {z: generate_wfa_curve(sex, z) for z in sd_lines.keys()}
    
    fig, ax = plt.subplots(figsize=(12, 7.5))
    
    x = curves[0][0]
    
    _fill_zone_between_curves(ax, x, curves[-3][1], curves[-2][1], '#FFE6E6', 0.4, 'Gizi Buruk')
    _fill_zone_between_curves(ax, x, curves[-2][1], curves[-1][1], '#FFEBCC', 0.35, 'Gizi Kurang')
    _fill_zone_between_curves(ax, x, curves[-1][1], curves[1][1],  '#E8F5E9', 0.45, 'Normal')
    _fill_zone_between_curves(ax, x, curves[1][1],  curves[2][1],  '#FFF3CD', 0.35, 'Risiko Lebih')
    _fill_zone_between_curves(ax, x, curves[2][1],  curves[3][1],  '#F8D7DA', 0.4, 'Gizi Lebih')
    
    for z, (color, linestyle, linewidth) in sd_lines.items():
        label = "Median (WHO)" if z == 0 else f"{z:+d} SD"
        ax.plot(
            curves[z][0], curves[z][1],
            color=color,
            linestyle=linestyle,
            linewidth=linewidth,
            label=label,
            zorder=5,
            alpha=0.9
        )
    
    if weight is not None:
        z_waz = payload['z'].get('waz')
        
        if z_waz is not None:
            if abs(z_waz) > 3:
                point_color = '#8B0000'
                point_size = 500
            elif abs(z_waz) > 2:
                point_color = '#DC143C'
                point_size = 450
            elif abs(z_waz) > 1:
                point_color = theme['primary']
                point_size = 400
            else:
                point_color = theme['secondary']
                point_size = 400
        else:
            point_color = theme['secondary']
            point_size = 400
        
        ax.scatter(
            [age], [weight],
            s=point_size,
            c=point_color,
            edgecolors='white',
            linewidths=3,
            label=f"Data Anak ({weight:.1f} kg)",
            zorder=10,
            marker='o',
            alpha=1.0
        )
        
        ax.annotate(
            f"{weight:.1f} kg\nZ: {format_zscore(z_waz)}",
            (age, weight),
            xytext=(10, 10),
            textcoords='offset points',
            fontsize=10,
            fontweight='bold',
            bbox=dict(
                boxstyle='round,pad=0.6',
                facecolor=point_color,
                edgecolor='white',
                linewidth=2,
                alpha=0.9
            ),
            color='white',
            zorder=11
        )
    
    ax.set_xlabel("Usia (bulan)", fontsize=12, fontweight='bold')
    ax.set_ylabel("Berat Badan (kg)", fontsize=12, fontweight='bold')
    ax.set_title(
        f"Grafik Berat Badan menurut Umur (BB/U) - WHO Standards\n"
        f"{'Laki-laki' if sex == 'M' else 'Perempuan'} | Usia: {age:.1f} bulan",
        fontsize=14,
        fontweight='bold',
        pad=15
    )
    
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)
    ax.legend(loc='upper left', framealpha=0.95, fancybox=True, shadow=True, fontsize=9)
    ax.set_xlim(-1, 62)
    ax.set_ylim(0, None)
    
    plt.tight_layout()
    
    return fig


def plot_height_for_age(payload: Dict, theme_name: str = "pink_pastel") -> Figure:
    """Plot Height-for-Age growth chart with child's data point"""
    from .utilities import format_zscore
    
    theme = apply_matplotlib_theme(theme_name)
    
    sex = payload['sex']
    age = payload['age_mo']
    height = payload.get('h')
    
    sd_lines = {
        -3: ('#DC143C', '-', 2.0),
        -2: ('#FF6347', '-', 2.5),
        -1: (theme['primary'], '--', 1.5),
        0: (theme['secondary'], '-', 2.5),
        1: (theme['primary'], '--', 1.5),
        2: ('#FF6347', '-', 2.5),
        3: ('#DC143C', '-', 2.0)
    }
    
    curves = {z: generate_hfa_curve(sex, z) for z in sd_lines.keys()}
    
    fig, ax = plt.subplots(figsize=(12, 7.5))
    
    x = curves[0][0]
    
    _fill_zone_between_curves(ax, x, curves[-3][1], curves[-2][1], '#FFE6E6', 0.4, 'Sangat Pendek')
    _fill_zone_between_curves(ax, x, curves[-2][1], curves[-1][1], '#FFEBCC', 0.35, 'Pendek')
    _fill_zone_between_curves(ax, x, curves[-1][1], curves[1][1],  '#E8F5E9', 0.45, 'Normal')
    _fill_zone_between_curves(ax, x, curves[1][1],  curves[2][1],  '#E3F2FD', 0.35, 'Tinggi')
    _fill_zone_between_curves(ax, x, curves[2][1],  curves[3][1],  '#E8EAF6', 0.4, 'Sangat Tinggi')
    
    for z, (color, linestyle, linewidth) in sd_lines.items():
        label = "Median (WHO)" if z == 0 else f"{z:+d} SD"
        ax.plot(
            curves[z][0], curves[z][1],
            color=color,
            linestyle=linestyle,
            linewidth=linewidth,
            label=label,
            zorder=5,
            alpha=0.9
        )
    
    if height is not None:
        z_haz = payload['z'].get('haz')
        
        if z_haz is not None:
            if abs(z_haz) > 3:
                point_color = '#8B0000'
                point_size = 500
            elif abs(z_haz) > 2:
                point_color = '#DC143C'
                point_size = 450
            elif abs(z_haz) > 1:
                point_color = theme['primary']
                point_size = 400
            else:
                point_color = theme['secondary']
                point_size = 400
        else:
            point_color = theme['secondary']
            point_size = 400
        
        ax.scatter(
            [age], [height],
            s=point_size,
            c=point_color,
            edgecolors='white',
            linewidths=3,
            label=f"Data Anak ({height:.1f} cm)",
            zorder=10,
            marker='o',
            alpha=1.0
        )
        
        ax.annotate(
            f"{height:.1f} cm\nZ: {format_zscore(z_haz)}",
            (age, height),
            xytext=(10, 10),
            textcoords='offset points',
            fontsize=10,
            fontweight='bold',
            bbox=dict(
                boxstyle='round,pad=0.6',
                facecolor=point_color,
                edgecolor='white',
                linewidth=2,
                alpha=0.9
            ),
            color='white',
            zorder=11
        )
    
    measurement_type = "Panjang Badan" if age < 24 else "Tinggi Badan"
    ax.set_xlabel("Usia (bulan)", fontsize=12, fontweight='bold')
    ax.set_ylabel(f"{measurement_type} (cm)", fontsize=12, fontweight='bold')
    ax.set_title(
        f"Grafik {measurement_type} menurut Umur (TB/U) - WHO Standards\n"
        f"{'Laki-laki' if sex == 'M' else 'Perempuan'} | Usia: {age:.1f} bulan",
        fontsize=14,
        fontweight='bold',
        pad=15
    )
    
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)
    ax.legend(loc='upper left', framealpha=0.95, fancybox=True, shadow=True, fontsize=9)
    ax.set_xlim(-1, 62)
    ax.set_ylim(40, None)
    
    plt.tight_layout()
    
    return fig


def plot_head_circumference_for_age(payload: Dict, theme_name: str = "pink_pastel") -> Figure:
    """Plot Head Circumference-for-Age growth chart"""
    from .utilities import format_zscore
    
    theme = apply_matplotlib_theme(theme_name)
    
    sex = payload['sex']
    age = payload['age_mo']
    head_circ = payload.get('hc')
    
    if head_circ is None:
        fig, ax = plt.subplots(figsize=(12, 7.5))
        ax.text(
            0.5, 0.5,
            "Data lingkar kepala tidak tersedia",
            ha='center', va='center',
            transform=ax.transAxes,
            fontsize=14,
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        )
        ax.set_title("Grafik Lingkar Kepala menurut Umur (LK/U)")
        return fig
    
    sd_lines = {
        -3: ('#DC143C', '-', 2.0),
        -2: ('#FF6347', '-', 2.5),
        -1: (theme['primary'], '--', 1.5),
        0: (theme['secondary'], '-', 2.5),
        1: (theme['primary'], '--', 1.5),
        2: ('#FF6347', '-', 2.5),
        3: ('#DC143C', '-', 2.0)
    }
    
    curves = {z: generate_hcfa_curve(sex, z) for z in sd_lines.keys()}
    
    fig, ax = plt.subplots(figsize=(12, 7.5))
    
    x = curves[0][0]
    
    _fill_zone_between_curves(ax, x, curves[-3][1], curves[-2][1], '#FFE6E6', 0.4, 'Mikrosefali')
    _fill_zone_between_curves(ax, x, curves[-2][1], curves[2][1],  '#E8F5E9', 0.45, 'Normal')
    _fill_zone_between_curves(ax, x, curves[2][1],  curves[3][1],  '#FFE6E6', 0.4, 'Makrosefali')
    
    for z, (color, linestyle, linewidth) in sd_lines.items():
        label = "Median (WHO)" if z == 0 else f"{z:+d} SD"
        ax.plot(
            curves[z][0], curves[z][1],
            color=color,
            linestyle=linestyle,
            linewidth=linewidth,
            label=label,
            zorder=5,
            alpha=0.9
        )
    
    z_hcz = payload['z'].get('hcz')
    
    if z_hcz is not None:
        if abs(z_hcz) > 2:
            point_color = '#DC143C'
            point_size = 500
        elif abs(z_hcz) > 1:
            point_color = theme['primary']
            point_size = 450
        else:
            point_color = theme['secondary']
            point_size = 400
    else:
        point_color = theme['secondary']
        point_size = 400
    
    ax.scatter(
        [age], [head_circ],
        s=point_size,
        c=point_color,
        edgecolors='white',
        linewidths=3,
        label=f"Data Anak ({head_circ:.1f} cm)",
        zorder=10,
        marker='o',
        alpha=1.0
    )
    
    ax.annotate(
        f"{head_circ:.1f} cm\nZ: {format_zscore(z_hcz)}",
        (age, head_circ),
        xytext=(10, 10),
        textcoords='offset points',
        fontsize=10,
        fontweight='bold',
        bbox=dict(
            boxstyle='round,pad=0.6',
            facecolor=point_color,
            edgecolor='white',
            linewidth=2,
            alpha=0.9
        ),
        color='white',
        zorder=11
    )
    
    ax.set_xlabel("Usia (bulan)", fontsize=12, fontweight='bold')
    ax.set_ylabel("Lingkar Kepala (cm)", fontsize=12, fontweight='bold')
    ax.set_title(
        f"Grafik Lingkar Kepala menurut Umur (LK/U) - WHO Standards\n"
        f"{'Laki-laki' if sex == 'M' else 'Perempuan'} | Usia: {age:.1f} bulan",
        fontsize=14,
        fontweight='bold',
        pad=15
    )
    
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)
    ax.legend(loc='upper left', framealpha=0.95, fancybox=True, shadow=True, fontsize=9)
    ax.set_xlim(-1, 62)
    ax.set_ylim(28, None)
    
    plt.tight_layout()
    
    return fig


def plot_weight_for_length(payload: Dict, theme_name: str = "pink_pastel") -> Figure:
    """Plot Weight-for-Length growth chart"""
    from .utilities import format_zscore
    
    theme = apply_matplotlib_theme(theme_name)
    
    sex = payload['sex']
    age = payload['age_mo']
    weight = payload.get('w')
    height = payload.get('h')
    
    if weight is None or height is None:
        fig, ax = plt.subplots(figsize=(12, 7.5))
        ax.text(
            0.5, 0.5,
            "Data berat dan tinggi badan diperlukan untuk grafik BB/TB",
            ha='center', va='center',
            transform=ax.transAxes,
            fontsize=14,
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        )
        ax.set_title("Grafik Berat Badan menurut Tinggi Badan (BB/TB)")
        return fig
    
    sd_lines = {
        -3: ('#DC143C', '-', 2.0),
        -2: ('#FF6347', '-', 2.5),
        -1: (theme['primary'], '--', 1.5),
        0: (theme['secondary'], '-', 2.5),
        1: (theme['primary'], '--', 1.5),
        2: ('#FF6347', '-', 2.5),
        3: ('#DC143C', '-', 2.0)
    }
    
    curves = {z: generate_wfl_curve(sex, age, z) for z in sd_lines.keys()}
    
    fig, ax = plt.subplots(figsize=(12, 7.5))
    
    lengths = curves[0][0]
    
    _fill_zone_between_curves(ax, lengths, curves[-3][1], curves[-2][1], '#FFE6E6', 0.4, 'Gizi Buruk')
    _fill_zone_between_curves(ax, lengths, curves[-2][1], curves[-1][1], '#FFEBCC', 0.35, 'Gizi Kurang')
    _fill_zone_between_curves(ax, lengths, curves[-1][1], curves[1][1],  '#E8F5E9', 0.45, 'Normal')
    _fill_zone_between_curves(ax, lengths, curves[1][1],  curves[2][1],  '#FFF3CD', 0.35, 'Risiko Lebih')
    _fill_zone_between_curves(ax, lengths, curves[2][1],  curves[3][1],  '#F8D7DA', 0.4, 'Gizi Lebih')
    
    for z, (color, linestyle, linewidth) in sd_lines.items():
        label = "Median (WHO)" if z == 0 else f"{z:+d} SD"
        ax.plot(
            curves[z][0], curves[z][1],
            color=color,
            linestyle=linestyle,
            linewidth=linewidth,
            label=label,
            zorder=5,
            alpha=0.9
        )
    
    z_whz = payload['z'].get('whz')
    
    if z_whz is not None:
        if abs(z_whz) > 3:
            point_color = '#8B0000'
            point_size = 500
        elif abs(z_whz) > 2:
            point_color = '#DC143C'
            point_size = 450
        elif abs(z_whz) > 1:
            point_color = theme['primary']
            point_size = 400
        else:
            point_color = theme['secondary']
            point_size = 400
    else:
        point_color = theme['secondary']
        point_size = 400
    
    ax.scatter(
        [height], [weight],
        s=point_size,
        c=point_color,
        edgecolors='white',
        linewidths=3,
        label=f"Data Anak ({weight:.1f} kg)",
        zorder=10,
        marker='o',
        alpha=1.0
    )
    
    ax.annotate(
        f"{weight:.1f} kg / {height:.1f} cm\nZ: {format_zscore(z_whz)}",
        (height, weight),
        xytext=(10, 10),
        textcoords='offset points',
        fontsize=10,
        fontweight='bold',
        bbox=dict(
            boxstyle='round,pad=0.6',
            facecolor=point_color,
            edgecolor='white',
            linewidth=2,
            alpha=0.9
        ),
        color='white',
        zorder=11
    )
    
    measurement_type = "Panjang Badan" if age < 24 else "Tinggi Badan"
    ax.set_xlabel(f"{measurement_type} (cm)", fontsize=12, fontweight='bold')
    ax.set_ylabel("Berat Badan (kg)", fontsize=12, fontweight='bold')
    ax.set_title(
        f"Grafik Berat Badan menurut {measurement_type} (BB/TB) - WHO Standards\n"
        f"{'Laki-laki' if sex == 'M' else 'Perempuan'} | Usia: {age:.1f} bulan",
        fontsize=14,
        fontweight='bold',
        pad=15
    )
    
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.7)
    ax.legend(loc='upper left', framealpha=0.95, fancybox=True, shadow=True, fontsize=9)
    ax.set_xlim(BOUNDS['wfl_l'][0] - 2, BOUNDS['wfl_l'][1] + 2)
    ax.set_ylim(0, None)
    
    plt.tight_layout()
    
    return fig


def plot_zscore_summary_bars(payload: Dict, theme_name: str = "pink_pastel") -> Figure:
    """Plot bar chart summarizing all z-scores"""
    from .utilities import format_zscore
    
    theme = apply_matplotlib_theme(theme_name)
    
    z_scores = payload.get('z', {})
    
    indices = []
    values = []
    colors = []
    labels_text = []
    
    for key, label in [('waz', 'BB/U'), ('haz', 'TB/U'), ('whz', 'BB/TB'), 
                       ('baz', 'IMT/U'), ('hcz', 'LK/U')]:
        z = z_scores.get(key)
        if z is not None and not math.isnan(z):
            indices.append(label)
            values.append(z)
            labels_text.append(format_zscore(z))
            
            if abs(z) > 3:
                colors.append('#8B0000')
            elif abs(z) > 2:
                colors.append('#DC143C')
            elif abs(z) > 1:
                colors.append('#FFA500')
            else:
                colors.append('#28a745')
    
    if not indices:
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.text(
            0.5, 0.5,
            "Tidak ada data z-score tersedia",
            ha='center', va='center',
            transform=ax.transAxes,
            fontsize=14
        )
        return fig
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    bars = ax.bar(indices, values, color=colors, edgecolor='white', linewidth=2, alpha=0.85)
    
    for bar, val, txt in zip(bars, values, labels_text):
        height = bar.get_height()
        y_offset = 0.3 if height > 0 else -0.5
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + y_offset,
            txt,
            ha='center',
            va='bottom' if height > 0 else 'top',
            fontsize=12,
            fontweight='bold',
            color='black'
        )
    
    ax.axhline(y=-3, color='#DC143C', linestyle='--', linewidth=1.5, alpha=0.6, label='-3 SD')
    ax.axhline(y=-2, color='#FF6347', linestyle='--', linewidth=1.5, alpha=0.6, label='-2 SD')
    ax.axhline(y=0, color=theme['secondary'], linestyle='-', linewidth=2, alpha=0.7, label='Median')
    ax.axhline(y=2, color='#FF6347', linestyle='--', linewidth=1.5, alpha=0.6, label='+2 SD')
    ax.axhline(y=3, color='#DC143C', linestyle='--', linewidth=1.5, alpha=0.6, label='+3 SD')
    
    ax.axhspan(-3, -2, facecolor='#FFE6E6', alpha=0.3, zorder=0)
    ax.axhspan(-2, 2, facecolor='#E8F5E9', alpha=0.3, zorder=0)
    ax.axhspan(2, 3, facecolor='#FFF3CD', alpha=0.3, zorder=0)
    
    ax.set_xlabel("Indeks Antropometri", fontsize=12, fontweight='bold')
    ax.set_ylabel("Z-Score", fontsize=12, fontweight='bold')
    ax.set_title(
        "Ringkasan Z-Score Semua Indeks WHO\n"
        f"Anak: {payload.get('name_child', 'N/A')} | "
        f"{'Laki-laki' if payload['sex'] == 'M' else 'Perempuan'} | "
        f"Usia: {payload['age_mo']:.1f} bulan",
        fontsize=14,
        fontweight='bold',
        pad=15
    )
    
    ax.grid(True, alpha=0.3, axis='y', linestyle='--', linewidth=0.7)
    ax.legend(loc='upper right', framealpha=0.95, fancybox=True, shadow=True, fontsize=9)
    ax.set_ylim(-4, 4)
    
    plt.tight_layout()
    
    return fig


# ==============================================================================
# CLEANUP UTILITY
# ==============================================================================

def cleanup_matplotlib_figures(figures: Union[Figure, List[Figure]]):
    """Properly cleanup matplotlib figures to prevent memory leaks"""
    if figures is None:
        return
    
    if isinstance(figures, Figure):
        figures = [figures]
    
    for fig in figures:
        if fig is not None:
            plt.close(fig)


def save_figure_to_file(fig: Figure, filename: str = None) -> str:
    """Save figure to file and return path"""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chart_{timestamp}.png"
    
    filepath = os.path.join(OUTPUTS_DIR, filename)
    fig.savefig(filepath, format='png', bbox_inches='tight', dpi=150)
    
    return filepath


print("✅ Growth Charts module loaded")
