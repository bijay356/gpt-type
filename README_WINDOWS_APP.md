# GPT-TYPE Windows Desktop Software

Welcome to the **GPT-TYPE** offline Windows Desktop Application.

---

## 🚀 How to Run Immediately (Zero Install / 1-Click)

1. Simply double-click **`Start-GPT-TYPE-Desktop.bat`** (in `f:\blogger web\`) or **`Start-GPT-TYPE.bat`** (inside `windows-app/`).
2. The application will instantly launch in a dedicated, high-performance desktop window without browser bars or distractions!
3. All **123+ languages**, **Typeshala Preeti & Unicode**, and the **Ramayan Archery Game** work **100% offline without any internet connection**.

---

## 🛠️ How to Build an Official `.exe` Installer with Electron

If you want to compile a standalone Windows installer (`GPT-TYPE-Setup.exe`) or portable executable:

1. Open PowerShell or Command Prompt in `f:\blogger web\windows-app`:
   ```bash
   cd "f:\blogger web\windows-app"
   ```
2. Install Electron dependencies (one-time setup):
   ```bash
   npm install
   ```
3. Test in Electron:
   ```bash
   npm start
   ```
4. Build the standalone `.exe` installer:
   ```bash
   npm run dist
   ```
   The generated Windows executable installer will be created inside the `windows-app\dist\` folder!
