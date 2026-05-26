from flask import Flask, request, jsonify, render_template_string
from supabase import create_client, Client
from datetime import datetime
import pytz

app = Flask(__name__)

# ==========================================
# KONFIGURASI SUPABASE 
# ==========================================
SUPABASE_URL = "https://xgsnzorbquzmzgsgwrfj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhnc256b3JicXV6bXpnc2d3cmZqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk2ODQ3NTksImV4cCI6MjA5NTI2MDc1OX0.HcYBj6Cdoo4oyALiL3VxXG6DBqg2HORvBopH8fyysYc"
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
        const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhnc256b3JicXV6bXpnc2d3cmZqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk2ODQ3NTksImV4cCI6MjA5NTI2MDc1OX0.HcYBj6Cdoo4oyALiL3VxXG6DBqg2HORvBopH8fyysYc';
        
        const supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

        setInterval(() => {
            document.getElementById('jam-digital').innerText = new Date().toLocaleString('id-ID', { dateStyle: 'full', timeStyle: 'medium' }) + ' WIB';
        }, 1000);

        async function fetchLogAbsensi() {
            try {
                const now = new Date();
                const offset = now.getTimezoneOffset() * 60000;
                const localISOTime = (new Date(now - offset)).toISOString().slice(0, -1);
                const hariIni = localISOTime.split('T')[0];

                const { data, error } = await supabaseClient
                    .from('log_absensi')
                    .select('*')
                    .gte('waktu_tap', `${hariIni}T00:00:00`)
                    .order('waktu_tap', { ascending: false });
                    
                if (error) {
                    console.error('Error dari Supabase:', error);
                    return; 
                }
                
                perbaruiTampilan(data || []); 
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
                let waktuText = "Waktu Tidak Valid";
                if (log.waktu_tap) {
                    const dateObj = new Date(log.waktu_tap);
                    waktuText = dateObj.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit', second: '2-digit' }) + ' WIB';
                }
                
                const jenisAbsen = log.jenis_absen || 'Tidak Diketahui';
                const warnaBadge = jenisAbsen === 'Masuk' ? 'bg-green-100 text-green-800' : 
                                   (jenisAbsen === 'Pulang' ? 'bg-orange-100 text-orange-800' : 'bg-gray-100 text-gray-800');
                                   
                const status = log.status || '-';
                
                const baris = `
                    <tr class="border-b border-gray-200 hover:bg-gray-50 transition duration-150">
                        <td class="px-6 py-4 font-mono text-gray-600">${waktuText}</td>
                        <td class="px-6 py-4 font-bold">${log.uid_kartu || '-'}</td>
                        <td class="px-6 py-4">
                            <span class="px-3 py-1 rounded-full text-xs font-bold ${warnaBadge}">
                                ${jenisAbsen}
                            </span>
                        </td>
                        <td class="px-6 py-4 font-semibold text-blue-600">${status}</td>
                    </tr>
                `;
                tabelBody.innerHTML += baris;
            });
        }
        
        fetchLogAbsensi();
        setInterval(fetchLogAbsensi, 5000);
    </script>
</body>
</html>
"""

# ==========================================
# RUTE SAPU JAGAT & AUTO-SAVE KARTU
# ==========================================
@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'OPTIONS'])
@app.route('/<path:path>', methods=['GET', 'POST', 'OPTIONS'])
def rute_master(path):
    
    if request.method == 'POST':
        try:
            data = request.json
            if not data or 'uid' not in data:
                return jsonify({"status": "gagal", "pesan": "Format Salah"}), 400
                
            uid_kartu = data['uid']
            karyawan = supabase.table('karyawan').select('*').eq('uid_kartu', uid_kartu).execute()
            
            # --- AUTO-SAVE KARTU TIDAK DIKENAL ---
            if not karyawan.data:
                data_kartu_baru = {"uid_kartu": uid_kartu, "nama": "BELUM TERDAFTAR"}
                supabase.table('karyawan').insert(data_kartu_baru).execute()
                return jsonify({"status": "gagal", "pesan": "Kartu Disimpan!"}), 404
                
            nama_karyawan = karyawan.data[0]['nama']

            if nama_karyawan == "BELUM TERDAFTAR":
                return jsonify({"status": "gagal", "pesan": "Ganti Nama Dulu!"}), 403
            
            sekarang = datetime.now(tz)
            jam =媽媽 = sekarang.hour
            tanggal_hari_ini = sekarang.strftime("%Y-%m-%d")
            
            # ATURAN JAM JAM LONGGAR UNTUK TESTING
            if 0 <= jam < 13:
                jenis_absen = "Masuk"
            elif 13 <= jam <= 23:
                jenis_absen = "Pulang"
            else:
                return jsonify({"status": "gagal", "pesan": f"Di luar jam absen!"}), 403
                
            log_hari_ini = supabase.table('log_absensi').select('*').eq('uid_kartu', uid_kartu).eq('jenis_absen', jenis_absen).gte('waktu_tap', f"{tanggal_hari_ini}T00:00:00+07:00").execute()
                
            if log_hari_ini.data:
                return jsonify({"status": "gagal", "pesan": f"Sudah absen {jenis_absen}!"}), 409
                
            data_insert = {"uid_kartu": uid_kartu, "jenis_absen": jenis_absen, "status": "Hadir"}
            supabase.table('log_absensi').insert(data_insert).execute()
            
            return jsonify({"status": "sukses", "pesan": f"Halo {nama_karyawan}, Absen Berhasil!"}), 200

        except Exception as e:
            return jsonify({"status": "gagal", "pesan": "Error Sistem"}), 500

    return render_template_string(HTML_DASHBOARD)

if __name__ == '__main__':
    app.run(debug=True)