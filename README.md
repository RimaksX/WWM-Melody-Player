<div align="center">

# WWM Melody Player

**A lightweight, automated MIDI instrument player for *Where Winds Meet*.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)](https://www.python.org/)
[![Release](https://img.shields.io/badge/release-v1.0-orange?style=flat-square)](https://github.com/RimaksX/WWM-Melody-Player/releases)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)

</div>

---

## ⚡ Overview

**WWM Melody Player** allows you to play `.mid` files automatically using the in-game instrument system. Built specifically for **Where Winds Meet**, it offers smart transposition, multi-threaded input for chords, and a sleek console interface.

## ✨ Key Features

*   **🎹 Smart Analysis:** Automatically calculates the best key transposition to fit the game's limited 3-octave range.
*   **🧠 Playback Modes:**
    *   **Strict:** Plays only valid notes for a clean, classical sound.
    *   **Fold:** Wraps high/low notes into the playable range for a richer, fuller sound.
    *   **Melody:** Prioritizes high notes for solos.
*   **🚀 Self-Contained:** Automatically deploys necessary folders (`Music`, `locales`) upon first launch.
*   **🌍 Localization:** Full English and Russian support (auto-detected).

---

## 📥 Quick Start

1.  **Download** the latest `.exe` from the [Releases Page](https://github.com/RimaksX/WWM-Melody-Player/releases).
2.  **Run** `WWM_Melody_Player.exe` as **Administrator**.
    > ⚠️ **Note:** Admin rights are required for the program to send keystrokes to the game window.
3.  The program will create a `Music` folder next to the executable.
4.  **Place** your `.mid` files into the `Music` folder.

---

## 🎮 Controls

| Key | Action             |
| :--- |:-------------------|
| **F8** | **Start Playback** |
| **ESC** | **Stop**           |
| **0** | **Back**           |

---

## 📄 Disclaimer
This software is an external automation tool. While it does not inject code into the game, use it at your own risk. The developer is not responsible for any account penalties.