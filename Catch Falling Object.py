import tkinter as tk  # Mengimpor modul GUI utama Tkinter
import random  # Mengimpor modul acak untuk posisi spawner objek
import time  # Mengimpor modul waktu untuk durasi teks popup skor
import pygame  # Mengimpor Pygame untuk manajemen audio

# ==============================================================================
# 1. BAGIAN: ENTITAS OBJEK JATUH (GameObject)
# Fungsi: Mengatur siklus hidup objek (pembuatan visual, pergerakan, & koordinat)
# ==============================================================================
class GameObject:
    def __init__(self, canvas, x, y, speed, skor, jenis, master_game):
        self.canvas = canvas  # Menyimpan referensi kanvas tempat menggambar
        self.x = x  # Mengatur posisi koordinat X awal objek
        self.y = y  # Mengatur posisi koordinat Y awal objek
        self.speed = speed  # Mengatur kecepatan jatuh objek per frame
        self.skor = skor  # Mengatur nilai poin penambahan/pengurangan objek
        self.jenis = jenis  # Menyimpan tipe objek ('pensil', 'buku', 'bom', dll)
        self.master_game = master_game  # Menyimpan referensi kelas utama Game untuk mengambil gambar
        self.id = None  # Inisialisasi ID visual komponen utama Tkinter
        self.active = True  # Status aktif objek di dalam permainan

    def draw(self):
        # MENGATASI EROR KORDINAT: Menggunakan anchor="nw" agar koordinat dihitung dari pojok kiri atas gambar
        if self.jenis in self.master_game.images:
            self.id = self.canvas.create_image(self.x, self.y, image=self.master_game.images[self.jenis], anchor="nw")
        else:
            # Fallback jika gambar lokal tidak ditemukan, diganti kotak darurat agar tidak crash
            self.id = self.canvas.create_rectangle(self.x, self.y, self.x+25, self.y+25, fill="red")

    def fall(self):
        if self.active:  
            try:
                self.canvas.move(self.id, 0, self.speed)  # Menggeser visual objek ke bawah di kanvas
                
                # MENGATASI EROR MISSED: Menggunakan bbox untuk mengambil koordinat fisik terbawah objek gambar secara riil
                coords = self.get_coords()
                if coords:
                    y2 = coords[3]  # Index 3 melambangkan sisi fisik paling bawah dari gambar objek
                    if y2 > 720:  # Jika bagian bawah gambar melewati batas tinggi layar 720 piksel
                        self.active = False  # Matikan status aktif objek
                        self.destroy_visual()  # Hapus visual dari kanvas memori
                        return False  # Mengembalikan sinyal FALSE untuk memicu hitungan MISSED di Game Loop
            except tk.TclError:  
                self.active = False
                return False
        return True  

    def get_coords(self):
        if not self.id or not self.active:  
            return None
        try:
            # Menggunakan bbox (Bounding Box) untuk mendapatkan 4 titik pembatas (x1,y1,x2,y2) dari gambar
            return self.canvas.bbox(self.id)
        except tk.TclError:
            return None

    def destroy_visual(self):
        try:
            if self.id:  
                self.canvas.delete(self.id)  
        except tk.TclError:
            pass

# ==============================================================================
# 2. BAGIAN: ENTITAS KERANJANG PEMAIN (Basket)
# Fungsi: Mengatur pergerakan horizontal cepat dan area penangkapan pemain
# ==============================================================================
class Basket:
    def __init__(self, canvas, width_multiplier=1.0, color="white", master_game=None):
        self.canvas = canvas  
        self.master_game = master_game
        self.width = int(80 * width_multiplier)  # Dimensi lebar dasar keranjang
        self.height = 30  # Tinggi dimensi keranjang
        self.x = 600  # Posisi awal horizontal tengah layar
        self.y = 650  # Posisi vertikal menetap bawah layar
        self.speed = 25  # Kecepatan gerak responsif tinggi
        
        # MENGUBAH KERANJANG MENJADI GAMBAR BERDASARKAN UKURAN SETTING
        ukuran_aktif = self.master_game.basket_size.lower()
        key_gambar = f"basket_{ukuran_aktif}"  # Menghasilkan key pencari: 'basket_small', 'basket_medium', dll
        
        if key_gambar in self.master_game.images:
            # Menggambar keranjang menggunakan file PNG lokal dengan titik jangkar kiri-atas (North-West)
            self.id = self.canvas.create_image(self.x, self.y, image=self.master_game.images[key_gambar], anchor="nw")
        else:
            # Fallback geometris kotak jika file gambar keranjang lokal tidak ditemukan di folder
            self.id = self.canvas.create_rectangle(self.x, self.y, self.x+self.width, self.y+self.height, fill=color, outline=color)

    def update_position(self, move_left, move_right):
        try:
            if move_left and self.x > 0:  
                self.x -= self.speed  
                if self.x < 0: self.x = 0  
                self.canvas.moveto(self.id, self.x, self.y)  # Memindahkan posisi gambar secara absolut
            if move_right and self.x < (1280 - self.width):  
                self.x += self.speed  
                if self.x > (1280 - self.width): self.x = 1280 - self.width  
                self.canvas.moveto(self.id, self.x, self.y)  
        except tk.TclError:
            pass

    def get_coords(self):
        try:
            # Menggunakan bbox untuk mendapatkan koordinat kotak pembatas fisik gambar keranjang kustom secara akurat
            return self.canvas.bbox(self.id)
        except tk.TclError:
            return None

# ==============================================================================
# 3. BAGIAN: TEKS POPUP SKOR (ScorePopup)
# Fungsi: Memberikan feedback visual angka poin (+10, -50) saat objek tertangkap
# ==============================================================================
class ScorePopup:
    def __init__(self, canvas, x, y, text, color="white"):
        self.canvas = canvas  
        self.id = self.canvas.create_text(x, y, text=text, fill=color, font=("Courier", 16, "bold"))  
        self.start_time = time.time()  
        self.duration = 0.8  

    def update(self):
        try:
            if time.time() - self.start_time > self.duration:  
                self.canvas.delete(self.id)  
                return False  
            return True  
        except tk.TclError:
            return False

# ==============================================================================
# 4. BAGIAN: INTI UTAMA GAMEPLAY (Game)
# Fungsi: Mengatur loop game, spawner objek, hitungan nyawa gambar, dan cek kalah/menang
# ==============================================================================
class Game:
    def __init__(self, root, difficulty='easy', tema='dark', saved_state=None, basket_size='Medium'):
        self.root = root  
        self.difficulty = difficulty  
        self.tema = tema  
        self.basket_size = basket_size  # Menyimpan string ukuran aktif ('Small', 'Medium', 'Large')
        self.canvas = tk.Canvas(root, width=1280, height=720, highlightthickness=0)  
        self.canvas.pack()  

        if tema == 'dark':
            self.bg = 'black'
            self.fg = 'white'
        else:
            self.bg = 'white'
            self.fg = 'black'

        self.images = {}  
        self.memuat_aset_gambar()  # Memuat gambar-gambar lokal termasuk aset keranjang baru
        
        multipliers = {'Small': 0.7, 'Medium': 1.0, 'Large': 1.4}  
        self.basket_multiplier = multipliers.get(basket_size, 1.0)  

        self.target_skor = 300  
        
        if saved_state:
            self.skor = saved_state['skor']
            self.nyawa = saved_state['nyawa']
            self.missed_counter = saved_state['missed_counter']
        else:
            self.skor = 0
            self.nyawa = 5 if difficulty == 'easy' else 3  
            self.missed_counter = 0  

        self.game_over = False  
        self.paused = False  
        self.loop_running = False  

        self.key_left = False  
        self.key_right = False  

        if difficulty == 'easy':
            self.base_speed = 5
            self.spawn_rate = 50  
            self.bom_chance = 0.25
        else:
            self.base_speed = 9
            self.spawn_rate = 30
            self.bom_chance = 0.4

        # Mengirimkan parameter 'self' ke dalam konstruktor Basket agar dapat mengakses aset gambar
        self.basket = Basket(self.canvas, self.basket_multiplier, self.fg, self)  
        self.objects = []  
        self.popups = []  
        self.ui_hearts = []  
        self.frame_count = 0  

        self.ui_skor = self.canvas.create_text(120, 30, text=f"SCORE: {self.skor}/{self.target_skor}", fill=self.fg, font=("Courier", 18, "bold"))
        self.ui_missed_text = self.canvas.create_text(380, 30, text=f"MISSED OBJ: {self.missed_counter}/7", fill=self.fg, font=("Courier", 18, "bold"))
        
        self.leave_btn = self.canvas.create_text(1100, 30, text="↩ Leave", fill=self.fg, font=("Courier", 14, "bold"), activefill="gray")
        self.canvas.tag_bind(self.leave_btn, "<Button-1>", lambda e: self.leave_game())  

        self.pause_btn = self.canvas.create_text(1230, 30, text="⏸ Pause", fill=self.fg, font=("Courier", 14, "bold"), activefill="gray")
        self.canvas.tag_bind(self.pause_btn, "<Button-1>", lambda e: self.toggle_pause())  

        self.gambar_ulang_ui_nyawa_emot()  
        self.setup_keyboard_bindings()
        pygame.mixer.music.set_volume(0.4)  
        self.game_loop()  

    def memuat_aset_gambar(self):
        # ==================================================================
        # 1. PENGATURAN GAMBAR LATAR BELAKANG (BACKGROUND IMAGE)
        # ==================================================================
        try:
            if self.tema == 'dark':
                self.bg_image = tk.PhotoImage(file="gelap.png")  # <--- Letakkan file Background Gelap di sini
            else:
                self.bg_image = tk.PhotoImage(file="terang.png")  # <--- Letakkan file Background Terang di sini
            self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")
        except Exception:
            self.canvas.configure(bg=self.bg)

        # ==================================================================
        # 2. PENGATURAN GAMBAR OBJEK, NYAWA, DAN KERANJANG KUSTOM
        # ==================================================================
        file_names = {
            'hati': 'hati.png',            # <--- File gambar nyawa
            'bom': 'bom.png',              # <--- File gambar bom
            'pensil': 'pensil.png',        # <--- File gambar pensil
            'buku': 'buku.png',            # <--- File gambar buku
            'penghapus': 'penghapus.png',  # <--- File gambar penghapus
            'penggaris': 'penggaris.png',  # <--- File gambar penggaris
            'basket_small': 'small.png',   # <--- File gambar keranjang SMALL
            'basket_medium': 'medium.png', # <--- File gambar keranjang MEDIUM
            'basket_large': 'large.png'    # <--- File gambar keranjang LARGE
        }
        
        for jenis, file_path in file_names.items():
            try:
                self.images[jenis] = tk.PhotoImage(file=file_path)
            except Exception:
                pass
        try:
            self.sfx_bom = pygame.mixer.Sound("suarabom.mp3") 
            self.sfx_bom.set_volume(0.2)  # Atur volume ke 20% biar pas
            self.sfx_tangkap = pygame.mixer.Sound("suarabarang.mp3") 
            self.sfx_tangkap.set_volume(0.3)  # Atur volume ke 30%

        except Exception:
            self.sfx_bom = None      

    def gambar_ulang_ui_nyawa_emot(self):
        for heart_id in self.ui_hearts:
            self.canvas.delete(heart_id)  
        self.ui_hearts.clear()  
        
        if 'hati' in self.images:  
            for i in range(self.nyawa):  
                h_id = self.canvas.create_image(550 + (i * 35), 30, image=self.images['hati'], anchor="center")
                self.ui_hearts.append(h_id)  

    def setup_keyboard_bindings(self):
        self.root.bind("<KeyPress-Left>", self.press_left)
        self.root.bind("<KeyRelease-Left>", self.release_left)
        self.root.bind("<KeyPress-Right>", self.press_right)
        self.root.bind("<KeyRelease-Right>", self.release_right)
        self.root.bind("<KeyPress-a>", self.press_left)
        self.root.bind("<KeyRelease-a>", self.release_left)
        self.root.bind("<KeyPress-d>", self.press_right)
        self.root.bind("<KeyRelease-d>", self.release_right)
        self.root.bind("<p>", lambda e: self.toggle_pause())  

    def press_left(self, event): self.key_left = True  
    def release_left(self, event): self.key_left = False  
    def press_right(self, event): self.key_right = True  
    def release_right(self, event): self.key_right = False  

    def toggle_pause(self):
        self.paused = not self.paused  
        if self.paused:
            self.canvas.itemconfig(self.pause_btn, text="▶ Play")  
            self.loop_running = False
            pygame.mixer.music.set_volume(0.1)  # Mengecilkan suara ke 10% saat pause  
        else:
            self.canvas.itemconfig(self.pause_btn, text="⏸ Pause")
            pygame.mixer.music.set_volume(0.4)  # Mengembalikan suara ke 40% saat lanjut main  
            if not self.loop_running:
                self.game_loop()  

    def spawn_object(self):
        if random.random() < self.bom_chance:
            jenis = 'bom'
            skor = -30 if self.difficulty == 'easy' else -50 
        else:
            barang = [('pensil', 10), ('buku', 20), ('penghapus', 15), ('penggaris', 25)]
            jenis, skor = random.choice(barang)

        x = random.randint(50, 1200)  
        obj = GameObject(self.canvas, x, 0, self.base_speed, skor, jenis, self)  
        obj.draw()  
        self.objects.append(obj)  

    def check_collision(self, obj):
        if not obj.active: return False  
        basket_coords = self.basket.get_coords()  
        obj_coords = obj.get_coords()  
        if not basket_coords or not obj_coords: return False
        bx1, by1, bx2, by2 = basket_coords  
        ox1, oy1, ox2, oy2 = obj_coords  
        return (bx1 < ox2 and bx2 > ox1 and by1 < oy2 and by2 > oy1)

    def kurangi_nyawa_mekanik(self):
        self.nyawa -= 1  
        self.gambar_ulang_ui_nyawa_emot()  
        if self.nyawa <= 0:  
            self.end_game("kalah")  

    def handle_catch(self, obj):
        # ==============================================================================
        # LOGIKA JIKA MENANGKAP BOM (NYAWA -1 DAN SKOR BERKURANG SESUAI LEVEL)
        # ==============================================================================
        if obj.jenis == 'bom':
            if hasattr(self, 'sfx_bom') and self.sfx_bom: # buat mainkan suara bom
                self.sfx_bom.play()
            obj.active = False
            obj.destroy_visual()  
            if obj in self.objects: 
                self.objects.remove(obj)  
            
            # Pengecekan level kesulitan untuk menentukan potongan skor
            if self.difficulty == 'easy':
                potongan_skor = 25
                teks_popup = "-25"
            else:
                potongan_skor = 50
                teks_popup = "-50"
            
            # Mengurangi skor pemain dan memastikan skor tidak minus di bawah 0
            self.skor -= potongan_skor
            if self.skor < 0: 
                self.skor = 0
            
            # Menampilkan popup peringatan di atas keranjang
            popup = ScorePopup(self.canvas, self.basket.x + (self.basket.width // 2), self.basket.y - 20, teks_popup, "red")
            self.popups.append(popup)  
            
            # Memperbarui teks skor di layar UI
            self.canvas.itemconfig(self.ui_skor, text=f"SCORE: {self.skor}/{self.target_skor}")
            
            # Mengurangi nyawa pemain
            self.kurangi_nyawa_mekanik()  
            return

        # ==============================================================================
        # LOGIKA JIKA MENANGKAP OBJEK BIASA (SKOR BERTAMBAH)
        # ==============================================================================
        if hasattr(self, 'sfx_tangkap') and self.sfx_tangkap:
                self.sfx_tangkap.play() #buat mainkan suara tangkap barang biasa
        self.skor += obj.skor  
        if self.skor < 0: 
            self.skor = 0  
        
        text = f"+{int(obj.skor)}"  
        popup = ScorePopup(self.canvas, self.basket.x + (self.basket.width // 2), self.basket.y - 20, text, self.fg)
        self.popups.append(popup)  

        obj.active = False
        obj.destroy_visual()  
        if obj in self.objects: 
            self.objects.remove(obj)  
            
        self.canvas.itemconfig(self.ui_skor, text=f"SCORE: {self.skor}/{self.target_skor}")  

        if self.skor >= self.target_skor:  
            self.end_game("menang")

    def leave_game(self):
        self.game_over = True  
        self.loop_running = False  
        try: self.canvas.destroy()  
        except tk.TclError: pass
        saved_state = {'skor': self.skor, 'nyawa': self.nyawa, 'missed_counter': self.missed_counter, 'difficulty': self.difficulty}
        pygame.mixer.music.set_volume(0.1)  # Perkecil volume karena kembali ke menu
        Menu(self.root, self.tema, saved_state, basket_size=self.basket_size)  

    def end_game(self, hasil):
        self.game_over = True  
        self.loop_running = False
        if hasil == "kalah":
            pygame.mixer.music.stop()  # Stop total backsong utama
            pygame.mixer.music.load("gameover.mp3") # Load file
            pygame.mixer.music.set_volume(0.4)  # Set volume 40%
            pygame.mixer.music.play(1)  # Angka 1 artinya cuma diputar sekali (tidak looping)

        elif hasil == "menang":
            pygame.mixer.music.stop()  # Stop total backsong utama
            pygame.mixer.music.load("win.mp3") 
            pygame.mixer.music.set_volume(0.4)  # Set volume suara menang (40%)
            pygame.mixer.music.play(1)  # Putar 1 kali saja 
        try:
            self.canvas.create_text(640, 360, text=f"GAME {hasil.upper()}", fill=self.fg, font=("Courier", 36, "bold"))
            self.root.after(3500, lambda: self.clear_and_return())  #waktu 3.5 detik untuk menampilkan hasil sebelum kembali ke menu utama
        except tk.TclError:
            pass

    def clear_and_return(self):
        try: self.canvas.destroy()  
        except tk.TclError: pass
       # load ulang file backsong awal untuk menu utama
        pygame.mixer.music.load("backsong.mp3") 
        pygame.mixer.music.play(-1)  # Putar ulang secara looping
        pygame.mixer.music.set_volume(0.1)  # Set 10% untuk menu utama
        Menu(self.root, self.tema, saved_state=None, basket_size=self.basket_size)  

    def game_loop(self):
        if self.game_over or self.paused:  
            self.loop_running = False  
            return
        self.loop_running = True  

        self.basket.update_position(self.key_left, self.key_right)  

        self.frame_count += 1  
        if self.frame_count % self.spawn_rate == 0:  
            self.spawn_object()  

        for obj in self.objects[:]:  
            if not obj.fall():  # JIKA FUNGSI FALL MENGEMBALIKAN LOGIKA FALSE (MENYENTUH LANTAI)
                if obj in self.objects: self.objects.remove(obj)  
                
                if obj.jenis != 'bom':  
                    self.missed_counter += 1  # Tambah hitungan missed dari 0 ke 7
                    try:
                        self.canvas.itemconfig(self.ui_missed_text, text=f"MISSED OBJ: {self.missed_counter}/7")
                    except tk.TclError:
                        return
                    
                    if self.missed_counter >= 7:  # Jika pelanggaran menyentuh angka 7
                        self.missed_counter = 0  # Reset kembali ke angka 0
                        try: self.canvas.itemconfig(self.ui_missed_text, text=f"MISSED OBJ: 0/7")
                        except tk.TclError: pass
                        self.kurangi_nyawa_mekanik()  # Potong 1 ikon gambar hati nyawa pemain
                        if self.game_over: return  
            
            elif self.check_collision(obj):  
                self.handle_catch(obj)  
                if self.game_over: return

        for pop in self.popups[:]:  
            if not pop.update(): self.popups.remove(pop)

        if not self.game_over and not self.paused:  
            try: self.root.after(20, self.game_loop)  
            except tk.TclError: self.loop_running = False
        else:
            self.loop_running = False  

# ==============================================================================
# 5. BAGIAN: KELAS MENU UTAMA DAN SETTING (Menu)
# Fungsi: Mengatur tampilan menu depan, pemilihan level, animasi teks, & ganti tema
# ==============================================================================
class Menu:
    def __init__(self, root, tema='dark', saved_state=None, basket_size='Medium'):
        self.root = root  
        self.tema = tema  
        self.saved_state = saved_state   
        self.basket_size = basket_size  
        self.canvas = tk.Canvas(root, width=1280, height=720, highlightthickness=0)  
        self.canvas.pack()  

        if tema == 'dark':
            self.bg = 'black'
            self.fg = 'white'
        else:
            self.bg = 'white'
            self.fg = 'black'
        self.canvas.configure(bg=self.bg)  

        self.canvas.create_text(640, 150, text="CATCH FALLING OBJECT", fill=self.fg, font=("Courier", 32, "bold"))
        self.canvas.create_text(640, 200, text="[ PIXEL EDITION ]", fill=self.fg, font=("Courier", 16))

        if self.saved_state:
            # Jika ada game yang tersimpan, tombol disusun rapat dari Y=300 sampai Y=420
            self.play_btn = self.canvas.create_text(640, 300, text="▶ CONTINUE GAME", fill="yellow", font=("Courier", 24, "bold"), activefill="gray")
            self.canvas.tag_bind(self.play_btn, "<Button-1>", lambda e: self.start_game(continue_match=True))
            
            self.new_game_btn = self.canvas.create_text(640, 360, text="🆕 NEW GAME", fill=self.fg, font=("Courier", 20, "bold"), activefill="gray")
            self.canvas.tag_bind(self.new_game_btn, "<Button-1>", self.choose_difficulty)
            
            # Tombol Settings dan Exit diturunkan sedikit jika menu penuh
            y_settings = 420
            y_exit = 480
        else:
            # JIKA TIDAK ADA GAME TERSIMPAN (Kondisi pada gambar Anda)
            # Tombol PLAY diletakkan di Y=320, dan SETTINGS dinaikkan ke Y=380 agar rapat
            self.play_btn = self.canvas.create_text(640, 320, text="▶ PLAY", fill=self.fg, font=("Courier", 24, "bold"), activefill="gray")
            self.canvas.tag_bind(self.play_btn, "<Button-1>", self.choose_difficulty)
            
            y_settings = 380
            y_exit = 440

        # Menggunakan variabel dinamis y_settings dan y_exit agar posisi adaptif
        self.settings_btn = self.canvas.create_text(640, y_settings, text="⚙ SETTINGS", fill=self.fg, font=("Courier", 24, "bold"), activefill="gray")
        self.canvas.tag_bind(self.settings_btn, "<Button-1>", self.open_settings)

        self.exit_btn = self.canvas.create_text(640, y_exit, text="✕ EXIT", fill=self.fg, font=("Courier", 24, "bold"), activefill="gray")
        self.canvas.tag_bind(self.exit_btn, "<Button-1>", lambda e: root.destroy())

    def choose_difficulty(self, event):
        self.canvas.delete("all")  
        self.canvas.create_text(640, 200, text="SELECT DIFFICULTY", fill=self.fg, font=("Courier", 28, "bold"))

        easy_btn = self.canvas.create_text(640, 320, text="EASY (5 LIVES)", fill=self.fg, font=("Courier", 22), activefill="gray")
        hard_btn = self.canvas.create_text(640, 400, text="HARD (3 LIVES, FASTER)", fill=self.fg, font=("Courier", 22), activefill="gray")
        back_btn = self.canvas.create_text(640, 500, text="← BACK", fill=self.fg, font=("Courier", 18), activefill="gray")

        self.canvas.tag_bind(easy_btn, "<Button-1>", lambda e: self.start_game(difficulty='easy'))
        self.canvas.tag_bind(hard_btn, "<Button-1>", lambda e: self.start_game(difficulty='hard'))
        self.canvas.tag_bind(back_btn, "<Button-1>", lambda e: self.refresh_menu())

    def start_game(self, difficulty='easy', continue_match=False):
        try: self.canvas.destroy()  
        except tk.TclError: pass
        if continue_match and self.saved_state:
            Game(self.root, self.saved_state['difficulty'], self.tema, saved_state=self.saved_state, basket_size=self.basket_size)
        else:
            Game(self.root, difficulty, self.tema, saved_state=None, basket_size=self.basket_size)

    def animate_text_change(self, text_id, target_text, current_step=0):
        chars = "$%&#@*+O"  
        try:
            if current_step < 3:  
                random_str = "".join(random.choice(chars) for _ in range(len(target_text)))  
                self.canvas.itemconfig(text_id, text=random_str)  
                self.root.after(60, lambda: self.animate_text_change(text_id, target_text, current_step + 1))
            else:
                self.canvas.itemconfig(text_id, text=target_text)  
        except tk.TclError:
            pass

    def open_settings(self, event):
        self.canvas.delete("all")  
        self.canvas.create_text(640, 150, text="SETTINGS", fill=self.fg, font=("Courier", 28, "bold"))
        
        self.info_theme = self.canvas.create_text(640, 230, text=f"Theme      : {'DARK' if self.tema=='dark' else 'LIGHT'}", fill=self.fg, font=("Courier", 16))
        self.info_size = self.canvas.create_text(640, 270, text=f"Basket Size : {self.basket_size.upper()}", fill=self.fg, font=("Courier", 16))

        toggle_btn = self.canvas.create_text(640, 350, text="[ TOGGLE THEME ]", fill=self.fg, font=("Courier", 20, "bold"), activefill="gray")
        size_btn = self.canvas.create_text(640, 420, text="[ CHANGE BASKET SIZE ]", fill=self.fg, font=("Courier", 20, "bold"), activefill="gray")
        back_btn = self.canvas.create_text(640, 520, text="← BACK TO MENU", fill=self.fg, font=("Courier", 18), activefill="gray")

        self.canvas.tag_bind(toggle_btn, "<Button-1>", lambda e: self.toggle_theme())
        self.canvas.tag_bind(size_btn, "<Button-1>", lambda e: self.toggle_basket_size())
        self.canvas.tag_bind(back_btn, "<Button-1>", lambda e: self.refresh_menu())

    def toggle_theme(self):
        self.tema = 'light' if self.tema == 'dark' else 'dark'  
        self.canvas.delete("all")  
        self.open_settings(None)  
        self.animate_text_change(self.info_theme, f"Theme      : {'DARK' if self.tema=='dark' else 'LIGHT'}")  

    def toggle_basket_size(self):
        sizes = ['Small', 'Medium', 'Large']  
        current_index = sizes.index(self.basket_size)  
        next_index = (current_index + 1) % len(sizes)  
        self.basket_size = sizes[next_index]  
        self.animate_text_change(self.info_size, f"Basket Size : {self.basket_size.upper()}")  

    def refresh_menu(self):
        try: self.canvas.destroy()  
        except tk.TclError: pass
        Menu(self.root, self.tema, self.saved_state, basket_size=self.basket_size)  

# ==============================================================================
# 6. BAGIAN: BLOK INSTANCE PROSES UTAMA (Main Execution)
# ==============================================================================
if __name__ == "__main__":
    # BARIS INI UNTUK BACKSONG
    pygame.mixer.init()  # Menginisialisasi sistem audio
    pygame.mixer.music.load("backsong.mp3")
    pygame.mixer.music.play(-1)  # Angka -1 membuat lagu diputar berulang (looping terus)
    pygame.mixer.music.set_volume(0.1)  # Mengatur volume awal ke 10% biar ga kaget

    root = tk.Tk()  
    root.title("Catch Falling Object - Pixel Edition")  
    root.geometry("1280x720")  
    root.resizable(False, False)  
    Menu(root, tema='dark')  
    root.mainloop()
