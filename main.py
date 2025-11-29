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

try:
    ctypes.windll.winmm.timeBeginPeriod(1)
except:
    pass

init(autoreset=True)

BIND_START = 'f8'
BIND_STOP = 'esc'

PRESS_DURATION = 0.003
MOD_GAP = 0.015
pydirectinput.PAUSE = 0.0

GAME_MIN_NOTE = 48
GAME_MAX_NOTE = 83

TRACKS_DIR = 'Music'
LOCALES_DIR = 'locales'
CONFIG_FILE = 'config.json'

KEYS_21 = {
    3: ['z', 'x', 'c', 'v', 'b', 'n', 'm'],
    4: ['a', 's', 'd', 'f', 'g', 'h', 'j'],
    5: ['q', 'w', 'e', 'r', 't', 'y', 'u']
}

MAP_36 = {
    0: [('z', 0), ('a', 0), ('q', 0)], 1: [('z', 1), ('a', 1), ('q', 1)],
    2: [('x', 0), ('s', 0), ('w', 0)], 3: [('c', 2), ('d', 2), ('e', 2)],
    4: [('c', 0), ('d', 0), ('e', 0)], 5: [('v', 0), ('f', 0), ('r', 0)],
    6: [('v', 1), ('f', 1), ('r', 1)], 7: [('b', 0), ('g', 0), ('t', 0)],
    8: [('b', 1), ('g', 1), ('t', 1)], 9: [('n', 0), ('h', 0), ('y', 0)],
    10: [('m', 2), ('j', 2), ('u', 2)], 11: [('m', 0), ('j', 0), ('u', 0)]
}

EMBEDDED_LOCALES = {
    "en": {
        "lang_name": "English",
        "app_title": "WWM MELODY PLAYER",
        "menu_player": "Music Player",
        "menu_settings": "Settings",
        "menu_exit": "Exit",
        "settings_title": "Settings",
        "settings_lang_title": "Interface Language",
        "settings_layout_title": "Keyboard Layout",
        "settings_select": "Select option:",
        "settings_saved": "Settings saved!",
        "player_list_title": "Track List",
        "player_no_files": "No MIDI files found in 'Music' folder.",
        "player_select": "Select track number:",
        "player_analyzing": "Analyzing Harmony...",
        "player_rendering": "Pre-rendering events...",
        "step_layout_title": "Step 1: Choose Layout",
        "step_mode_title": "Step 2: Choose Mode",
        "stat_header": "COMPATIBILITY REPORT",
        "stat_compatible": "Playable Notes",
        "layout_21": "21 Keys (Standard)",
        "layout_36": "36 Keys (Chromatic)",
        "rec_title": "RECOMMENDATION",
        "rec_layout_21_reason": "Simple track. (Select: 21 Keys)",
        "rec_layout_36_reason": "Complex track / Accidentals. (Select: 36 Keys)",
        "rec_mode_strict_reason": "Fits perfectly in range. (Select: Strict)",
        "rec_mode_fold_reason": "Wide range, folding required. (Select: Fold)",
        "mode_strict": "Strict",
        "mode_fold": "Fold",
        "mode_melody": "Melody",
        "desc_strict": "Clean sound. Skips notes outside range.",
        "desc_fold": "Full sound. Wraps notes into range.",
        "desc_melody": "Solo mode. Prioritizes high notes.",
        "ui_back": "Back",
        "ui_auto": "Press Enter for recommended",
        "ui_layout": "Layout",
        "ui_mode": "Mode",
        "ui_shift": "Transpose",
        "play_ready": "READY TO PLAY",
        "play_info": "Engine: Pre-Render (Precision Mode)",
        "play_ctrl_start": "[F8] Start Playback",
        "play_ctrl_active": ">>> [F8] Playing...  |  [ESC] Stop <<<",
        "play_stopped": "Stopped.",
        "play_done": "Finished."
    },
    "ru": {
        "lang_name": "Русский",
        "app_title": "WWM MELODY PLAYER",
        "menu_player": "Музыкальный плеер",
        "menu_settings": "Настройки",
        "menu_exit": "Выход",
        "settings_title": "Настройки",
        "settings_lang_title": "Язык интерфейса",
        "settings_layout_title": "Настройка раскладки",
        "settings_select": "Выберите опцию:",
        "settings_saved": "Настройки сохранены!",
        "player_list_title": "Список треков",
        "player_no_files": "Нет файлов в папке 'Music'.",
        "player_select": "Номер трека:",
        "player_analyzing": "Анализ гармонии...",
        "player_rendering": "Пре-рендеринг событий...",
        "step_layout_title": "Шаг 1: Выбор раскладки",
        "step_mode_title": "Шаг 2: Выбор режима",
        "stat_header": "ОТЧЕТ О СОВМЕСТИМОСТИ",
        "stat_compatible": "Попадание в ноты",
        "layout_21": "21 Клавиша (Стандарт)",
        "layout_36": "36 Клавиш (Хроматика)",
        "rec_title": "РЕКОМЕНДАЦИЯ",
        "rec_layout_21_reason": "Трек простой. (Выберите: 21 Клавиша)",
        "rec_layout_36_reason": "Трек сложный / полутона. (Выберите: 36 Клавиш)",
        "rec_mode_strict_reason": "Все ноты влезают. (Выберите: Strict)",
        "rec_mode_fold_reason": "Широкий диапазон. (Выберите: Fold)",
        "mode_strict": "Strict (Чистый)",
        "mode_fold": "Fold (Полный)",
        "mode_melody": "Melody (Соло)",
        "desc_strict": "Пропуск нот вне диапазона.",
        "desc_fold": "Сжатие октав (все ноты).",
        "desc_melody": "Приоритет высоких нот.",
        "ui_back": "Назад",
        "ui_auto": "Нажмите Enter для авто-выбора",
        "ui_layout": "Раскладка",
        "ui_mode": "Режим",
        "ui_shift": "Сдвиг",
        "play_ready": "ГОТОВ К ЗАПУСКУ",
        "play_info": "Движок: Pre-Render (Точный режим)",
        "play_ctrl_start": "[F8] Начать воспроизведение",
        "play_ctrl_active": ">>> [F8] Играет...  |  [ESC] Стоп <<<",
        "play_stopped": "Остановлено.",
        "play_done": "Готово."
    }
}

C_TITLE = Style.BRIGHT + Fore.WHITE
C_TEXT = Style.BRIGHT + Fore.WHITE
C_ACCENT = Fore.YELLOW
C_SUCCESS = Fore.GREEN
C_ERROR = Fore.RED
C_INPUT = Fore.CYAN
C_DIM = Fore.LIGHTBLACK_EX
SEPARATOR = Fore.WHITE + "————————————————————"


class MidiRenderer:
    def __init__(self, filename, layout, mode, shift):
        self.filename = filename
        self.layout = layout
        self.mode = mode
        self.shift = shift
        self.events = []
        self.render()

    def get_key_action(self, note):
        final = note + self.shift

        if self.mode == 2:
            while final > GAME_MAX_NOTE: final -= 12
            while final < GAME_MIN_NOTE: final += 12
        elif self.mode == 1:
            if not (GAME_MIN_NOTE <= final <= GAME_MAX_NOTE):
                return None

        octave = (final // 12) - 1
        base = final % 12

        if self.layout == 36:
            if octave in [3, 4, 5]: return MAP_36[base][octave - 3]
        else:
            scale = {0: 0, 2: 1, 4: 2, 5: 3, 7: 4, 9: 5, 11: 6}
            if base in scale and octave in KEYS_21:
                return (KEYS_21[octave][scale[base]], 0)
        return None

    def render(self):
        mid = mido.MidiFile(self.filename)
        temp_timeline = {}
        current_time = 0.0

        for msg in mid:
            current_time += msg.time
            if msg.type == 'note_on' and msg.velocity > 0:
                if hasattr(msg, 'channel') and msg.channel == 9: continue

                action = self.get_key_action(msg.note)
                if action:
                    ts = round(current_time, 3)
                    if ts not in temp_timeline: temp_timeline[ts] = []
                    if action not in temp_timeline[ts]:
                        temp_timeline[ts].append(action)

        self.events = sorted(temp_timeline.items())

    def play(self, stop_event):
        if not self.events: return
        start_perf = time.perf_counter()

        for timestamp, actions in self.events:
            if stop_event.is_set(): break

            while True:
                if stop_event.is_set(): return
                current_perf = time.perf_counter() - start_perf
                wait_time = timestamp - current_perf

                if wait_time <= 0:
                    break

                if wait_time > 0.002:
                    time.sleep(wait_time - 0.001)
                else:
                    pass

            self.execute_batch(actions)

    def execute_batch(self, batch):
        g_none = [k for k, m in batch if m == 0]
        g_shift = [k for k, m in batch if m == 1]
        g_ctrl = [k for k, m in batch if m == 2]

        if g_none:
            for k in g_none: pydirectinput.keyDown(k)
            time.sleep(PRESS_DURATION)
            for k in g_none: pydirectinput.keyUp(k)

        if (g_shift or g_ctrl) and g_none: time.sleep(MOD_GAP)

        if g_shift:
            pydirectinput.keyDown('shift')
            for k in g_shift: pydirectinput.keyDown(k)
            time.sleep(PRESS_DURATION)
            for k in g_shift: pydirectinput.keyUp(k)
            pydirectinput.keyUp('shift')

        if g_ctrl and g_shift: time.sleep(MOD_GAP)

        if g_ctrl:
            pydirectinput.keyDown('ctrl')
            for k in g_ctrl: pydirectinput.keyDown(k)
            time.sleep(PRESS_DURATION)
            for k in g_ctrl: pydirectinput.keyUp(k)
            pydirectinput.keyUp('ctrl')


class BardApp:
    def __init__(self):
        self.lang = 'en'
        self.texts = {}
        self.init_files()
        self.load_config()
        self.load_locale()

    def init_files(self):
        if not os.path.exists(TRACKS_DIR): os.makedirs(TRACKS_DIR)
        if not os.path.exists(LOCALES_DIR): os.makedirs(LOCALES_DIR)

        for code, content in EMBEDDED_LOCALES.items():
            path = os.path.join(LOCALES_DIR, f"{code}.json")
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(content, f, indent=4, ensure_ascii=False)
            except:
                pass

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    self.lang = json.load(f).get('language', 'en')
            except:
                pass

    def save_config(self):
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump({'language': self.lang}, f)
        except:
            pass

    def load_locale(self):
        path = os.path.join(LOCALES_DIR, f'{self.lang}.json')
        if not os.path.exists(path):
            if self.lang in EMBEDDED_LOCALES:
                pass

        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self.texts = json.load(f)
                    return
            except:
                pass
        self.texts = {}

    def t(self, key):
        return self.texts.get(key, f"[{key}]")

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def header(self, txt):
        print(f"\n{C_TITLE}{txt.upper()}\n{SEPARATOR}")

    def print_item(self, idx, text, active=False):
        marker = f"{C_SUCCESS}●" if active else f"{C_TEXT}○"
        print(f"{C_ACCENT}[{idx}] {marker} {C_TEXT}{text}")

    def prompt(self):
        return input(f"\n{C_INPUT}> {Style.RESET_ALL}")

    def print_back(self):
        print(f"\n{C_ACCENT}[0] {C_TEXT}{self.t('ui_back')}")

    def get_notes(self, path):
        notes = []
        try:
            mid = mido.MidiFile(path)
            for msg in mid:
                if msg.type == 'note_on' and msg.velocity > 0:
                    if hasattr(msg, 'channel') and msg.channel == 9: continue
                    notes.append(msg.note)
        except:
            pass
        return notes

    def analyze(self, notes):
        if not notes: return (0, 0, 0, 0, 0, 0)
        total = len(notes)
        scale_21 = {0, 2, 4, 5, 7, 9, 11}

        best_sh21 = 0;
        max_s21 = -1
        for sh in range(-12, 13):
            hits = 0
            for n in notes:
                t = n + sh
                if (t % 12) in scale_21 and GAME_MIN_NOTE <= t <= GAME_MAX_NOTE: hits += 1
            if hits > max_s21: max_s21, best_sh21 = hits, sh
        fold_hits_21 = sum(1 for n in notes if ((n + best_sh21) % 12) in scale_21)

        best_sh36 = 0;
        max_s36 = -1
        for sh in range(-12, 13):
            hits = sum(1 for n in notes if GAME_MIN_NOTE <= (n + sh) <= GAME_MAX_NOTE)
            if hits > max_s36: max_s36, best_sh36 = hits, sh

        return (best_sh21, (max_s21 / total) * 100, (fold_hits_21 / total) * 100,
                best_sh36, (max_s36 / total) * 100, 100.0)

    def color_stat(self, val):
        if val >= 99: return C_SUCCESS
        if val >= 80: return C_ACCENT
        return C_ERROR

    def menu_main(self):
        while True:
            self.clear()
            self.header(self.t('app_title'))
            print(f"{C_ACCENT}[1] {C_TEXT}{self.t('menu_player')}")
            print(f"{C_ACCENT}[2] {C_TEXT}{self.t('menu_settings')}")
            print(f"{C_ACCENT}[3] {C_TEXT}{self.t('menu_exit')}")
            c = self.prompt()
            if c == '1':
                self.menu_player()
            elif c == '2':
                self.menu_settings()
            elif c == '3':
                sys.exit()

    def menu_settings(self):
        while True:
            self.clear()
            self.header(self.t('settings_title'))
            langs = []
            if os.path.exists(LOCALES_DIR):
                for f in os.listdir(LOCALES_DIR):
                    if f.endswith('.json'):
                        try:
                            with open(os.path.join(LOCALES_DIR, f), encoding='utf-8') as fl:
                                langs.append((f[:-5], json.load(fl).get('lang_name', '?')))
                        except:
                            pass

            print(f"{C_TEXT}{self.t('settings_lang_title')}")
            for i, (code, name) in enumerate(langs):
                self.print_item(i + 1, name, code == self.lang)
            self.print_back()
            print(f"{C_TEXT}{self.t('settings_select')}")
            try:
                c = self.prompt()
                if c == '0': return
                idx = int(c) - 1
                if 0 <= idx < len(langs):
                    self.lang = langs[idx][0];
                    self.save_config();
                    self.load_locale()
                    print(f"{C_SUCCESS}OK");
                    time.sleep(0.3)
            except:
                continue

    def menu_player(self):
        while True:
            self.clear()
            files = []
            if os.path.exists(TRACKS_DIR):
                files = [f for f in os.listdir(TRACKS_DIR) if f.lower().endswith(('.mid', '.midi'))]
            self.header(self.t('player_list_title'))
            if not files:
                print(f"{C_ERROR}{self.t('player_no_files')}");
                self.print_back();
                self.prompt();
                return

            for i, f in enumerate(files): print(f"{C_ACCENT}[{i + 1}] {C_TEXT}{f}")
            self.print_back();
            print(f"{C_TEXT}{self.t('player_select')}")

            try:
                c = self.prompt()
                if c == '0': return
                idx = int(c) - 1
                if 0 <= idx < len(files): self.flow_setup(os.path.join(TRACKS_DIR, files[idx]), files[idx])
            except:
                continue

    def flow_setup(self, path, name):
        print(f"\n{C_TEXT}{self.t('player_analyzing')}")
        notes = self.get_notes(path)
        (sh21, s21, f21, sh36, s36, f36) = self.analyze(notes)

        self.clear()
        self.header(self.t('step_layout_title'))
        print(f"{C_TEXT}{self.t('stat_header')}")
        print(
            f"{C_ACCENT}{self.t('layout_21'):<30} {self.color_stat(f21)}{f21:.0f}% {C_TEXT}{self.t('stat_compatible')}")
        print(
            f"{C_ACCENT}{self.t('layout_36'):<30} {self.color_stat(f36)}{f36:.0f}% {C_TEXT}{self.t('stat_compatible')}")

        rec_layout = 36
        reason = self.t('rec_layout_36_reason')
        if s21 >= 98 or f21 >= 98: rec_layout = 21; reason = self.t('rec_layout_21_reason')

        print(f"\n{C_SUCCESS}{self.t('rec_title')}: {C_TEXT}{reason}")
        print(f"{SEPARATOR}")
        print(f"{C_ACCENT}[1] {C_TEXT}{self.t('layout_21')}")
        print(f"{C_ACCENT}[2] {C_TEXT}{self.t('layout_36')}")
        self.print_back();
        print(f"{C_TEXT}{self.t('ui_auto')}")

        try:
            l = self.prompt()
            if l == '0': return
            layout = 36 if l == '2' else 21 if l == '1' else rec_layout
        except:
            layout = rec_layout

        self.clear()
        self.header(self.t('step_mode_title'))

        ts = s36 if layout == 36 else s21
        tf = f36 if layout == 36 else f21
        shift = sh36 if layout == 36 else sh21

        print(f"{C_TEXT}{self.t('stat_header')} ({layout})")
        print(f"{C_TEXT}{self.t('mode_strict'):<20} {self.color_stat(ts)}{ts:.0f}%")
        print(f"{C_TEXT}{self.t('mode_fold'):<20} {self.color_stat(tf)}{tf:.0f}%")

        rec_mode = 2
        rm = self.t('rec_mode_fold_reason')
        if ts >= 99: rec_mode = 1; rm = self.t('rec_mode_strict_reason')

        print(f"\n{C_SUCCESS}{self.t('rec_title')}: {C_TEXT}{rm}")
        print(f"{SEPARATOR}")
        print(f"{C_ACCENT}[1] {C_TEXT}{self.t('mode_strict')} {C_DIM}- {self.t('desc_strict')}")
        print(f"{C_ACCENT}[2] {C_TEXT}{self.t('mode_fold')}   {C_DIM}- {self.t('desc_fold')}")
        print(f"{C_ACCENT}[3] {C_TEXT}{self.t('mode_melody')} {C_DIM}- {self.t('desc_melody')}")
        self.print_back();
        print(f"{C_TEXT}{self.t('ui_auto')}")

        try:
            m = self.prompt()
            if m == '0': return
            mode = int(m) if m else rec_mode
        except:
            mode = rec_mode

        if mode == 3 and notes: shift = GAME_MAX_NOTE - max(notes)

        print(f"\n{C_TEXT}{self.t('player_rendering')}")
        renderer = MidiRenderer(path, layout, mode, shift)

        self.clear()
        self.header(name)
        print(f"{C_TEXT}{self.t('ui_layout')}: {C_ACCENT}{layout} {C_TEXT}| {self.t('play_info')}")
        print(f"{C_TEXT}{self.t('ui_mode')}:   {C_ACCENT}{mode} {C_DIM}({self.t('ui_shift')}: {shift})\n")

        print(f"{C_TEXT}{self.t('play_ready')}")
        print(f"{C_ACCENT}{self.t('play_ctrl_start')}")
        self.print_back()

        stop_event = threading.Event()
        start = False
        while True:
            if keyboard.is_pressed(BIND_START): start = True; break
            if keyboard.is_pressed(BIND_STOP) or keyboard.is_pressed('0'): break
            time.sleep(0.01)
        if not start: return

        print(f"\n{C_SUCCESS}{self.t('play_ctrl_active')}")

        play_thread = threading.Thread(target=renderer.play, args=(stop_event,))
        play_thread.start()

        while play_thread.is_alive():
            if keyboard.is_pressed(BIND_STOP):
                stop_event.set()
                print(f"\n{C_ERROR}{self.t('play_stopped')}")
                break
            time.sleep(0.05)

        play_thread.join()

        time.sleep(0.3)
        pydirectinput.keyUp('shift');
        pydirectinput.keyUp('ctrl')

        if not stop_event.is_set():
            print(f"\n{C_SUCCESS}{self.t('play_done')}")
        time.sleep(1.5)


if __name__ == "__main__":
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print("Run as Admin!");
        input()
    else:
        try:
            BardApp().menu_main()
        except KeyboardInterrupt:
            sys.exit()