from flask import Flask, request, jsonify
from supabase import create_client, Client
from datetime import datetime
import pytz

app = Flask(__name__)

# ==========================================
# KONFIGURASI SUPABASE (Masukkan Kunci Anda)
# ==========================================
SUPABASE_URL = "https://xgsnzorbquzmzgsgwrfj.supabase.co/rest/v1/"
SUPABASE_KEY = "sb_secret_Aq7y_yw0Q0Jf2eMwpYmQFw_NbIHh8N8"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
tz = pytz.timezone('Asia/Jakarta')

# ==========================================
# 1. RUTE HALAMAN UTAMA (Mencegah Crash di Vercel)
# ==========================================
@app.route('/', methods=['GET'])
def halaman_utama():
    return jsonify({
        "status": "Online",
        "pesan": "Mesin Absensi Vercel Siap Menerima Data!"
    }), 200

# ==========================================
# 2. RUTE UTAMA UNTUK ALAT ESP32
# ==========================================
@app.route('/api/scan', methods=['POST'])
def scan_rfid():
    data = request.json
    if not data or 'uid' not in data:
        return jsonify({"status": "gagal", "pesan": "Format Salah"}), 400
        
    uid_kartu = data['uid']
    karyawan = supabase.table('karyawan').select('*').eq('uid_kartu', uid_kartu).execute()
    
    if not karyawan.data:
        return jsonify({"status": "gagal", "pesan": "Kartu Tidak Dikenal"}), 404
        
    nama_karyawan = karyawan.data[0]['nama']
    sekarang = datetime.now(tz)
    jam = sekarang.hour
    tanggal_hari_ini = sekarang.strftime("%Y-%m-%d")
    
    if 6 <= jam < 8:
        jenis_absen = "Masuk"
    elif 16 <= jam < 18:
        jenis_absen = "Pulang"
    else:
        return jsonify({"status": "gagal", "pesan": f"Di luar jam absen!"}), 403
        
    log_hari_ini = supabase.table('log_absensi').select('*').eq('uid_kartu', uid_kartu).eq('jenis_absen', jenis_absen).gte('waktu_tap', f"{tanggal_hari_ini}T00:00:00+07:00").execute()
        
    if log_hari_ini.data:
        return jsonify({"status": "gagal", "pesan": f"Sudah absen {jenis_absen}!"}), 409
        
    data_insert = {"uid_kartu": uid_kartu, "jenis_absen": jenis_absen, "status": "Hadir"}
    supabase.table('log_absensi').insert(data_insert).execute()
    
    return jsonify({"status": "sukses", "pesan": f"Halo {nama_karyawan}, Absen Berhasil!"}), 200