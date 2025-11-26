#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
#==============================================================================
#                    AnthroHPK v4.0 - KPSP DATA
#           Kuesioner Pra Skrining Perkembangan (Depkes/Kemenkes RI)
#==============================================================================
"""

from typing import List, Optional, Dict

# ==============================================================================
# KPSP QUESTIONS BY AGE
# ==============================================================================

KPSP_QUESTIONS = {
    3: {
        "age_label": "3 bulan",
        "domain_focus": ["Motorik Kasar", "Bahasa", "Sosialisasi"],
        "questions": [
            {
                "id": "3-1",
                "domain": "Motorik Kasar",
                "question": "Apakah anak dapat mengangkat kepalanya 45° saat tengkurap?",
                "how_to_test": "Letakkan bayi tengkurap, amati apakah ia mengangkat kepala",
                "normal_response": "Bayi dapat mengangkat kepala minimal 45° dari alas"
            },
            {
                "id": "3-2",
                "domain": "Sosialisasi",
                "question": "Apakah anak tersenyum saat diajak bicara atau tersenyum sendiri?",
                "how_to_test": "Ajak bayi berbicara atau tersenyum",
                "normal_response": "Bayi tersenyum sebagai respon sosial"
            },
            {
                "id": "3-3",
                "domain": "Bahasa",
                "question": "Apakah anak mengeluarkan suara-suara (mengoceh)?",
                "how_to_test": "Dengarkan apakah bayi mengeluarkan suara vokal",
                "normal_response": "Bayi mengeluarkan suara 'aaa', 'uuu', dll"
            },
            {
                "id": "3-4",
                "domain": "Motorik Halus",
                "question": "Apakah anak dapat menatap dan mengikuti wajah ibu/pengasuh?",
                "how_to_test": "Gerakkan wajah Anda perlahan dari kiri ke kanan",
                "normal_response": "Mata bayi mengikuti gerakan wajah"
            },
            {
                "id": "3-5",
                "domain": "Motorik Halus",
                "question": "Apakah anak berusaha meraih benda atau mainan yang ditunjukkan?",
                "how_to_test": "Tunjukkan mainan berwarna cerah di depan bayi",
                "normal_response": "Bayi berusaha mengulurkan tangan ke arah mainan"
            }
        ]
    },
    6: {
        "age_label": "6 bulan",
        "domain_focus": ["Motorik Kasar", "Motorik Halus", "Bahasa"],
        "questions": [
            {
                "id": "6-1",
                "domain": "Motorik Kasar",
                "question": "Apakah anak dapat duduk dengan bantuan (bersandar)?",
                "how_to_test": "Dudukkan bayi dengan bantuan bantal atau sandaran",
                "normal_response": "Bayi dapat mempertahankan posisi duduk dengan bantuan"
            },
            {
                "id": "6-2",
                "domain": "Motorik Halus",
                "question": "Apakah anak dapat memindahkan mainan dari tangan satu ke tangan lain?",
                "how_to_test": "Berikan mainan kecil ke satu tangan bayi",
                "normal_response": "Bayi memindahkan mainan ke tangan lainnya"
            },
            {
                "id": "6-3",
                "domain": "Bahasa",
                "question": "Apakah anak mengeluarkan suara vokal seperti 'a-u-o'?",
                "how_to_test": "Ajak bayi 'berbicara', amati vokalisasinya",
                "normal_response": "Bayi menghasilkan variasi suara vokal"
            },
            {
                "id": "6-4",
                "domain": "Sosialisasi",
                "question": "Apakah anak tertawa keras saat bermain atau diajak bercanda?",
                "how_to_test": "Bermain cilukba atau menggelitik ringan",
                "normal_response": "Bayi tertawa dengan suara keras"
            },
            {
                "id": "6-5",
                "domain": "Sosialisasi",
                "question": "Apakah anak mengenal orang asing (tampak malu atau marah)?",
                "how_to_test": "Perhatikan reaksi bayi saat bertemu orang baru",
                "normal_response": "Bayi menunjukkan reaksi berbeda terhadap orang asing"
            }
        ]
    },
    9: {
        "age_label": "9 bulan",
        "domain_focus": ["Motorik Kasar", "Motorik Halus", "Bahasa"],
        "questions": [
            {
                "id": "9-1",
                "domain": "Motorik Kasar",
                "question": "Apakah anak dapat duduk sendiri tanpa bantuan minimal 1 menit?",
                "how_to_test": "Dudukkan bayi tanpa sandaran, amati keseimbangan",
                "normal_response": "Bayi duduk stabil minimal 1 menit"
            },
            {
                "id": "9-2",
                "domain": "Motorik Kasar",
                "question": "Apakah anak dapat merangkak maju (bukan mundur)?",
                "how_to_test": "Letakkan mainan di depan bayi saat tengkurap",
                "normal_response": "Bayi merangkak maju menuju mainan"
            },
            {
                "id": "9-3",
                "domain": "Bahasa",
                "question": "Apakah anak mengucapkan 'mama' atau 'papa' (meski berlebihan)?",
                "how_to_test": "Dengarkan vokalisasi bayi sepanjang hari",
                "normal_response": "Bayi mengucapkan suku kata berulang seperti ma-ma, pa-pa"
            },
            {
                "id": "9-4",
                "domain": "Motorik Halus",
                "question": "Apakah anak dapat meraih benda kecil dengan jempol dan telunjuk?",
                "how_to_test": "Letakkan benda kecil (seperti kismis) di depan bayi",
                "normal_response": "Bayi mengambil dengan pincer grasp"
            },
            {
                "id": "9-5",
                "domain": "Sosialisasi",
                "question": "Apakah anak dapat menirukan gerakan tepuk tangan?",
                "how_to_test": "Tepuk tangan di depan bayi, ajak menirukan",
                "normal_response": "Bayi mencoba menirukan gerakan tepuk tangan"
            }
        ]
    },
    12: {
        "age_label": "12 bulan",
        "domain_focus": ["Motorik Kasar", "Bahasa", "Kemandirian"],
        "questions": [
            {
                "id": "12-1",
                "domain": "Motorik Kasar",
                "question": "Apakah anak dapat berdiri sendiri minimal 5 detik tanpa berpegangan?",
                "how_to_test": "Bantu anak berdiri lalu lepaskan pegangan",
                "normal_response": "Anak berdiri seimbang minimal 5 detik"
            },
            {
                "id": "12-2",
                "domain": "Motorik Kasar",
                "question": "Apakah anak dapat berjalan berpegangan pada furniture?",
                "how_to_test": "Amati anak berjalan menyusuri sofa/meja",
                "normal_response": "Anak berjalan sambil berpegangan (cruising)"
            },
            {
                "id": "12-3",
                "domain": "Bahasa",
                "question": "Apakah anak dapat mengucapkan 2-3 kata yang bermakna?",
                "how_to_test": "Catat kata-kata yang diucapkan dengan makna",
                "normal_response": "Anak mengucapkan kata seperti mama, papa, susu"
            },
            {
                "id": "12-4",
                "domain": "Kemandirian",
                "question": "Apakah anak dapat minum dari cangkir sendiri?",
                "how_to_test": "Berikan cangkir/sippy cup berisi air",
                "normal_response": "Anak memegang dan minum sendiri"
            },
            {
                "id": "12-5",
                "domain": "Bahasa",
                "question": "Apakah anak dapat menunjuk benda yang diinginkannya?",
                "how_to_test": "Perhatikan cara anak berkomunikasi",
                "normal_response": "Anak menunjuk dengan jari telunjuk"
            }
        ]
    },
    15: {
        "age_label": "15 bulan",
        "domain_focus": ["Motorik Kasar", "Bahasa", "Motorik Halus"],
        "questions": [
            {
                "id": "15-1",
                "domain": "Motorik Kasar",
                "question": "Apakah anak dapat berjalan sendiri dengan stabil minimal 5 langkah?",
                "how_to_test": "Minta anak berjalan ke arah Anda",
                "normal_response": "Anak berjalan tanpa berpegangan minimal 5 langkah"
            },
            {
                "id": "15-2",
                "domain": "Kemandirian",
                "question": "Apakah anak dapat minum dari gelas tanpa tumpah?",
                "how_to_test": "Berikan gelas dengan sedikit air",
                "normal_response": "Anak minum tanpa banyak tumpah"
            },
            {
                "id": "15-3",
                "domain": "Bahasa",
                "question": "Apakah anak dapat mengucapkan 4-6 kata dengan jelas?",
                "how_to_test": "Catat kata-kata yang diucapkan anak",
                "normal_response": "Minimal 4 kata yang dapat dimengerti"
            },
            {
                "id": "15-4",
                "domain": "Motorik Halus",
                "question": "Apakah anak dapat menumpuk 2 kubus dengan stabil?",
                "how_to_test": "Berikan kubus/balok, contohkan cara menumpuk",
                "normal_response": "Anak menumpuk 2 kubus tanpa jatuh"
            },
            {
                "id": "15-5",
                "domain": "Kemandirian",
                "question": "Apakah anak dapat membantu melepas sepatunya sendiri?",
                "how_to_test": "Longgarkan sepatu, minta anak melepas",
                "normal_response": "Anak membantu proses melepas sepatu"
            }
        ]
    },
    18: {
        "age_label": "18 bulan",
        "domain_focus": ["Motorik Kasar", "Bahasa", "Kemandirian"],
        "questions": [
            {
                "id": "18-1",
                "domain": "Motorik Kasar",
                "question": "Apakah anak dapat berlari minimal 5 langkah berturut-turut?",
                "how_to_test": "Ajak anak bermain kejar-kejaran",
                "normal_response": "Anak berlari beberapa langkah"
            },
            {
                "id": "18-2",
                "domain": "Motorik Kasar",
                "question": "Apakah anak dapat naik tangga dengan bantuan pegangan?",
                "how_to_test": "Temani anak naik tangga sambil berpegangan",
                "normal_response": "Anak naik tangga dengan pegangan"
            },
            {
                "id": "18-3",
                "domain": "Bahasa",
                "question": "Apakah anak dapat mengucapkan 10-15 kata yang berbeda?",
                "how_to_test": "Catat semua kata yang diucapkan anak",
                "normal_response": "Minimal 10 kata bermakna"
            },
            {
                "id": "18-4",
                "domain": "Kemandirian",
                "question": "Apakah anak dapat makan sendiri dengan sendok?",
                "how_to_test": "Berikan sendok dan makanan lunak",
                "normal_response": "Anak menyendok dan memasukkan ke mulut"
            },
            {
                "id": "18-5",
                "domain": "Bahasa",
                "question": "Apakah anak dapat menunjuk minimal 2 bagian tubuhnya?",
                "how_to_test": "Tanya 'mana hidung?', 'mana mata?'",
                "normal_response": "Anak menunjuk dengan benar minimal 2 bagian"
            }
        ]
    },
    21: {
        "age_label": "21 bulan",
        "domain_focus": ["Motorik Kasar", "Bahasa", "Kognitif"],
        "questions": [
            {
                "id": "21-1",
                "domain": "Motorik Kasar",
                "question": "Apakah anak dapat menendang bola ke depan tanpa jatuh?",
                "how_to_test": "Letakkan bola di depan anak",
                "normal_response": "Anak menendang dengan keseimbangan"
            },
            {
                "id": "21-2",
                "domain": "Motorik Kasar",
                "question": "Apakah anak dapat naik tangga dengan 1 kaki bergantian?",
                "how_to_test": "Amati cara anak naik tangga",
                "normal_response": "Anak bergantian kaki (bukan 2 kaki per anak tangga)"
            },
            {
                "id": "21-3",
                "domain": "Bahasa",
                "question": "Apakah anak dapat mengucapkan kalimat 2-3 kata?",
                "how_to_test": "Dengarkan ucapan anak sehari-hari",
                "normal_response": "Contoh: 'mau susu', 'mama pergi'"
            },
            {
                "id": "21-4",
                "domain": "Motorik Halus",
                "question": "Apakah anak dapat membalik halaman buku satu per satu?",
                "how_to_test": "Berikan buku bergambar dengan halaman tebal",
                "normal_response": "Anak membalik satu halaman dalam sekali waktu"
            },
            {
                "id": "21-5",
                "domain": "Kognitif",
                "question": "Apakah anak dapat mengikuti perintah sederhana 2 tahap?",
                "how_to_test": "Contoh: 'Ambil bola, berikan ke mama'",
                "normal_response": "Anak melakukan kedua instruksi berurutan"
            }
        ]
    },
    24: {
        "age_label": "24 bulan",
        "domain_focus": ["Motorik Kasar", "Bahasa", "Kognitif"],
        "questions": [
            {
                "id": "24-1",
                "domain": "Motorik Kasar",
                "question": "Apakah anak dapat melompat dengan 2 kaki bersamaan?",
                "how_to_test": "Contohkan gerakan melompat",
                "normal_response": "Kedua kaki terangkat dari tanah bersamaan"
            },
            {
                "id": "24-2",
                "domain": "Motorik Kasar",
                "question": "Apakah anak dapat naik-turun tangga tanpa pegangan?",
                "how_to_test": "Amati anak naik turun tangga (dengan pengawasan)",
                "normal_response": "Anak berjalan naik/turun tanpa berpegangan"
            },
            {
                "id": "24-3",
                "domain": "Bahasa",
                "question": "Apakah anak dapat membuat kalimat 3-4 kata yang runtut?",
                "how_to_test": "Dengarkan percakapan anak",
                "normal_response": "Contoh: 'Aku mau makan nasi'"
            },
            {
                "id": "24-4",
                "domain": "Motorik Halus",
                "question": "Apakah anak dapat menggambar garis vertikal setelah dicontohkan?",
                "how_to_test": "Gambar garis vertikal, minta anak meniru",
                "normal_response": "Anak menggambar garis dari atas ke bawah"
            },
            {
                "id": "24-5",
                "domain": "Kognitif",
                "question": "Apakah anak dapat mengikuti perintah kompleks 3 tahap?",
                "how_to_test": "'Ambil buku, letakkan di meja, duduk di kursi'",
                "normal_response": "Anak melakukan ketiga instruksi berurutan"
            }
        ]
    }
}


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def get_kpsp_questions_for_month(month: int) -> List[str]:
    """
    Get KPSP questions for specific month
    
    Args:
        month: Age in months
        
    Returns:
        List of question strings, empty if no KPSP for this age
    """
    # Find nearest KPSP age (3, 6, 9, 12, 15, 18, 21, 24)
    kpsp_ages = sorted(KPSP_QUESTIONS.keys())
    
    nearest_age = None
    for age in kpsp_ages:
        if month >= age:
            nearest_age = age
        else:
            break
    
    if nearest_age is None or nearest_age not in KPSP_QUESTIONS:
        return []
    
    return [q["question"] for q in KPSP_QUESTIONS[nearest_age]["questions"]]


def get_kpsp_full_for_month(month: int) -> Optional[Dict]:
    """
    Get full KPSP data for specific month
    
    Args:
        month: Age in months
        
    Returns:
        Dictionary with full KPSP data or None
    """
    kpsp_ages = sorted(KPSP_QUESTIONS.keys())
    
    nearest_age = None
    for age in kpsp_ages:
        if month >= age:
            nearest_age = age
    
    if nearest_age is None or nearest_age not in KPSP_QUESTIONS:
        return None
    
    return KPSP_QUESTIONS[nearest_age]


def interpret_kpsp_result(yes_count: int, total: int = 5) -> Dict:
    """
    Interpret KPSP screening result
    
    Args:
        yes_count: Number of "Yes" answers
        total: Total number of questions (default 5)
        
    Returns:
        Dictionary with interpretation
    """
    no_count = total - yes_count
    
    if no_count == 0:
        return {
            "status": "Sesuai",
            "color": "#28a745",
            "emoji": "✅",
            "recommendation": "Perkembangan anak sesuai dengan usianya. Lanjutkan stimulasi dan pemantauan rutin.",
            "action": "Lakukan KPSP ulang sesuai jadwal usia berikutnya."
        }
    elif no_count == 1:
        return {
            "status": "Meragukan",
            "color": "#ffc107",
            "emoji": "⚠️",
            "recommendation": "Ada 1 aspek perkembangan yang perlu perhatian. Lakukan stimulasi lebih intensif pada area tersebut.",
            "action": "Ulangi KPSP dalam 2 minggu. Jika masih ada jawaban 'Tidak', konsultasi ke tenaga kesehatan."
        }
    else:  # no_count >= 2
        return {
            "status": "Kemungkinan Penyimpangan",
            "color": "#dc3545",
            "emoji": "🚨",
            "recommendation": "Terdeteksi kemungkinan keterlambatan perkembangan. Segera lakukan pemeriksaan lebih lanjut.",
            "action": "SEGERA rujuk ke dokter anak atau klinik tumbuh kembang untuk evaluasi menyeluruh."
        }


def generate_kpsp_html(month: int, answers: List[bool] = None) -> str:
    """
    Generate HTML for KPSP display
    
    Args:
        month: Age in months
        answers: List of boolean answers (True=Yes, False=No), optional
        
    Returns:
        HTML string for display
    """
    kpsp_data = get_kpsp_full_for_month(month)
    
    if not kpsp_data:
        return """
        <div style="padding: 15px; background: #f8f9fa; border-radius: 10px;">
            <p>Tidak ada KPSP untuk usia ini. KPSP dilakukan pada usia 3, 6, 9, 12, 15, 18, 21, dan 24 bulan.</p>
        </div>
        """
    
    html = f"""
    <div style="padding: 20px; background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%); 
                border-radius: 15px; margin: 10px 0;">
        <h3 style="color: #2c3e50; margin: 0 0 15px 0;">
            🧠 Skrining KPSP - {kpsp_data['age_label']}
        </h3>
        <p style="color: #666; margin-bottom: 15px;">
            <strong>Domain yang dinilai:</strong> {', '.join(kpsp_data['domain_focus'])}
        </p>
        <p style="color: #888; font-size: 0.9em; margin-bottom: 15px;">
            Jawab YA atau TIDAK untuk setiap pertanyaan berikut:
        </p>
        <ol style="padding-left: 20px;">
    """
    
    for i, q in enumerate(kpsp_data["questions"]):
        answer_indicator = ""
        if answers and i < len(answers):
            if answers[i]:
                answer_indicator = '<span style="color: #28a745; font-weight: bold;"> ✓ YA</span>'
            else:
                answer_indicator = '<span style="color: #dc3545; font-weight: bold;"> ✗ TIDAK</span>'
        
        html += f"""
            <li style="margin: 10px 0; padding: 10px; background: white; border-radius: 8px; 
                       box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <strong style="color: #34495e;">{q['question']}</strong>{answer_indicator}
                <br>
                <small style="color: #7f8c8d;">
                    📋 <em>Cara uji: {q['how_to_test']}</em>
                </small>
            </li>
        """
    
    html += """
        </ol>
        <div style="margin-top: 15px; padding: 10px; background: #fff3cd; border-radius: 8px;">
            <p style="margin: 0; color: #856404;">
                <strong>📌 Interpretasi:</strong> Jika ada ≥2 jawaban TIDAK, segera konsultasi ke tenaga kesehatan.
            </p>
        </div>
    </div>
    """
    
    return html


print("✅ KPSP data loaded")
