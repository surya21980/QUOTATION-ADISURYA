# Ganti dengan link kamu
#SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTNxHkSCvjIgy40LYeVZyQ3HLemYVpE6TnvxjXhj2ifNxBbOePlHZ7CYfYpR2x00Yjpjs0zVH6jQEc8/pub?output=csv"

import streamlit as st
import pandas as pd
import re

# Konfigurasi Halaman
st.set_page_config(page_title="Sistem Database", layout="wide")

st.title("📦 Sistem Database Terpadu")

# Ganti dengan link CSV Google Sheets kamu
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTNxHkSCvjIgy40LYeVZyQ3HLemYVpE6TnvxjXhj2ifNxBbOePlHZ7CYfYpR2x00Yjpjs0zVH6jQEc8/pub?output=csv"

@st.cache_data(ttl=600)
def load_data():
    return pd.read_csv(SHEET_URL)

try:
    df = load_data()
    
    # Membuat Tab
    tab1, tab2 = st.tabs(["🛒 Penawaran (Sales)", "📊 Manajemen (Direksi)"])

    # --- TAB 1: AREA SALES ---
    with tab1:
        st.subheader("Area Pencarian Penawaran")
        search_sales = st.text_input("🔍 Cari PN atau Keterangan [(,) (;) untuk banyak]:", key="s_sales")
        
        if search_sales:
            queries = [q.strip() for q in re.split(r'[;,]', search_sales)]
            
            # URUTAN KOLOM BARU SESUAI PERMINTAAN
            df_sales = df[['PART NUMBER', 'KETERANGAN', 'MEREK', 'HARGA', 'BARIS KE', 'CUST']]
            
            filtered = df_sales[df_sales.apply(lambda row: any(any(str(q).lower() in str(cell).lower() for q in queries) for cell in row), axis=1)]
            
            if not filtered.empty:
                # KONFIGURASI TABEL (Format ribuan dan perataan)
                st.dataframe(
                    filtered, 
                    use_container_width=True, 
                    hide_index=True,
                    column_config={
                        "PART NUMBER": st.column_config.TextColumn("PART NUMBER"),
                        "KETERANGAN": st.column_config.TextColumn("KETERANGAN"),
                        "MEREK": st.column_config.TextColumn("MEREK"),
                        "HARGA": st.column_config.NumberColumn("HARGA", format="%,d"), # Format ribuan dengan koma
                        "BARIS KE": st.column_config.NumberColumn("BARIS KE", format="%,d"),
                        "CUST": st.column_config.TextColumn("CUST")
                    }
                )
                
                # --- BAGIAN COPY KE WA (Hanya sampai HARGA) ---
                # Kita buat tabel baru khusus untuk disalin, hanya berisi 4 kolom
                df_copy = filtered[['PART NUMBER', 'KETERANGAN', 'MEREK', 'HARGA']]
                
                # Mengubah hanya 4 kolom tersebut menjadi format CSV text
                csv_text = df_copy.to_csv(index=False, sep='\t')
                
                st.text_area("Copy tabel ini untuk Excel/WA :", 
                             value=csv_text, 
                             height=150,
                             help="Klik kotak ini, lalu tekan Ctrl+A (Select All) dan Ctrl+C (Copy)")
            else:
                st.warning("Data tidak ditemukan.")

    # --- TAB 2: AREA DIREKSI (DENGAN PASSWORD) ---
    with tab2:
        st.subheader("📊 Area Manajemen Direksi")
        
        # Inisialisasi status login di memori aplikasi
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False

        # Jika belum login, tampilkan kotak password
        if not st.session_state.logged_in:
            password = st.text_input("Masukkan Password Direksi:", type="password", key="pass_input")
            if password == "Admin123": # GANTI PASSWORD KAMU
                st.session_state.logged_in = True
                st.rerun() # Refresh halaman agar kotak password hilang
            elif password:
                st.error("Password Salah!")
        
        # Jika sudah login, tampilkan isi datanya
        if st.session_state.logged_in:
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.rerun()
            
            search_dir = st.text_input("🔍 Cari PN atau Keterangan [(,) (;) untuk banyak]:", key="s_dir")
            df_dir = df[['PART NUMBER', 'KETERANGAN', 'MEREK', 'MODAL', 'SUPPLIER']]
            
            # (Lanjutkan dengan kode filtering dan dataframe seperti sebelumnya)
            if search_dir:
                queries = [q.strip() for q in re.split(r'[;,]', search_dir)]
                filtered_dir = df_dir[df_dir.apply(lambda row: any(any(str(q).lower() in str(cell).lower() for q in queries) for cell in row), axis=1)]
                st.dataframe(filtered_dir, use_container_width=True, hide_index=True)
            else:
                st.dataframe(df_dir, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Error memuat data: {e}")