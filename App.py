import streamlit as st
import pandas as pd
import re
import requests

# Konfigurasi Halaman
st.set_page_config(page_title="Sistem Database", layout="wide")

st.title("📦 Sistem Database Terpadu")

# Ambil data dari Secrets
SHEET_URL = st.secrets["SHEET_URL"]

@st.cache_data(ttl=600)
def load_data():
    df = pd.read_csv(SHEET_URL)
    # PENTING: Membersihkan spasi tersembunyi di nama kolom
    df.columns = df.columns.str.strip()
    return df

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
            
            # Kolom untuk Sales
            df_sales = df[['PART NUMBER', 'KETERANGAN', 'MEREK', 'HARGA', 'BARIS KE', 'TANGGAL UPDATE', 'CUST']]
            
            filtered = df_sales[df_sales.apply(lambda row: any(any(str(q).lower() in str(cell).lower() for q in queries) for cell in row), axis=1)]
            
            if not filtered.empty:
                st.dataframe(
                    filtered, 
                    use_container_width=True, 
                    hide_index=True,
                    column_config={
                        "PART NUMBER": st.column_config.TextColumn("PART NUMBER"),
                        "KETERANGAN": st.column_config.TextColumn("KETERANGAN"),
                        "MEREK": st.column_config.TextColumn("MEREK"),
                        "HARGA": st.column_config.NumberColumn("HARGA", format="%,d"),
                        "BARIS KE": st.column_config.NumberColumn("BARIS KE", format="%d"),
                        "CUST": st.column_config.TextColumn("CUST")
                    }
                )
                
                # Copy tabel khusus untuk WA (4 kolom)
                df_copy = filtered[['PART NUMBER', 'KETERANGAN', 'MEREK', 'HARGA']]
                csv_text = df_copy.to_csv(index=False, sep='\t')
                st.text_area("Copy tabel ini untuk Excel/WA:", value=csv_text, height=150)
            
            # --- CEK BARANG TIDAK DITEMUKAN ---
            not_found = []
            for q in queries:
                if not df.apply(lambda row: row.astype(str).str.contains(q, case=False).any(), axis=1).any():
                    not_found.append(q)
            
            if not_found:
                st.error(f"Peringatan: Item berikut tidak ditemukan: **{', '.join(not_found)}**")
                # Notifikasi Telegram
                try:
                    TOKEN = st.secrets["TELEGRAM_TOKEN"]
                    CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]
                    pesan = f"⚠️ Sales mencari barang tapi tidak ada: {', '.join(not_found)}"
                    requests.get(f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={pesan}")
                    st.success("Notifikasi sudah dikirim ke Direksi!")
                except:
                    st.warning("Gagal mengirim notifikasi.")

    # --- TAB 2: AREA DIREKSI ---
    with tab2:
        st.subheader("📊 Area Manajemen Direksi")
        if 'logged_in' not in st.session_state: st.session_state.logged_in = False

        if not st.session_state.logged_in:
            password = st.text_input("Masukkan Password Direksi:", type="password", key="pass_input")
            if password == "Admin123": # GANTI PASSWORD DISINI
                st.session_state.logged_in = True
                st.rerun()
            elif password: st.error("Password Salah!")
        
        if st.session_state.logged_in:
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.rerun()
            
            search_dir = st.text_input("🔍 Cari data internal:", key="s_dir")
            # DITAMBAHKAN KOLOM 'ALTER'
            df_dir = df[['PART NUMBER', 'KETERANGAN', 'MEREK', 'HARGA', 'MODAL', 'SUPPLIER', 'ALTER']]
            
            if search_dir:
                queries = [q.strip() for q in re.split(r'[;,]', search_dir)]
                filtered_dir = df_dir[df_dir.apply(lambda row: any(any(str(q).lower() in str(cell).lower() for q in queries) for cell in row), axis=1)]
                st.dataframe(filtered_dir, use_container_width=True, hide_index=True)
            else:
                st.dataframe(df_dir, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Error memuat data: {e}")