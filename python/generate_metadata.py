import os
import json
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
# IMPORT BARU UNTUK M4A
from mutagen.mp4 import MP4, MP4Tags
from mutagen.id3 import ID3NoHeaderError

# --- Konfigurasi (Tidak ada perubahan di sini) ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))

AUDIO_DIRECTORY = os.path.join(PROJECT_ROOT, "TTML")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "json")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "metadata.json")

GITHUB_BASE_URL = "https://raw.githubusercontent.com/Ramadani1t/DB-TTML-ID/main/"
# --------------------

def get_song_metadata(filepath):
    """Membaca metadata ID3/MP4 dari sebuah file MP3 atau M4A."""
    
    # Menentukan class yang akan digunakan berdasarkan ekstensi file
    file_extension = os.path.splitext(filepath)[1].lower()

    try:
        if file_extension == '.m4a':
            # Gunakan mutagen.mp4.MP4 untuk file M4A
            audio = MP4(filepath)
            
            # Metadata MP4 menggunakan key khusus (contoh: '\xa9nam' untuk title)
            # Karena EasyID3 tidak bekerja di sini, kita harus memetakan secara manual
            tags = {}
            if audio.tags:
                tags['title'] = audio.tags.get('\xa9nam', [''])[0]
                tags['artist'] = audio.tags.get('\xa9ART', [''])[0]
                tags['album'] = audio.tags.get('\xa9alb', [''])[0]
            else:
                return None
            
        elif file_extension == '.mp3':
            # Gunakan mutagen.mp3.MP3 (dengan EasyID3) untuk file MP3
            audio = MP3(filepath, ID3=EasyID3)
            tags = audio.tags
            if tags is None:
                return None

        else:
            # Lewati file dengan ekstensi yang tidak didukung
            return None

        # Ambil data metadata dari dictionary 'tags'
        title = tags.get('title', [''])[0]
        artist = tags.get('artist', [''])[0]
        album = tags.get('album', [''])[0] 
        
        # Penanganan khusus untuk MP3/EasyID3, tags sudah string (tidak perlu [''][0])
        # Ini mencegah error jika EasyID3 digunakan (tapi seharusnya sudah ditangani di atas)
        if file_extension == '.mp3':
            title = tags.get('title', [''])[0] if isinstance(tags.get('title'), list) else tags.get('title', '')
            artist = tags.get('artist', [''])[0] if isinstance(tags.get('artist'), list) else tags.get('artist', '')
            album = tags.get('album', [''])[0] if isinstance(tags.get('album'), list) else tags.get('album', '')
        
        # Jika title atau artist tidak ditemukan, lewati
        if not title or not artist:
            return None
            
        return {
            "title": str(title),  # Pastikan semua output adalah string
            "artist": str(artist),
            "album": str(album)
        }
    except ID3NoHeaderError:
        print(f"File tidak memiliki header ID3: {filepath}")
        return None
    except Exception as e:
        print(f"Error saat memproses file {filepath}: {e}")
        return None

# --- Fungsi main() (Tidak ada perubahan signifikan, hanya menyatukan kode) ---

def main():
    """Fungsi utama untuk scan folder, baca metadata, dan buat file JSON."""
    all_metadata = []
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    for root, _, files in os.walk(AUDIO_DIRECTORY):
        for filename in files:
            # Perhatikan: daftar ekstensi yang dicari di sini sudah benar
            if filename.lower().endswith(('.mp3', '.m4a')):
                filepath = os.path.join(root, filename)
                metadata = get_song_metadata(filepath)
                
                if metadata:
                    relative_path = os.path.relpath(root, PROJECT_ROOT).replace(os.sep, '/')
                    metadata['path'] = relative_path
                    
                    # Membuat path file relatif untuk URL
                    relative_file_path = os.path.relpath(filepath, PROJECT_ROOT).replace(os.sep, '/')
                    file_url = f"{GITHUB_BASE_URL}{relative_file_path.replace(' ', '%20')}"
                    metadata['audio_link'] = file_url
                    
                    # Cari file lirik (.ttml atau .lrc) yang namanya sama
                    base_name = os.path.splitext(filepath)[0]
                    lrc_file = base_name + ".lrc"
                    ttml_file = base_name + ".ttml"
                    
                    metadata['lirik_link'] = ""
                    
                    if os.path.exists(ttml_file):
                        relative_lirik_path = os.path.relpath(ttml_file, PROJECT_ROOT).replace(os.sep, '/')
                        metadata['lirik_link'] = f"{GITHUB_BASE_URL}{relative_lirik_path.replace(' ', '%20')}"
                    elif os.path.exists(lrc_file):
                        relative_lirik_path = os.path.relpath(lrc_file, PROJECT_ROOT).replace(os.sep, '/')
                        metadata['lirik_link'] = f"{GITHUB_BASE_URL}{relative_lirik_path.replace(' ', '%20')}"
                        
                    all_metadata.append(metadata)

    all_metadata.sort(key=lambda x: (x['artist'].lower(), x['title'].lower()))

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_metadata, f, indent=4, ensure_ascii=False)
        
    print(f"✅ Berhasil! File '{OUTPUT_FILE}' telah dibuat dengan {len(all_metadata)} lagu.")

if __name__ == "__main__":
    main()
