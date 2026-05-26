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
            th { background-color: #2563eb !important; color: white !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
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
        
        <div class="flex space-x-2 mb-6 no-print border-b border-gray-200 pb-2 overflow-x-auto">
            <button onclick="bukaTab('live')" id="btn-tab-live" class="px-5 py-2 bg-blue-600 text-white font-semibold rounded-t-lg shadow-sm transition whitespace-nowrap">
                <i class="fa-solid fa-desktop mr-2"></i>Live Monitor
            </button>
            <button onclick="bukaTab('rekap')" id="btn-tab-rekap" class="px-5 py-2 bg-gray-200 text-gray-600 hover:bg-gray-300 font-semibold rounded-t-lg shadow-sm transition whitespace-nowrap">
                <i class="fa-solid fa-calendar-day mr-2"></i>Rekap Harian
            </button>
            <button onclick="bukaTab('bulanan')" id="btn-tab-bulanan" class="px-5 py-2 bg-gray-200 text-gray-600 hover:bg-gray-300 font-semibold rounded-t-lg shadow-sm transition whitespace-nowrap">
                <i class="fa-solid fa-calendar-days mr-2"></i>Rekap Bulanan
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
                <h2 class="font-bold text-slate-700 mb-4 text-sm uppercase tracking-wide border-b pb-2"><i class="fa-solid fa-filter mr-2"></i>Filter Laporan Harian</h2>
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
                <h1 class="text-2xl font-bold uppercase">Laporan Presensi Harian</h1>
                <h2 class="text-lg font-semibold text-gray-700">SMK Kota Mungkid</h2>
                <p id="teks-periode-cetak" class="text-sm text-gray-500 mt-1">Periode: -</p>
            </div>

            <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                <div class="bg-slate-100 text-slate-700 p-4 flex justify-between items-center border-b border-gray-200 no-print">
                    <h2 class="font-bold text-md"><i class="fa-solid fa-file-invoice mr-2"></i>Hasil Pencarian</h2>
                    <div class="space-x-2">
                        <button onclick="downloadCSV()" class="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded shadow transition">
                            <i class="fa-solid fa-file-excel mr-1"></i> Excel
                        </button>
                        <button onclick="window.print()" class="px-3 py-1.5 bg-slate-700 hover:bg-slate-800 text-white text-xs font-bold rounded shadow transition">
                            <i class="fa-solid fa-print mr-1"></i> Cetak A4
                        </button>
                    </div>
                </div>
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse" id="tabel-rekap-utama">
                        <thead class="bg-blue-600 text-white text-xs uppercase font-bold border-b border-blue-700">
                            <tr>
                                <th class="px-4 py-3">No</th>
                                <th class="px-4 py-3">Hari dan Tanggal</th>
                                <th class="px-4 py-3">Nama</th>
                                <th class="px-4 py-3 text-center">Jam Datang</th>
                                <th class="px-4 py-3 text-center">Jam Pulang</th>
                                <th class="px-4 py-3 text-center">Status</th>
                            </tr>
                        </thead>
                        <tbody id="tabel-body-rekap" class="text-sm divide-y divide-gray-100">
                            <tr><td colspan="6" class="px-6 py-8 text-center text-gray-400">Silakan atur filter dan klik Cari untuk menampilkan laporan.</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <div id="tab-bulanan" class="hidden print-area">
            <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100 mb-6 no-print">
                <h2 class="font-bold text-slate-700 mb-4 text-sm uppercase tracking-wide border-b pb-2"><i class="fa-solid fa-filter mr-2"></i>Filter Laporan Bulanan</h2>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
                    <div>
                        <label class="block text-xs font-semibold text-gray-500 mb-1">Pilih Bulan</label>
                        <input type="month" id="filter-bulan" class="w-full border border-gray-300 rounded-lg p-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition">
                    </div>
                    <div class="flex space-x-2">
                        <button onclick="tarikDataBulanan()" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded-lg text-sm transition shadow-sm">
                            <i class="fa-solid fa-chart-pie mr-2"></i>Lihat Statistik
                        </button>
                    </div>
                </div>
            </div>

            <div class="hidden print:block text-center mb-6">
                <h1 class="text-2xl font-bold uppercase">Laporan Presensi Bulanan</h1>
                <h2 class="text-lg font-semibold text-gray-700">SMK Kota Mungkid</h2>
                <p id="teks-bulan-cetak" class="text-sm text-gray-500 mt-1">Bulan: -</p>
            </div>

            <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
                <div class="bg-slate-100 text-slate-700 p-4 flex justify-between items-center border-b border-gray-200 no-print">
                    <h2 class="font-bold text-md"><i class="fa-solid fa-chart-column mr-2"></i>Statistik Kehadiran Bulanan</h2>
                    <button onclick="window.print()" class="px-3 py-1.5 bg-slate-700 hover:bg-slate-800 text-white text-xs font-bold rounded shadow transition">
                        <i class="fa-solid fa-print mr-1"></i> Cetak A4
                    </button>
                </div>
                <div class="overflow-x-auto">
                    <table class="w-full text-left border-collapse">
                        <thead class="bg-blue-600 text-white text-xs uppercase font-bold border-b border-blue-700">
                            <tr>
                                <th class="px-6 py-3 w-16">No</th>
                                <th class="px-6 py-3">Nama Siswa/Karyawan</th>
                                <th class="px-6 py-3 text-center">Total Masuk (Hari)</th>
                                <th class="px-6 py-3 text-center">Total Pulang (Hari)</th>
                            </tr>
                        </thead>
                        <tbody id="tabel-body-bulanan" class="text-sm divide-y divide-gray-100">
                            <tr><td colspan="4" class="px-6 py-8 text-center text-gray-400">Silakan pilih bulan dan klik Lihat Statistik.</td></tr>
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
        let dataSiapCetak = []; 

        setInterval(() => {
            document.getElementById('jam-digital').innerText = new Date().toLocaleString('id-ID', { dateStyle: 'full', timeStyle: 'medium' }) + ' WIB';
        }, 1000);

        function bukaTab(namaTab) {
            document.getElementById('tab-live').classList.add('hidden');
            document.getElementById('tab-rekap').classList.add('hidden');
            document.getElementById('tab-bulanan').classList.add('hidden');
            
            document.getElementById('btn-tab-live').className = 'px-5 py-2 bg-gray-200 text-gray-600 hover:bg-gray-300 font-semibold rounded-t-lg shadow-sm transition whitespace-nowrap';
            document.getElementById('btn-tab-rekap').className = 'px-5 py-2 bg-gray-200 text-gray-600 hover:bg-gray-300 font-semibold rounded-t-lg shadow-sm transition whitespace-nowrap';
            document.getElementById('btn-tab-bulanan').className = 'px-5 py-2 bg-gray-200 text-gray-600 hover:bg-gray-300 font-semibold rounded-t-lg shadow-sm transition whitespace-nowrap';
            
            if (namaTab === 'live') {
                document.getElementById('tab-live').classList.remove('hidden');
                document.getElementById('btn-tab-live').className = 'px-5 py-2 bg-blue-600 text-white font-semibold rounded-t-lg shadow-sm transition whitespace-nowrap';
            } else if (namaTab === 'rekap') {
                document.getElementById('tab-rekap').classList.remove('hidden');
                document.getElementById('btn-tab-rekap').className = 'px-5 py-2 bg-blue-600 text-white font-semibold rounded-t-lg shadow-sm transition whitespace-nowrap';
            } else {
                document.getElementById('tab-bulanan').classList.remove('hidden');
                document.getElementById('btn-tab-bulanan').className = 'px-5 py-2 bg-blue-600 text-white font-semibold rounded-t-lg shadow-sm transition whitespace-nowrap';
            }
        }

        async function muatDaftarNama() {
            const { data, error } = await supabaseClient.from('karyawan').select('uid_kartu, nama').order('nama', { ascending: true });
            if (!error && data) {
                const selectEl = document.getElementById('filter-nama');
                data.forEach(k => {
                    mapKaryawan[k.uid_kartu] = k.nama;
                    if (k.nama !== "BELUM TERDAFTAR") {
                        selectEl.innerHTML += `<option value="${k.uid_kartu}">${k.nama}</option>`;
                    }
                });
            }
        }

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

        async function tarikDataRekap() {
            const tglStart = document.getElementById('filter-start').value;
            const tglEnd = document.getElementById('filter-end').value;
            const uidPilihan = document.getElementById('filter-nama').value;
            const tabelBody = document.getElementById('tabel-body-rekap');

            if(!tglStart || !tglEnd) {
                alert("Juragan, mohon isi Dari Tanggal dan Sampai Tanggal terlebih dahulu!");
                return;
            }

            tabelBody.innerHTML = '<tr><td colspan="6" class="px-6 py-8 text-center text-blue-500"><i class="fa-solid fa-spinner fa-spin mr-2"></i>Sedang menyusun laporan 1 baris...</td></tr>';
            
            const dateS = new Date(tglStart); const dateE = new Date(tglEnd);
            document.getElementById('teks-periode-cetak').innerText = `Periode: ${dateS.toLocaleDateString('id-ID')} s/d ${dateE.toLocaleDateString('id-ID')}`;

            try {
                let query = supabaseClient.from('log_absensi').select('*')
                            .gte('waktu_tap', `${tglStart}T00:00:00`)
                            .lte('waktu_tap', `${tglEnd}T23:59:59`)
                            .order('waktu_tap', { ascending: true });

                if(uidPilihan !== 'SEMUA') {
                    query = query.eq('uid_kartu', uidPilihan);
                }

                const { data, error } = await query;
                if (error) throw error;

                const dataMentah = data || [];
                tabelBody.innerHTML = '';

                if (dataMentah.length === 0) {
                    tabelBody.innerHTML = '<tr><td colspan="6" class="px-6 py-8 text-center text-gray-500">Tidak ada data absensi pada periode tersebut.</td></tr>';
                    return;
                }

                const groupedObj = {};
                const namaHari = ['Minggu', 'Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu'];
                
                dataMentah.forEach(log => {
                    const dateObj = new Date(log.waktu_tap);
                    const tglSort = dateObj.toISOString().split('T')[0]; 
                    const namaHariIni = namaHari[dateObj.getDay()];
                    const tglText = `${namaHariIni}, ${dateObj.toLocaleDateString('id-ID', { day: '2-digit', month: '2-digit', year: 'numeric' })}`;
                    const waktuText = dateObj.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
                    const namaAsli = mapKaryawan[log.uid_kartu] || log.uid_kartu;
                    
                    const key = log.uid_kartu + "_" + tglSort;

                    if(!groupedObj[key]) {
                        groupedObj[key] = {
                            tglSort: tglSort,
                            tanggal: tglText,
                            nama: namaAsli,
                            datang: '-',
                            pulang: '-'
                        };
                    }

                    if(log.jenis_absen === 'Masuk') {
                        groupedObj[key].datang = waktuText;
                    } else if (log.jenis_absen === 'Pulang') {
                        groupedObj[key].pulang = waktuText;
                    }
                });

                dataSiapCetak = Object.values(groupedObj).sort((a, b) => a.tglSort.localeCompare(b.tglSort));

                let noUrut = 1;
                dataSiapCetak.forEach(item => {
                    let statusCetak = "";
                    let warnaStatus = "";
                    
                    if (item.datang !== '-' && item.pulang !== '-') {
                        statusCetak = "Datang & Pulang";
                        warnaStatus = "text-green-600 bg-green-50 px-2 py-1 rounded-full border border-green-200";
                    } else if (item.datang !== '-' && item.pulang === '-') {
                        statusCetak = "Datang Saja";
                        warnaStatus = "text-blue-600 bg-blue-50 px-2 py-1 rounded-full border border-blue-200";
                    } else if (item.datang === '-' && item.pulang !== '-') {
                        statusCetak = "Pulang Saja";
                        warnaStatus = "text-orange-600 bg-orange-50 px-2 py-1 rounded-full border border-orange-200";
                    }

                    tabelBody.innerHTML += `
                        <tr class="hover:bg-slate-50 border-b border-gray-100">
                            <td class="px-4 py-3 text-slate-500">${noUrut++}</td>
                            <td class="px-4 py-3 text-slate-700">${item.tanggal}</td>
                            <td class="px-4 py-3 font-bold text-slate-800">${item.nama}</td>
                            <td class="px-4 py-3 text-center font-mono text-slate-600">${item.datang}</td>
                            <td class="px-4 py-3 text-center font-mono text-slate-600">${item.pulang}</td>
                            <td class="px-4 py-3 text-center"><span class="text-xs font-bold ${warnaStatus}">${statusCetak}</span></td>
                        </tr>
                    `;
                });

            } catch (err) {
                console.error(err);
                tabelBody.innerHTML = '<tr><td colspan="6" class="px-6 py-8 text-center text-red-500">Gagal menarik data rekap.</td></tr>';
            }
        }

        async function tarikDataBulanan() {
            const blnValue = document.getElementById('filter-bulan').value;
            const tabelBody = document.getElementById('tabel-body-bulanan');

            if(!blnValue) {
                alert("Juragan, pilih bulannya dulu ya!");
                return;
            }

            tabelBody.innerHTML = '<tr><td colspan="4" class="px-6 py-8 text-center text-blue-500"><i class="fa-solid fa-spinner fa-spin mr-2"></i>Menghitung statistik bulanan...</td></tr>';
            
            const namaBulan = new Date(blnValue + "-01").toLocaleDateString('id-ID', { month: 'long', year: 'numeric' });
            document.getElementById('teks-bulan-cetak').innerText = `Bulan: ${namaBulan}`;

            try {
                const arrTgl = blnValue.split('-');
                const yyyy = arrTgl[0];
                const mm = arrTgl[1];
                const lastDay = new Date(yyyy, mm, 0).getDate(); 
                
                const startStr = `${blnValue}-01T00:00:00`;
                const endStr = `${blnValue}-${lastDay}T23:59:59`;

                const { data, error } = await supabaseClient.from('log_absensi')
                    .select('*')
                    .gte('waktu_tap', startStr)
                    .lte('waktu_tap', endStr);
                    
                if (error) throw error;

                const dataMentah = data || [];
                tabelBody.innerHTML = '';

                if (dataMentah.length === 0) {
                    tabelBody.innerHTML = '<tr><td colspan="4" class="px-6 py-8 text-center text-gray-500">Tidak ada absensi di bulan ini.</td></tr>';
                    return;
                }

                let stats = {};
                
                dataMentah.forEach(log => {
                    const uid = log.uid_kartu;
                    if(!stats[uid]) {
                        stats[uid] = { 
                            nama: mapKaryawan[uid] || uid, 
                            masuk: 0, 
                            pulang: 0 
                        };
                    }
                    if(log.jenis_absen === 'Masuk') stats[uid].masuk++;
                    else if (log.jenis_absen === 'Pulang') stats[uid].pulang++;
                });

                const arrStats = Object.values(stats).sort((a, b) => a.nama.localeCompare(b.nama));
                
                let noUrut = 1;
                arrStats.forEach(item => {
                    tabelBody.innerHTML += `
                        <tr class="hover:bg-slate-50 border-b border-gray-100">
                            <td class="px-6 py-3 text-slate-500">${noUrut++}</td>
                            <td class="px-6 py-3 font-bold text-slate-800">${item.nama}</td>
                            <td class="px-6 py-3 text-center font-bold text-green-600">${item.masuk}</td>
                            <td class="px-6 py-3 text-center font-bold text-orange-600">${item.pulang}</td>
                        </tr>
                    `;
                });

            } catch(err) {
                console.error(err);
                tabelBody.innerHTML = '<tr><td colspan="4" class="px-6 py-8 text-center text-red-500">Gagal menarik data bulanan.</td></tr>';
            }
        }

        function downloadCSV() {
            if(dataSiapCetak.length === 0) {
                alert("Belum ada data rekap yang ditarik. Silakan klik Cari dulu.");
                return;
            }
            
            let isiCSV = "No,Hari Tanggal,Nama,Jam Datang,Jam Pulang,Status\\n";
            let noCSV = 1;
            
            dataSiapCetak.forEach(item => {
                let statusCetak = "";
                if (item.datang !== '-' && item.pulang !== '-') statusCetak = "Datang & Pulang";
                else if (item.datang !== '-' && item.pulang === '-') statusCetak = "Datang Saja";
                else if (item.datang === '-' && item.pulang !== '-') statusCetak = "Pulang Saja";

                isiCSV += `${noCSV++},"${item.tanggal}","${item.nama}",${item.datang},${item.pulang},${statusCetak}\\n`;
            });

            const blob = new Blob([isiCSV], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement("a");
            const url = URL.createObjectURL(blob);
            link.setAttribute("href", url);
            link.setAttribute("download", "Laporan_Absensi_Harian.csv");
            link.style.visibility = 'hidden';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }

        (async function init() {
            const hariIniLokal = new Date(new Date().getTime() - (new Date().getTimezoneOffset() * 60000)).toISOString().split('T')[0];
            document.getElementById('filter-start').value = hariIniLokal;
            document.getElementById('filter-end').value = hariIniLokal;
            
            const blnLokal = hariIniLokal.substring(0, 7); // Format YYYY-MM
            document.getElementById('filter-bulan').value = blnLokal;

            await muatDaftarNama();
            muatLiveHarian();
            setInterval(muatLiveHarian, 5000); 
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
            
            # ATURAN JAM (Longgar Untuk Testing)
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