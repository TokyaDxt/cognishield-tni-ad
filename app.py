"""
CogniShield TNI-AD: Prototype Sistem Deteksi Dini Disinformasi & Polarisasi Kognitif
Kategori Lomba: Siber Sosial (Cognitive Domain)
Kartika Cyber Hackathon 2026 - PUSSIBERAD x CODEPOLITAN
Versi: Pure-Python (Bebas Ketergantungan DLL/C-Extension Windows)
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import re
from datetime import datetime

# ==========================================
# KONFIGURASI HALAMAN & TEMA
# ==========================================
st.set_page_config(
    page_title="CogniShield TNI-AD | Cyber Cognitive Defense",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Dark Tactical Theme)
st.markdown("""
<style>
    .main {
        background-color: #0b111e;
    }
    .stMetric {
        background: rgba(18, 27, 46, 0.7);
        border: 1px solid #1f2e4d;
        border-radius: 8px;
        padding: 10px 14px;
    }
    .badge-tactical {
        background-color: #1e3a5f;
        color: #58a6ff;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 0.82rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 6px;
    }
    .alert-card-danger {
        background-color: rgba(110, 24, 24, 0.25);
        border-left: 4px solid #f85149;
        padding: 12px 16px;
        border-radius: 4px;
        margin-top: 10px;
    }
    .alert-card-warning {
        background-color: rgba(122, 94, 25, 0.25);
        border-left: 4px solid #d29922;
        padding: 12px 16px;
        border-radius: 4px;
        margin-top: 10px;
    }
    .alert-card-success {
        background-color: rgba(29, 87, 45, 0.25);
        border-left: 4px solid #2ea043;
        padding: 12px 16px;
        border-radius: 4px;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# MODUL ANALISIS NLP & HEURISTIK KOGNITIF
# ==========================================

PROVOCATIVE_KEYWORDS = [
    "hancurkan", "serang", "lawan", "makar", "gulingkan", "revolusi", "pemberontak",
    "bohong", "antek", "penghianat", "bangsat", "darurat", "biadab", "laknat",
    "serbu", "bakar", "kudeta", "tumbangkan", "musnahkan", "bubarkan", "kafir"
]

CLICKBAIT_FABRICATION_KEYWORDS = [
    "viral!", "rahasia terbongkar", "wajib tahu", "jangan percaya", "terbongkar!",
    "gempar!", "kebohongan besar", "fakta mengerikan", "terbukti sudah", "sebar luas",
    "bocoran a1", "sebelum dihapus", "video mengejutkan", "beredar kabar"
]

OFFICIAL_CREDIBLE_ENTITIES = [
    "tni", "puspen tni", "kodam", "pussiberad", "kemhan", "kapolri", "pemerintah",
    "kementerian", "resmi", "siaran pers", "konferensi pers", "klarifikasi"
]


def clean_text(text: str) -> str:
    """Membersihkan teks dan normalisasi karakter dasar."""
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"@\w+|#\w+", "", text)
    return text.strip()


def calculate_mdcri(text: str, sensitivity: float = 1.0) -> dict:
    """Menghitung Multi-Dimensional Cognitive Risk Index (MDCRI)."""
    if not text.strip():
        return {
            "overall_score": 0,
            "level": "Netral",
            "polarization": 0,
            "fabrication": 0,
            "aggression": 0,
            "detected_provocative": [],
            "detected_clickbait": [],
            "has_official_source": False,
        }

    cleaned = clean_text(text)
    lower_text = cleaned.lower()
    words = re.findall(r"\b\w+\b", lower_text)
    total_words = max(len(words), 1)

    # 1. Deteksi Kata Pemicu Provokasi
    detected_provocative = [w for w in PROVOCATIVE_KEYWORDS if w in lower_text]
    provocative_count = len(detected_provocative)
    provocation_score = min(100.0, (provocative_count * 25.0 / (total_words ** 0.5)) * 15 * sensitivity)

    # 2. Deteksi Pola Sensasionalisme / Fabrikasi
    detected_clickbait = [phrase for phrase in CLICKBAIT_FABRICATION_KEYWORDS if phrase in lower_text]
    fabrication_score = min(100.0, (len(detected_clickbait) * 35.0) * sensitivity)

    has_official_source = any(ent in lower_text for ent in OFFICIAL_CREDIBLE_ENTITIES)
    if has_official_source:
        fabrication_score = max(0.0, fabrication_score - 25.0)

    # 3. Anomali Agresi Teks (Kapitalisasi & Tanda Seru)
    caps_count = sum(1 for c in text if c.isupper())
    caps_ratio = caps_count / max(len(text), 1)
    exclamation_count = len(re.findall(r"!{2,}", text)) + text.count("!")
    aggression_score = min(100.0, (caps_ratio * 70.0 + exclamation_count * 10.0) * sensitivity)

    overall_score = (provocation_score * 0.45) + (fabrication_score * 0.35) + (aggression_score * 0.20)
    overall_score = min(100.0, round(overall_score, 1))

    if overall_score >= 65:
        level = "BAHAYA (High Risk)"
    elif overall_score >= 35:
        level = "WASPADA (Medium Risk)"
    else:
        level = "AMAN (Low Risk / Organik)"

    return {
        "overall_score": overall_score,
        "level": level,
        "polarization": round(provocation_score, 1),
        "fabrication": round(fabrication_score, 1),
        "aggression": round(aggression_score, 1),
        "detected_provocative": detected_provocative,
        "detected_clickbait": detected_clickbait,
        "has_official_source": has_official_source,
    }


def compute_jaccard_similarity(text1: str, text2: str) -> float:
    """Menghitung kemiripan kata antar dua teks (Jaccard Index)."""
    set1 = set(re.findall(r"\b\w{3,}\b", text1.lower()))
    set2 = set(re.findall(r"\b\w{3,}\b", text2.lower()))
    if not set1 or not set2:
        return 0.0
    return len(set1.intersection(set2)) / len(set1.union(set2))


# ==========================================
# SIDEBAR SISTEM
# ==========================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/shield.png", width=64)
    st.title("CogniShield TNI-AD")
    st.caption("Pusat Siber Angkatan Darat (PUSSIBERAD)")
    
    st.markdown("---")
    st.markdown("**Status Komando Operasional:**")
    st.success("🟢 Mode On-Premise Aktif (Air-Gapped Ready)")
    st.info("🌐 Domain: Siber Sosial (Cognitive Warfare)")
    
    st.markdown("---")
    st.subheader("⚙️ Parameter Sensitivitas")
    sensitivity = st.slider("Ambang Deteksi Anomali", min_value=0.5, max_value=2.0, value=1.0, step=0.1)
    
    st.markdown("---")
    st.caption("**Kartika Cyber Hackathon 2026**\nPlatform prototipe deteksi dini manipulasi opini publik dan astroturfing terorganisir.")


# ==========================================
# HEADER HALAMAN UTAMA
# ==========================================
st.markdown("""
<div style='border-bottom: 2px solid #1f2e4d; padding-bottom: 12px; margin-bottom: 20px;'>
    <h1 style='color: #ffffff; margin-bottom: 4px;'>🛡️ CogniShield TNI-AD</h1>
    <p style='color: #8b949e; font-size: 1.05rem;'>
        Sistem Intelijen Kognitif & Deteksi Dini Disinformasi Terkoordinasi untuk Ketahanan Ruang Siber Nasional
    </p>
    <div>
        <span class='badge-tactical'>Kategori: Siber Sosial</span>
        <span class='badge-tactical'>Arsitektur: NLP Multi-Dimensional</span>
        <span class='badge-tactical'>Status: Purwarupa Fungsional</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ==========================================
# TAB FITUR APLIKASI
# ==========================================
tab1, tab2, tab3 = st.tabs([
    "🔍 Analisis Narasi Tunggal", 
    "🤖 Deteksi Pola Buzzer & Astroturfing", 
    "📑 Ringkasan Laporan Taktis"
])

# ----------------------------------------------------
# TAB 1: ANALISIS NARASI TUNGGAL
# ----------------------------------------------------
with tab1:
    st.subheader("Uji Cepat Risiko Konten & Polarisasi Opini")
    st.write("Masukkan teks narasi isu viral, kutipan media sosial, atau pilih contoh kasus pengujian di bawah:")

    col_btn1, col_btn2, col_btn3 = st.columns(3)
    preset_text = ""
    
    with col_btn1:
        if st.button("🚩 Contoh: Narasi Provokatif & Seruan Kerusuhan"):
            preset_text = (
                "VIRAL! RAKYAT WAJIB TAHU! Terbongkar fakta mengerikan tentang konspirasi pengkhianat negara. "
                "Jangan percaya klarifikasi pemerintah lagi! Sebarkan kabar ini seluas-luasnya sebelum dihapus! "
                "Mari kita serbu dan gulingkan antek-antek asing, lawan sampai titik darah penghabisan!!"
            )
    with col_btn2:
        if st.button("🟡 Contoh: Isu Sensasional Tanpa Rujukan"):
            preset_text = (
                "Bocoran A1! Beredar kabar rahasia di grup tertutup bahwa fasilitas pertahanan sedang mengalami ancaman darurat. "
                "Aparat sengaja menutup-nutupi kejadian aslinya dari publik. Wajib waspada kabar mengejutkan esok hari!"
            )
    with col_btn3:
        if st.button("🟢 Contoh: Rilis Pers Resmi TNI AD"):
            preset_text = (
                "Siaran pers resmi Pusat Penerangan TNI: Menanggapi kabar di media sosial mengenai pergerakan pasukan, "
                "TNI AD menyampaikan klarifikasi bahwa kegiatan tersebut merupakan latihan terencana dalam rangka Hari Juang Kartika. "
                "Masyarakat diimbau tetap tenang dan menyaring informasi dari saluran terverifikasi."
            )

    user_input = st.text_area(
        "Teks Narasi yang Diinvestigasi:",
        value=preset_text if preset_text else "",
        height=140,
        placeholder="Ketik atau tempel teks berita / narasi media sosial di sini..."
    )

    if st.button("🚀 Jalankan Analisis Kognitif", type="primary"):
        if not user_input.strip():
            st.warning("Silakan masukkan teks narasi terlebih dahulu.")
        else:
            with st.spinner("Menganalisis indikator kognitif dan polarisasi bahasa..."):
                res = calculate_mdcri(user_input, sensitivity=sensitivity)

            col_left, col_right = st.columns([1, 1])

            with col_left:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=res["overall_score"],
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Skor Risiko Kognitif (MDCRI)", 'font': {'size': 20, 'color': "white"}},
                    number={'suffix': "%", 'font': {'color': "white"}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
                        'bar': {'color': "#58a6ff"},
                        'bgcolor': "rgba(0,0,0,0)",
                        'borderwidth': 2,
                        'bordercolor': "#30363d",
                        'steps': [
                            {'range': [0, 35], 'color': "rgba(46, 160, 67, 0.45)"},
                            {'range': [35, 65], 'color': "rgba(210, 153, 34, 0.45)"},
                            {'range': [65, 100], 'color': "rgba(248, 81, 73, 0.45)"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 65
                        }
                    }
                ))
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    height=280,
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                st.plotly_chart(fig, use_container_width=True)

            with col_right:
                st.markdown("#### Status Evaluasi Intelijen")
                if "BAHAYA" in res["level"]:
                    st.markdown(f"<div class='alert-card-danger'><h3>🚨 {res['level']}</h3>"
                                f"Terdeteksi potensi manipulasi opini terstruktur dengan intensitas permusuhan tinggi.</div>", 
                                unsafe_allow_html=True)
                elif "WASPADA" in res["level"]:
                    st.markdown(f"<div class='alert-card-warning'><h3>⚠️ {res['level']}</h3>"
                                f"Terdeteksi sensasionalisme dan klaim sepihak tanpa verifikasi sumber resmi.</div>", 
                                unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='alert-card-success'><h3>✅ {res['level']}</h3>"
                                f"Pola bahasa wajar, berimbang, atau mencantumkan rujukan entitas resmi.</div>", 
                                unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                m1, m2, m3 = st.columns(3)
                m1.metric("Polarisasi Ujaran", f"{res['polarization']}%")
                m2.metric("Indeks Fabrikasi", f"{res['fabrication']}%")
                m3.metric("Agresi Tipografi", f"{res['aggression']}%")

            st.markdown("---")
            st.markdown("#### Detail Temuan Linguistik")
            col_d1, col_d2 = st.columns(2)
            
            with col_d1:
                st.markdown("**Kata Pemicu Permusuhan / Polarisasi:**")
                if res["detected_provocative"]:
                    for word in res["detected_provocative"]:
                        st.markdown(f"- `<span style='color: #f85149; font-weight: bold;'>{word}</span>`", unsafe_allow_html=True)
                else:
                    st.write("*(Tidak ditemukan kata pemicu provokasi eksplisit)*")

            with col_d2:
                st.markdown("**Frasa Sensasional / Clickbait:**")
                if res["detected_clickbait"]:
                    for phrase in res["detected_clickbait"]:
                        st.markdown(f"- `<span style='color: #d29922; font-weight: bold;'>{phrase}</span>`", unsafe_allow_html=True)
                else:
                    st.write("*(Tidak ditemukan frasa clickbait ekstrem)*")

            st.markdown("---")
            st.markdown("#### 🎯 Rekomendasi Tindakan Satuan")
            if "BAHAYA" in res["level"]:
                st.error("""
                1. **Eskalasi Pantauan:** Pantau penyebaran tagar dan kata kunci terkait dalam 6 jam ke depan.
                2. **Kontra-Narasi:** Rekomendasikan diseminasi fakta dari penerangan satuan resmi untuk mencegah polarisasi meluas.
                3. **Pengarsipan Bukti:** Amankan metadata sumber penyebar pertama untuk kepentingan analisis digital forensik.
                """)
            elif "WASPADA" in res["level"]:
                st.warning("""
                1. **Verifikasi Silang:** Hubungi satuan terkait untuk memvalidasi klaim isu sebelum memberi tanggapan.
                2. **Pantau Tren:** Masukkan ke dalam antrean monitoring berkala untuk mendeteksi lonjakan volume postingan.
                """)
            else:
                st.info("Konten dalam batas kewajaran. Tidak memerlukan tindakan intervensi aktif.")


# ----------------------------------------------------
# TAB 2: DETEKSI POLA BUZZER & ASTROTURFING
# ----------------------------------------------------
with tab2:
    st.subheader("Analisis Keseragaman Pesan Terkoordinasi (*Astroturfing*)")
    st.write(
        "Operasi buzzer terkoordinasi seringkali menyebarkan narasi dengan pola kata yang hampir identik "
        "melalui banyak akun palsu (*copy-paste massal*). Masukkan beberapa postingan untuk mengukur kesamaannya:"
    )

    default_posts = (
        "Post 1: Terbongkar kebohongan antek asing, rakyat harus turun ke jalan serentak besok pagi!\n"
        "---\n"
        "Post 2: Terbongkar sudah kebohongan antek asing, rakyat wajib turun ke jalan serentak besok!\n"
        "---\n"
        "Post 3: Rakyat harus tahu kebohongan antek asing, ayo turun ke jalan serentak besok pagi!\n"
        "---\n"
        "Post 4: Siang ini cuaca di Surabaya cukup terik dan lalu lintas ramai lancar."
    )

    posts_input = st.text_area("Kumpulan Unggahan yang Dicocokkan (Pisahkan dengan baris '---'):", value=default_posts, height=180)

    if st.button("🔬 Analisis Korelasi Akun", type="primary"):
        posts = [p.strip() for p in posts_input.split("---") if p.strip()]
        if len(posts) < 2:
            st.warning("Masukkan minimal 2 postingan untuk menghitung matriks kesamaan.")
        else:
            n = len(posts)
            # Menggunakan pure-Python list of lists (tanpa numpy)
            similarity_matrix = []
            for i in range(n):
                row = []
                for j in range(n):
                    row.append(round(compute_jaccard_similarity(posts[i], posts[j]) * 100, 1))
                similarity_matrix.append(row)

            labels = [f"Post {i+1}" for i in range(n)]

            col_mat, col_sum = st.columns([1.2, 1])

            with col_mat:
                fig_heatmap = px.imshow(
                    similarity_matrix,
                    x=labels,
                    y=labels,
                    color_continuous_scale="Reds",
                    text_auto=True,
                    title="Matriks Kesamaan Redaksional (%)"
                )
                fig_heatmap.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
                st.plotly_chart(fig_heatmap, use_container_width=True)

            with col_sum:
                high_sim_pairs = []
                for i in range(n):
                    for j in range(i + 1, n):
                        if similarity_matrix[i][j] >= 45.0:
                            high_sim_pairs.append((labels[i], labels[j], similarity_matrix[i][j]))

                st.markdown("#### Indikasi Orkestrasi Buzzer")
                if high_sim_pairs:
                    st.error(f"🚨 **Terdeteksi {len(high_sim_pairs)} pasangan postingan dengan kemiripan tinggi!**")
                    st.write("Kemungkinan besar pesan disebarkan menggunakan pola terorganisir (*template script*):")
                    for p1, p2, sim in high_sim_pairs:
                        st.markdown(f"- **{p1}** ↔ **{p2}**: Kemiripan **{sim}%**")
                else:
                    st.success("✅ Seluruh postingan memiliki variasi bahasa organik. Tidak terindikasi kampanye copy-paste seragam.")


# ----------------------------------------------------
# TAB 3: RINGKASAN LAPORAN TAKTIS
# ----------------------------------------------------
with tab3:
    st.subheader("Format Lembar Ringkasan Intelijen Kognitif")
    st.write("Ekspor ringkasan hasil evaluasi ke dalam format laporan siap cetak untuk pimpinan atau komando operasional:")

    now_str = datetime.now().strftime("%d %B %Y, %H:%M WIB")
    
    report_text = f"""# LEMBAR RINGKASAN INTELIJEN KOGNITIF (LRIK)
**SISTEM:** CogniShield TNI-AD (PUSSIBERAD)  
**WAKTU ANALISIS:** {now_str}  
**KLASIFIKASI:** TERBATAS / INTERNAL SATUAN  

---

### I. LATAR BELAKANG PENELUSURAN
Analisis dilakukan terhadap indikasi operasi pengaruh (*influence operation*) dan narasi disinformasi berbasis teks di ruang siber publik.

### II. HASIL PENGUKURAN RISIKO (MDCRI)
- Status Ancaman: **WASPADA TINGGI**
- Indeks Polarisasi Emosional: 78.4%
- Indeks Fabrikasi Fakta: 65.0%
- Indikasi Koordinasi Buzzer: Terdeteksi 3 simpul akun menyebarkan narasi kembar.

### III. KESIMPULAN & REKOMENDASI TAKTIS
1. Narasi mengandung unsur agitasi terstruktur yang menargetkan persepsi publik terhadap stabilitas nasional.
2. Direkomendasikan kepada bagian penerangan untuk merilis data tandingan berbasis fakta terverifikasi.
3. Tim pemantauan siber melanjutkan penjejakan alamat IP sumber dan klaster akun amplifikator.

---
*Dokumen ini digenerate secara otomatis oleh Purwarupa CogniShield TNI-AD - Kartika Cyber Hackathon 2026*
"""
    st.text_area("Draf Laporan Taktis (Markdown):", value=report_text, height=320)
    st.download_button(
        label="📥 Unduh Laporan (.md)",
        data=report_text,
        file_name="Laporan_Intelijen_CogniShield.md",
        mime="text/markdown"
    )