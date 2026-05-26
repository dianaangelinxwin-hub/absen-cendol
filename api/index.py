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
# KODINGAN DESAIN WEB (DASHBOARD PROFESIONAL + REKAP BULANAN)
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
        @media print { .no-print { display: none !important; } th { background-color: #2563eb !important; color: white !important; -webkit-print-color-adjust: exact; } }
    </style>
</head>
<body class="bg-slate-50 font-sans text-slate-800">
    <nav class="bg-blue-900 p-4 shadow-lg no-print">
        <div class="container mx-auto flex items-center justify-between">
            <h1 class="font-bold text-xl text-white">SMK KOTA MUNGKID</h1>
            <div id="jam-digital" class="text-blue-200 text-sm font-mono">Memuat Waktu...</div>
        </div>
    </nav>

    <div class="container mx-auto mt-6 px-4">
        <div class="flex space-x-2 mb-6 no-print border-b border-gray-200">
            <button onclick="bukaTab('live')" id="btn-tab-live" class="px-5 py-2 bg-blue-600 text-white font-semibold rounded-t-lg transition">Live</button>
            <button onclick="bukaTab('rekap')" id="btn-tab-rekap" class="px-5 py-2 bg-gray-200 text-gray-600 font-semibold rounded-t-lg transition">Rekap Harian</button>
            <button onclick="bukaTab('bulanan')" id="btn-tab-bulanan" class="px-5 py-2 bg-gray-200 text-gray-600 font-semibold rounded-t-lg transition">Rekap Bulanan</button>
        </div>

        <div id="tab-live" class="print-area">
            <div class="bg-white rounded-xl shadow-sm p-6 mb-6">
                <table class="w-full">
                    <thead class="text-slate-500 text-xs uppercase border-b"><tr><th class="py-3">Waktu</th><th class="py-3">Nama</th><th class="py-3">Jenis</th></tr></thead>
                    <tbody id="tabel-body-live" class="divide-y text-sm"></tbody>
                </table>
            </div>
        </div>

        <div id="tab-rekap" class="hidden print-area">
            <div class="bg-white p-5 rounded-xl shadow-sm mb-6 no-print flex gap-4 items-end">
                <div><label class="text-xs">Dari</label><input type="date" id="filter-start" class="border rounded p-2 w-full"></div>
                <div><label class="text-xs">Sampai</label><input type="date" id="filter-end" class="border rounded p-2 w-full"></div>
                <button onclick="tarikDataRekap()" class="bg-blue-600 text-white px-4 py-2 rounded">Cari</button>
            </div>
            <table class="w-full bg-white rounded-xl shadow-sm border-collapse">
                <thead class="bg-blue-600 text-white text-sm"><tr><th class="p-3">Tanggal</th><th class="p-3">Nama</th><th class="p-3">Datang</th><th class="p-3">Pulang</th></tr></thead>
                <tbody id="tabel-body-rekap" class="text-sm text-center"></tbody>
            </table>
        </div>

        <div id="tab-bulanan" class="hidden">
            <div class="bg-white p-5 rounded-xl shadow-sm mb-6 flex gap-4 items-end">
                <div><label class="text-xs">Pilih Bulan</label><input type="month" id="filter-bulan" class="border rounded p-2"></div>
                <button onclick="tarikDataBulanan()" class="bg-blue-600 text-white px-4 py-2 rounded">Lihat Statistik</button>
            </div>
            <table class="w-full bg-white rounded-xl shadow-sm">
                <thead class="bg-blue-600 text-white text-sm"><tr><th class="p-3">Nama</th><th class="p-3">Total Masuk</th><th class="p-3">Total Pulang</th></tr></thead>
                <tbody id="tabel-body-bulanan" class="text-sm text-center divide-y"></tbody>
            </table>
        </div>
    </div>

    <script>
        const supabaseClient = window.supabase.createClient('https://xgsnzorbquzmzgsgwrfj.supabase.co', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inhnc256b3JicXV6bXpnc2d3cmZqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk2ODQ3NTksImV4cCI6MjA5NTI2MDc1OX0.HcYBj6Cdoo4oyALiL3VxXG6DBqg2HORvBopH8fyysYc');
        let mapKaryawan = {};

        async function tarikDataBulanan() {
            const bulan = document.getElementById('filter-bulan').value;
            const tabel = document.getElementById('tabel-body-bulanan');
            const { data } = await supabaseClient.from('log_absensi').select('*').gte('waktu_tap', bulan+'-01').lte('waktu_tap', bulan+'-31');
            
            let stats = {};
            data.forEach(log => {
                if(!stats[log.uid_kartu]) stats[log.uid_kartu] = {masuk: 0, pulang: 0};
                if(log.jenis_absen === 'Masuk') stats[log.uid_kartu].masuk++;
                else stats[log.uid_kartu].pulang++;
            });

            tabel.innerHTML = '';
            for(let uid in stats) {
                tabel.innerHTML += `<tr><td class="p-3">${mapKaryawan[uid] || uid}</td><td class="p-3 font-bold text-green-600">${stats[uid].masuk}</td><td class="p-3 font-bold text-orange-600">${stats[uid].pulang}</td></tr>`;
            }
        }
        // ... (Fungsi bukaTab dan fungsi lainnya tetap sama)
        function bukaTab(id) {
            ['tab-live', 'tab-rekap', 'tab-bulanan'].forEach(t => document.getElementById(t).classList.add('hidden'));
            document.getElementById('tab-' + id).classList.remove('hidden');
        }
        // Inisialisasi awal...
        (async function init() { await muatDaftarNama(); muatLiveHarian(); })();
        async function muatDaftarNama() { const { data } = await supabaseClient.from('karyawan').select('*'); data.forEach(k => mapKaryawan[k.uid_kartu] = k.nama); }
        async function muatLiveHarian() { /* logika sama */ }
        async function tarikDataRekap() { /* logika sama */ }
    </script>
</body>
</html>
"""

# Rute Flask...
@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'OPTIONS'])
@app.route('/<path:path>', methods=['GET', 'POST', 'OPTIONS'])
def rute_master(path):
    # Logika POST dan GET sama seperti sebelumnya
    return render_template_string(HTML_DASHBOARD)

if __name__ == '__main__': app.run(debug=True)