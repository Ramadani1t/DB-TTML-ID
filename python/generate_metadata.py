import os
import json
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3NoHeaderError

# --- Konfigurasi ---
# Mendeteksi path absolut dari direktori tempat skrip ini berada
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Mendapatkan path root proyek (satu level di atas folder 'python')
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))

# Path diatur relatif terhadap root proyek
AUDIO_DIRECTORY = os.path.join(PROJECT_ROOT, "TTML")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "json")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "metadata.json")

# URL dasar untuk link di GitHub (tetap sama)
GITHUB_BASE_URL = "https://github.com/Ramadani1t/DB-TTML-ID/blob/main/"
# --------------------

def get_song_metadata(filepath):
    """Membaca metadata ID3 dari sebuah file MP3."""
    try:
        audio = MP3(filepath, ID3=EasyID3)
        if audio.tags is None:
            return None
        
        title = audio.tags.get('title', [''])[0]
        artist = audio.tags.get('artist', [''])[0]
        album = audio.tags.get('album', [''])[0] # Menambahkan pengambilan data album
        
        if not title or not artist:
            return None
            
        return {
            "title": title,
            "artist": artist,
            "album": album
        }
    except ID3NoHeaderError:
        print(f"File tidak memiliki header ID3: {filepath}")
        return None
    except Exception as e:
        print(f"Error saat memproses file {filepath}: {e}")
        return None

def main():
    """Fungsi utama untuk scan folder, baca metadata, dan buat file JSON."""
    all_metadata = []
    
    # Memastikan folder output 'json' ada, jika tidak, maka buat folder tersebut
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Berjalan melalui semua file di direktori TTML
    for root, _, files in os.walk(AUDIO_DIRECTORY):
        for filename in files:
            if filename.lower().endswith(('.mp3', '.m4a')):
                filepath = os.path.join(root, filename)
                metadata = get_song_metadata(filepath)
                
                if metadata:
                    # Mengambil path relatif dari folder TTML (contoh: TTML/NewJeans)
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
                    
                    # Default lirik_link adalah string kosong
                    metadata['lirik_link'] = ""
                    
                    if os.path.exists(ttml_file):
                        relative_lirik_path = os.path.relpath(ttml_file, PROJECT_ROOT).replace(os.sep, '/')
                        metadata['lirik_link'] = f"{GITHUB_BASE_URL}{relative_lirik_path.replace(' ', '%20')}"
                    elif os.path.exists(lrc_file):
                        relative_lirik_path = os.path.relpath(lrc_file, PROJECT_ROOT).replace(os.sep, '/')
                        metadata['lirik_link'] = f"{GITHUB_BASE_URL}{relative_lirik_path.replace(' ', '%20')}"
                        
                    all_metadata.append(metadata)

    # Mengurutkan daftar lagu berdasarkan artis, lalu judul
    all_metadata.sort(key=lambda x: (x['artist'].lower(), x['title'].lower()))

    # Tulis semua metadata yang terkumpul ke dalam file JSON
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_metadata, f, indent=4, ensure_ascii=False)
        
    print(f"✅ Berhasil! File '{OUTPUT_FILE}' telah dibuat dengan {len(all_metadata)} lagu.")

if __name__ == "__main__":
    main()
