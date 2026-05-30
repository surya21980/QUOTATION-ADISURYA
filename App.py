# Ganti dengan link kamu
#SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTNxHkSCvjIgy40LYeVZyQ3HLemYVpE6TnvxjXhj2ifNxBbOePlHZ7CYfYpR2x00Yjpjs0zVH6jQEc8/pub?output=csv"

import streamlit as st
import pandas as pd

# Konfigurasi Halaman
st.set_page_config(page_title="Database Sales", layout="wide")

st.title("📦 Database Penawaran")
st.write("Cari item dengan cepat dan buat format pesan untuk WhatsApp.")

# Ganti link di bawah ini dengan link CSV Google Sheets kamu
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTNxHkSCvjIgy40LYeVZyQ3HLemYVpE6TnvxjXhj2ifNxBbOePlHZ7CYfYpR2x00Yjpjs0zVH6jQEc8/pub?output=csv" 

@st.cache_data(ttl=600)
def load_data():
    return pd.read_csv(SHEET_URL)

try:
    df = load_data()
    
    # Bagian Pencarian
    search_query = st.text_input("🔍 Ketik Part Number atau Keterangan (Pisahkan dengan koma untuk cari banyak):")
    
    if search_query:
        queries = [q.strip() for q in search_query.split(',')]
        
        # Filter data
        filtered_df = df[df.apply(lambda row: any(
            any(str(q).lower() in str(cell).lower() for q in queries) 
            for cell in row
        ), axis=1)]
        
        # Pengecekan barang tidak ditemukan
        not_found = [q for q in queries if not df.apply(lambda row: row.astype(str).str.contains(q, case=False).any(), axis=1).any()]

        if not filtered_df.empty:
            st.success(f"Ditemukan {len(filtered_df)} item.")
            st.dataframe(filtered_df, use_container_width=True, hide_index=True)
            
            st.write("---")
            st.subheader("📋 Copy Data Hasil Pencarian")
            
            # Mengubah tabel hasil pencarian menjadi format CSV text
            csv_text = filtered_df.to_csv(index=False, sep='\t') # sep='\t' agar saat di-paste ke Excel/WA rapi per kolom
            
            st.text_area("Copy teks tabel ini (Bisa langsung di-paste ke Excel/WA):", 
                         value=csv_text, 
                         height=200,
                         help="Klik kotak ini, lalu tekan Ctrl+A (Select All) dan Ctrl+C (Copy)")
            
            # Tambahan tombol download untuk jaga-jaga
            st.download_button(
                label="📥 Download Hasil Pencarian (.csv)",
                data=filtered_df.to_csv(index=False).encode('utf-8'),
                file_name='hasil_pencarian.csv',
                mime='text/csv',
            )
        
        if not_found:
            st.error(f"Peringatan: Item berikut tidak ditemukan di database: **{', '.join(not_found)}**")
            
    else:
        st.info("Silakan mulai mengetik di kolom pencarian untuk melihat data.")

except Exception as e:
    st.error(f"Terjadi kesalahan: {e}. Pastikan link Google Sheets sudah benar.")