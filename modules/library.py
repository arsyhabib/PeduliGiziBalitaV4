#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
#==============================================================================
#                    AnthroHPK v4.0 - LIBRARY MODULE
#              Perpustakaan Ibu Balita - 40+ Artikel Edukasi
#==============================================================================
"""

from typing import Dict, List, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.articles import (
    ARTIKEL_DATABASE,
    ARTICLE_CATEGORIES,
    get_article_by_id,
    search_articles,
    get_articles_by_category,
    get_categories,
    format_article_content
)

# ==============================================================================
# HTML GENERATORS FOR LIBRARY
# ==============================================================================

def generate_library_home_html() -> str:
    """Generate library homepage HTML with categories"""
    
    html = """
    <div style='background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
                padding: 25px; border-radius: 20px; margin-bottom: 20px;'>
        <h2 style='color: #2e7d32; margin: 0 0 10px 0;'>📚 Perpustakaan Ibu Balita</h2>
        <p style='color: #1b5e20; margin: 0; font-size: 1.1em;'>
            Koleksi artikel edukasi untuk mendukung tumbuh kembang optimal si kecil
        </p>
    </div>
    
    <!-- Category Cards -->
    <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px;'>
    """
    
    category_icons = {
        "Gizi & Stunting": "🥗",
        "Nutrisi & MPASI": "🍽️",
        "Tumbuh Kembang": "📈",
        "Kesehatan Ibu": "🤰",
        "Imunisasi": "💉",
        "ASI & Menyusui": "🤱",
        "Perkembangan Anak": "🧒",
        "Tips Parenting": "👨‍👩‍👧"
    }
    
    category_colors = {
        "Gizi & Stunting": "#e8f5e9",
        "Nutrisi & MPASI": "#fff3e0",
        "Tumbuh Kembang": "#e3f2fd",
        "Kesehatan Ibu": "#fce4ec",
        "Imunisasi": "#f3e5f5",
        "ASI & Menyusui": "#e0f7fa",
        "Perkembangan Anak": "#fff8e1",
        "Tips Parenting": "#f1f8e9"
    }
    
    for category in ARTICLE_CATEGORIES:
        icon = category_icons.get(category, "📖")
        bg_color = category_colors.get(category, "#f5f5f5")
        article_count = len(get_articles_by_category(category))
        
        html += f"""
        <div style='background: {bg_color}; padding: 20px; border-radius: 15px;
                    text-align: center; cursor: pointer; transition: transform 0.2s;'
             onmouseover="this.style.transform='scale(1.02)'"
             onmouseout="this.style.transform='scale(1)'">
            <div style='font-size: 2.5em; margin-bottom: 10px;'>{icon}</div>
            <h4 style='color: #333; margin: 0 0 5px 0;'>{category}</h4>
            <p style='color: #666; margin: 0; font-size: 0.9em;'>{article_count} artikel</p>
        </div>
        """
    
    html += "</div>"
    
    # Latest Articles
    html += """
    <div style='background: white; padding: 20px; border-radius: 15px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);'>
        <h3 style='color: #1565c0; margin: 0 0 15px 0;'>📰 Artikel Terbaru</h3>
        <div style='display: grid; gap: 15px;'>
    """
    
    # Show first 5 articles
    for article in ARTIKEL_DATABASE[:5]:
        html += generate_article_card_html(article)
    
    html += "</div></div>"
    
    return html


def generate_article_card_html(article: Dict) -> str:
    """Generate HTML card for single article"""
    
    return f"""
    <div style='display: flex; gap: 15px; padding: 15px; background: #fafafa;
                border-radius: 12px; align-items: center;'>
        <img src='{article.get("image_url", "")}' 
             style='width: 100px; height: 80px; object-fit: cover; border-radius: 8px;'
             alt='{article["title"]}'
             onerror="this.src='https://images.pexels.com/photos/3845126/pexels-photo-3845126.jpeg?auto=compress&cs=tinysrgb&w=100'">
        <div style='flex: 1;'>
            <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 5px;'>
                <span style='background: #e3f2fd; color: #1565c0; padding: 2px 8px;
                             border-radius: 4px; font-size: 0.75em;'>
                    {article.get("kategori", "Umum")}
                </span>
            </div>
            <h4 style='margin: 0 0 5px 0; color: #333;'>{article["title"]}</h4>
            <p style='margin: 0; color: #666; font-size: 0.9em; 
                      display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
                      overflow: hidden;'>
                {article.get("summary", "")}
            </p>
            <p style='margin: 5px 0 0 0; color: #888; font-size: 0.8em;'>
                📎 {article.get("source", "AnthroHPK")}
            </p>
        </div>
    </div>
    """


def generate_article_list_html(category: str = "", query: str = "") -> str:
    """Generate article list HTML with optional filtering"""
    
    # Get filtered articles
    articles = search_articles(query=query, category=category)
    
    if not articles:
        return """
        <div style='padding: 40px; text-align: center; background: #f5f5f5; border-radius: 15px;'>
            <div style='font-size: 3em; margin-bottom: 15px;'>🔍</div>
            <h3 style='color: #666; margin: 0 0 10px 0;'>Tidak ada artikel ditemukan</h3>
            <p style='color: #888; margin: 0;'>Coba kata kunci lain atau pilih kategori berbeda</p>
        </div>
        """
    
    title = f"Kategori: {category}" if category and category != "Semua Kategori" else "Semua Artikel"
    if query:
        title = f"Hasil pencarian: '{query}'"
    
    html = f"""
    <div style='background: #e8f5e9; padding: 15px; border-radius: 10px; margin-bottom: 15px;'>
        <h3 style='color: #2e7d32; margin: 0;'>📚 {title}</h3>
        <p style='color: #388e3c; margin: 5px 0 0 0;'>{len(articles)} artikel ditemukan</p>
    </div>
    <div style='display: grid; gap: 15px;'>
    """
    
    for article in articles:
        html += generate_article_card_html(article)
    
    html += "</div>"
    
    return html


def generate_article_full_html(article_id: int) -> str:
    """Generate full article HTML"""
    
    article = get_article_by_id(article_id)
    
    if not article:
        return """
        <div style='padding: 40px; text-align: center; background: #ffebee; border-radius: 15px;'>
            <div style='font-size: 3em; margin-bottom: 15px;'>❌</div>
            <h3 style='color: #c62828; margin: 0;'>Artikel tidak ditemukan</h3>
        </div>
        """
    
    content_html = format_article_content(article.get("full_content", ""))
    
    html = f"""
    <!-- Article Header -->
    <div style='position: relative; margin-bottom: 20px;'>
        <img src='{article.get("image_url", "")}' 
             style='width: 100%; height: 200px; object-fit: cover; border-radius: 15px;'
             alt='{article["title"]}'
             onerror="this.src='https://images.pexels.com/photos/3845126/pexels-photo-3845126.jpeg?auto=compress&cs=tinysrgb&w=800'">
        <div style='position: absolute; bottom: 0; left: 0; right: 0; 
                    background: linear-gradient(transparent, rgba(0,0,0,0.8));
                    padding: 20px; border-radius: 0 0 15px 15px;'>
            <span style='background: #4CAF50; color: white; padding: 4px 12px;
                         border-radius: 20px; font-size: 0.8em;'>
                {article.get("kategori", "Umum")}
            </span>
            <h2 style='color: white; margin: 10px 0 5px 0;'>{article["title"]}</h2>
            <p style='color: #ddd; margin: 0; font-size: 0.9em;'>
                📎 Sumber: {article.get("source", "AnthroHPK")}
            </p>
        </div>
    </div>
    
    <!-- Article Content -->
    <div style='background: white; padding: 25px; border-radius: 15px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                line-height: 1.8; color: #333;'>
        {content_html}
    </div>
    
    <!-- Share & Actions -->
    <div style='display: flex; gap: 10px; margin-top: 15px; justify-content: center;'>
        <button style='background: #25D366; color: white; border: none; padding: 10px 20px;
                       border-radius: 8px; cursor: pointer; font-weight: bold;'>
            📲 Bagikan via WhatsApp
        </button>
        <button style='background: #1877F2; color: white; border: none; padding: 10px 20px;
                       border-radius: 8px; cursor: pointer; font-weight: bold;'>
            📘 Bagikan via Facebook
        </button>
    </div>
    """
    
    return html


def generate_library_search_html(query: str, category: str = "") -> str:
    """Generate search results HTML"""
    
    articles = search_articles(query=query, category=category)
    
    html = f"""
    <div style='background: #e3f2fd; padding: 15px; border-radius: 10px; margin-bottom: 15px;'>
        <h3 style='color: #1565c0; margin: 0;'>🔍 Hasil Pencarian</h3>
        <p style='color: #1976d2; margin: 5px 0 0 0;'>
            Ditemukan {len(articles)} artikel untuk "{query}"
            {f' dalam kategori "{category}"' if category and category != "Semua Kategori" else ''}
        </p>
    </div>
    """
    
    if articles:
        html += "<div style='display: grid; gap: 15px;'>"
        for article in articles:
            html += generate_article_card_html(article)
        html += "</div>"
    else:
        html += """
        <div style='padding: 30px; text-align: center; background: #f5f5f5; border-radius: 15px;'>
            <p style='color: #666; margin: 0;'>Tidak ada artikel yang cocok dengan pencarian Anda.</p>
            <p style='color: #888; margin: 10px 0 0 0; font-size: 0.9em;'>
                Tips: Coba kata kunci yang lebih umum atau periksa ejaan
            </p>
        </div>
        """
    
    return html


# ==============================================================================
# CATEGORY DROPDOWN OPTIONS
# ==============================================================================

def get_category_dropdown_options() -> List[str]:
    """Get list of categories for dropdown"""
    return ["Semua Kategori"] + ARTICLE_CATEGORIES


# ==============================================================================
# ARTICLE COUNT FUNCTIONS
# ==============================================================================

def get_total_articles() -> int:
    """Get total number of articles"""
    return len(ARTIKEL_DATABASE)


def get_category_counts() -> Dict[str, int]:
    """Get article count per category"""
    counts = {}
    for category in ARTICLE_CATEGORIES:
        counts[category] = len(get_articles_by_category(category))
    return counts


# ==============================================================================
# MAIN HANDLER FUNCTIONS (untuk app.py)
# ==============================================================================

def generate_library_html(kategori: str = "", search_query: str = "") -> str:
    """
    Main handler for library display
    
    Args:
        kategori: Category filter (or "Semua Kategori")
        search_query: Search term
        
    Returns:
        HTML string
    """
    # If both empty, show home
    if not kategori or kategori == "Semua Kategori":
        if not search_query:
            return generate_library_home_html()
    
    # If search query provided
    if search_query:
        return generate_library_search_html(search_query, kategori)
    
    # If category provided
    return generate_article_list_html(category=kategori, query="")


def get_article_html(article_id: int) -> str:
    """
    Get full article HTML
    
    Args:
        article_id: Article ID
        
    Returns:
        HTML string
    """
    return generate_article_full_html(article_id)


print(f"✅ Library module loaded: {get_total_articles()} articles available")
