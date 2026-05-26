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
# KODINGAN DESAIN WEB (DASHBOARD PROFESIONAL)
# ==========================================
HTML_DASHBOARD = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistem Presensi Profesional</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        /* Gaya khusus untuk mode Print (Cetak) */
        @media print {
            .no-print { display: none !important; }
            body { background-color: white !important; color: black !important; }
            .print-area { width: 100% !important; box-shadow: none !important; border: none !important; }
            th, td { border: 1px solid #ddd !important; }
        }
    </style>
</head>
<body class="bg-slate-50 font-sans leading-normal tracking-normal text-slate-800">
    
    <nav class="bg-blue-900 p-4 shadow-lg no-print">
        <div class="container mx-auto flex flex-col md:flex-row items-center justify-between">
            <div class="flex items-center text-white mb-2 md:mb-0">
                <i class="fa-solid fa-school text-2xl mr-3"></i>
                <div>
                    <h1 class="font-bold text-xl tracking-wide">SMK KOTA MUNGKID</h1>
                    <p class="text-xs text-blue-200">Sistem Presensi RFID Terpadu</p>
                </div>
            </div>
            <div class="bg-blue-950 px-4 py-2 rounded-lg text-blue-100 font-mono text-sm shadow-inner border border-blue-800" id="jam-digital">
                Memuat Waktu...
            </div>
        </div>
    </nav>

    <div class="container mx-auto mt-6 px-4 mb-10">
        
        <div class="flex space-x-2 mb-6 no-print border-b border-gray-200 pb-2">
            <button onclick="bukaTab('live')" id="btn-tab-live" class="px-5 py-2 bg-blue-600 text-white font-semibold rounded-t-lg shadow-sm transition">
                <i class="fa-solid fa-desktop mr-2"></i>Live Monitor
            </button>
            <button onclick="bukaTab('rekap')" id="btn-tab-rekap" class="px-5 py-2 bg-gray-200 text-gray-600 hover:bg-gray-300 font-semibold rounded-t-lg shadow-sm transition">
                <i class="fa-solid fa-file-lines mr-2"></i>Rekap & Laporan
            </button>
        </div>

        <div id="tab-live" class="print-area">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6 no-print">
                <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100 flex items-center justify-between border-l-4 border-l-blue-500">
                    <div>
                        <h3 class="text-gray-500 text-xs font-bold uppercase tracking-wider">Total Tap Hari Ini</h3>
                        <p class="text-3xl font-black text-slate-700 mt-1" id="total-tap">0</p>
                    </div>
                    <div class="p-3 bg-blue-50 rounded-full text-blue-500"><i class="fa-solid fa-users fa-lg"></i></div>
                </div>
                <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100 flex items-center justify-between border-l-4 border-l-green-500">
                    <div>
                        <h3 class="text-gray-500 text-xs font-bold uppercase tracking-wider">Hadir (Masuk)</h3>
                        <p class="text-3xl font-black text-green-600 mt-1" id="total-masuk">0</p>
                    </div>
                    <div class="p-3 bg-green-50 rounded-full text-green-500"><i class="fa-solid fa-arrow-right-to-bracket fa-lg"></i></div>
                </div>
                <div class="bg-white rounded-xl p-6 shadow-sm border border-gray-100 flex items-center justify-between border-l-4 border-l-orange-500">
                    <div>
                        <h3 class="text-gray-500 text-xs font-bold uppercase tracking-wider">Sesi Pulang</h3>
                        <p class="text-3xl font-black text-orange-500 mt-1" id="total-pulang">0</p>
                    </div>
                    <div class="p-3 bg-orange-50 rounded-full text-orange-500"><i class="fa-solid fa-house-person-leave fa-lg"></i></div>
                </div>
            </div>

            <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                <div class="bg-slate-800 text-white p-4 flex justify-between items-center no-print">
                    <h2 class="font-bold text-md"><i class="fa-solid fa-list-check mr-2"></i>Log Kehadiran (Hari Ini)</h2>
                    <span class="flex items-center text-xs text-green-400 bg-slate-700 px-3 py-1 rounded-full border border-slate-600">
                        <span class="w-2 h-2 rounded-full bg-green-500 mr-2 animate-pulse"></span>Live Update
                    </span>
                </div>
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse">
                        <thead class="bg-slate-50 text-slate-500 text-xs uppercase font-bold border-b border-gray-200">
                            <tr>
                                <th class="px-6 py-4">Waktu</th>
                                <th class="px-6 py-4">Nama Siswa/Karyawan</th>
                                <th class="px-6 py-4">Jenis Absen</th>
                                <th class="px-6 py-4">Status</th>
                            </tr>
                        </thead>
                        <tbody id="tabel-body-live" class="text-sm divide-y divide-gray-100">
                            <tr><td colspan="4" class="px-6 py-8 text-center text-gray-400">Memuat data hari ini...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <div id="tab-rekap" class="hidden print-area">
            <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100 mb-6 no-print">
                <h2 class="font-bold text-slate-700 mb-4 text-sm uppercase tracking-wide border-b pb-2"><i class="fa-solid fa-filter mr-2"></i>Filter Laporan</h2>
                <div class="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
                    <div>
                        <label class="block text-xs font-semibold text-gray-500 mb-1">Dari Tanggal</label>
                        <input type="date" id="filter-start" class="w-full border border-gray-300 rounded-lg p-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-gray-500 mb-1">Sampai Tanggal</label>
                        <input type="date" id="filter-end" class="w-full border border-gray-300 rounded-lg p-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-gray-500 mb-1">Nama Spesifik (Opsional)</label>
                        <select id="filter-nama" class="w-full border border-gray-300 rounded-lg p-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition">
                            <option value="SEMUA">-- Semua Orang --</option>
                            </select>
                    </div>
                    <div class="flex space-x-2">
                        <button onclick="tarikDataRekap()" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg text-sm transition shadow-sm">
                            <i class="fa-solid fa-magnifying-glass mr-2"></i>Cari
                        </button>
                    </div>
                </div>
            </div>

            <div class="hidden print:block text-center mb-6">
                <h1 class="text-2xl font-bold uppercase">Laporan Presensi</h1>
                <h2 class="text-lg font-semibold text-gray-700">SMK Kota Mungkid</h2>
                <p id="teks-periode-cetak" class="text-sm text-gray-500 mt-1">Periode: -</p>
            </div>

            <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                <div class="bg-slate-100 text-slate-700 p-4 flex justify-between items-center border-b border-gray-200 no-print">
                    <h2 class="font-bold text-md"><i class="fa-solid fa-file-invoice mr-2"></i>Hasil Pencarian</h2>
                    <div class="space-x-2">
                        <button onclick="downloadCSV()" class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded shadow transition">
                            <i class="fa-solid fa-file-excel mr-1"></i> Excel (CSV)
                        </button>
                        <button onclick="window.print()" class="px-3 py-1.5 bg-slate-700 hover:bg-slate-800 text-white text-xs font-bold rounded shadow transition">
                            <i class="fa-solid fa-print mr-1"></i> Cetak A4
                        </button>
                    </div>
                </div>
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse" id="tabel-rekap-utama">
                        <thead class="bg-slate-50 text-slate-500 text-xs uppercase font-bold border-b border-gray-200">
                            <tr>
                                <th class="px-6 py-4">Tanggal</th>
                                <th class="px-6 py-4">Waktu</th>
                                <th class="px-6 py-4">Nama</th>
                                <th class="px-6 py-4">Jenis</th>
                                <th class="px-6 py-4">Status</th>
                            </tr>
                        </thead>
                        <tbody id="tabel-body-rekap" class="text-sm divide-y divide-gray-100">
                            <tr><td colspan="5" class="px-6 py-8 text-center text-gray-400">Silakan atur filter dan klik Cari untuk menampilkan data laporan.</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

    </div>

    <script>
        const SUPABASE_URL = 'https://xgsnzorbquzmzgsgwrfj.supabase.co';
        const SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhnc256b3JicXV6bXpnc2d3cmZqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk2ODQ3NTksImV4cCI6MjA5NTI2MDc1OX0.HcYBj6Cdoo4oyALiL3VxXG6DBqg2HORvBopH8fyysYc';
        const supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

        let mapKaryawan = {}; 
        let dataRekapTersimpan = []; // Menyimpan data sementara untuk fungsi export Excel

        // 1. Jam Digital
        setInterval(() => {
            document.getElementById('jam-digital').innerText = new Date().toLocaleString('id-ID', { dateStyle: 'full', timeStyle: 'medium' }) + ' WIB';
        }, 1000);

        // 2. Perpindahan Tab (Live vs Rekap)
        function bukaTab(namaTab) {
            document.getElementById('tab-live').classList.add('hidden');
            document.getElementById('tab-rekap').classList.add('hidden');
            
            document.getElementById('btn-tab-live').className = 'px-5 py-2 bg-gray-200 text-gray-600 hover:bg-gray-300 font-semibold rounded-t-lg shadow-sm transition';
            document.getElementById('btn-tab-rekap').className = 'px-5 py-2 bg-gray-200 text-gray-600 hover:bg-gray-300 font-semibold rounded-t-lg shadow-sm transition';
            
            if (namaTab === 'live') {
                document.getElementById('tab-live').classList.remove('hidden');
                document.getElementById('btn-tab-live').className = 'px-5 py-2 bg-blue-600 text-white font-semibold rounded-t-lg shadow-sm transition';
            } else {
                document.getElementById('tab-rekap').classList.remove('hidden');
                document.getElementById('btn-tab-rekap').className = 'px-5 py-2 bg-blue-600 text-white font-semibold rounded-t-lg shadow-sm transition';
            }
        }

        // 3. Mengambil Kamus Nama (Tabel Karyawan)
        async function muatDaftarNama() {
            const { data, error } = await supabaseClient.from('karyawan').select('uid_kartu, nama').order('nama', { ascending: true });
            if (!error && data) {
                const selectEl = document.getElementById('filter-nama');
                data.forEach(k => {
                    mapKaryawan[k.uid_kartu] = k.nama; // Menyimpan memori terjemahan UID ke Nama
                    if (k.nama !== "BELUM TERDAFTAR") {
                        selectEl.innerHTML += `<option value="${k.uid_kartu}">${k.nama}</option>`;
                    }
                });
            }
        }

        // 4. Proses Tab LIVE (Berjalan Otomatis)
        async function muatLiveHarian() {
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
                    
                if (error) return;

                const dataAman = data || [];
                document.getElementById('total-tap').innerText = dataAman.length;
                document.getElementById('total-masuk').innerText = dataAman.filter(d => d.jenis_absen === 'Masuk').length;
                document.getElementById('total-pulang').innerText = dataAman.filter(d => d.jenis_absen === 'Pulang').length;
                
                const tabelBody = document.getElementById('tabel-body-live');
                tabelBody.innerHTML = '';
                
                if (dataAman.length === 0) {
                    tabelBody.innerHTML = '<tr><td colspan="4" class="px-6 py-8 text-center text-gray-400 font-medium">Belum ada absen masuk hari ini.</td></tr>';
                    return;
                }
                
                dataAman.forEach(log => {
                    const dateObj = new Date(log.waktu_tap);
                    const waktuText = dateObj.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' }) + ' WIB';
                    const namaAsli = mapKaryawan[log.uid_kartu] || `<span class="text-red-500"><i class="fa-solid fa-triangle-exclamation mr-1"></i>Belum Terdaftar (${log.uid_kartu})</span>`;
                    const badge = log.jenis_absen === 'Masuk' ? 'bg-green-100 text-green-700 border-green-200' : 'bg-orange-100 text-orange-700 border-orange-200';
                    
                    tabelBody.innerHTML += `
                        <tr class="hover:bg-slate-50 transition duration-150">
                            <td class="px-6 py-4 font-mono text-gray-500 font-semibold">${waktuText}</td>
                            <td class="px-6 py-4 font-bold text-slate-700">${namaAsli}</td>
                            <td class="px-6 py-4"><span class="px-3 py-1 rounded-md text-xs font-bold border ${badge}">${log.jenis_absen}</span></td>
                            <td class="px-6 py-4 font-semibold text-blue-600"><i class="fa-regular fa-circle-check mr-1"></i>${log.status}</td>
                        </tr>
                    `;
                });
            } catch (err) { console.log(err); }
        }

        // 5. Proses Tab REKAP (Manual via Tombol Cari)
        async function tarikDataRekap() {
            const tglStart = document.getElementById('filter-start').value;
            const tglEnd = document.getElementById('filter-end').value;
            const uidPilihan = document.getElementById('filter-nama').value;
            const tabelBody = document.getElementById('tabel-body-rekap');

            if(!tglStart || !tglEnd) {
                alert("Juragan, mohon isi Dari Tanggal dan Sampai Tanggal terlebih dahulu!");
                return;
            }

            tabelBody.innerHTML = '<tr><td colspan="5" class="px-6 py-8 text-center text-blue-500"><i class="fa-solid fa-spinner fa-spin mr-2"></i>Sedang menggali database...</td></tr>';
            document.getElementById('teks-periode-cetak').innerText = `Periode: ${tglStart} s/d ${tglEnd}`;

            try {
                let query = supabaseClient.from('log_absensi').select('*')
                            .gte('waktu_tap', `${tglStart}T00:00:00`)
                            .lte('waktu_tap', `${tglEnd}T23:59:59`)
                            .order('waktu_tap', { ascending: true }); // Diurutkan dari terlama ke terbaru untuk laporan

                // Jika memfilter 1 orang saja
                if(uidPilihan !== 'SEMUA') {
                    query = query.eq('uid_kartu', uidPilihan);
                }

                const { data, error } = await query;
                if (error) throw error;

                dataRekapTersimpan = data || [];
                tabelBody.innerHTML = '';

                if (dataRekapTersimpan.length === 0) {
                    tabelBody.innerHTML = '<tr><td colspan="5" class="px-6 py-8 text-center text-gray-500">Tidak ada data absensi pada periode tersebut.</td></tr>';
                    return;
                }

                dataRekapTersimpan.forEach(log => {
                    const dateObj = new Date(log.waktu_tap);
                    const tglText = dateObj.toLocaleDateString('id-ID', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' });
                    const waktuText = dateObj.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' });
                    const namaAsli = mapKaryawan[log.uid_kartu] || log.uid_kartu;

                    tabelBody.innerHTML += `
                        <tr class="hover:bg-slate-50 border-b border-gray-100">
                            <td class="px-6 py-3 text-slate-600">${tglText}</td>
                            <td class="px-6 py-3 font-mono text-slate-500">${waktuText}</td>
                            <td class="px-6 py-3 font-bold text-slate-700">${namaAsli}</td>
                            <td class="px-6 py-3 font-semibold text-slate-600">${log.jenis_absen}</td>
                            <td class="px-6 py-3 text-blue-600">${log.status}</td>
                        </tr>
                    `;
                });
            } catch (err) {
                console.error(err);
                tabelBody.innerHTML = '<tr><td colspan="5" class="px-6 py-8 text-center text-red-500">Gagal menarik data rekap.</td></tr>';
            }
        }

        // 6. Fungsi Download CSV (Excel)
        function downloadCSV() {
            if(dataRekapTersimpan.length === 0) {
                alert("Belum ada data rekap yang ditarik. Silakan klik Cari dulu.");
                return;
            }
            
            // Membuat Header Kolom Excel
            let isiCSV = "Tanggal,Waktu,Nama,Jenis Absen,Status\\n";
            
            dataRekapTersimpan.forEach(log => {
                const dateObj = new Date(log.waktu_tap);
                const tglText = dateObj.toLocaleDateString('id-ID');
                const waktuText = dateObj.toLocaleTimeString('id-ID');
                const namaAsli = mapKaryawan[log.uid_kartu] || log.uid_kartu;
                
                isiCSV += `${tglText},${waktuText},"${namaAsli}",${log.jenis_absen},${log.status}\\n`;
            });

            // Men-trigger unduhan di browser
            const blob = new Blob([isiCSV], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement("a");
            const url = URL.createObjectURL(blob);
            link.setAttribute("href", url);
            link.setAttribute("download", "Laporan_Absensi_SMK.csv");
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }

        // Eksekusi Awal Saat Web Dibuka
        (async function init() {
            // Set tanggal rekap default ke hari ini
            const hariIniLokal = new Date(new Date().getTime() - (new Date().getTimezoneOffset() * 60000)).toISOString().split('T')[0];
            document.getElementById('filter-start').value = hariIniLokal;
            document.getElementById('filter-end').value = hariIniLokal;

            await muatDaftarNama();
            muatLiveHarian();
            setInterval(muatLiveHarian, 5000); // Live update tiap 5 detik
        })();
    </script>
</body>
</html>
"""

# ==========================================
# RUTE SAPU JAGAT & AUTO-SAVE KARTU (TETAP SAMA)
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
            jam = sekarang.hour
            tanggal_hari_ini = sekarang.strftime("%Y-%m-%d")
            
            # ATURAN JAM (Kembali Longgar Untuk Testing)
            if 0 <= jam < 11:
                jenis_absen = "Masuk"
            elif 11 <= jam <= 23:
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