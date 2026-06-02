# PC Monitor Serial Sender

A Windows desktop app that reads your PC's live hardware stats (CPU, GPU, RAM,
network, temperatures) and streams them over a serial (USB) connection to an
Arduino/microcontroller driving one or more I²C character LCDs (1602 / 2004).

Built with Tkinter, it ships as a single `main.py` and is designed to run as a
standalone Windows EXE (PyInstaller-compatible). Branded as *Rozakos Industries*.

---

## Features

- **Live hardware monitoring**
  - CPU load & temperature
  - GPU load, VRAM usage & temperature
  - RAM usage (used / total)
  - Network down/up throughput and NIC link speed
- **Serial streaming** to an Arduino at a configurable baud rate (default `115200`).
- **Mixed LCD support** — each discovered I²C address can be configured as a
  `1602` (16×2) or `2004` (20×4) display at runtime.
- **Auto-discovery** — the firmware reports the LCDs it finds (`FOUND_LCD=0x27`)
  and the app picks them up automatically.
- **Configurable pages** — choose which metric "pages" (CPU / GPU / RAM / NET)
  are shown, in what order, and the per-page dwell time.
- **Dark themed GUI** with a simulated on-screen LCD preview and a live log.
- **System tray** support (minimize to tray, start minimized).
- **Start-on-boot** via an elevated logon Scheduled Task (no UAC prompt at login).
- **Self-installing dependencies** — auto-installs `pythonnet`, the
  .NET 9 Desktop Runtime, and downloads LibreHardwareMonitor for temperatures.

---

## Download

Prebuilt Windows binary (no install needed):

**[Download PC-Monitor-Sender.exe](https://github.com/Rozakos/PC-Monitor-Serial-Sender/releases/latest)** — from the latest release.

Run it as administrator (the app self-elevates) so CPU/GPU temperatures work;
LibreHardwareMonitor is downloaded automatically on first run. Prefer to build
it yourself? See [Building an EXE](#building-an-exe).

## Requirements

- Windows 10 / 11
- Python 3.x (if running from source)
- An Arduino (or compatible MCU) flashed with the companion firmware that parses
  the serial protocol below and drives the I²C LCD(s).

### Python packages

```
pip install pyserial psutil pystray pillow pythonnet
```

| Package | Purpose |
| --- | --- |
| `pyserial` | Serial communication with the Arduino |
| `psutil` | CPU / RAM / network stats |
| `pystray` + `pillow` | System-tray icon |
| `pythonnet` | Bridge to LibreHardwareMonitor (`.NET`) for temperatures |

> Temperatures rely on **LibreHardwareMonitor** (`LibreHardwareMonitorLib.dll`),
> which the app can download automatically. Reading sensors requires the app to
> run **elevated** (admin) — it will offer to relaunch itself via UAC.

---

## Running

From source:

```powershell
python main.py
```

Or build a standalone EXE (see [Building an EXE](#building-an-exe)) and run that.
The app stores its settings at `~/.pcmonitor_sender.json`.

### Quick start

1. Connect the Arduino over USB.
2. Launch the app and open the **Settings** tab.
3. Pick the serial **port** (use *Scan* to list available ports) and **baud rate**.
4. Choose which pages to display and their order.
5. Click **Start**. The app connects, waits for the firmware's `READY`, and
   begins streaming. Discovered LCDs appear in the LCD config — set each to
   `1602` or `2004` as appropriate.

---

## Building an EXE

No installer is required — the app builds into a single self-contained `.exe`.
LibreHardwareMonitor is downloaded at runtime and settings live in your user
profile, so nothing else needs bundling.

The simplest way:

```powershell
.\build.ps1
```

This installs PyInstaller if needed and builds from `PC-Monitor-Sender.spec`,
producing `dist\PC-Monitor-Sender.exe`. Use `.\build.ps1 -Clean` to wipe
`build\` and `dist\` first.

Equivalent manual command:

```powershell
pyinstaller PC-Monitor-Sender.spec
```

The spec produces a **windowed** (no console) one-file EXE with `icon.ico`
embedded and bundled, and pins the dynamic imports (`pystray`, `PIL`,
`pyserial`, `pythonnet`/`clr`) so they aren't missed.

Notes:

- The app **self-elevates via UAC at runtime**, so the EXE doesn't need an
  admin manifest.
- One-file EXEs unpack to a temp dir on launch, so first start is a little
  slower. Bare PyInstaller EXEs can also trip SmartScreen/AV false positives —
  code-signing resolves that.

## Serial protocol

The app opens the port with DTR/RTS de-asserted (to avoid resetting the board),
waits up to 8 s for a line containing `READY`, then sends one stats frame
per loop terminated by `\r\n`. Fields are `;`-separated `KEY=VALUE` groups.

**Example frame:**

```
CPU=423;RAM=587;GPU=120;DL=45;UL=12;RAMU=9381;RAMT=16384;VRAM=512;VRAMT=2048;TEMP=565;GPUT=489;LSPD=1000;PG=15;PDLY=3000;PGORD=0,1,2,3;LCD2004=38
```

| Field | Meaning |
| --- | --- |
| `CPU` | CPU load × 10 (e.g. `423` = 42.3 %) |
| `RAM` | RAM usage × 10 |
| `GPU` | GPU load × 10 |
| `DL` / `UL` | Download / upload throughput in KB/s |
| `RAMU` / `RAMT` | RAM used / total, in MB |
| `VRAM` / `VRAMT` | VRAM used / total, in MB |
| `TEMP` | CPU temp × 10 (`-1` = N/A) |
| `GPUT` | GPU temp × 10 (`-1` = N/A) |
| `LSPD` | NIC link speed, Mbps |
| `PG` | Page bitmask (bit0=CPU, bit1=GPU, bit2=RAM, bit3=NET) |
| `PDLY` | Per-page dwell time, ms |
| `PGORD` | Page display order, e.g. `0,1,2,3` |
| `LCD2004` | Comma-separated decimal I²C addresses configured as 20×4 (omitted if none) |

**Device → host messages the app listens for:**

- `READY` — firmware is up and ready to receive frames.
- `FOUND_LCD=0x27` — an LCD was discovered at the given I²C address.

**Host → device commands:**

- `IDENT` — sent when you click *Identify*, so the firmware can flash an ID on
  each screen to help you map addresses to physical displays.

---

## Settings & persistence

Settings are saved to `~/.pcmonitor_sender.json`, including the selected port,
baud rate, page selection/order, page delay, LCD type map, and the
LibreHardwareMonitor DLL path. Start-on-boot is implemented as a Windows logon
Scheduled Task named `RozakosPCMonitorSender` that runs with highest privileges
so the elevated app launches silently and minimized to tray.

---

## License / Branding

*Rozakos Industries* — <https://rozakos.com>
