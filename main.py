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
    # Header wajib untuk file m3u (hanya ditulis satu kali di bagian paling atas)
    filtered_lines = ["#EXTM3U"] 
    total_added_count = 0

    # Melakukan pengulangan untuk setiap URL di dalam SOURCE_URLS
    for url in SOURCE_URLS:
        print(f"\nMengunduh playlist dari: {url}")
        try:
            # Menambahkan timeout 15 detik agar skrip tidak hang jika server sumber mati
            response = requests.get(url, timeout=15)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Gagal mengunduh dari {url}: {e}")
            continue # Lanjut ke URL berikutnya jika URL ini gagal

        lines = response.text.splitlines()
        keep_next_line = False
        added_count_per_url = 0

        for line in lines:
            if line.startswith("#EXTINF"):
                # Mengecek apakah ada nama channel dari TARGET_CHANNELS di baris ini
                if any(channel.lower() in line.lower() for channel in TARGET_CHANNELS):
                    filtered_lines.append(line)
                    keep_next_line = True
                    added_count_per_url += 1
                    total_added_count += 1
                else:
                    keep_next_line = False
            # Menyimpan baris URL streaming
            elif keep_next_line and line.strip() and not line.startswith("#"):
                filtered_lines.append(line)
                keep_next_line = False
        
        print(f"Berhasil menemukan {added_count_per_url} channel dari sumber ini.")

    # Menyimpan semua hasil gabungan ke file baru
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(filtered_lines))
    
    print(f"\nSelesai! Berhasil memfilter total {total_added_count} channel dari {len(SOURCE_URLS)} sumber.")

if __name__ == "__main__":
    filter_m3u()
