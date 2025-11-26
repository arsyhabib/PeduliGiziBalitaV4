#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
#==============================================================================
#                    AnthroHPK v4.0 - PDF EXPORT MODULE
#              Export Hasil Analisis ke PDF dan CSV
#==============================================================================
"""

import os
import io
import csv
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date
import traceback

# ReportLab imports for PDF generation
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm, mm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        Image, PageBreak, HRFlowable
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️ ReportLab not available - PDF export will be disabled")

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import APP_VERSION, APP_TITLE, CONTACT_WA, OUTPUTS_DIR

# ==============================================================================
# PDF STYLES
# ==============================================================================

def get_pdf_styles():
    """Get custom PDF styles"""
    if not REPORTLAB_AVAILABLE:
        return None
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#c2185b'),
        spaceAfter=20,
        alignment=TA_CENTER
    ))
    
    styles.add(ParagraphStyle(
        name='CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#666666'),
        spaceAfter=10,
        alignment=TA_CENTER
    ))
    
    styles.add(ParagraphStyle(
        name='SectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1565c0'),
        spaceBefore=15,
        spaceAfter=10
    ))
    
    styles.add(ParagraphStyle(
        name='SubSection',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#2e7d32'),
        spaceBefore=10,
        spaceAfter=5
    ))
    
    styles.add(ParagraphStyle(
        name='BodyText',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        spaceAfter=8
    ))
    
    styles.add(ParagraphStyle(
        name='SmallText',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#888888'),
        spaceAfter=5
    ))
    
    styles.add(ParagraphStyle(
        name='AlertText',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#c62828'),
        spaceBefore=5,
        spaceAfter=5
    ))
    
    styles.add(ParagraphStyle(
        name='GoodText',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#2e7d32'),
        spaceBefore=5,
        spaceAfter=5
    ))
    
    return styles


# ==============================================================================
# PDF GENERATION FUNCTIONS
# ==============================================================================

def generate_growth_report_pdf(
    child_data: Dict,
    z_scores: Dict,
    classifications: Dict,
    recommendations: List[str] = None,
    chart_paths: List[str] = None
) -> Optional[str]:
    """
    Generate comprehensive growth assessment PDF report
    
    Args:
        child_data: {"nama": str, "tanggal_lahir": str, "jenis_kelamin": str, 
                     "usia_bulan": float, "bb": float, "tb": float, "lk": float}
        z_scores: {"waz": float, "haz": float, "whz": float, "baz": float, "hcz": float}
        classifications: {"status_gizi": str, "status_tinggi": str, etc.}
        recommendations: List of recommendation strings
        chart_paths: List of chart image file paths
        
    Returns:
        Path to generated PDF file or None if failed
    """
    if not REPORTLAB_AVAILABLE:
        print("❌ ReportLab not available")
        return None
    
    try:
        styles = get_pdf_styles()
        
        # Create output directory
        os.makedirs(OUTPUTS_DIR, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        child_name = child_data.get('nama', 'Anak').replace(' ', '_')
        filename = f"Laporan_Pertumbuhan_{child_name}_{timestamp}.pdf"
        filepath = os.path.join(OUTPUTS_DIR, filename)
        
        # Create document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Build content
        story = []
        
        # === HEADER ===
        story.append(Paragraph(f"📊 LAPORAN PEMANTAUAN PERTUMBUHAN", styles['CustomTitle']))
        story.append(Paragraph(f"{APP_TITLE} v{APP_VERSION}", styles['CustomSubtitle']))
        story.append(Paragraph(f"Tanggal: {datetime.now().strftime('%d %B %Y')}", styles['CustomSubtitle']))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e0e0e0')))
        story.append(Spacer(1, 10))
        
        # === DATA ANAK ===
        story.append(Paragraph("👶 Data Anak", styles['SectionHeader']))
        
        child_table_data = [
            ["Nama", child_data.get('nama', '-')],
            ["Tanggal Lahir", child_data.get('tanggal_lahir', '-')],
            ["Jenis Kelamin", child_data.get('jenis_kelamin', '-')],
            ["Usia", f"{child_data.get('usia_bulan', 0):.1f} bulan"],
            ["Berat Badan", f"{child_data.get('bb', 0):.2f} kg"],
            ["Tinggi/Panjang Badan", f"{child_data.get('tb', 0):.1f} cm"],
            ["Lingkar Kepala", f"{child_data.get('lk', 0):.1f} cm"]
        ]
        
        child_table = Table(child_table_data, colWidths=[5*cm, 10*cm])
        child_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f5')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0'))
        ]))
        story.append(child_table)
        story.append(Spacer(1, 15))
        
        # === Z-SCORE RESULTS ===
        story.append(Paragraph("📈 Hasil Analisis Z-Score (WHO)", styles['SectionHeader']))
        
        def format_zscore_cell(z: float) -> Tuple[str, colors.Color]:
            if z is None:
                return "-", colors.HexColor('#888888')
            if z < -3:
                return f"{z:.2f}", colors.HexColor('#b71c1c')
            elif z < -2:
                return f"{z:.2f}", colors.HexColor('#e65100')
            elif z <= 2:
                return f"{z:.2f}", colors.HexColor('#2e7d32')
            elif z <= 3:
                return f"{z:.2f}", colors.HexColor('#1565c0')
            else:
                return f"{z:.2f}", colors.HexColor('#6a1b9a')
        
        zscore_data = [
            ["Indikator", "Z-Score", "Status"]
        ]
        
        indicators = [
            ("BB/U (WAZ)", z_scores.get('waz'), classifications.get('status_bb_u', '-')),
            ("TB/U (HAZ)", z_scores.get('haz'), classifications.get('status_tb_u', '-')),
            ("BB/TB (WHZ)", z_scores.get('whz'), classifications.get('status_bb_tb', '-')),
            ("IMT/U (BAZ)", z_scores.get('baz'), classifications.get('status_imt_u', '-')),
            ("LK/U (HCZ)", z_scores.get('hcz'), classifications.get('status_lk_u', '-'))
        ]
        
        for name, z, status in indicators:
            z_text, _ = format_zscore_cell(z)
            zscore_data.append([name, z_text, status])
        
        zscore_table = Table(zscore_data, colWidths=[5*cm, 4*cm, 6*cm])
        zscore_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565c0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')])
        ]))
        story.append(zscore_table)
        story.append(Spacer(1, 15))
        
        # === INTERPRETASI ===
        story.append(Paragraph("📋 Interpretasi Hasil", styles['SectionHeader']))
        
        # Overall status
        overall_status = classifications.get('status_gizi', 'Tidak diketahui')
        if 'Buruk' in overall_status or 'Sangat' in overall_status:
            story.append(Paragraph(f"⚠️ Status Gizi: {overall_status}", styles['AlertText']))
        elif 'Kurang' in overall_status or 'Pendek' in overall_status:
            story.append(Paragraph(f"📊 Status Gizi: {overall_status}", styles['BodyText']))
        else:
            story.append(Paragraph(f"✅ Status Gizi: {overall_status}", styles['GoodText']))
        
        story.append(Spacer(1, 10))
        
        # === RECOMMENDATIONS ===
        if recommendations:
            story.append(Paragraph("💡 Rekomendasi", styles['SectionHeader']))
            for rec in recommendations:
                story.append(Paragraph(f"• {rec}", styles['BodyText']))
            story.append(Spacer(1, 10))
        
        # === CHARTS (if available) ===
        if chart_paths:
            story.append(PageBreak())
            story.append(Paragraph("📊 Grafik Pertumbuhan", styles['SectionHeader']))
            
            for chart_path in chart_paths:
                if os.path.exists(chart_path):
                    try:
                        img = Image(chart_path, width=16*cm, height=10*cm)
                        story.append(img)
                        story.append(Spacer(1, 10))
                    except Exception as e:
                        print(f"⚠️ Could not add chart {chart_path}: {e}")
        
        # === FOOTER ===
        story.append(Spacer(1, 20))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e0e0e0')))
        story.append(Paragraph(
            f"Laporan ini dibuat oleh {APP_TITLE} | Kontak: {CONTACT_WA}",
            styles['SmallText']
        ))
        story.append(Paragraph(
            "⚠️ Laporan ini bukan pengganti konsultasi medis. "
            "Selalu konsultasikan dengan tenaga kesehatan untuk evaluasi lebih lanjut.",
            styles['SmallText']
        ))
        
        # Build PDF
        doc.build(story)
        
        print(f"✅ PDF generated: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        traceback.print_exc()
        return None


def generate_checklist_pdf(
    month: int,
    child_data: Dict = None,
    checklist_items: Dict = None
) -> Optional[str]:
    """
    Generate monthly checklist PDF
    
    Args:
        month: Age in months
        child_data: Optional child information
        checklist_items: Dict with checklist sections
        
    Returns:
        Path to generated PDF file
    """
    if not REPORTLAB_AVAILABLE:
        return None
    
    try:
        styles = get_pdf_styles()
        os.makedirs(OUTPUTS_DIR, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Checklist_Bulan_{month}_{timestamp}.pdf"
        filepath = os.path.join(OUTPUTS_DIR, filename)
        
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        story = []
        
        # Header
        story.append(Paragraph(f"📋 CHECKLIST BULANAN", styles['CustomTitle']))
        story.append(Paragraph(f"Usia: {month} Bulan", styles['CustomSubtitle']))
        story.append(Paragraph(f"Tanggal: {datetime.now().strftime('%d %B %Y')}", styles['CustomSubtitle']))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e0e0e0')))
        story.append(Spacer(1, 15))
        
        if child_data:
            story.append(Paragraph(f"Nama Anak: {child_data.get('nama', '-')}", styles['BodyText']))
            story.append(Spacer(1, 10))
        
        # Checklist sections
        if checklist_items:
            for section, items in checklist_items.items():
                story.append(Paragraph(f"📌 {section}", styles['SubSection']))
                for item in items:
                    story.append(Paragraph(f"☐ {item}", styles['BodyText']))
                story.append(Spacer(1, 10))
        
        # Footer
        story.append(Spacer(1, 20))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e0e0e0')))
        story.append(Paragraph(
            f"Dibuat dengan {APP_TITLE} v{APP_VERSION}",
            styles['SmallText']
        ))
        
        doc.build(story)
        
        print(f"✅ Checklist PDF generated: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"❌ Error generating checklist PDF: {e}")
        traceback.print_exc()
        return None


# ==============================================================================
# CSV EXPORT FUNCTIONS
# ==============================================================================

def export_growth_data_csv(data_list: List[Dict], child_name: str = "Anak") -> Optional[str]:
    """
    Export growth measurement data to CSV
    
    Args:
        data_list: List of measurements [{"tanggal": str, "usia_bulan": float, "bb": float, "tb": float, "lk": float}, ...]
        child_name: Child's name for filename
        
    Returns:
        Path to generated CSV file
    """
    try:
        os.makedirs(OUTPUTS_DIR, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Data_Pertumbuhan_{child_name.replace(' ', '_')}_{timestamp}.csv"
        filepath = os.path.join(OUTPUTS_DIR, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'Tanggal Pengukuran',
                'Usia (bulan)',
                'Berat Badan (kg)',
                'Tinggi Badan (cm)',
                'Lingkar Kepala (cm)',
                'WAZ',
                'HAZ',
                'WHZ',
                'Catatan'
            ])
            
            # Data rows
            for data in data_list:
                writer.writerow([
                    data.get('tanggal', ''),
                    data.get('usia_bulan', ''),
                    data.get('bb', ''),
                    data.get('tb', ''),
                    data.get('lk', ''),
                    data.get('waz', ''),
                    data.get('haz', ''),
                    data.get('whz', ''),
                    data.get('catatan', '')
                ])
        
        print(f"✅ CSV generated: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"❌ Error generating CSV: {e}")
        traceback.print_exc()
        return None


def export_immunization_csv(immunization_data: List[Dict], child_name: str = "Anak") -> Optional[str]:
    """
    Export immunization record to CSV
    
    Args:
        immunization_data: List of immunization records
        child_name: Child's name
        
    Returns:
        Path to generated CSV file
    """
    try:
        os.makedirs(OUTPUTS_DIR, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Imunisasi_{child_name.replace(' ', '_')}_{timestamp}.csv"
        filepath = os.path.join(OUTPUTS_DIR, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            writer.writerow([
                'Usia (bulan)',
                'Nama Vaksin',
                'Status',
                'Tanggal Pemberian',
                'Catatan'
            ])
            
            for record in immunization_data:
                writer.writerow([
                    record.get('usia', ''),
                    record.get('vaksin', ''),
                    record.get('status', 'Belum'),
                    record.get('tanggal', ''),
                    record.get('catatan', '')
                ])
        
        print(f"✅ Immunization CSV generated: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"❌ Error generating CSV: {e}")
        traceback.print_exc()
        return None


# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def is_pdf_available() -> bool:
    """Check if PDF generation is available"""
    return REPORTLAB_AVAILABLE


def get_export_formats() -> List[str]:
    """Get list of available export formats"""
    formats = ["CSV"]
    if REPORTLAB_AVAILABLE:
        formats.insert(0, "PDF")
    return formats


# Alias for backward compatibility
def export_data_to_csv(data_list: List[Dict], child_name: str = "Anak") -> Optional[str]:
    """Alias for export_growth_data_csv"""
    return export_growth_data_csv(data_list, child_name)


print(f"✅ PDF Export module loaded (ReportLab: {'Available' if REPORTLAB_AVAILABLE else 'Not Available'})")
