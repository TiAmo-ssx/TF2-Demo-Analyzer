[中文](./README.md) | English

# TF2 Demo Analyzer

Got a pile of TF2 demos sitting on your hard drive? Their filenames are just a string of timestamps — they look familiar, but you can't remember who carried that match and who got stomped.

> Turn a pile of `.dem` files gathering dust on your hard drive into a readable match report.

A TF2 (Team Fortress 2) demo analysis tool. Pick a `.dem` file, parse out the match data, and view the report in your browser.

## ✨ Features

- 🔍 Demo parsing: a Rust parser based on [demostf/parser](https://github.com/demostf/parser) that extracts players, kills, classes, weapons, rounds, chat, and more
- 💾 Data stored in a local SQLite database, queryable anytime
- 🧾 SHA-256 dedup, so the same demo never gets imported twice
- 🖥️ Desktop UI (Tkinter) for selecting and parsing files; parsing runs in a background thread so the UI stays responsive
- 📊 Web dashboard (Flask + Chart.js) showing red vs blue totals, player charts, rounds, etc.
- 🗂️ Manage page with search, sorting, and multi-select delete; deleting only affects the database, not the files on disk
- 🌐 Supports 中文 / English / 한국어 / 日本語
- 📦 Packaged with PyInstaller into a portable exe — the target machine doesn't need Python or anything else

## 🚀 Getting Started

### Download the release

1. Download `TF2-Demo-Analyzer-v1.0.0.zip` from [Releases](https://github.com/TiAmo-ssx/TF2-Demo-Analyzer/releases) and unzip it.
2. Double-click `TF2-Demo-Analyzer.exe`.
3. Click "Add files" or "Add folder" to pick your `.dem` files, then click "Start parsing".
4. When it's done, the web report opens automatically — or use "Open dashboard" / "Manage matches".

### Build from source

```bash
git clone https://github.com/TiAmo-ssx/TF2-Demo-Analyzer.git
cd TF2-Demo-Analyzer
pip install -r requirements.txt
```

Note: the repo doesn't include `parse_demo.exe` (the Rust parser binary). Download it from Releases or build the Rust parser yourself and put it at `resources/parser/parse_demo.exe`.

To package:

```bash
build.bat
```

or:

```bash
python -m PyInstaller --clean --noconfirm TF2-Demo-Analyzer.spec
```

The output is in `dist/TF2-Demo-Analyzer/`.

## 📁 Project Structure

```
TF2-Demo-Analyzer/
├── app.py                   # entry point
├── config/config.py         # paths and config
├── core/                    # core logic
│   ├── parser.py            #   Rust parser wrapper
│   ├── analyzer.py          #   data analysis
│   ├── database.py          #   SQLite database
│   ├── hash_manager.py      #   SHA-256 dedup
│   └── task_manager.py      #   batch task orchestration
├── gui/main_window.py       # Tkinter main window
├── web/                     # Flask web app
│   ├── server.py            #   server, free-port lookup
│   ├── routes.py            #   routes
│   ├── templates/           #   templates
│   └── static/              #   CSS / JS / Chart.js
├── utils/i18n.py            # i18n
├── requirements.txt
├── build.bat                # build script
└── TF2-Demo-Analyzer.spec   # PyInstaller config
```

## 💾 Where the Data Lives

- Development: `workspace/` inside the project
- Release (exe): `%LOCALAPPDATA%\TF2-Demo-Analyzer`

The database is stored in the user directory rather than next to the exe, so it still works if the program is installed somewhere like `Program Files` that isn't writable.

## ❓ FAQ

- Does deleting a record delete the demo file? No — it only affects the database.
- Can others access the web page? No — the server only listens on `127.0.0.1`.
- What if the port is taken? It automatically finds a free port.
- Does the language setting persist? Yes — the web page uses a cookie, the desktop app uses `settings.json`.

## 🙏 Acknowledgments

Demo parsing is powered by [demostf/parser](https://github.com/demostf/parser). Thanks to the project for providing the Rust library built specifically for TF2 demos, which brings richer data to this project.

## 📄 License

You're free to use, copy, modify, distribute, and use the software commercially, provided you keep the original copyright notice and license text when distributing the software or substantial portions of it.

The software is provided "as is", and the author is not responsible for any problems or losses arising from its use.

[MIT](./LICENSE)

## P.S.

This is probably the final version — I don't have much energy left to keep improving it 😬. If you run into problems, you can find me on Bilibili 😯

Here's the link 🤲 https://space.bilibili.com/505994875/
