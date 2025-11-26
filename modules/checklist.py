#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
#==============================================================================
#                    AnthroHPK v4.0 - CHECKLIST MODULE
#           Checklist Sehat Bulanan (Independen dari Kalkulator WHO)
#==============================================================================
"""

from typing import Dict, List, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.immunization import get_immunization_for_month, generate_immunization_html
from data.kpsp import get_kpsp_questions_for_month, generate_kpsp_html
from config import KPSP_YOUTUBE_VIDEOS, MPASI_YOUTUBE_VIDEOS

# ==============================================================================
# MILESTONE PERKEMBANGAN PER BULAN
# ==============================================================================

DEVELOPMENT_MILESTONES = {
    0: {
        "motorik_kasar": ["Refleks menggenggam", "Refleks rooting (mencari puting)"],
        "motorik_halus": ["Tangan masih mengepal"],
        "bahasa": ["Menangis untuk berkomunikasi"],
        "sosial": ["Merespon suara ibu"]
    },
    1: {
        "motorik_kasar": ["Mengangkat kepala sebentar saat tengkurap"],
        "motorik_halus": ["Mulai memperhatikan tangannya"],
        "bahasa": ["Mengeluarkan suara 'aaa'"],
        "sosial": ["Mulai tersenyum sosial"]
    },
    2: {
        "motorik_kasar": ["Mengangkat kepala 45° saat tengkurap"],
        "motorik_halus": ["Tangan mulai terbuka"],
        "bahasa": ["Cooing (suara vokal)"],
        "sosial": ["Tersenyum saat diajak bicara"]
    },
    3: {
        "motorik_kasar": ["Mengangkat kepala 90° saat tengkurap", "Menopang dengan lengan"],
        "motorik_halus": ["Meraih benda di dekatnya"],
        "bahasa": ["Mengoceh dengan variasi"],
        "sosial": ["Tertawa keras"]
    },
    4: {
        "motorik_kasar": ["Berguling dari tengkurap ke telentang"],
        "motorik_halus": ["Menggenggam mainan"],
        "bahasa": ["Babbling (ba-ba-ba)"],
        "sosial": ["Mengenal wajah familiar"]
    },
    5: {
        "motorik_kasar": ["Berguling dua arah"],
        "motorik_halus": ["Memindahkan benda antar tangan"],
        "bahasa": ["Variasi babbling meningkat"],
        "sosial": ["Stranger anxiety mulai muncul"]
    },
    6: {
        "motorik_kasar": ["Duduk dengan bantuan", "Merangkak mundur"],
        "motorik_halus": ["Mengambil benda dengan seluruh telapak tangan"],
        "bahasa": ["Mengucapkan konsonan"],
        "sosial": ["Bermain cilukba"]
    },
    7: {
        "motorik_kasar": ["Duduk tanpa bantuan sebentar"],
        "motorik_halus": ["Memukul-mukul mainan"],
        "bahasa": ["Ma-ma, pa-pa tanpa makna"],
        "sosial": ["Melambaikan tangan"]
    },
    8: {
        "motorik_kasar": ["Duduk stabil sendiri", "Merangkak maju"],
        "motorik_halus": ["Pincer grasp mulai berkembang"],
        "bahasa": ["Mengerti 'tidak'"],
        "sosial": ["Bermain bersama orang dewasa"]
    },
    9: {
        "motorik_kasar": ["Merangkak cepat", "Berdiri berpegangan"],
        "motorik_halus": ["Mengambil benda kecil dengan jempol-telunjuk"],
        "bahasa": ["1 kata bermakna"],
        "sosial": ["Menunjuk untuk meminta"]
    },
    10: {
        "motorik_kasar": ["Cruising (jalan berpegangan furniture)"],
        "motorik_halus": ["Memasukkan benda ke wadah"],
        "bahasa": ["2-3 kata bermakna"],
        "sosial": ["Meniru gerakan sederhana"]
    },
    11: {
        "motorik_kasar": ["Berdiri sendiri sebentar"],
        "motorik_halus": ["Menumpuk 2 kubus"],
        "bahasa": ["Mengikuti instruksi sederhana"],
        "sosial": ["Main bertepuk tangan"]
    },
    12: {
        "motorik_kasar": ["Berjalan dengan bantuan/sendiri"],
        "motorik_halus": ["Mencoret-coret"],
        "bahasa": ["4-6 kata bermakna"],
        "sosial": ["Minum dari gelas sendiri"]
    },
    15: {
        "motorik_kasar": ["Berjalan stabil", "Naik tangga merangkak"],
        "motorik_halus": ["Menumpuk 3-4 kubus"],
        "bahasa": ["10-15 kata"],
        "sosial": ["Makan sendiri dengan sendok (berantakan)"]
    },
    18: {
        "motorik_kasar": ["Berlari", "Naik tangga dengan bantuan"],
        "motorik_halus": ["Menumpuk 4-5 kubus", "Membalik halaman buku"],
        "bahasa": ["20-50 kata", "Kalimat 2 kata"],
        "sosial": ["Mulai bermain paralel"]
    },
    21: {
        "motorik_kasar": ["Melompat di tempat", "Menendang bola"],
        "motorik_halus": ["Menggambar garis vertikal"],
        "bahasa": ["Kalimat 2-3 kata", "Menunjuk gambar di buku"],
        "sosial": ["Mengikuti instruksi 2 tahap"]
    },
    24: {
        "motorik_kasar": ["Melompat dengan 2 kaki", "Naik turun tangga sendiri"],
        "motorik_halus": ["Menumpuk 6+ kubus", "Memutar pegangan pintu"],
        "bahasa": ["50-200 kata", "Kalimat 3-4 kata"],
        "sosial": ["Bermain pura-pura", "Toilet training mulai"]
    }
}

# ==============================================================================
# REKOMENDASI NUTRISI PER FASE
# ==============================================================================

NUTRITION_RECOMMENDATIONS = {
    "0-6": {
        "title": "ASI Eksklusif",
        "recommendations": [
            "🤱 ASI on demand (8-12x/hari)",
            "💧 Tidak perlu air/makanan tambahan",
            "😴 Skin-to-skin untuk bonding",
            "💊 Vitamin D jika diperlukan (konsultasi dokter)"
        ]
    },
    "6-9": {
        "title": "MPASI Awal",
        "recommendations": [
            "🥣 MPASI 2-3x sehari + ASI",
            "🍗 Protein hewani di SETIAP makan",
            "🧈 Tambahkan lemak (EVOO, santan)",
            "📈 Tingkatkan tekstur bertahap"
        ]
    },
    "9-12": {
        "title": "MPASI Lanjutan",
        "recommendations": [
            "🍽️ 3x makan + 2x snack + ASI",
            "🥕 Finger food untuk latih self-feeding",
            "🍖 Variasi protein setiap hari",
            "🥛 Mulai latih minum dari gelas"
        ]
    },
    "12-24": {
        "title": "Makanan Keluarga",
        "recommendations": [
            "🍚 Menu keluarga dengan modifikasi",
            "🥗 Prinsip 4 bintang di setiap makan",
            "🍫 Hindari gula dan garam berlebihan",
            "💧 Cukupi kebutuhan air (600-1000ml)"
        ]
    }
}

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def get_milestone_for_month(month: int) -> Dict:
    """Get development milestones for specific month"""
    # Find nearest milestone
    milestone_ages = sorted(DEVELOPMENT_MILESTONES.keys())
    
    nearest = 0
    for age in milestone_ages:
        if month >= age:
            nearest = age
    
    return DEVELOPMENT_MILESTONES.get(nearest, DEVELOPMENT_MILESTONES[0])


def get_nutrition_phase(month: int) -> Dict:
    """Get nutrition recommendations based on age phase"""
    if month < 6:
        return NUTRITION_RECOMMENDATIONS["0-6"]
    elif month < 9:
        return NUTRITION_RECOMMENDATIONS["6-9"]
    elif month < 12:
        return NUTRITION_RECOMMENDATIONS["9-12"]
    else:
        return NUTRITION_RECOMMENDATIONS["12-24"]


def generate_video_links_html(videos: List[Dict]) -> str:
    """Generate HTML for video links"""
    if not videos:
        return "<p style='color: #888;'>Tidak ada video tersedia.</p>"
    
    html = "<div style='display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 15px;'>"
    
    for video in videos:
        html += f"""
        <div style='background: white; border-radius: 10px; padding: 15px; 
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
            <div style='font-weight: bold; color: #333; margin-bottom: 8px;'>
                {video['title']}
            </div>
            <div style='color: #666; font-size: 0.9em; margin-bottom: 8px;'>
                {video['description']}
            </div>
            <div style='color: #888; font-size: 0.85em; margin-bottom: 10px;'>
                ⏱️ {video['duration']}
            </div>
            <a href='{video['url']}' target='_blank' 
               style='display: inline-block; background: linear-gradient(135deg, #ff6b9d, #ff9a9e);
                      color: white; padding: 8px 16px; border-radius: 6px; 
                      text-decoration: none; font-weight: 600; font-size: 0.9em;'>
                ▶️ Tonton Video
            </a>
        </div>
        """
    
    html += "</div>"
    return html


# ==============================================================================
# MAIN CHECKLIST GENERATOR (INDEPENDEN)
# ==============================================================================

def generate_monthly_checklist(month: int, z_scores: Dict = None) -> str:
    """
    Generate comprehensive monthly checklist HTML
    
    CATATAN: Fungsi ini TIDAK MEMERLUKAN data dari kalkulator WHO.
    Parameter z_scores bersifat opsional untuk personalisasi rekomendasi.
    
    Args:
        month: Age in months
        z_scores: Optional z-score data for personalized recommendations
        
    Returns:
        HTML string with complete checklist
    """
    
    # Initialize variables - handle case when z_scores is None
    waz = 0
    haz = 0
    whz = 0
    
    if z_scores:
        waz = z_scores.get('waz', 0) or 0
        haz = z_scores.get('haz', 0) or 0
        whz = z_scores.get('whz', 0) or 0
    
    has_zscore_data = z_scores is not None and any([waz, haz, whz])
    
    html_parts = []
    
    # ==== HEADER ====
    html_parts.append(f"""
    <div style='background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); 
                padding: 20px; border-radius: 15px; margin-bottom: 20px;'>
        <h2 style='color: #c2185b; margin: 0;'>📋 Checklist Bulan ke-{month}</h2>
        <p style='color: #880e4f; margin: 5px 0 0 0;'>
            Panduan lengkap untuk usia {month} bulan
        </p>
    </div>
    """)
    
    # ==== ALERT JIKA TIDAK ADA DATA Z-SCORE ====
    if not has_zscore_data:
        html_parts.append("""
        <div style='background: #e3f2fd; padding: 15px; border-radius: 10px; 
                    margin-bottom: 20px; border-left: 4px solid #2196f3;'>
            <p style='margin: 0; color: #1565c0;'>
                ℹ️ <strong>Mode Mandiri:</strong> Checklist ini dapat digunakan tanpa 
                melakukan analisis di Kalkulator Gizi terlebih dahulu.
            </p>
        </div>
        """)
    
    # ==== PERSONALIZED ALERT (jika ada data z-score) ====
    if has_zscore_data:
        if whz < -2 or waz < -2:
            html_parts.append("""
            <div style='background: #ffebee; padding: 15px; border-radius: 10px; 
                        margin-bottom: 20px; border-left: 4px solid #e53935;'>
                <h4 style='color: #c62828; margin: 0 0 10px 0;'>⚠️ PERHATIAN KHUSUS</h4>
                <p style='margin: 0; color: #b71c1c;'>
                    Berdasarkan hasil analisis, anak memerlukan perhatian khusus pada aspek gizi.
                    Prioritaskan rekomendasi nutrisi dan konsultasi ke tenaga kesehatan.
                </p>
            </div>
            """)
        elif haz < -2:
            html_parts.append("""
            <div style='background: #fff3e0; padding: 15px; border-radius: 10px; 
                        margin-bottom: 20px; border-left: 4px solid #ff9800;'>
                <h4 style='color: #e65100; margin: 0 0 10px 0;'>📊 MONITORING TINGGI BADAN</h4>
                <p style='margin: 0; color: #bf360c;'>
                    Perlu pemantauan ketat pada pertumbuhan linear. 
                    Pastikan asupan protein dan kalsium tercukupi.
                </p>
            </div>
            """)
    
    # ==== VIDEO EDUKASI ====
    html_parts.append("""
    <div style='background: white; padding: 20px; border-radius: 15px; 
                margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);'>
        <h3 style='color: #6a1b9a; margin: 0 0 15px 0;'>🎥 Video Edukasi</h3>
    """)
    
    # KPSP Videos
    html_parts.append("""
        <h4 style='color: #7b1fa2; margin: 15px 0 10px 0;'>📊 Panduan Skrining KPSP</h4>
    """)
    html_parts.append(generate_video_links_html(KPSP_YOUTUBE_VIDEOS))
    
    # MPASI Videos (jika relevan)
    if month >= 6:
        mpasi_ages = sorted(MPASI_YOUTUBE_VIDEOS.keys())
        nearest_mpasi_age = 6
        for age in mpasi_ages:
            if month >= age:
                nearest_mpasi_age = age
        
        mpasi_videos = MPASI_YOUTUBE_VIDEOS.get(nearest_mpasi_age, [])
        if mpasi_videos:
            html_parts.append(f"""
            <h4 style='color: #7b1fa2; margin: 20px 0 10px 0;'>
                🍽️ Panduan MPASI ({nearest_mpasi_age} bulan)
            </h4>
            """)
            html_parts.append(generate_video_links_html(mpasi_videos))
    
    html_parts.append("</div>")
    
    # ==== MILESTONE PERKEMBANGAN ====
    milestones = get_milestone_for_month(month)
    
    html_parts.append("""
    <div style='background: white; padding: 20px; border-radius: 15px; 
                margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);'>
        <h3 style='color: #00695c; margin: 0 0 15px 0;'>🎯 Target Perkembangan</h3>
        <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;'>
    """)
    
    milestone_colors = {
        "motorik_kasar": ("#e8f5e9", "#2e7d32", "🏃"),
        "motorik_halus": ("#e3f2fd", "#1565c0", "✋"),
        "bahasa": ("#fce4ec", "#c2185b", "🗣️"),
        "sosial": ("#fff3e0", "#ef6c00", "👋")
    }
    
    for domain, items in milestones.items():
        bg_color, text_color, icon = milestone_colors.get(domain, ("#f5f5f5", "#333", "📌"))
        domain_name = domain.replace("_", " ").title()
        
        html_parts.append(f"""
        <div style='background: {bg_color}; padding: 15px; border-radius: 10px;'>
            <h4 style='color: {text_color}; margin: 0 0 10px 0;'>{icon} {domain_name}</h4>
            <ul style='margin: 0; padding-left: 20px; color: #333;'>
        """)
        
        for item in items:
            html_parts.append(f"<li style='margin: 5px 0;'>{item}</li>")
        
        html_parts.append("</ul></div>")
    
    html_parts.append("</div></div>")
    
    # ==== REKOMENDASI NUTRISI ====
    nutrition = get_nutrition_phase(month)
    
    html_parts.append(f"""
    <div style='background: white; padding: 20px; border-radius: 15px; 
                margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);'>
        <h3 style='color: #bf360c; margin: 0 0 15px 0;'>🍽️ {nutrition['title']}</h3>
        <ul style='margin: 0; padding-left: 20px;'>
    """)
    
    for rec in nutrition['recommendations']:
        html_parts.append(f"<li style='margin: 8px 0; font-size: 1.05em;'>{rec}</li>")
    
    # Personalized nutrition (if z-score data available)
    if has_zscore_data and (whz < -2 or waz < -2):
        html_parts.append("""
        </ul>
        <div style='background: #fff8e1; padding: 15px; border-radius: 10px; margin-top: 15px;'>
            <h4 style='color: #f57f17; margin: 0 0 10px 0;'>⚡ Rekomendasi Tambahan (Kejar Tumbuh)</h4>
            <ul style='margin: 0; padding-left: 20px;'>
                <li>Tingkatkan frekuensi makan (5-6x/hari)</li>
                <li>Tambah protein hewani di setiap makan</li>
                <li>Makanan padat energi (alpukat, kacang)</li>
                <li>Konsultasi dokter untuk suplementasi</li>
            </ul>
        </div>
        """)
    else:
        html_parts.append("</ul>")
    
    html_parts.append("</div>")
    
    # ==== IMUNISASI ====
    imm = get_immunization_for_month(month)
    html_parts.append(generate_immunization_html(month))
    
    # ==== KPSP ====
    html_parts.append(generate_kpsp_html(month))
    
    # ==== FOOTER ====
    html_parts.append(f"""
    <div style='background: #f5f5f5; padding: 15px; border-radius: 10px; 
                margin-top: 20px; text-align: center;'>
        <p style='margin: 0; color: #666; font-size: 0.9em;'>
            📆 Checklist untuk usia {month} bulan | 
            🏥 Konsultasi ke tenaga kesehatan jika ada kekhawatiran
        </p>
    </div>
    """)
    
    return "".join(html_parts)


# ==============================================================================
# QUICK CHECKLIST (SIMPLIFIED VERSION)
# ==============================================================================

def generate_quick_checklist(month: int) -> str:
    """Generate simplified quick checklist"""
    
    milestones = get_milestone_for_month(month)
    nutrition = get_nutrition_phase(month)
    immunizations = get_immunization_for_month(month)
    
    html = f"""
    <div style='padding: 15px; background: linear-gradient(135deg, #e8f5e9, #c8e6c9); border-radius: 12px;'>
        <h3 style='margin: 0 0 15px 0; color: #2e7d32;'>✅ Quick Checklist - {month} Bulan</h3>
        
        <div style='margin-bottom: 15px;'>
            <strong>🎯 Yang Seharusnya Bisa Dilakukan:</strong>
            <ul style='margin: 5px 0; padding-left: 25px;'>
    """
    
    # Get key milestones
    for domain in ['motorik_kasar', 'bahasa']:
        if domain in milestones and milestones[domain]:
            html += f"<li>{milestones[domain][0]}</li>"
    
    html += "</ul></div>"
    
    # Nutrition highlight
    html += f"""
        <div style='margin-bottom: 15px;'>
            <strong>🍽️ Fokus Nutrisi:</strong> {nutrition['title']}
        </div>
    """
    
    # Immunization
    if immunizations:
        html += f"""
        <div style='background: #ffecb3; padding: 10px; border-radius: 8px;'>
            <strong>💉 Imunisasi Bulan Ini:</strong> {', '.join(immunizations)}
        </div>
        """
    
    html += "</div>"
    
    return html


print("✅ Checklist module loaded (independent mode)")
