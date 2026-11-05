import os
import json
import logging
from datetime import datetime
import pytz
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load Environment Variables dari file .env
load_dotenv()

# Konfigurasi Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("CRT-Webhook")

app = Flask(__name__)

# Konfigurasi Telegram dari Environment
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
TIMEZONE_STR = os.getenv("TIMEZONE", "Asia/Jakarta")

def kirim_ke_telegram(pesan: str) -> bool:
    """
    Mengirimkan pesan berformat Markdown ke Telegram API.
    """
    if not BOT_TOKEN or not CHAT_ID:
        logger.error("BOT_TOKEN atau CHAT_ID belum disetel di environment!")
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": pesan,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        res_data = response.json()
        if response.status_code == 200 and res_data.get("ok"):
            logger.info("Berhasil mengirim pesan ke Telegram.")
            return True
        else:
            logger.error(f"Gagal mengirim pesan Telegram: {res_data}")
            return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Koneksi ke Telegram API error: {e}")
        return False

def format_pesan_telegram(data: dict) -> str:
    """
    Menyusun template pesan notifikasi yang rapi, profesional, dan kaya emoji.
    """
    simbol = data.get("simbol", "UNKNOWN")
    tf = data.get("tf", "N/A")
    sinyal = data.get("sinyal", "ALERT").upper()
    pesan_tambahan = data.get("pesan", "-")
    harga = data.get("harga", "N/A")

    # Waktu lokal (WIB secara default)
    try:
        tz = pytz.timezone(TIMEZONE_STR)
        waktu_sekarang = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Styling visual berdasarkan jenis sinyal
    if "BUY" in sinyal:
        header_emoji = "🟢🚀"
        badge_sinyal = "🟢 *BUY (SWEEP LOW)*"
        rekomendasi = "Cari konfirmasi *CHoCH / MSS Bullish* di chart M5 sebelum Entry."
    elif "SELL" in sinyal:
        header_emoji = "🔴🔻"
        badge_sinyal = "🔴 *SELL (SWEEP HIGH)*"
        rekomendasi = "Cari konfirmasi *CHoCH / MSS Bearish* di chart M5 sebelum Entry."
    else:
        header_emoji = "⚠️ℹ️"
        badge_sinyal = f"⚪ *{sinyal}*"
        rekomendasi = "Pantau price action lebih lanjut."

    template = (
        f"{header_emoji} *CRT LIQUIDITY SWEEP DETECTED* {header_emoji}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📌 *Simbol:* `{simbol}`\n"
        f"⏱ *Timeframe Acuan:* `{tf}`\n"
        f"🎯 *Arah Sinyal:* {badge_sinyal}\n"
        f"💰 *Harga Terakhir:* `{harga}`\n"
        f"📝 *Keterangan:* {pesan_tambahan}\n"
        f"🕒 *Waktu:* `{waktu_sekarang} ({TIMEZONE_STR})`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💡 *Action Plan M5:*\n"
        f"{rekomendasi}\n"
        f"⚠️ _Gunakan manajemen risiko & Stop Loss ketat!_"
    )
    return template

@app.route("/", methods=["GET"])
def health_check():
    """Endpoint untuk tes apakah server hidup."""
    return jsonify({
        "status": "online",
        "service": "CRT TradingView Webhook to Telegram",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }), 200

@app.route("/test-telegram", methods=["GET"])
def test_telegram():
    """Endpoint bantu untuk memverifikasi bot token & chat id berfungsi."""
    test_msg = "🔔 *Tes Notifikasi Bot CRT Telegram Berhasil!* Server Webhook Anda siap menerima sinyal dari TradingView."
    success = kirim_ke_telegram(test_msg)
    if success:
        return jsonify({"success": True, "message": "Pesan tes berhasil dikirim ke Telegram"}), 200
    else:
        return jsonify({"success": False, "message": "Gagal mengirim ke Telegram. Cek konfigurasi BOT_TOKEN dan CHAT_ID di file .env!"}), 500

@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Endpoint penerima payload Webhook dari TradingView.
    Mendukung format JSON langsung maupun raw text string JSON.
    """
    try:
        # 1. Parsing Body Request
        payload = None
        if request.is_json:
            payload = request.get_json(silent=True)
        
        # Fallback jika TradingView mengirim data sebagai raw string/text/plain
        if not payload:
            raw_data = request.get_data(as_text=True)
            if raw_data:
                try:
                    payload = json.loads(raw_data)
                except json.JSONDecodeError:
                    logger.warning(f"Gagal decode JSON dari raw body: {raw_data}")
                    return jsonify({"status": "error", "message": "Format data bukan JSON yang valid"}), 400

        if not payload or not isinstance(payload, dict):
            logger.warning("Payload kosong atau tidak bertipe objek/dict.")
            return jsonify({"status": "error", "message": "Data payload kosong atau format tidak sesuai"}), 400

        logger.info(f"Menerima payload TradingView: {payload}")

        # 2. Format pesan ramah pembaca
        teks_telegram = format_pesan_telegram(payload)

        # 3. Teruskan ke Telegram
        terkirim = kirim_ke_telegram(teks_telegram)

        if terkirim:
            return jsonify({"status": "success", "message": "Alert berhasil diproses dan dikirim ke Telegram"}), 200
        else:
            return jsonify({"status": "error", "message": "Gagal meneruskan alert ke API Telegram"}), 502

    except Exception as e:
        logger.error(f"Terjadi kesalahan internal pada endpoint webhook: {e}", exc_info=True)
        return jsonify({"status": "error", "message": f"Internal server error: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    logger.info(f"Menjalankan server Webhook di port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
