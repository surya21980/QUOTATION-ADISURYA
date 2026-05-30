# Ganti dengan link kamu
#SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTNxHkSCvjIgy40LYeVZyQ3HLemYVpE6TnvxjXhj2ifNxBbOePlHZ7CYfYpR2x00Yjpjs0zVH6jQEc8/pub?output=csv"

import streamlit as st
import pandas as pd
import re

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
    search_query = st.text_input("🔍 Ketik [P/N] [Desc] atau [Merek] - [Pisahkan dengan (,) atau (;) untuk cari banyak]:")
    
    if search_query:
        #queries = [q.strip() for q in search_query.split(',')]
        queries = [q.strip() for q in re.split(r'[;,]', search_query)]
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
            
                    
            # --- BAGIAN COPY DALAM FORMAT TABEL (CSV) ---
            st.write("---")
            st.subheader("📋 Copy Data Hasil Pencarian")
            
            # Pilih hanya kolom yang ingin ditampilkan (Urutannya harus sama dengan nama kolom di Excel kamu)
            kolom_untuk_dicopy = ['PART NUMBER', 'KETERANGAN', 'HARGA', 'MEREK']
            df_untuk_copy = filtered_df[kolom_untuk_dicopy]
            
            # Mengubah dataframe pilihan menjadi format CSV text
            csv_text = df_untuk_copy.to_csv(index=False, sep='\t') 
            
            st.text_area("Copy teks tabel ini (Bisa langsung di-paste ke Excel/WA):", 
                         value=csv_text, 
                         height=200,
                         help="Klik kotak ini, lalu tekan Ctrl+A (Select All) dan Ctrl+C (Copy)")
            
                    
        if not_found:
            st.error(f"Peringatan: Item berikut tidak ditemukan di database: **{', '.join(not_found)}**")
            
    else:
        st.info("Silakan mulai mengetik di kolom pencarian untuk melihat data.")

except Exception as e:
    st.error(f"Terjadi kesalahan: {e}. Pastikan link Google Sheets sudah benar.")