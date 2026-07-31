import requests
from urllib.parse import urlparse

# Konfigurasi: Masukkan semua URL m3u sumber Anda
SOURCE_URLS = [
    "https://raw.githubusercontent.com/apistech/project/c6e25cbd1ce74b8283930227a742149ddf0d73a0/IndihomeTV.m3u",
	"https://raw.githubusercontent.com/mimipipi22/live/refs/heads/main/lelipur",
    "https://raw.githubusercontent.com/dhasap/dhanytv/main/dhanytv.m3u",
    "https://raw.githubusercontent.com/anomnim/anomnim.github.io/main/pl/shareext.m3u"
]

# 1. Filter Nama Channel (Kosongkan [] jika ingin semua nama channel)
TARGET_CHANNELS = [] 

# 2. Filter Kategori/Atribut (Hanya mengambil baris #EXTINF yang mengandung kata-kata ini)
TARGET_GROUPS = ["nasional", "indonesia"]

OUTPUT_FILE = "filtered_playlist.m3u"

def check_link_active(url, user_agent=None):
    """Fungsi untuk mengecek apakah link streaming aktif (HTTP 200 OK)"""
    headers = {}
    if user_agent:
        headers['User-Agent'] = user_agent
    else:
        headers['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36"
    
    try:
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
                line_lower = line_stripped.lower()
                
                # Cek Filter Grup/Atribut (Apakah ada kata "nasional" atau "indonesia")
                matches_group = False
                if TARGET_GROUPS:
                    if any(group in line_lower for group in TARGET_GROUPS):
                        matches_group = True
                else:
                    matches_group = True # Lolos jika list kosong
                    
                # Cek Filter Nama Channel (Opsional)
                matches_channel = False
                if TARGET_CHANNELS:
                    if any(channel.lower() in line_lower for channel in TARGET_CHANNELS):
                        matches_channel = True
                else:
                    matches_channel = True # Lolos jika list kosong
                
                # Channel hanya akan diproses jika memenuhi KEDUA filter di atas
                if matches_group and matches_channel:
                    is_collecting = True
                    current_channel_block = [line_stripped]
                    current_user_agent = None
                else:
                    is_collecting = False
                    
            # Jika baris ini adalah bagian dari channel yang sedang ditampung
            elif is_collecting:
                if line_stripped.startswith("#"):
                    current_channel_block.append(line_stripped)
                    # Mencari dan menyimpan User-Agent jika ada
                    if "http-user-agent=" in line_lower:
                        parts = line_lower.split("http-user-agent=", 1)
                        if len(parts) > 1:
                            current_user_agent = parts[1].strip()
                else:
                    # Baris ini adalah URL streaming
                    stream_url = line_stripped
                    
                    # 1. Validasi Domain (Hanya https://*.dens.tv)
                    parsed_url = urlparse(stream_url)
                    is_dens_tv = (parsed_url.scheme == "https" and parsed_url.netloc.endswith(".dens.tv"))

                    if is_dens_tv:
                        print(f"Mengecek link: {parsed_url.netloc}...")
                        
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

    # Menyimpan hasil akhir
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(filtered_lines))
    
    print(f"\n======================================")
    print(f"SELESAI! Berhasil menyimpan {total_added_count} channel.")
    print(f"======================================")

if __name__ == "__main__":
    filter_m3u()
