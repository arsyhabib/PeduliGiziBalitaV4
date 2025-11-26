#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
#==============================================================================
#                    AnthroHPK v4.0 - WHO CALCULATOR MODULE
#                Z-Score Calculations & Classifications
#==============================================================================
"""

import math
import traceback
from typing import Dict, Optional
from functools import lru_cache

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CALC_CONFIG

# ==============================================================================
# WHO CALCULATOR INITIALIZATION
# ==============================================================================

calc = None

try:
    from pygrowup import Calculator
    calc = Calculator(**CALC_CONFIG)
    print("✅ WHO Calculator (pygrowup) initialized successfully")
except ImportError as e:
    print(f"⚠️ pygrowup import failed: {e}")
    calc = None
except Exception as e:
    print(f"⚠️ WHO Calculator init error: {e}")
    traceback.print_exc()
    calc = None

if calc is None:
    print("⚠️ WARNING: WHO Calculator unavailable - limited functionality")


def get_calculator():
    """Get the WHO calculator instance"""
    return calc


def is_calculator_available() -> bool:
    """Check if WHO calculator is available"""
    return calc is not None


# ==============================================================================
# SAFE Z-SCORE CALCULATION
# ==============================================================================

def _safe_z_calc(calc_func, *args) -> Optional[float]:
    """
    Safely call WHO calculator function with error handling
    
    Args:
        calc_func: Calculator method to call
        *args: Arguments to pass to the calculator
        
    Returns:
        Z-score float or None if calculation fails
    """
    if calc is None:
        return None
    
    try:
        z = calc_func(*args)
        
        if z is None:
            return None
        
        z_float = float(z)
        
        # Check for invalid values (NaN or Inf)
        if math.isnan(z_float) or math.isinf(z_float):
            return None
        
        return z_float
    except Exception:
        return None


# ==============================================================================
# Z-SCORE CALCULATIONS
# ==============================================================================

def calculate_all_zscores(sex: str, 
                          age_months: float, 
                          weight: Optional[float], 
                          height: Optional[float], 
                          head_circ: Optional[float]) -> Dict[str, Optional[float]]:
    """
    Calculate all WHO z-scores for a child
    
    Args:
        sex: 'M' (male) or 'F' (female)
        age_months: Age in months
        weight: Weight in kg
        height: Height/length in cm
        head_circ: Head circumference in cm
        
    Returns:
        Dictionary with keys:
            - waz: Weight-for-Age Z-score
            - haz: Height-for-Age Z-score (or LAZ if < 24 months)
            - whz: Weight-for-Height Z-score (or WFL if < 24 months)
            - baz: BMI-for-Age Z-score
            - hcz: Head Circumference-for-Age Z-score
    """
    results = {
        'waz': None,
        'haz': None,
        'whz': None,
        'baz': None,
        'hcz': None
    }
    
    if calc is None:
        return results
    
    # Weight-for-Age (WAZ)
    if weight is not None:
        results['waz'] = _safe_z_calc(calc.wfa, weight, age_months, sex)
    
    # Height-for-Age (HAZ) / Length-for-Age (LAZ)
    if height is not None:
        results['haz'] = _safe_z_calc(calc.lhfa, height, age_months, sex)
    
    # Weight-for-Height (WHZ) / Weight-for-Length (WFL)
    if weight is not None and height is not None:
        results['whz'] = _safe_z_calc(calc.wfl, weight, age_months, sex, height)
    
    # BMI-for-Age (BAZ)
    if weight is not None and height is not None and height > 0:
        bmi = weight / ((height / 100) ** 2)
        results['baz'] = _safe_z_calc(calc.bmifa, bmi, age_months, sex)
    
    # Head Circumference-for-Age (HCZ)
    if head_circ is not None:
        results['hcz'] = _safe_z_calc(calc.hcfa, head_circ, age_months, sex)
    
    return results


# ==============================================================================
# PERMENKES RI 2020 CLASSIFICATION
# ==============================================================================

def classify_permenkes_2020(z_scores: Dict[str, Optional[float]]) -> Dict[str, str]:
    """
    Classify nutritional status according to Permenkes RI No. 2 Tahun 2020
    
    Args:
        z_scores: Dictionary of z-scores from calculate_all_zscores()
        
    Returns:
        Dictionary with Permenkes classifications for each index
    """
    classifications = {}
    
    # Weight-for-Age (BB/U)
    waz = z_scores.get('waz')
    if waz is not None and not math.isnan(waz):
        if waz < -3:
            classifications['waz'] = "Berat Badan Sangat Kurang"
        elif waz < -2:
            classifications['waz'] = "Berat Badan Kurang"
        elif waz <= 2:
            classifications['waz'] = "Berat Badan Normal"
        else:
            classifications['waz'] = "Risiko Berat Badan Lebih"
    else:
        classifications['waz'] = "Data Tidak Tersedia"
    
    # Height-for-Age (TB/U)
    haz = z_scores.get('haz')
    if haz is not None and not math.isnan(haz):
        if haz < -3:
            classifications['haz'] = "Sangat Pendek (Severely Stunted)"
        elif haz < -2:
            classifications['haz'] = "Pendek (Stunted)"
        elif haz <= 3:
            classifications['haz'] = "Tinggi Badan Normal"
        else:
            classifications['haz'] = "Tinggi Badan Berlebih"
    else:
        classifications['haz'] = "Data Tidak Tersedia"
    
    # Weight-for-Height (BB/TB)
    whz = z_scores.get('whz')
    if whz is not None and not math.isnan(whz):
        if whz < -3:
            classifications['whz'] = "Gizi Buruk (Severely Wasted)"
        elif whz < -2:
            classifications['whz'] = "Gizi Kurang (Wasted)"
        elif whz <= 2:
            classifications['whz'] = "Gizi Baik (Normal)"
        elif whz <= 3:
            classifications['whz'] = "Berisiko Gizi Lebih (Possible Risk of Overweight)"
        else:
            classifications['whz'] = "Gizi Lebih (Overweight)"
    else:
        classifications['whz'] = "Data Tidak Tersedia"
    
    # BMI-for-Age (IMT/U)
    baz = z_scores.get('baz')
    if baz is not None and not math.isnan(baz):
        if baz < -3:
            classifications['baz'] = "Gizi Buruk (Severely Wasted)"
        elif baz < -2:
            classifications['baz'] = "Gizi Kurang (Wasted)"
        elif baz <= 1:
            classifications['baz'] = "Gizi Baik (Normal)"
        elif baz <= 2:
            classifications['baz'] = "Berisiko Gizi Lebih (Possible Risk of Overweight)"
        elif baz <= 3:
            classifications['baz'] = "Gizi Lebih (Overweight)"
        else:
            classifications['baz'] = "Obesitas (Obese)"
    else:
        classifications['baz'] = "Data Tidak Tersedia"
    
    # Head Circumference-for-Age (LK/U)
    hcz = z_scores.get('hcz')
    if hcz is not None and not math.isnan(hcz):
        if abs(hcz) <= 2:
            classifications['hcz'] = "Normal"
        elif hcz < -2:
            classifications['hcz'] = "Mikrosefali (perlu evaluasi)"
        else:
            classifications['hcz'] = "Makrosefali (perlu evaluasi)"
    else:
        classifications['hcz'] = "Data Tidak Tersedia"
    
    return classifications


# ==============================================================================
# WHO STANDARDS CLASSIFICATION
# ==============================================================================

def classify_who_standards(z_scores: Dict[str, Optional[float]]) -> Dict[str, str]:
    """
    Classify nutritional status according to WHO Child Growth Standards
    
    Args:
        z_scores: Dictionary of z-scores from calculate_all_zscores()
        
    Returns:
        Dictionary with WHO classifications for each index
    """
    classifications = {}
    
    # Weight-for-Age
    waz = z_scores.get('waz')
    if waz is not None and not math.isnan(waz):
        if waz < -3:
            classifications['waz'] = "Severely underweight"
        elif waz < -2:
            classifications['waz'] = "Underweight"
        elif waz <= 2:
            classifications['waz'] = "Normal weight"
        else:
            classifications['waz'] = "Overweight"
    else:
        classifications['waz'] = "N/A"
    
    # Height-for-Age
    haz = z_scores.get('haz')
    if haz is not None and not math.isnan(haz):
        if haz < -3:
            classifications['haz'] = "Severely stunted"
        elif haz < -2:
            classifications['haz'] = "Stunted"
        elif haz <= 3:
            classifications['haz'] = "Normal height"
        else:
            classifications['haz'] = "Tall"
    else:
        classifications['haz'] = "N/A"
    
    # Weight-for-Height
    whz = z_scores.get('whz')
    if whz is not None and not math.isnan(whz):
        if whz < -3:
            classifications['whz'] = "Severely wasted"
        elif whz < -2:
            classifications['whz'] = "Wasted"
        elif whz <= 2:
            classifications['whz'] = "Normal"
        elif whz <= 3:
            classifications['whz'] = "Risk of overweight"
        else:
            classifications['whz'] = "Overweight"
    else:
        classifications['whz'] = "N/A"
    
    # BMI-for-Age
    baz = z_scores.get('baz')
    if baz is not None and not math.isnan(baz):
        if baz < -3:
            classifications['baz'] = "Severely wasted"
        elif baz < -2:
            classifications['baz'] = "Wasted"
        elif baz <= 1:
            classifications['baz'] = "Normal"
        elif baz <= 2:
            classifications['baz'] = "Risk of overweight"
        elif baz <= 3:
            classifications['baz'] = "Overweight"
        else:
            classifications['baz'] = "Obese"
    else:
        classifications['baz'] = "N/A"
    
    # Head Circumference-for-Age
    hcz = z_scores.get('hcz')
    if hcz is not None and not math.isnan(hcz):
        if abs(hcz) <= 2:
            classifications['hcz'] = "Normal"
        elif hcz < -2:
            classifications['hcz'] = "Microcephaly"
        else:
            classifications['hcz'] = "Macrocephaly"
    else:
        classifications['hcz'] = "N/A"
    
    return classifications


# ==============================================================================
# Z-SCORE VALIDATION
# ==============================================================================

def validate_zscores(z_scores: Dict[str, Optional[float]]) -> tuple:
    """
    Validate z-scores for extreme values that need attention
    
    Args:
        z_scores: Dictionary of z-scores
        
    Returns:
        Tuple of (errors, warnings)
    """
    from .utilities import format_zscore
    
    errors = []
    warnings = []
    
    warn_threshold = 3
    critical_threshold = 5
    
    for key, z in z_scores.items():
        if z is None or math.isnan(z):
            continue
        
        name = {
            'waz': 'WAZ (BB/U)',
            'haz': 'HAZ (TB/U)',
            'whz': 'WHZ (BB/TB)',
            'baz': 'BAZ (IMT/U)',
            'hcz': 'HCZ (LK/U)'
        }.get(key, key)
        
        abs_z = abs(z)
        
        if abs_z > critical_threshold:
            errors.append(
                f"🚨 {name} = {format_zscore(z)} sangat ekstrem (|Z| > {critical_threshold}). "
                f"PENTING: Verifikasi ulang semua pengukuran dan konsultasi dokter anak."
            )
        elif abs_z > warn_threshold:
            warnings.append(
                f"⚠️ {name} = {format_zscore(z)} di luar rentang umum (|Z| > {warn_threshold}). "
                f"Verifikasi ulang pengukuran atau konsultasi tenaga kesehatan."
            )
    
    return errors, warnings


# ==============================================================================
# EASY MODE - NORMAL RANGES REFERENCE
# ==============================================================================

@lru_cache(maxsize=256)
def get_normal_ranges(sex: str, age_months: float) -> Dict[str, Dict[str, float]]:
    """
    Get normal ranges for anthropometric measurements at given age
    
    Args:
        sex: 'M' or 'F'
        age_months: Age in months
        
    Returns:
        Dictionary with normal ranges for weight, height, head circumference
    """
    if calc is None:
        return {}
    
    from .growth_charts import invert_zscore_function
    from config import BOUNDS
    
    ranges = {}
    
    # Weight-for-Age ranges
    try:
        def wfa_func(w):
            return _safe_z_calc(calc.wfa, w, age_months, sex)
        
        lo, hi = BOUNDS['wfa']
        
        ranges['weight'] = {
            'min_normal': round(invert_zscore_function(wfa_func, -2, lo, hi), 2),
            'median': round(invert_zscore_function(wfa_func, 0, lo, hi), 2),
            'max_normal': round(invert_zscore_function(wfa_func, 2, lo, hi), 2),
            'unit': 'kg'
        }
    except Exception:
        pass
    
    # Height-for-Age ranges
    try:
        def hfa_func(h):
            return _safe_z_calc(calc.lhfa, h, age_months, sex)
        
        lo, hi = BOUNDS['hfa']
        
        ranges['height'] = {
            'min_normal': round(invert_zscore_function(hfa_func, -2, lo, hi), 1),
            'median': round(invert_zscore_function(hfa_func, 0, lo, hi), 1),
            'max_normal': round(invert_zscore_function(hfa_func, 2, lo, hi), 1),
            'unit': 'cm'
        }
    except Exception:
        pass
    
    # Head Circumference ranges
    try:
        def hcfa_func(hc):
            return _safe_z_calc(calc.hcfa, hc, age_months, sex)
        
        lo, hi = BOUNDS['hcfa']
        
        ranges['head_circ'] = {
            'min_normal': round(invert_zscore_function(hcfa_func, -2, lo, hi), 1),
            'median': round(invert_zscore_function(hcfa_func, 0, lo, hi), 1),
            'max_normal': round(invert_zscore_function(hcfa_func, 2, lo, hi), 1),
            'unit': 'cm'
        }
    except Exception:
        pass
    
    return ranges


print("✅ WHO Calculator module loaded")
