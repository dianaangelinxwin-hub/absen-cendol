from flask import Flask, request, jsonify, render_template_string
from supabase import create_client, Client
from datetime import datetime
import pytz

app = Flask(__name__)

# ==========================================
# KONFIGURASI SUPABASE 
# ==========================================
SUPABASE_URL = "https://xgsnzorbquzmzgsgwrfj.supabase.co"
SUPABASE_KEY = "sb_secret_Aq7y_yw0Q0Jf2eMwpYmQFw_NbIHh8N8"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
tz = pytz.timezone('Asia/Jakarta')

# ==========================================
# KODINGAN DESAIN WEB (Dilebur Langsung)
# ==========================================
HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Live Dashboard Presensi</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
</head>
<body class="bg-gray-100 font-sans leading-normal tracking-normal">
    <nav class="bg-blue-800 p-4 shadow-lg">
        <div class="container mx-auto flex items-center justify-between">
            <div class="text-white font-bold text-xl">
                Sistem Presensi SMK Kota Mungkid
            </div>
            <div class="text-blue-200 text-sm" id="jam-digital">
                Memuat Waktu...
            </div>
        </div>
    </nav>
    <div class="container mx-auto mt-8 px-4">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div class="bg-white rounded-lg p-6 shadow-md border-l-4 border-blue-500">
                <h3 class="text-gray-500 text-sm font-bold uppercase">Total Tap Hari Ini</h3>
                <p class="text-3xl font-bold text-gray-800 mt-2" id="total-tap">0</p>
            </div>
            <div class="bg-white rounded-lg p-6 shadow-md border-l-4 border-green-500">
                <h3 class="text-gray-500 text-sm font-bold uppercase">Sesi Masuk</h3>
                <p class="text-3xl font-bold text-green-600 mt-2" id="total-masuk">0</p>
            </div>
            <div class="bg-white rounded-lg p-6 shadow-md border-l-4 border-orange-500">
                <h3 class="text-gray-500 text-sm font-bold uppercase">Sesi Pulang</h3>
                <p class="text-3xl font-bold text-orange-600 mt-2" id="total-pulang">0</p>
            </div>
        </div>
        <div class="bg-white rounded-lg shadow-md overflow-hidden">
            <div class="bg-gray-800 text-white p-4 flex justify-between items-center">
                <h2 class="font-bold text-lg">Log Kehadiran Live</h2>
                <span class="flex items-center text-xs text-green-400">
                    <span class="w-2 h-2 rounded-full bg-green-500 mr-2 animate-pulse"></span>
                    Live Update (5d)
                </span>
            </div>
            <div class="overflow-x-auto">
                <table class="w-full whitespace-nowrap">
                    <thead class="bg-gray-100 text-gray-600 text-left text-sm font-bold uppercase">
                        <tr>
                            <th class="px-6 py-3">Waktu Tap</th>
                            <th class="px-6 py-3">UID Kartu</th>
                            <th class="px-6 py-3">Jenis Absen</th>
                            <th class="px-6 py-3">Status</th>
                        </tr>
                    </thead>
                    <tbody id="tabel-body" class="text-sm text-gray-700">
                        <tr>
                            <td colspan="4" class="px-6 py-8 text-center text-gray-500">Memuat data dari database...</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    <script>
        const SUPABASE_URL = 'https://xgsnzorbquzmzgsgwrfj.supabase.co';
        const SUPABASE_KEY = 'sb_secret_Aq7y_yw0Q0Jf2eMwpYmQFw_NbIHh8N8';
        const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

        async function fetchLogAbsensi() {
            try {
                const hariIni = new Date().toISOString().split('T')[0];
                const { data, error } = await supabase
                    .from('log_absensi')
                    .select('*')
                    .gte('waktu_tap', `${hariIni}T00:00:00Z`)
                    .order('waktu_tap', { ascending: false });
                if (error) throw error;
                perbaruiTampilan(data);
            } catch (err) {
                console.error('Gagal mengambil data:', err.message);
            }
        }

        function perbaruiTampilan(data) {
            const tabelBody = document.getElementById('tabel-body');
            document.getElementById('total-tap').innerText = data.length;
            document.getElementById('total-masuk').innerText = data.filter(d => d.jenis_absen === 'Masuk').length;
            document.getElementById('total-pulang').innerText = data.filter(d => d.jenis_absen === 'Pulang').length;
            tabelBody.innerHTML = '';
            if (data.length === 0) {
                tabelBody.innerHTML = '<tr><td colspan="4" class="px-6 py-8 text-center text-gray-500">Belum ada data absensi hari ini.</td></tr>';
                return;
            }
            data.forEach(log => {
                const waktu = new Date(log.waktu_tap).toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
                const warnaBadge = log.jenis_absen === 'Masuk' ? 'bg-green-100 text-green-800' : 'bg-orange-100 text-orange-800';
                const baris = `
                    <tr class="border-b border-gray-200 hover:bg-gray-50 transition duration-150">
                        <td class="px-6 py-4 font-mono text-gray-600">${waktu} WIB</td>
                        <td class="px-6 py-4 font-bold">${log.uid_kartu}</td>
                        <td class="px-6 py-4">
                            <span class="px-3 py-1 rounded-full text-xs font-bold ${warnaBadge}">
                                ${log.jenis_absen}
                            </span>
                        </td>
                        <td class="px-6 py-4 font-semibold text-blue-600">${log.status}</td>
                    </tr>
                `;
                tabelBody.innerHTML += baris;
            });
        }
        setInterval(() => {
            document.getElementById('jam-digital').innerText = new Date().toLocaleString('id-ID', { dateStyle: 'full', timeStyle: 'medium' }) + ' WIB';
        }, 1000);
        fetchLogAbsensi();
        setInterval(fetchLogAbsensi, 5000);
    </script>
</body>
</html>
"""

# ==========================================
# 1. RUTE HALAMAN UTAMA (Memanggil String HTML)
# ==========================================
@app.route('/', methods=['GET'])
def halaman_utama():
    return render_template_string(HTML_DASHBOARD)

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

if __name__ == '__main__':
    app.run(debug=True)