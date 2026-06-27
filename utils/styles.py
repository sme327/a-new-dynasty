"""CSS injection and reusable HTML components."""
import streamlit as st
from utils.data import MANAGER_EMOJI


_CSS = """
        /* ── Dynasty Green · A New Dynasty ─────────────────────────────────── */
        .stApp { background-color: #07120D !important; }
        .main  { background-color: #07120D !important; }
        #MainMenu { visibility: hidden; }
        footer    { visibility: hidden; }
        header    { visibility: hidden; }
        [data-testid="stSidebar"]        { display: none !important; }
        [data-testid="collapsedControl"] { display: none !important; }
        .main .block-container {
            padding-top: 80px !important;
            padding-left: 2.5rem !important;
            padding-right: 2.5rem !important;
            max-width: 1280px;
        }
        .tl-nav {
            position: fixed;
            top: 0; left: 0; right: 0;
            z-index: 9999;
            background: #07120D;
            border-bottom: 1px solid rgba(212,175,55,0.35);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 2.5rem;
            height: 62px;
        }
        .tl-nav-brand {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 1.35rem;
            color: #D4AF37;
            letter-spacing: 5px;
            text-decoration: none !important;
        }
        .tl-nav-links { display: flex; gap: 1rem; align-items: center; flex-wrap: nowrap; }
        .tl-nav-link {
            font-family: 'Inter', sans-serif;
            font-size: 0.62rem;
            font-weight: 500;
            color: #B8C3B5;
            text-decoration: none !important;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            padding: 4px 0;
            border-bottom: 2px solid transparent;
            transition: color 0.2s, border-color 0.2s;
            white-space: nowrap;
        }
        .tl-nav-link:hover { color: #3FA66B; border-bottom-color: #3FA66B; }
        .tl-nav-link.active { color: #D4AF37; border-bottom-color: #D4AF37; }
        .tl-hero { text-align: center; padding: 2.5rem 0 1.5rem; }
        .tl-hero-title {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 5rem;
            color: #D4AF37;
            letter-spacing: 10px;
            line-height: 1;
            margin: 0;
        }
        .tl-hero-subtitle {
            font-family: 'Inter', sans-serif;
            font-size: 0.78rem;
            color: #B8C3B5;
            letter-spacing: 6px;
            text-transform: uppercase;
            margin-top: 0.5rem;
        }
        .tl-page-title {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 3.2rem;
            color: #D4AF37;
            letter-spacing: 6px;
            line-height: 1;
            margin: 0;
        }
        .tl-page-subtitle {
            font-family: 'Inter', sans-serif;
            font-size: 0.72rem;
            color: #B8C3B5;
            letter-spacing: 3px;
            text-transform: uppercase;
            margin-top: 0.3rem;
            margin-bottom: 1.5rem;
        }
        .tl-divider {
            height: 1px;
            background: linear-gradient(to right, transparent, #D4AF37, transparent);
            margin: 1.5rem auto;
            border: none;
        }
        .tl-divider-full {
            height: 1px;
            background: linear-gradient(to right, rgba(46,139,87,0.4), rgba(212,175,55,0.3), rgba(46,139,87,0.4));
            margin: 1.5rem 0;
            border: none;
        }
        .tl-section-label {
            font-family: 'Inter', sans-serif;
            font-size: 0.65rem;
            color: #3FA66B;
            letter-spacing: 4px;
            text-transform: uppercase;
            margin-bottom: 0.25rem;
        }
        .tl-section-title {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 1.8rem;
            color: #F5F3EA;
            letter-spacing: 3px;
            margin: 0 0 1rem 0;
        }
        .tl-metric {
            background: #102418;
            border: 1px solid rgba(212,175,55,0.3);
            border-radius: 8px;
            padding: 1.4rem 1rem;
            text-align: center;
            box-shadow: 0 0 20px rgba(46,139,87,0.08);
        }
        .tl-metric-value {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 3.2rem;
            color: #D4AF37;
            line-height: 1;
            margin: 0;
        }
        .tl-metric-label {
            font-family: 'Inter', sans-serif;
            font-size: 0.62rem;
            color: #B8C3B5;
            letter-spacing: 3px;
            text-transform: uppercase;
            margin-top: 0.4rem;
        }
        .tl-card {
            background: #102418;
            border: 1px solid rgba(46,139,87,0.4);
            border-radius: 8px;
            padding: 1.5rem;
        }
        .tl-card-gold {
            background: #102418;
            border: 1px solid #D4AF37;
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 0 30px rgba(212,175,55,0.08), 0 0 60px rgba(46,139,87,0.06);
        }
        .tl-champion-card {
            background: #102418;
            border: 2px solid #D4AF37;
            border-radius: 12px;
            padding: 2.5rem 2rem;
            text-align: center;
            box-shadow: 0 0 60px rgba(212,175,55,0.12), 0 0 120px rgba(46,139,87,0.10);
        }
        .tl-champion-season {
            font-family: 'Inter', sans-serif;
            font-size: 0.7rem;
            color: #B8C3B5;
            letter-spacing: 4px;
            text-transform: uppercase;
        }
        .tl-champion-team {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 3.2rem;
            color: #D4AF37;
            letter-spacing: 4px;
            line-height: 1;
            margin: 0.4rem 0 0.2rem;
        }
        .tl-champion-manager {
            font-family: 'Inter', sans-serif;
            font-size: 1rem;
            color: #F5F3EA;
            font-weight: 500;
        }
        .tl-champion-score {
            font-family: 'Inter', sans-serif;
            font-size: 0.8rem;
            color: #B8C3B5;
            margin-top: 0.75rem;
        }
        .tl-mini-champ {
            background: #102418;
            border: 1px solid rgba(212,175,55,0.3);
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
        }
        .tl-mini-champ-year {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 1.4rem;
            color: #D4AF37;
            letter-spacing: 2px;
            line-height: 1;
        }
        .tl-mini-champ-team {
            font-family: 'Inter', sans-serif;
            font-size: 0.78rem;
            color: #F5F3EA;
            font-weight: 500;
            margin-top: 0.3rem;
        }
        .tl-mini-champ-mgr {
            font-family: 'Inter', sans-serif;
            font-size: 0.68rem;
            color: #B8C3B5;
            margin-top: 0.1rem;
        }
        .tl-nav-card {
            background: #102418;
            border: 1px solid rgba(46,139,87,0.4);
            border-radius: 8px;
            padding: 1.5rem;
            text-align: center;
            text-decoration: none !important;
            display: block;
            transition: border-color 0.2s, box-shadow 0.2s, transform 0.2s;
        }
        .tl-nav-card:hover {
            border-color: #D4AF37;
            box-shadow: 0 0 24px rgba(46,139,87,0.18), 0 0 8px rgba(212,175,55,0.10);
            transform: translateY(-2px);
        }
        .tl-nav-card-icon { font-size: 2rem; margin-bottom: 0.5rem; }
        .tl-nav-card-title {
            font-family: 'Oswald', sans-serif;
            font-size: 0.95rem;
            color: #D4AF37;
            letter-spacing: 2px;
            text-transform: uppercase;
        }
        .tl-nav-card-desc {
            font-family: 'Inter', sans-serif;
            font-size: 0.72rem;
            color: #B8C3B5;
            margin-top: 0.3rem;
            line-height: 1.4;
        }
        .tl-trophy-card {
            background: #102418;
            border: 1px solid rgba(46,139,87,0.4);
            border-radius: 8px;
            padding: 1.2rem 1.5rem;
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        .tl-trophy-card.gold-border { border-color: #D4AF37; }
        .tl-trophy-count {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 2.8rem;
            color: #D4AF37;
            line-height: 1;
            min-width: 2rem;
            text-align: center;
        }
        .tl-trophy-name {
            font-family: 'Inter', sans-serif;
            font-size: 1rem;
            color: #F5F3EA;
            font-weight: 600;
        }
        .tl-trophy-years {
            font-family: 'Inter', sans-serif;
            font-size: 0.72rem;
            color: #B8C3B5;
            margin-top: 0.15rem;
        }
        .tl-avatar {
            border-radius: 50%;
            background: #102418;
            border: 2px solid #D4AF37;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto;
            box-shadow: 0 0 20px rgba(212,175,55,0.15), 0 0 40px rgba(46,139,87,0.10);
        }
        .tl-profile-name {
            font-family: 'Bebas Neue', sans-serif;
            font-size: 2.6rem;
            color: #D4AF37;
            letter-spacing: 4px;
            line-height: 1;
            margin: 0.5rem 0 0.1rem;
        }
        .tl-profile-meta {
            font-family: 'Inter', sans-serif;
            font-size: 0.72rem;
            color: #B8C3B5;
            letter-spacing: 2px;
            text-transform: uppercase;
        }
        .tl-table {
            width: 100%;
            border-collapse: collapse;
            font-family: 'Inter', sans-serif;
            font-size: 0.85rem;
        }
        .tl-table th {
            background: #102418;
            color: #D4AF37;
            font-weight: 600;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            font-size: 0.68rem;
            padding: 0.7rem 1rem;
            border-bottom: 1px solid rgba(46,139,87,0.5);
            text-align: left;
        }
        .tl-table td {
            padding: 0.6rem 1rem;
            color: #F5F3EA;
            border-bottom: 1px solid rgba(46,139,87,0.15);
        }
        .tl-table tr:last-child td { border-bottom: none; }
        .tl-table tr:hover td { background: rgba(46,139,87,0.06); }
        .tl-table .gold  { color: #D4AF37; font-weight: 600; }
        .tl-table .muted { color: #B8C3B5; }
        .tl-table .center { text-align: center; }
        .tl-table .right  { text-align: right; }
        div[data-testid="stMarkdownContainer"] p { color: #F5F3EA; }
        .stSelectbox > label { color: #B8C3B5 !important; font-family: 'Inter', sans-serif; font-size: 0.75rem !important; letter-spacing: 2px; text-transform: uppercase; }
        div[data-baseweb="select"] { background: #102418 !important; border-color: rgba(46,139,87,0.5) !important; }

        /* ── MOBILE NAV ─────────────────────────────────── */
        .tl-nav-toggle-cb { display: none; }
        .tl-nav-hamburger {
            display: none;
            cursor: pointer;
            color: #D4AF37;
            font-size: 1.6rem;
            line-height: 1;
            user-select: none;
            padding: 4px 2px;
        }
        @media (max-width: 900px) {
            .main .block-container {
                padding-top: 64px !important;
                padding-left: 1rem !important;
                padding-right: 1rem !important;
            }
            .tl-nav {
                height: auto;
                min-height: 52px;
                padding: 0 1.25rem;
                flex-wrap: wrap;
                align-items: center;
                justify-content: space-between;
            }
            .tl-nav-brand { font-size: 1.1rem; letter-spacing: 3px; }
            .tl-nav-hamburger { display: block; }
            .tl-nav-links {
                display: none;
                flex-direction: column;
                width: 100%;
                gap: 0;
                padding: 0.4rem 0 0.75rem;
                border-top: 1px solid rgba(46,139,87,0.3);
                margin-top: 4px;
            }
            .tl-nav-toggle-cb:checked ~ .tl-nav-links { display: flex; }
            .tl-nav-link {
                padding: 0.5rem 0.25rem;
                font-size: 0.72rem;
                border-bottom: none !important;
                border-left: 2px solid transparent;
                padding-left: 0.6rem;
                transition: border-color 0.15s, color 0.15s;
            }
            .tl-nav-link.active {
                border-left-color: #D4AF37;
                border-bottom-color: transparent !important;
            }
            .tl-nav-link:hover {
                border-left-color: #3FA66B;
                border-bottom-color: transparent !important;
            }
        }
"""

_FONTS_URL = "https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;500;600;700&family=Oswald:wght@400;500;600;700&display=swap"


def inject_css():
    css = _CSS.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
    st.html(
        f"""<script>
(function() {{
    if (document.getElementById('tl-css')) return;
    var l = document.createElement('link');
    l.rel = 'stylesheet';
    l.href = '{_FONTS_URL}';
    document.head.appendChild(l);
    var s = document.createElement('style');
    s.id = 'tl-css';
    s.textContent = `{css}`;
    document.head.appendChild(s);
}})();
</script>""",
        unsafe_allow_javascript=True,
    )


def render_nav(active: str = "home"):
    pages = [
        ("home",              "/",                   "Home"),
        ("champions",         "/champions",           "Champions"),
        ("league_timeline",   "/league_timeline",     "Timeline"),
        ("league_history",    "/league_history",      "League History"),
        ("season_archive",    "/season_archive",      "Season Archive"),
        ("manager_profiles",  "/manager_profiles",    "Managers"),
        ("franchise_profiles","/franchise_profiles",  "Franchises"),
        ("draft_center",      "/draft_center",        "Draft Center"),
        ("keeper_hall",       "/keeper_hall",         "Keeper Hall"),
        ("rivalries",         "/rivalries",           "Rivalries"),
    ]
    links = "".join(
        f'<a href="{href}" class="tl-nav-link{" active" if active == key else ""}" target="_self">{label}</a>'
        for key, href, label in pages
    )
    st.markdown(
        f"""
        <div class="tl-nav">
            <a href="/" class="tl-nav-brand">A NEW DYNASTY</a>
            <input type="checkbox" id="tl-nav-toggle" class="tl-nav-toggle-cb">
            <label for="tl-nav-toggle" class="tl-nav-hamburger">&#9776;</label>
            <div class="tl-nav-links">{links}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def avatar_html(name: str, size: int = 64) -> str:
    emoji = MANAGER_EMOJI.get(name, "👤")
    return (
        f'<div class="tl-avatar" style="width:{size}px;height:{size}px;font-size:{size//2}px;">'
        f"{emoji}</div>"
    )


def metric_card(value: str, label: str) -> str:
    return (
        f'<div class="tl-metric">'
        f'<div class="tl-metric-value">{value}</div>'
        f'<div class="tl-metric-label">{label}</div>'
        f"</div>"
    )


def section_header(label: str, title: str) -> str:
    return (
        f'<div class="tl-section-label">{label}</div>'
        f'<div class="tl-section-title">{title}</div>'
    )


def render_page_footer(href: str, cta: str, tagline: str) -> None:
    st.markdown(
        f"""
        <div style="text-align:center;padding:4rem 0 2.5rem;">
            <div style="height:1px;background:linear-gradient(to right,transparent,#D4AF37,transparent);
                        margin:0 auto 2.25rem;max-width:400px;"></div>
            <div style="font-family:'Bebas Neue',sans-serif;font-size:1.35rem;color:#F5F5F5;
                        letter-spacing:4px;line-height:1.9;">
                {tagline}
            </div>
            <div style="margin-top:1.75rem;">
                <a href="{href}" target="_self"
                   style="font-family:'Inter',sans-serif;font-size:0.72rem;color:#D4AF37;
                          letter-spacing:4px;text-transform:uppercase;text-decoration:none;
                          border-bottom:1px solid rgba(212,175,55,0.6);padding-bottom:3px;">
                    {cta} &nbsp;&rarr;
                </a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def html_table(headers: list, rows: list) -> str:
    th = "".join(f"<th>{h}</th>" for h in headers)
    tbody = ""
    for row in rows:
        cells = "".join(
            f'<td class="{v[1]}">{v[0]}</td>' if isinstance(v, tuple) else f"<td>{v}</td>"
            for v in row
        )
        tbody += f"<tr>{cells}</tr>"
    return f"<table class='tl-table'><thead><tr>{th}</tr></thead><tbody>{tbody}</tbody></table>"
