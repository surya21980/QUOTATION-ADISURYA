import streamlit as st
import pandas as pd

# Konfigurasi halaman agar rapi
st.set_page_config(page_title="Database Sales", layout="wide")

st.title("📦 Database Penawaran")
st.write("Gunakan kolom di bawah untuk mencari item dengan cepat.")

# Ganti dengan link kamu
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTNxHkSCvjIgy40LYeVZyQ3HLemYVpE6TnvxjXhj2ifNxBbOePlHZ7CYfYpR2x00Yjpjs0zVH6jQEc8/pub?output=csv"

@st.cache_data(ttl=600)
def load_data():
    return pd.read_csv(SHEET_URL)

try:
    df = load_data()
    
    # Input pencarian
    search_query = st.text_input("🔍 Ketik Part Number atau Keterangan barang yang dicari:")
    
    if search_query:
        # Pecah input berdasarkan koma
        queries = [q.strip() for q in search_query.split(',')]
        
        # Cari item yang ditemukan
        found_data = df[df.apply(lambda row: any(
            any(str(q).lower() in str(cell).lower() for q in queries) 
            for cell in row
        ), axis=1)]
        
        # --- LOGIKA PENGECEKAN BARANG TIDAK ADA ---
        # Mencari item mana dari list 'queries' yang TIDAK ada di dataframe
        not_found = []
        for q in queries:
            if not df.apply(lambda row: row.astype(str).str.contains(q, case=False).any(), axis=1).any():
                not_found.append(q)

        # Menampilkan hasil
        if not found_data.empty:
            st.success(f"Ditemukan {len(found_data)} item.")
            st.dataframe(found_data, use_container_width=True, hide_index=True)
        
        # Menampilkan barang yang tidak ditemukan
        if not_found:
            st.error(f"Peringatan: Item berikut tidak ditemukan di database: **{', '.join(not_found)}**")
            st.write("Catatan: Segera update database untuk item di atas.")
    else:
        st.info("Silakan mulai mengetik...")

except Exception as e:
    st.error("Terjadi kesalahan saat memuat data. Pastikan link Google Sheets sudah benar.")