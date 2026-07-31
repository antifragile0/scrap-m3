import requests
from urllib.parse import urlparse

# Konfigurasi: Masukkan semua URL m3u sumber Anda ke dalam list ini
SOURCE_URLS = [
    "https://github.com/apistech/project/blob/c6e25cbd1ce74b8283930227a742149ddf0d73a0/IndihomeTV.m3u",
    "https://raw.githubusercontent.com/dhasap/dhanytv/main/dhanytv.m3u",
    "https://raw.githubusercontent.com/anomnim/anomnim.github.io/main/pl/shareext.m3u"
]

# Kosongkan list ini [] jika Anda ingin mengambil SEMUA channel dari dens.tv.
# Atau isi nama channel jika Anda hanya ingin channel dens.tv tertentu (misal: ["Berita Satu", "HBO"])
TARGET_CHANNELS = [] 

OUTPUT_FILE = "filtered_playlist.m3u"

def check_link_active(url, user_agent=None):
    """Fungsi untuk mengecek apakah link streaming aktif (HTTP 200 OK)"""
    headers = {}
    # Gunakan User-Agent asli dari baris EXTVLCOPT jika tersedia
    if user_agent:
        headers['User-Agent'] = user_agent
    else:
        # Fallback User-Agent jika tidak ada di file m3u
        headers['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36"
    
    try:
        # Menggunakan stream=True agar Python hanya memuat header URL, bukan mengunduh video stream-nya
        with requests.get(url, headers=headers, stream=True, timeout=10) as response:
            return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def filter_m3u():
    filtered_lines = ["#EXTM3U"] 
    total_added_count = 0

    for url_source in SOURCE_URLS:
        print(f"\n--- Memproses sumber: {url_source} ---")
        try:
            response = requests.get(url_source, timeout=15)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Gagal mengunduh sumber: {e}")
            continue

        lines = response.text.splitlines()
        
        is_collecting = False
        current_channel_block = []
        current_user_agent = None

        for line in lines:
            line_stripped = line.strip()
            
            if not line_stripped:
                continue
                
            # Saat menemukan awal channel (#EXTINF)
            if line_stripped.startswith("#EXTINF"):
                # Filter Nama Channel (jika TARGET_CHANNELS tidak kosong)
                if TARGET_CHANNELS:
                    if any(channel.lower() in line_stripped.lower() for channel in TARGET_CHANNELS):
                        is_collecting = True
                    else:
                        is_collecting = False
                else:
                    # Jika TARGET_CHANNELS kosong, kita tampung dulu semuanya, nanti difilter dari domain
                    is_collecting = True
                
                if is_collecting:
                    current_channel_block = [line_stripped]
                    current_user_agent = None
                    
            # Jika baris ini adalah bagian dari channel yang sedang ditampung
            elif is_collecting:
                if line_stripped.startswith("#"):
                    current_channel_block.append(line_stripped)
                    # Mencari dan menyimpan User-Agent jika ada di baris ini
                    if "http-user-agent=" in line_stripped.lower():
                        parts = line_stripped.split("http-user-agent=", 1)
                        if len(parts) > 1:
                            current_user_agent = parts[1].strip()
                else:
                    # Baris ini adalah URL streaming
                    stream_url = line_stripped
                    
                    # 1. Validasi Domain (Hanya https://*.dens.tv)
                    parsed_url = urlparse(stream_url)
                    is_dens_tv = (parsed_url.scheme == "https" and parsed_url.netloc.endswith(".dens.tv"))

                    if is_dens_tv:
                        print(f"Menguji link: {parsed_url.netloc}...")
                        
                        # 2. Validasi Link Aktif
                        if check_link_active(stream_url, current_user_agent):
                            print("  -> STATUS: AKTIF (Disimpan)")
                            current_channel_block.append(stream_url)
                            filtered_lines.extend(current_channel_block)
                            total_added_count += 1
                        else:
                            print("  -> STATUS: MATI / ERROR (Dibuang)")
                    
                    # Reset state untuk memindai channel selanjutnya
                    is_collecting = False
                    current_channel_block = []
                    current_user_agent = None

    # Menyimpan hasil akhir ke file m3u
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(filtered_lines))
    
    print(f"\n======================================")
    print(f"SELESAI! Berhasil menyimpan {total_added_count} channel dens.tv yang aktif.")
    print(f"======================================")

if __name__ == "__main__":
    filter_m3u()
