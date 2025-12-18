# gui_app.py
import streamlit as st
import pandas as pd

from benchmark import run_single_experiment

# ----------------------------
# Sayfa ayarı + küçük stil dokunuşu
# ----------------------------
st.set_page_config(page_title="Algo Energy GUI", layout="wide")

st.markdown("""
<style>
/* başlık altı boşluğu */
.block-container { padding-top: 1.2rem; padding-bottom: 2rem; }
/* kart hissi */
div[data-testid="stMetric"] {
    background: #0f172a10;
    border: 1px solid #0f172a20;
    border-radius: 14px;
    padding: 12px 14px;
}
/* dataframe kenar */
div[data-testid="stDataFrame"] {
    border: 1px solid #0f172a20;
    border-radius: 14px;
    overflow: hidden;
}
</style>
""", unsafe_allow_html=True)

st.title("Divide & Conquer Enerji Deneyi")
st.caption("MergeSort vs QuickSort — süre, sayaçlar, proxy enerji ve (opsiyonel) CodeCarbon tahmini ölçümleri")

# ----------------------------
# Sol panel: kullanıcı seçimleri
# ----------------------------
with st.sidebar:
    st.header("Deney Ayarları")
    n = st.selectbox("Dizi boyutu (n)", [1000, 5000, 10000], index=0)
    mode = st.selectbox(
        "Senaryo (mode)",
        ["random", "sorted", "reversed"],
        index=0,
        help="random: rastgele, sorted: önceden sıralı, reversed: ters sıralı"
    )
    repetitions = st.slider(
        "Tekrar sayısı (repetitions)",
        min_value=1, max_value=20, value=5, step=1,
        help="Her senaryoyu kaç kez koşup ortalama alınacağını belirler."
    )

    st.divider()
    st.write("Çıktılar:")
    st.write("- avg_time_ms: ortalama süre (ms)")
    st.write("- avg_comp: ortalama karşılaştırma sayısı")
    st.write("- avg_assign: ortalama atama/swap sayısı")
    st.write("- energy_proxy: avg_comp + avg_assign")
    st.write("- energy_joule / emissions_kg: CodeCarbon (tahmini)")

run = st.button("Deneyi Başlat ▶️", use_container_width=True)

# ----------------------------
# Yardımcı: kısa yorum paragrafı üretici
# ----------------------------
def scenario_text(mode_: str) -> str:
    if mode_ == "random":
        return ("Random (rastgele) senaryo, algoritmaların **ortalama durum** davranışını görmek için seçilir. "
                "Gerçek hayata en yakın giriş tipidir ve MergeSort ile QuickSort’un tipik performans farkını ortaya çıkarır.")
    if mode_ == "sorted":
        return ("Sorted (önceden sıralı) senaryo, algoritmaların **özel giriş düzenlerinde** nasıl davrandığını ölçer. "
                "Bazı QuickSort pivot stratejilerinde bu senaryo maliyeti artırabildiği için özellikle önemlidir.")
    if mode_ == "reversed":
        return ("Reversed (ters sıralı) senaryo, **kötü duruma yakın** bir stres testidir. "
                "Algoritmaların zorlayıcı veri düzenlerinde süre ve işlem sayısı açısından nasıl değiştiğini gösterir.")
    return ""

def compare_paragraph(m, q, mode_: str) -> str:
    # Basit kıyas metni
    faster = "MergeSort" if m["avg_time_ms"] < q["avg_time_ms"] else "QuickSort"
    lower_proxy = "MergeSort" if m["energy_proxy"] < q["energy_proxy"] else "QuickSort"

    # fark yüzdesi
    t_diff = abs(m["avg_time_ms"] - q["avg_time_ms"])
    t_base = min(m["avg_time_ms"], q["avg_time_ms"]) or 1e-9
    t_pct = (t_diff / t_base) * 100.0

    e_diff = abs(m["energy_proxy"] - q["energy_proxy"])
    e_base = min(m["energy_proxy"], q["energy_proxy"]) or 1e-9
    e_pct = (e_diff / e_base) * 100.0

    return (
        f"Bu çalışmada **n={m['n']}** ve **{mode_}** senaryosu için her algoritma **{m['repetitions']}** kez çalıştırılıp "
        f"ortalama değerler alınmıştır. Süre ölçümüne göre **{faster}** daha hızlı görünmektedir "
        f"(yaklaşık **%{t_pct:.1f}** fark). İşlem tabanlı proxy enerji metriğinde (avg_comp + avg_assign) ise "
        f"**{lower_proxy}** daha düşük maliyet üretmiştir (yaklaşık **%{e_pct:.1f}** fark). "
        f"{scenario_text(mode_)}"
    )

# ----------------------------
# Deney çalıştırma
# ----------------------------
if run:
    with st.spinner("Çalıştırılıyor..."):
        merge_res, quick_res = run_single_experiment(n, mode, repetitions)

    # tablo
    df = pd.DataFrame([merge_res, quick_res])

    cols = [
        "algo", "n", "mode", "repetitions",
        "avg_time_ms", "avg_comp", "avg_assign",
        "energy_proxy", "energy_joule", "emissions_kg"
    ]
    df = df[cols]

    # daha okunur format (tablo gösteriminde)
    df_show = df.copy()
    df_show["avg_time_ms"] = df_show["avg_time_ms"].map(lambda x: f"{x:.3f}")
    df_show["avg_comp"] = df_show["avg_comp"].map(lambda x: f"{x:.1f}")
    df_show["avg_assign"] = df_show["avg_assign"].map(lambda x: f"{x:.1f}")
    df_show["energy_proxy"] = df_show["energy_proxy"].map(lambda x: f"{x:.1f}")
    df_show["energy_joule"] = df_show["energy_joule"].map(lambda x: "-" if x is None else f"{x:.2f}")
    df_show["emissions_kg"] = df_show["emissions_kg"].map(lambda x: "-" if x is None else f"{x:.8f}")

    st.success("Bitti ✅")

    # ----------------------------
    # Üst metrik kartları
    # ----------------------------
    st.subheader("Özet Metrikler")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("MergeSort süre", f"{merge_res['avg_time_ms']:.3f} ms")
    c2.metric("QuickSort süre", f"{quick_res['avg_time_ms']:.3f} ms")
    c3.metric("MergeSort energy_proxy", f"{merge_res['energy_proxy']:.1f}")
    c4.metric("QuickSort energy_proxy", f"{quick_res['energy_proxy']:.1f}")

    # küçük not (codecarbon)
    with st.expander("Not: CodeCarbon ölçümleri nasıl okunmalı?"):
        st.write(
            "CodeCarbon bu senaryoyu (n, mode, repetitions) kapsayan tek bir ölçüm alır. "
            "Bu yüzden aynı senaryoda MergeSort ve QuickSort satırlarında energy_joule / emissions_kg "
            "değerleri **aynı görünebilir**. Proxy enerji metriği (energy_proxy) ise algoritmaya özeldir."
        )

    # ----------------------------
    # Sekmeler: tablo / grafik / yorum
    # ----------------------------
    tab1, tab2, tab3 = st.tabs(["📋 Sonuç Tablosu", "📊 Grafikler", "📝 yorum"])

    with tab1:
        st.dataframe(df_show, use_container_width=True)

    with tab2:
        left, right = st.columns(2)

        with left:
            st.markdown("**avg_time_ms (ms)**")
            chart_df = df.set_index("algo")[["avg_time_ms"]]
            st.bar_chart(chart_df)

        with right:
            st.markdown("**energy_proxy (avg_comp + avg_assign)**")
            chart_df2 = df.set_index("algo")[["energy_proxy"]]
            st.bar_chart(chart_df2)

    with tab3:
        st.markdown("### Sonuç açıklaması")
        st.write(compare_paragraph(merge_res, quick_res, mode))

        st.markdown("### Senaryo açıklaması")
        st.info(scenario_text(mode))

else:
    st.info("Soldan ayarları seçip **Deneyi Başlat ▶️** butonuna bas.")
