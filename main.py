import requests

# Konfigurasi: Masukkan semua URL m3u Anda ke dalam list ini
SOURCE_URLS = [
    "https://github.com/apistech/project/blob/c6e25cbd1ce74b8283930227a742149ddf0d73a0/IndihomeTV.m3u",
    "https://raw.githubusercontent.com/dhasap/dhanytv/main/dhanytv.m3u",
    "https://raw.githubusercontent.com/anomnim/anomnim.github.io/main/pl/shareext.m3u"
]

# Masukkan kata kunci nama channel yang ingin disimpan (case-insensitive)
TARGET_CHANNELS = [
    "ANTV",
    "Metro TV",
    "BTV",
    "Berita Satu",
    "MDTV",
    "Berita Satu", 
    "CNN Indonesia", 
    "Kompas TV",
    "Indosiar",
    "TVRI",
    "iNews",
    "TransTV",
    "Trans7"
]

OUTPUT_FILE = "filtered_playlist.m3u"

def filter_m3u():
    # Header wajib untuk file m3u
    filtered_lines = ["#EXTM3U"] 
    total_added_count = 0

    for url in SOURCE_URLS:
        print(f"\nMengunduh playlist dari: {url}")
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Gagal mengunduh dari {url}: {e}")
            continue

        lines = response.text.splitlines()
        
        is_matching_channel = False
        current_channel_block = []
        added_count_per_url = 0

        for line in lines:
            line_stripped = line.strip()
            
            # Abaikan baris kosong
            if not line_stripped:
                continue
                
            # Jika menemukan baris awal channel (#EXTINF)
            if line_stripped.startswith("#EXTINF"):
                # Cek apakah nama channel sesuai dengan target
                if any(channel.lower() in line_stripped.lower() for channel in TARGET_CHANNELS):
                    is_matching_channel = True
                    current_channel_block = [line_stripped] # Mulai menyimpan blok baru
                else:
                    is_matching_channel = False
                    
            # Jika sedang berada di blok channel yang lolos filter
            elif is_matching_channel:
                if line_stripped.startswith("#"):
                    # Menyimpan baris opsi tambahan seperti #EXTVLCOPT, #EXTGRP, dll
                    current_channel_block.append(line_stripped)
                else:
                    # Ini adalah baris URL streaming (tidak diawali '#')
                    current_channel_block.append(line_stripped)
                    
                    # Masukkan seluruh blok channel ke dalam list akhir
                    filtered_lines.extend(current_channel_block)
                    
                    # Reset state untuk mencari channel berikutnya
                    is_matching_channel = False
                    current_channel_block = []
                    
                    added_count_per_url += 1
                    total_added_count += 1
        
        print(f"Berhasil menemukan {added_count_per_url} channel dari sumber ini.")

    # Menyimpan hasil ke file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(filtered_lines))
    
    print(f"\nSelesai! Berhasil memfilter total {total_added_count} channel.")

if __name__ == "__main__":
    filter_m3u()
