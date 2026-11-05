# 📊 Sistem Notifikasi Bot CRT (Candle Range Theory) Liquidity Sweep: TradingView ke Telegram

Proyek ini menyediakan solusi terpadu (All-in-One) untuk mendeteksi sinyal **Candle Range Theory (CRT) Liquidity Sweep** secara Multi-Timeframe (H1 & H4) pada chart time-frame rendah (M5) di TradingView, lalu meneruskannya secara otomatis ke **Telegram** menggunakan Webhook Server berbasis Python Flask.

---

## 📁 Struktur Direktori

```text
d:\Dokumen\XAU\
├── crt_screener.pine     # Script Indikator TradingView V5 (Anti-Repainting)
├── webhook_server.py     # Server Webhook Flask penerima alert TV & pengirim Telegram
├── requirements.txt      # Dependensi Python
├── Procfile              # Konfigurasi deploy cloud (Render / Railway)
├── .env.example          # Contoh variabel lingkungan (Token Bot & Chat ID)
└── README.md             # Panduan lengkap instalasi dan konfigurasi
```

---

## 🛠️ Komponen 1: Indikator TradingView V5 (`crt_screener.pine`)

### Logika & Aturan Strategi:
1. **Filter Ekspansi Candle Acuan (`index [2]`):**
   - Bukan Doji.
   - Ukuran *Body* minimal **60%** dari total range (`High - Low`).
2. **Setup SELL (Sweep High):**
   - Candle Acuan Bullish & Ekspansi.
   - Candle Trigger (`index [1]`) menembus `High` Acuan (`High > High Acuan`).
   - Candle Trigger **Close** di bawah `High` Acuan dan di atas `Low` Acuan (*Sweep High* terkonfirmasi).
3. **Setup BUY (Sweep Low):**
   - Candle Acuan Bearish & Ekspansi.
   - Candle Trigger (`index [1]`) menembus `Low` Acuan (`Low < Low Acuan`).
   - Candle Trigger **Close** di atas `Low` Acuan dan di bawah `High` Acuan (*Sweep Low* terkonfirmasi).
4. **Anti-Repainting MTF:**
   - Memakai custom function `f_cek_crt()` dengan `lookahead_off`.
   - Mengambil indeks `[2]` dan `[1]` dari candle higher timeframe yang **100% sudah closed**.
   - Mengecek transisi bar (`ta.change(htf_time) != 0`) agar sinyal M5 hanya dikirim **1x tepat saat candle H1/H4 ditutup**.

---

## 🐍 Komponen 2: Webhook Server Python (`webhook_server.py`)

### Fitur Utama:
- Framework Flask yang ringan dan cepat.
- Endpoint `POST /webhook` menerima payload JSON dari TradingView.
- Format pesan Telegram otomatis dan rapi dengan emoji, arah sinyal, harga, timeframe, dan action plan M5.
- Dilengkapi endpoint pengecekan:
  - `GET /` : Health check status server.
  - `GET /test-telegram` : Menguji apakah Bot Telegram berhasil mengirim pesan sebelum menghubungkannya ke TradingView.
- Penanganan error (*error handling*) tangguh terhadap request malformed atau koneksi timeout.

---

## 🚀 Panduan Pengaturan & Deployment

Lihat instruksi lengkap di pesan chat untuk panduan pembuatan bot Telegram, hosting server di Render.com, dan pengaturan Alert TradingView.
