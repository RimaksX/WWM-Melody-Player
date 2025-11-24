import mido
import pydirectinput
import time
import os
import ctypes
import keyboard
import threading
import json
import sys
from colorama import init, Fore, Style

# Сброс цвета
init(autoreset=True)

# --- КОНФИГУРАЦИЯ ---
BIND_START = 'f8'
BIND_STOP = 'esc'
PRESS_DURATION = 0.03
pydirectinput.PAUSE = 0.0

# Папки
TRACKS_DIR = 'Music'
LOCALES_DIR = 'locales'
CONFIG_FILE = 'config.json'

# WWM Range (C3 - B5)
GAME_MIN_NOTE = 48
GAME_MAX_NOTE = 83
KEYS = {
    3: ['z', 'x', 'c', 'v', 'b', 'n', 'm'],
    4: ['a', 's', 'd', 'f', 'g', 'h', 'j'],
    5: ['q', 'w', 'e', 'r', 't', 'y', 'u']
}
SCALE_WHITE_KEYS = {0: 0, 2: 1, 4: 2, 5: 3, 7: 4, 9: 5, 11: 6}

# --- ВСТРОЕННЫЕ ЯЗЫКИ (ДЛЯ САМОРАЗВЕРТЫВАНИЯ) ---
EMBEDDED_LOCALES = {
    "en": {
        "lang_name": "English",
        "app_title": "WWM MELODY PLAYER",
        "menu_player": "Music Player",
        "menu_settings": "Settings",
        "menu_exit": "Exit",
        "settings_title": "Settings",
        "settings_lang_title": "Interface Language",
        "settings_select": "Select language number:",
        "settings_changed": "Language changed!",
        "player_list_title": "Track List",
        "player_no_files": f"No MIDI files found in '{TRACKS_DIR}' folder.",
        "player_select": "Select track number:",
        "player_analyzing": "Analyzing harmony...",
        "player_stats": "Compatibility",
        "rec_title": "Recommendation",
        "rec_strict": "High Accuracy",
        "rec_fold": "Full Range",
        "mode_title": "Select Playback Mode",
        "mode_auto": "Press Enter for recommended",
        "mode_strict_desc": "Clean sound. Skips notes outside range.",
        "mode_fold_desc": "Rich sound. Wraps notes into range.",
        "mode_melody_desc": "Solo mode. Forces melody to highs.",
        "ui_mode_label": "Mode",
        "ui_shift_label": "Shift",
        "ui_back": "Back",
        "play_ready": "Ready to play",
        "play_controls_pre": "[F8] Start",
        "play_controls_active": ">>> [F8] Playing... | [ESC] Stop <<<",
        "play_stopped": "Stopped by user.",
        "play_done": "Track finished."
    },
    "ru": {
        "lang_name": "Русский",
        "app_title": "WWM MELODY PLAYER",
        "menu_player": "Музыкальный плеер",
        "menu_settings": "Настройки",
        "menu_exit": "Выход",
        "settings_title": "Настройки",
        "settings_lang_title": "Язык интерфейса",
        "settings_select": "Введите номер языка:",
        "settings_changed": "Язык изменен!",
        "player_list_title": "Список треков",
        "player_no_files": f"MIDI файлы не найдены в папке '{TRACKS_DIR}'.",
        "player_select": "Введите номер трека:",
        "player_analyzing": "Анализ гармонии...",
        "player_stats": "Совместимость",
        "rec_title": "Рекомендация",
        "rec_strict": "Высокая точность",
        "rec_fold": "Полный диапазон",
        "mode_title": "Режим воспроизведения",
        "mode_auto": "Нажмите Enter для авто-выбора",
        "mode_strict_desc": "Чистый звук. Пропуск нот вне диапазона.",
        "mode_fold_desc": "Насыщенный звук. Сжатие октав.",
        "mode_melody_desc": "Соло режим. Мелодия на высоких нотах.",
        "ui_mode_label": "Режим",
        "ui_shift_label": "Сдвиг",
        "ui_back": "Назад",
        "play_ready": "Готов к запуску",
        "play_controls_pre": "[F8] Старт",
        "play_controls_active": ">>> [F8] Играет... | [ESC] Стоп <<<",
        "play_stopped": "Остановлено пользователем.",
        "play_done": "Трек завершен."
    }
}

# --- COLOR THEME ---
C_TITLE = Style.BRIGHT + Fore.WHITE
C_TEXT = Style.BRIGHT + Fore.WHITE
C_ACCENT = Fore.YELLOW
C_SUCCESS = Fore.GREEN
C_ERROR = Fore.RED
C_INPUT = Fore.CYAN
SEPARATOR = Fore.WHITE + "————————————————————"


class BardApp:
    def __init__(self):
        self.lang = 'en'
        self.texts = {}

        # 1. Развертывание файловой системы
        self.initialize_filesystem()

        # 2. Загрузка
        self.load_config()
        self.load_locale()

    def initialize_filesystem(self):
        """Создает папки и файлы, если их нет"""
        # Создаем папку для треков
        if not os.path.exists(TRACKS_DIR):
            try:
                os.makedirs(TRACKS_DIR)
            except:
                pass

        # Создаем папку локализации
        if not os.path.exists(LOCALES_DIR):
            try:
                os.makedirs(LOCALES_DIR)
            except:
                pass

        # Создаем файлы языков по умолчанию, если их нет
        for lang_code, content in EMBEDDED_LOCALES.items():
            file_path = os.path.join(LOCALES_DIR, f"{lang_code}.json")
            if not os.path.exists(file_path):
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(content, f, indent=4, ensure_ascii=False)
                except Exception as e:
                    print(f"Error creating locale {lang_code}: {e}")

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    self.lang = json.load(f).get('language', 'en')
            except:
                pass

    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump({'language': self.lang}, f)

    def load_locale(self):
        path = os.path.join(LOCALES_DIR, f'{self.lang}.json')

        # Пытаемся загрузить внешний файл
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self.texts = json.load(f)
                    return
            except:
                pass

        # Если файла нет или ошибка - берем из памяти
        self.texts = EMBEDDED_LOCALES.get(self.lang, EMBEDDED_LOCALES['en'])

    def t(self, key):
        return self.texts.get(key, f"[{key}]")

    # --- UI HELPERS ---
    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self, title):
        print(f"\n{C_TITLE}{title.upper()}")
        print(f"{SEPARATOR}")

    def print_menu_item(self, index, text):
        print(f"{C_ACCENT}[{index}] {C_TEXT}{text}")

    def print_back_option(self):
        print(f"\n{C_ACCENT}[0] {C_TEXT}{self.t('ui_back')}")

    def input_prompt(self):
        return input(f"\n{C_INPUT}> {Style.RESET_ALL}")

    # --- LOGIC ---
    def press_worker(self, key):
        pydirectinput.keyDown(key)
        time.sleep(PRESS_DURATION)
        pydirectinput.keyUp(key)

    def get_clean_notes(self, midi_file):
        notes = []
        try:
            mid = mido.MidiFile(midi_file)
            for msg in mid:
                if msg.type == 'note_on' and msg.velocity > 0:
                    if hasattr(msg, 'channel') and msg.channel == 9: continue
                    notes.append(msg.note)
        except:
            pass
        return notes

    def analyze_best_shift(self, notes):
        if not notes: return 0
        best_shift = 0
        max_score = -float('inf')
        for shift in range(-12, 13):
            score = 0
            for note in notes:
                t = note + shift
                if (t % 12) in SCALE_WHITE_KEYS:
                    score += 10
                else:
                    score -= 50
                if GAME_MIN_NOTE <= t <= GAME_MAX_NOTE:
                    score += 5
                else:
                    score -= 2
            if score > max_score: max_score, best_shift = score, shift
        return best_shift

    def process_note(self, note, shift, mode):
        final_note = note + shift
        if mode == 2:  # FOLD
            while final_note > GAME_MAX_NOTE: final_note -= 12
            while final_note < GAME_MIN_NOTE: final_note += 12
        octave = (final_note // 12) - 1
        base = final_note % 12
        if base in SCALE_WHITE_KEYS and octave in KEYS:
            return KEYS[octave][SCALE_WHITE_KEYS[base]]
        return None

    # --- MENUS ---
    def menu_main(self):
        while True:
            self.clear()
            self.print_header(self.t('app_title'))

            self.print_menu_item(1, self.t('menu_player'))
            self.print_menu_item(2, self.t('menu_settings'))
            self.print_menu_item(3, self.t('menu_exit'))

            choice = self.input_prompt()
            if choice == '1':
                self.menu_player()
            elif choice == '2':
                self.menu_settings()
            elif choice == '3':
                sys.exit()

    def menu_settings(self):
        while True:
            self.clear()
            self.print_header(self.t('settings_title'))

            avail_langs = []
            if os.path.exists(LOCALES_DIR):
                for f in os.listdir(LOCALES_DIR):
                    if f.endswith('.json'):
                        try:
                            with open(os.path.join(LOCALES_DIR, f), 'r', encoding='utf-8') as file:
                                name = json.load(file).get('lang_name', f[:-5])
                                avail_langs.append({'code': f[:-5], 'name': name})
                        except:
                            continue

            print(f"{C_TEXT}{self.t('settings_lang_title')}\n")

            for i, l in enumerate(avail_langs):
                is_current = (l['code'] == self.lang)
                marker = f"{C_SUCCESS}●" if is_current else f"{C_TEXT}○"
                print(f"{C_ACCENT}[{i + 1}] {marker} {C_TEXT}{l['name']}")

            self.print_back_option()
            print(f"{C_TEXT}{self.t('settings_select')}")

            try:
                choice = self.input_prompt()
                if choice == '0': return
                idx = int(choice) - 1
                if 0 <= idx < len(avail_langs):
                    self.lang = avail_langs[idx]['code']
                    self.save_config()
                    self.load_locale()
                    print(f"{C_SUCCESS}OK")
                    time.sleep(0.5)
            except:
                continue

    def menu_player(self):
        while True:
            self.clear()
            # Сканируем папку Music
            files = []
            if os.path.exists(TRACKS_DIR):
                files = [f for f in os.listdir(TRACKS_DIR) if f.lower().endswith(('.mid', '.midi'))]

            self.print_header(self.t('player_list_title'))
            if not files:
                print(f"{C_ERROR}{self.t('player_no_files')}")
                self.print_back_option()
                self.input_prompt()
                return

            for i, f in enumerate(files):
                self.print_menu_item(i + 1, f)

            self.print_back_option()
            print(f"{C_TEXT}{self.t('player_select')}")

            try:
                raw = self.input_prompt()
                if raw == '0': return
                idx = int(raw) - 1
                if 0 <= idx < len(files):
                    # Передаем полный путь к файлу
                    full_path = os.path.join(TRACKS_DIR, files[idx])
                    self.play_logic(full_path, files[idx])  # передаем имя отдельно для заголовка
            except:
                continue

    def play_logic(self, full_path, display_name):
        print(f"\n{C_TEXT}{self.t('player_analyzing')}")
        notes = self.get_clean_notes(full_path)
        shift = self.analyze_best_shift(notes)

        total = len(notes) or 1
        s_hits = sum(1 for n in notes if
                     GAME_MIN_NOTE <= (n + shift) <= GAME_MAX_NOTE and ((n + shift) % 12) in SCALE_WHITE_KEYS)
        f_hits = sum(1 for n in notes if ((n + shift) % 12) in SCALE_WHITE_KEYS)
        pct_s, pct_f = (s_hits / total) * 100, (f_hits / total) * 100

        rec_mode = 1 if pct_s >= 90 else 2
        rec_str = "Strict" if rec_mode == 1 else "Fold"

        # Stats
        print(
            f"{C_TEXT}{self.t('player_stats')}: {C_SUCCESS}{pct_s:.0f}% Strict {C_TEXT}| {C_SUCCESS}{pct_f:.0f}% Fold")
        print(f"{C_SUCCESS}{self.t('rec_title')}: {rec_str.upper()} {C_TEXT}({self.t('ui_shift_label')}: {shift})")

        # Mode Selector
        print(f"\n{C_TITLE}{self.t('mode_title').upper()}")
        print(f"{SEPARATOR}")
        print(f"{C_ACCENT}[1] {C_TEXT}Strict {C_TEXT}- {self.t('mode_strict_desc')}")
        print(f"{C_ACCENT}[2] {C_TEXT}Fold   {C_TEXT}- {self.t('mode_fold_desc')}")
        print(f"{C_ACCENT}[3] {C_TEXT}Melody {C_TEXT}- {self.t('mode_melody_desc')}")

        self.print_back_option()
        print(f"{C_TEXT}{self.t('mode_auto')}")

        try:
            m_in = self.input_prompt()
            if m_in == '0': return
            mode = int(m_in) if m_in else rec_mode
        except:
            mode = rec_mode

        if mode == 3 and notes: shift = GAME_MAX_NOTE - max(notes)

        # PRE-PLAY
        self.clear()
        self.print_header(display_name)

        print(f"{C_TEXT}{self.t('ui_mode_label')}: {C_ACCENT}{mode}")
        print(f"{C_TEXT}{self.t('ui_shift_label')}: {C_ACCENT}{shift}\n")

        print(f"{C_TEXT}{self.t('play_ready')}")
        print(f"{C_ACCENT}{self.t('play_controls_pre')}")
        self.print_back_option()

        # Wait loop
        start_playing = False
        while True:
            if keyboard.is_pressed(BIND_START):
                start_playing = True
                break
            if keyboard.is_pressed(BIND_STOP) or keyboard.is_pressed('0'):
                start_playing = False
                break
            time.sleep(0.01)

        if not start_playing:
            time.sleep(0.3)
            return

        # PLAYING
        print(f"\n{C_SUCCESS}{self.t('play_controls_active')}")

        mid = mido.MidiFile(full_path)
        stop = False
        for msg in mid.play():
            if keyboard.is_pressed(BIND_STOP):
                print(f"\n{C_ERROR}{self.t('play_stopped')}")
                stop = True
                break
            if msg.type == 'note_on' and msg.velocity > 0:
                if hasattr(msg, 'channel') and msg.channel == 9: continue
                key = self.process_note(msg.note, shift, mode)
                if key: threading.Thread(target=self.press_worker, args=(key,), daemon=True).start()

        time.sleep(0.2)
        for r in KEYS.values():
            for k in r: pydirectinput.keyUp(k)

        if not stop: print(f"\n{C_SUCCESS}{self.t('play_done')}")
        time.sleep(1.5)


if __name__ == "__main__":
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print(f"{C_ERROR}ERROR: Run as Admin required!")
        input()
    else:
        try:
            app = BardApp()
            app.menu_main()
        except KeyboardInterrupt:
            sys.exit()