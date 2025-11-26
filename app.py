#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
#==============================================================================
#                         AnthroHPK v4.0
#           Aplikasi Monitoring Pertumbuhan Anak Indonesia
#                 WHO Growth Standards & Permenkes 2020
#==============================================================================
#
#  Dikembangkan untuk membantu orang tua dan tenaga kesehatan memantau
#  pertumbuhan dan perkembangan anak usia 0-60 bulan.
#
#  Fitur Utama:
#  - Kalkulator Z-Score WHO
#  - Grafik Pertumbuhan Interaktif
#  - Checklist Sehat Bulanan
#  - Panduan MPASI Lengkap (BARU)
#  - 1000 Hari Pertama Kehidupan (BARU)
#  - Fitur Kesehatan Ibu (BARU)
#  - Perpustakaan Edukasi
#  - Export PDF/CSV
#
#==============================================================================
"""

import os
import sys
import traceback
from datetime import date, datetime
from typing import Optional, Tuple, List, Dict

# FastAPI & Gradio
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import gradio as gr

# Configuration
from config import (
    APP_VERSION, APP_TITLE, APP_DESCRIPTION, CONTACT_WA, BASE_URL,
    BASE_DIR, STATIC_DIR, OUTPUTS_DIR, PYGROWUP_DIR,
    UI_THEMES, PREMIUM_PACKAGES, MOTIVATIONAL_QUOTES
)

# Utilities
from modules.utilities import (
    as_float, parse_date, calculate_age_from_dates, calculate_age_text,
    z_to_percentile, format_zscore, get_zscore_color, get_zscore_status_emoji,
    validate_anthropometry, get_random_quote, get_sex_code, get_sex_text
)

# WHO Calculator
from modules.who_calculator import (
    calculate_all_zscores, classify_permenkes_2020, classify_who_standards,
    validate_zscores, get_normal_ranges
)

# Growth Charts
from modules.growth_charts import (
    plot_weight_for_age, plot_height_for_age, 
    plot_head_circumference_for_age, plot_weight_for_length,
    plot_zscore_summary_bars, cleanup_matplotlib_figures
)

# Checklist
from modules.checklist import generate_monthly_checklist, generate_quick_checklist

# MPASI
from modules.mpasi import (
    generate_mpasi_overview_html, generate_mpasi_by_month_html,
    generate_allergy_guide_html, generate_mpasi_videos_html, generate_recipes_html
)

# 1000 Hari
from modules.first1000days import (
    generate_1000_days_dashboard, generate_1000_days_timeline,
    calculate_1000_days_progress
)

# Mother
from modules.mother import (
    generate_mother_nutrition_html, generate_laktasi_guide_html,
    generate_mental_health_html
)

# Kejar Tumbuh
from modules.kejar_tumbuh import (
    analyze_growth_velocity, kalkulator_kejar_tumbuh_handler
)

# Library
from modules.library import generate_library_html, get_article_html

# PDF Export
from modules.pdf_export import (
    generate_growth_report_pdf, export_data_to_csv
)

# Data
from data.articles import ARTIKEL_DATABASE, search_articles, get_categories
from data.immunization import get_immunization_for_month
from data.kpsp import get_kpsp_questions_for_month

# ==============================================================================
# FASTAPI SETUP
# ==============================================================================

app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION
)

# Mount static files
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

if os.path.exists(OUTPUTS_DIR):
    app.mount("/outputs", StaticFiles(directory=OUTPUTS_DIR), name="outputs")

# ==============================================================================
# GLOBAL STATE
# ==============================================================================

# Store data untuk multi-measurement (kejar tumbuh)
measurement_history = []

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def get_theme_css(theme_name: str = "pink_pastel") -> str:
    """Generate CSS for selected theme"""
    theme = UI_THEMES.get(theme_name, UI_THEMES["pink_pastel"])
    
    return f"""
    <style>
        :root {{
            --primary-color: {theme['primary']};
            --secondary-color: {theme['secondary']};
            --bg-color: {theme['bg']};
            --card-color: {theme['card']};
            --text-color: {theme['text']};
            --border-color: {theme['border']};
        }}
        
        .gradio-container {{
            background: {theme['bg']} !important;
        }}
        
        .card {{
            background: {theme['card']};
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 15px;
        }}
        
        .status-normal {{ color: #388e3c; }}
        .status-warning {{ color: #f57c00; }}
        .status-danger {{ color: #d32f2f; }}
        
        .header-gradient {{
            background: linear-gradient(135deg, {theme['primary']}88 0%, {theme['secondary']} 100%);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
        }}
    </style>
    """

# ==============================================================================
# KALKULATOR WHO - MAIN HANDLER
# ==============================================================================

def kalkulator_who_handler(
    nama: str,
    tgl_lahir: str,
    tgl_ukur: str,
    jenis_kelamin: str,
    berat_badan: str,
    tinggi_badan: str,
    lingkar_kepala: str,
    theme: str = "pink_pastel"
) -> Tuple[str, Optional[str], Optional[str], Optional[str], Optional[str], Optional[str]]:
    """
    Main handler for WHO Calculator
    
    Returns:
        Tuple of (hasil_html, wfa_plot, hfa_plot, hcfa_plot, wfl_plot, summary_plot)
    """
    try:
        # Parse inputs
        dob = parse_date(tgl_lahir)
        measurement_date = parse_date(tgl_ukur) if tgl_ukur else date.today()
        
        if not dob:
            return ("⚠️ Tanggal lahir tidak valid. Gunakan format YYYY-MM-DD atau DD/MM/YYYY", 
                    None, None, None, None, None)
        
        # Calculate age
        age_months, age_days = calculate_age_from_dates(dob, measurement_date)
        age_text = calculate_age_text(age_months)
        
        if age_months < 0 or age_months > 60:
            return ("⚠️ Usia harus antara 0-60 bulan untuk analisis WHO.", 
                    None, None, None, None, None)
        
        # Parse measurements
        bb = as_float(berat_badan)
        tb = as_float(tinggi_badan)
        lk = as_float(lingkar_kepala) if lingkar_kepala else None
        
        if bb is None or tb is None:
            return ("⚠️ Berat badan dan tinggi badan harus diisi dengan benar.", 
                    None, None, None, None, None)
        
        # Validate measurements
        sex_code = get_sex_code(jenis_kelamin)
        validation = validate_anthropometry(bb, tb, lk, age_months, sex_code)
        
        if not validation['valid']:
            warnings = "<br>".join(validation['warnings'])
            return (f"⚠️ Data pengukuran tidak valid:<br>{warnings}", 
                    None, None, None, None, None)
        
        # Calculate Z-scores
        zscores = calculate_all_zscores(
            weight=bb,
            height=tb,
            head_circ=lk,
            age_months=age_months,
            sex=sex_code
        )
        
        if not zscores or all(v is None for v in zscores.values()):
            return ("⚠️ Tidak dapat menghitung Z-score. Periksa data input.", 
                    None, None, None, None, None)
        
        # Classifications
        permenkes = classify_permenkes_2020(zscores)
        who_class = classify_who_standards(zscores)
        zscore_validation = validate_zscores(zscores)
        
        # Generate result HTML
        theme_data = UI_THEMES.get(theme, UI_THEMES["pink_pastel"])
        
        html = f"""
        <div style='background: linear-gradient(135deg, {theme_data['primary']}44 0%, {theme_data['secondary']}44 100%);
                    padding: 25px; border-radius: 20px; margin-bottom: 20px;'>
            <h2 style='color: {theme_data['primary']}; margin: 0 0 10px 0;'>
                📊 Hasil Analisis Pertumbuhan
            </h2>
            <p style='color: #666; margin: 0;'>
                <strong>{nama or 'Anak'}</strong> | {jenis_kelamin} | {age_text}
            </p>
        </div>
        """
        
        # Data Pengukuran
        html += f"""
        <div style='background: white; padding: 20px; border-radius: 15px; margin-bottom: 20px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);'>
            <h3 style='color: #333; margin: 0 0 15px 0;'>📏 Data Pengukuran</h3>
            <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px;'>
                <div style='background: #e3f2fd; padding: 15px; border-radius: 10px; text-align: center;'>
                    <div style='font-size: 0.9em; color: #666;'>Berat Badan</div>
                    <div style='font-size: 1.5em; font-weight: bold; color: #1565c0;'>{bb:.2f} kg</div>
                </div>
                <div style='background: #e8f5e9; padding: 15px; border-radius: 10px; text-align: center;'>
                    <div style='font-size: 0.9em; color: #666;'>Tinggi/Panjang Badan</div>
                    <div style='font-size: 1.5em; font-weight: bold; color: #2e7d32;'>{tb:.1f} cm</div>
                </div>
        """
        
        if lk:
            html += f"""
                <div style='background: #fff3e0; padding: 15px; border-radius: 10px; text-align: center;'>
                    <div style='font-size: 0.9em; color: #666;'>Lingkar Kepala</div>
                    <div style='font-size: 1.5em; font-weight: bold; color: #e65100;'>{lk:.1f} cm</div>
                </div>
            """
        
        html += "</div></div>"
        
        # Z-Scores
        html += """
        <div style='background: white; padding: 20px; border-radius: 15px; margin-bottom: 20px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);'>
            <h3 style='color: #333; margin: 0 0 15px 0;'>📈 Nilai Z-Score</h3>
            <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px;'>
        """
        
        zscore_labels = {
            'waz': ('BB/U', 'Berat untuk Usia'),
            'haz': ('TB/U', 'Tinggi untuk Usia'),
            'whz': ('BB/TB', 'Berat untuk Tinggi'),
            'baz': ('IMT/U', 'BMI untuk Usia'),
            'hcz': ('LK/U', 'Lingkar Kepala untuk Usia')
        }
        
        for key, (short, full) in zscore_labels.items():
            z = zscores.get(key)
            if z is not None:
                color = get_zscore_color(z)
                emoji = get_zscore_status_emoji(z)
                percentile = z_to_percentile(z)
                
                html += f"""
                <div style='background: {color}22; padding: 15px; border-radius: 10px; 
                            border-left: 4px solid {color};'>
                    <div style='font-size: 0.85em; color: #666;'>{full}</div>
                    <div style='font-size: 1.8em; font-weight: bold; color: {color};'>
                        {emoji} {format_zscore(z)}
                    </div>
                    <div style='font-size: 0.8em; color: #888;'>Persentil: {percentile:.1f}%</div>
                </div>
                """
        
        html += "</div></div>"
        
        # Klasifikasi Permenkes
        html += f"""
        <div style='background: white; padding: 20px; border-radius: 15px; margin-bottom: 20px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);'>
            <h3 style='color: #333; margin: 0 0 15px 0;'>🏥 Klasifikasi (Permenkes RI 2020)</h3>
            <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;'>
        """
        
        for category, status in permenkes.items():
            status_color = "#388e3c" if "Normal" in status else "#f57c00" if "Risiko" in status else "#d32f2f"
            html += f"""
            <div style='background: #f5f5f5; padding: 12px; border-radius: 8px;'>
                <div style='font-size: 0.85em; color: #666;'>{category}</div>
                <div style='font-weight: bold; color: {status_color};'>{status}</div>
            </div>
            """
        
        html += "</div></div>"
        
        # Warnings if any
        if zscore_validation['warnings']:
            html += """
            <div style='background: #fff3e0; padding: 15px; border-radius: 10px; margin-bottom: 20px;
                        border-left: 4px solid #ff9800;'>
                <h4 style='color: #e65100; margin: 0 0 10px 0;'>⚠️ Perhatian</h4>
                <ul style='margin: 0; padding-left: 20px;'>
            """
            for warning in zscore_validation['warnings']:
                html += f"<li style='margin: 5px 0;'>{warning}</li>"
            html += "</ul></div>"
        
        # Motivational quote
        quote = get_random_quote()
        html += f"""
        <div style='background: linear-gradient(135deg, {theme_data['primary']}22, {theme_data['secondary']}22);
                    padding: 15px; border-radius: 10px; text-align: center; font-style: italic; color: #666;'>
            💬 "{quote}"
        </div>
        """
        
        # Generate plots
        wfa_plot = plot_weight_for_age(age_months, bb, sex_code, theme)
        hfa_plot = plot_height_for_age(age_months, tb, sex_code, theme)
        hcfa_plot = plot_head_circumference_for_age(age_months, lk, sex_code, theme) if lk else None
        wfl_plot = plot_weight_for_length(tb, bb, sex_code, theme)
        summary_plot = plot_zscore_summary_bars(zscores, theme)
        
        # Cleanup
        cleanup_matplotlib_figures()
        
        return (html, wfa_plot, hfa_plot, hcfa_plot, wfl_plot, summary_plot)
        
    except Exception as e:
        print(f"❌ Error in kalkulator_who_handler: {e}")
        traceback.print_exc()
        return (f"❌ Terjadi kesalahan: {str(e)}", None, None, None, None, None)


# ==============================================================================
# MODE MUDAH HANDLER
# ==============================================================================

def mode_mudah_handler(
    usia_bulan: str,
    jenis_kelamin: str
) -> str:
    """Handler for Mode Mudah (Normal Ranges)"""
    try:
        age = as_float(usia_bulan)
        if age is None or age < 0 or age > 60:
            return "⚠️ Masukkan usia valid (0-60 bulan)"
        
        sex_code = get_sex_code(jenis_kelamin)
        ranges = get_normal_ranges(age, sex_code)
        
        if not ranges:
            return "⚠️ Tidak dapat mengambil data rentang normal"
        
        html = f"""
        <div style='background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
                    padding: 20px; border-radius: 15px; margin-bottom: 20px;'>
            <h2 style='color: #2e7d32; margin: 0;'>📋 Rentang Normal untuk Usia {int(age)} Bulan</h2>
            <p style='color: #1b5e20; margin: 5px 0 0 0;'>{jenis_kelamin}</p>
        </div>
        
        <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;'>
        """
        
        # Weight
        w = ranges.get('weight', {})
        html += f"""
        <div style='background: white; padding: 20px; border-radius: 15px; 
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);'>
            <h3 style='color: #1565c0; margin: 0 0 15px 0;'>⚖️ Berat Badan</h3>
            <div style='text-align: center; padding: 15px; background: #e3f2fd; border-radius: 10px;'>
                <div style='font-size: 1.8em; font-weight: bold; color: #1565c0;'>
                    {w.get('min', 0):.1f} - {w.get('max', 0):.1f} kg
                </div>
                <div style='color: #666; font-size: 0.9em;'>Median: {w.get('median', 0):.1f} kg</div>
            </div>
        </div>
        """
        
        # Height
        h = ranges.get('height', {})
        html += f"""
        <div style='background: white; padding: 20px; border-radius: 15px; 
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);'>
            <h3 style='color: #2e7d32; margin: 0 0 15px 0;'>📏 Tinggi Badan</h3>
            <div style='text-align: center; padding: 15px; background: #e8f5e9; border-radius: 10px;'>
                <div style='font-size: 1.8em; font-weight: bold; color: #2e7d32;'>
                    {h.get('min', 0):.1f} - {h.get('max', 0):.1f} cm
                </div>
                <div style='color: #666; font-size: 0.9em;'>Median: {h.get('median', 0):.1f} cm</div>
            </div>
        </div>
        """
        
        # Head circumference
        hc = ranges.get('head_circ', {})
        html += f"""
        <div style='background: white; padding: 20px; border-radius: 15px; 
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);'>
            <h3 style='color: #e65100; margin: 0 0 15px 0;'>🎯 Lingkar Kepala</h3>
            <div style='text-align: center; padding: 15px; background: #fff3e0; border-radius: 10px;'>
                <div style='font-size: 1.8em; font-weight: bold; color: #e65100;'>
                    {hc.get('min', 0):.1f} - {hc.get('max', 0):.1f} cm
                </div>
                <div style='color: #666; font-size: 0.9em;'>Median: {hc.get('median', 0):.1f} cm</div>
            </div>
        </div>
        """
        
        html += """
        </div>
        <p style='margin-top: 20px; color: #666; font-size: 0.9em; text-align: center;'>
            📌 Rentang normal = Z-score -2 SD hingga +2 SD berdasarkan standar WHO 2006
        </p>
        """
        
        return html
        
    except Exception as e:
        print(f"❌ Error in mode_mudah_handler: {e}")
        return f"❌ Terjadi kesalahan: {str(e)}"


# ==============================================================================
# CHECKLIST HANDLER
# ==============================================================================

def checklist_handler(usia_bulan: str) -> str:
    """Handler for monthly checklist"""
    try:
        age = as_float(usia_bulan)
        if age is None or age < 0 or age > 60:
            return "⚠️ Masukkan usia valid (0-60 bulan)"
        
        return generate_monthly_checklist(int(age))
        
    except Exception as e:
        print(f"❌ Error in checklist_handler: {e}")
        return f"❌ Terjadi kesalahan: {str(e)}"


# ==============================================================================
# MPASI HANDLERS
# ==============================================================================

def mpasi_overview_handler() -> str:
    """Handler for MPASI overview"""
    return generate_mpasi_overview_html()


def mpasi_by_month_handler(usia_bulan: str) -> str:
    """Handler for MPASI by month"""
    try:
        age = as_float(usia_bulan)
        if age is None or age < 6:
            return "⚠️ MPASI dimulai pada usia 6 bulan"
        return generate_mpasi_by_month_html(int(age))
    except Exception as e:
        return f"❌ Error: {str(e)}"


def mpasi_allergy_handler() -> str:
    """Handler for allergy guide"""
    return generate_allergy_guide_html()


def mpasi_recipe_handler(usia_bulan: str) -> str:
    """Handler for MPASI recipes"""
    try:
        age = as_float(usia_bulan) or 6
        return generate_recipes_html(int(age))
    except Exception as e:
        return f"❌ Error: {str(e)}"


# ==============================================================================
# 1000 HARI HANDLERS
# ==============================================================================

def first1000days_handler(tgl_lahir: str) -> str:
    """Handler for 1000 days dashboard"""
    try:
        dob = parse_date(tgl_lahir)
        if not dob:
            return "⚠️ Masukkan tanggal lahir yang valid"
        
        return generate_1000_days_dashboard(dob)
    except Exception as e:
        return f"❌ Error: {str(e)}"


def first1000days_timeline_handler() -> str:
    """Handler for 1000 days timeline"""
    return generate_1000_days_timeline()


# ==============================================================================
# MOTHER HANDLERS
# ==============================================================================

def mother_nutrition_handler(fase: str) -> str:
    """Handler for mother nutrition"""
    return generate_mother_nutrition_html(fase)


def mother_laktasi_handler() -> str:
    """Handler for lactation guide"""
    return generate_laktasi_guide_html()


def mother_mental_handler() -> str:
    """Handler for mental health"""
    return generate_mental_health_html()


# ==============================================================================
# LIBRARY HANDLERS
# ==============================================================================

def library_handler(kategori: str, search_query: str) -> str:
    """Handler for article library"""
    return generate_library_html(kategori, search_query)


def article_detail_handler(article_id: int) -> str:
    """Handler for article detail"""
    return get_article_html(article_id)


# ==============================================================================
# GRADIO INTERFACE
# ==============================================================================

def create_gradio_interface():
    """Create main Gradio interface with all tabs"""
    
    theme = gr.themes.Soft(
        primary_hue="pink",
        secondary_hue="rose",
    )
    
    with gr.Blocks(
        theme=theme,
        title=APP_TITLE,
        css="""
        .gradio-container { max-width: 1200px !important; }
        footer { display: none !important; }
        """
    ) as demo:
        
        # Header
        gr.HTML(f"""
        <div style='background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%);
                    padding: 30px; border-radius: 20px; text-align: center; margin-bottom: 20px;'>
            <h1 style='color: #c2185b; margin: 0; font-size: 2.5em;'>🍼 {APP_TITLE}</h1>
            <p style='color: #880e4f; margin: 10px 0 0 0; font-size: 1.1em;'>
                {APP_DESCRIPTION}
            </p>
            <p style='color: #666; margin: 5px 0 0 0; font-size: 0.9em;'>
                Versi {APP_VERSION} | Standar WHO 2006 & Permenkes RI 2020
            </p>
        </div>
        """)
        
        # Main Tabs
        with gr.Tabs():
            
            # ==================== TAB 1: KALKULATOR WHO ====================
            with gr.TabItem("🧮 Kalkulator Gizi", id="calculator"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### 📝 Data Anak")
                        calc_nama = gr.Textbox(label="Nama Anak", placeholder="Masukkan nama anak")
                        calc_tgl_lahir = gr.Textbox(label="Tanggal Lahir", placeholder="YYYY-MM-DD atau DD/MM/YYYY")
                        calc_tgl_ukur = gr.Textbox(label="Tanggal Pengukuran (opsional)", placeholder="Kosongkan untuk hari ini")
                        calc_jk = gr.Radio(["Laki-laki", "Perempuan"], label="Jenis Kelamin", value="Laki-laki")
                        
                        gr.Markdown("### 📏 Data Pengukuran")
                        calc_bb = gr.Textbox(label="Berat Badan (kg)", placeholder="Contoh: 8.5")
                        calc_tb = gr.Textbox(label="Tinggi/Panjang Badan (cm)", placeholder="Contoh: 72.5")
                        calc_lk = gr.Textbox(label="Lingkar Kepala (cm) - opsional", placeholder="Contoh: 44.0")
                        calc_theme = gr.Dropdown(
                            choices=list(UI_THEMES.keys()),
                            value="pink_pastel",
                            label="🎨 Tema Warna"
                        )
                        calc_btn = gr.Button("🔍 Analisis Pertumbuhan", variant="primary")
                    
                    with gr.Column(scale=2):
                        calc_result = gr.HTML(label="Hasil Analisis")
                        
                        with gr.Row():
                            calc_wfa = gr.Image(label="BB/U", type="filepath")
                            calc_hfa = gr.Image(label="TB/U", type="filepath")
                        
                        with gr.Row():
                            calc_hcfa = gr.Image(label="LK/U", type="filepath")
                            calc_wfl = gr.Image(label="BB/TB", type="filepath")
                        
                        calc_summary = gr.Image(label="Ringkasan Z-Score", type="filepath")
                
                calc_btn.click(
                    fn=kalkulator_who_handler,
                    inputs=[calc_nama, calc_tgl_lahir, calc_tgl_ukur, calc_jk, 
                           calc_bb, calc_tb, calc_lk, calc_theme],
                    outputs=[calc_result, calc_wfa, calc_hfa, calc_hcfa, calc_wfl, calc_summary]
                )
            
            # ==================== TAB 2: MODE MUDAH ====================
            with gr.TabItem("📋 Mode Mudah", id="easy_mode"):
                gr.Markdown("""
                ### 🎯 Rentang Normal Pertumbuhan
                Cek rentang normal berat badan, tinggi badan, dan lingkar kepala tanpa perlu menghitung Z-score.
                """)
                
                with gr.Row():
                    easy_usia = gr.Textbox(label="Usia (bulan)", placeholder="Contoh: 12")
                    easy_jk = gr.Radio(["Laki-laki", "Perempuan"], label="Jenis Kelamin", value="Laki-laki")
                
                easy_btn = gr.Button("📊 Lihat Rentang Normal", variant="primary")
                easy_result = gr.HTML()
                
                easy_btn.click(fn=mode_mudah_handler, inputs=[easy_usia, easy_jk], outputs=easy_result)
            
            # ==================== TAB 3: CHECKLIST ====================
            with gr.TabItem("✅ Checklist Sehat", id="checklist"):
                gr.Markdown("""
                ### 📋 Checklist Sehat Bulanan
                Panduan lengkap imunisasi, nutrisi, dan milestone perkembangan sesuai usia.
                """)
                
                checklist_usia = gr.Textbox(label="Usia Anak (bulan)", placeholder="Contoh: 9")
                checklist_btn = gr.Button("📋 Tampilkan Checklist", variant="primary")
                checklist_result = gr.HTML()
                
                checklist_btn.click(fn=checklist_handler, inputs=[checklist_usia], outputs=checklist_result)
            
            # ==================== TAB 4: MPASI ====================
            with gr.TabItem("🍽️ Panduan MPASI", id="mpasi"):
                with gr.Tabs():
                    with gr.TabItem("📚 Pengantar"):
                        mpasi_overview = gr.HTML(value=generate_mpasi_overview_html())
                    
                    with gr.TabItem("📅 Per Bulan"):
                        mpasi_usia = gr.Slider(minimum=6, maximum=24, step=1, value=6, 
                                              label="Usia Anak (bulan)")
                        mpasi_btn = gr.Button("Lihat Panduan", variant="primary")
                        mpasi_result = gr.HTML()
                        mpasi_btn.click(fn=mpasi_by_month_handler, 
                                       inputs=[mpasi_usia], outputs=mpasi_result)
                    
                    with gr.TabItem("🍳 Resep"):
                        recipe_usia = gr.Slider(minimum=6, maximum=24, step=1, value=6,
                                               label="Usia Anak (bulan)")
                        recipe_btn = gr.Button("Lihat Resep", variant="primary")
                        recipe_result = gr.HTML()
                        recipe_btn.click(fn=mpasi_recipe_handler,
                                        inputs=[recipe_usia], outputs=recipe_result)
                    
                    with gr.TabItem("⚠️ Alergi"):
                        allergy_result = gr.HTML(value=generate_allergy_guide_html())
            
            # ==================== TAB 5: 1000 HARI ====================
            with gr.TabItem("🌟 1000 Hari", id="first1000"):
                gr.Markdown("""
                ### 🌟 1000 Hari Pertama Kehidupan
                Periode emas dari konsepsi hingga usia 2 tahun.
                """)
                
                with gr.Tabs():
                    with gr.TabItem("📊 Dashboard"):
                        f1000_tgl = gr.Textbox(label="Tanggal Lahir Anak", placeholder="YYYY-MM-DD")
                        f1000_btn = gr.Button("Lihat Progress", variant="primary")
                        f1000_result = gr.HTML()
                        f1000_btn.click(fn=first1000days_handler, inputs=[f1000_tgl], outputs=f1000_result)
                    
                    with gr.TabItem("📅 Timeline"):
                        timeline_result = gr.HTML(value=generate_1000_days_timeline())
            
            # ==================== TAB 6: FITUR IBU ====================
            with gr.TabItem("👩 Fitur Ibu", id="mother"):
                with gr.Tabs():
                    with gr.TabItem("🍎 Nutrisi"):
                        mother_fase = gr.Radio(
                            ["menyusui", "hamil1", "hamil2", "hamil3"],
                            label="Fase",
                            value="menyusui",
                            info="Pilih fase untuk melihat kebutuhan nutrisi"
                        )
                        mother_nut_btn = gr.Button("Lihat Panduan", variant="primary")
                        mother_nut_result = gr.HTML()
                        mother_nut_btn.click(fn=mother_nutrition_handler, 
                                            inputs=[mother_fase], outputs=mother_nut_result)
                    
                    with gr.TabItem("🤱 Laktasi"):
                        laktasi_result = gr.HTML(value=generate_laktasi_guide_html())
                    
                    with gr.TabItem("💜 Kesehatan Mental"):
                        mental_result = gr.HTML(value=generate_mental_health_html())
            
            # ==================== TAB 7: PERPUSTAKAAN ====================
            with gr.TabItem("📚 Perpustakaan", id="library"):
                gr.Markdown("### 📚 Perpustakaan Ibu Balita")
                
                with gr.Row():
                    lib_kategori = gr.Dropdown(
                        choices=["Semua Kategori"] + get_categories(),
                        value="Semua Kategori",
                        label="Kategori"
                    )
                    lib_search = gr.Textbox(label="Cari Artikel", placeholder="Kata kunci...")
                
                lib_btn = gr.Button("🔍 Cari", variant="primary")
                lib_result = gr.HTML()
                
                lib_btn.click(fn=library_handler, inputs=[lib_kategori, lib_search], outputs=lib_result)
            
            # ==================== TAB 8: KEJAR TUMBUH ====================
            with gr.TabItem("📈 Kejar Tumbuh", id="catch_up"):
                gr.Markdown("""
                ### 📈 Analisis Growth Velocity
                Input beberapa pengukuran untuk melihat kecepatan pertumbuhan anak.
                """)
                
                gr.Markdown("""
                **Format Input:** Satu baris per pengukuran dengan format:
                `usia_bulan, berat_kg, tinggi_cm`
                
                Contoh:
                ```
                6, 7.5, 66
                9, 8.8, 72
                12, 9.5, 76
                ```
                """)
                
                kejar_data = gr.Textbox(
                    label="Data Pengukuran",
                    placeholder="6, 7.5, 66\n9, 8.8, 72\n12, 9.5, 76",
                    lines=5
                )
                kejar_jk = gr.Radio(["Laki-laki", "Perempuan"], label="Jenis Kelamin", value="Laki-laki")
                kejar_btn = gr.Button("📊 Analisis", variant="primary")
                kejar_result = gr.HTML()
                kejar_plot = gr.Image(label="Grafik Trajectory", type="filepath")
                
                def process_kejar_tumbuh(data_str, gender):
                    try:
                        lines = data_str.strip().split('\n')
                        data_list = []
                        for line in lines:
                            parts = [p.strip() for p in line.split(',')]
                            if len(parts) >= 3:
                                data_list.append({
                                    'usia_bulan': float(parts[0]),
                                    'bb': float(parts[1]),
                                    'tb': float(parts[2])
                                })
                        
                        if len(data_list) < 2:
                            return "⚠️ Minimal 2 data pengukuran diperlukan", None
                        
                        return kalkulator_kejar_tumbuh_handler(data_list, gender)
                    except Exception as e:
                        return f"❌ Error: {str(e)}", None
                
                kejar_btn.click(fn=process_kejar_tumbuh, 
                               inputs=[kejar_data, kejar_jk], 
                               outputs=[kejar_result, kejar_plot])
        
        # Footer
        gr.HTML(f"""
        <div style='margin-top: 30px; padding: 20px; background: #f5f5f5; 
                    border-radius: 15px; text-align: center;'>
            <p style='margin: 0; color: #666;'>
                <strong>{APP_TITLE}</strong> v{APP_VERSION}<br>
                Dibuat dengan ❤️ untuk Ibu dan Anak Indonesia<br>
                📞 Kontak: {CONTACT_WA}
            </p>
            <p style='margin: 10px 0 0 0; color: #888; font-size: 0.85em;'>
                ⚠️ Aplikasi ini untuk edukasi. Selalu konsultasikan ke tenaga kesehatan.
            </p>
        </div>
        """)
    
    return demo


# ==============================================================================
# MAIN
# ==============================================================================

# Create Gradio interface
demo = create_gradio_interface()

# Mount to FastAPI
app = gr.mount_gradio_app(app, demo, path="/")

# Run with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 7860)))
