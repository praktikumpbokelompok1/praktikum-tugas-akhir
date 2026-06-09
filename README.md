# Catch Falling Object - Pixel Edition

Sebuah game arcade berbasis desktop yang dibangun menggunakan **Python** dan **Tkinter** sebagai framework GUI utamanya, serta **Pygame** untuk manajemen audionya. Game ini mengimplementasikan konsep Pemrograman Berorientasi Objek (PBO/OOP) secara penuh, di mana pemain bertugas mengendalikan keranjang di bagian bawah layar untuk menangkap berbagai alat tulis yang berjatuhan sambil menghindari bom.

## 🌟 Fitur Utama

- **Sistem Drop Objek Dinamis**: Menghadirkan beragam jenis item jatuh (Pensil, Buku, Penghapus, Penggaris) dengan nilai skor berbeda, serta Bom yang berfungsi sebagai rintangan.
- **Pengaturan Tingkat Kesulitan**: 
  - **Easy**: Pemain dibekali 5 nyawa, kecepatan jatuh standar, dan peluang kemunculan bom lebih rendah.
  - **Hard**: Pemain dibekali 3 nyawa, kecepatan jatuh lebih cepat, dan peluang kemunculan bom lebih tinggi.
- **Manajemen Fitur Game Ringkas**: 
  - Mekanik *Pause/Play* (menekan tombol di layar atau tombol `P` pada keyboard).
  - Fitur *Save State/Continue Game* jika pemain keluar (*leave*) di tengah pertandingan.
- **Menu Settings Interaktif**:
  - Pengubahan tema visual secara langsung (*Toggle Theme*: Dark/Light Mode).
  - Pengubahan ukuran fisik keranjang (*Basket Size*: Small, Medium, Large) disertai animasi teks acak (*glitch effect*).
- **Feedback Visual & Audio**: Sistem popup teks skor dinamis (+ poin / - poin) langsung di atas posisi keranjang setiap kali berhasil menangkap objek.

## 🛠️ Konsep PBO yang Diterapkan

Kode program ini dibagi menjadi beberapa kelas entitas terpisah sesuai tanggung jawabnya:
1. `GameObject`: Mengatur siklus hidup objek jatuh (posisi, kecepatan jatuh, deteksi batas bawah layar, dan penghapusan memori visual).
2. `Basket`: Mengatur visualisasi keranjang pemain, kontrol horizontal responsif, pembatasan batas layar kanan-kiri, serta ukuran adaptif.
3. `ScorePopup`: Mengatur teks umpan balik visual berdurasi singkat saat terjadi interaksi penangkapan.
4. `Game`: Pengendali inti (*Core Engine*) yang mengatur game loop, kalkulasi skor target, pengecekan tabrakan (*collision*), manajemen nyawa, dan kondisi akhir game (menang/kalah).
5. `Menu`: Mengatur antarmuka awal, navigasi halaman pengaturan, manajemen state game yang disimpan, dan animasi teks.

## ⌨️ Kontrol Kendali

- **Gerak Kiri**: Tombol `Panah Kiri` atau `A`
- **Gerak Kanan**: Tombol `Panah Kanan` atau `D`
- **Jeda Game (Pause)**: Tombol `P` (atau klik tombol ⏸ di layar)

## 📦 Kebutuhan Aset Gambar & Audio

Agar game dapat berjalan dengan visual dan suara kustom secara penuh, pastikan file-file berikut berada di **folder yang sama** dengan file script Python Anda:

### 🖼️ Aset Gambar (.png)
- `gelap.png` & `terang.png` (Background utama kanvas)
- `hati.png` (Ikon indikator nyawa)
- `bom.png` (Aset rintangan bom)
- `pensil.png`, `buku.png`, `penghapus.png`, `penggaris.png` (Aset barang jatuh)
- `small.png`, `medium.png`, `large.png` (Aset keranjang sesuai ukuran pilihan)
- *Optional*: `nama_file_efek_kamu.png` (Jika kamu menambahkan visual efek ledakan bom)

### 🎵 Aset Audio (.mp3)
- File Backsong Utama (Saria's Song / musik pilihanmu)
- File SFX Bom (Suara ledakan saat mengenai bom)
- File SFX Tangkap (Suara saat mendapatkan alat tulis)
- File SFX Menang & Kalah (Suara akhir permainan)
