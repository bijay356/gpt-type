import os
import shutil
import subprocess
import zipfile

# Directory setup
launcher_dir = r'f:\blogger web\windows-app\launcher'
windows_app_dir = r'f:\blogger web\windows-app'
root_dir = r'f:\blogger web'

theme_path = os.path.join(root_dir, 'typeshala-blogger-theme.xml')
html_file = os.path.join(windows_app_dir, 'index.html')
ico = os.path.join(windows_app_dir, 'favicon.ico')
csc = r'C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe'

app_launcher_cs = os.path.join(launcher_dir, 'AppLauncher.cs')
un_cs = os.path.join(launcher_dir, 'Uninstall.cs')
un_exe = os.path.join(launcher_dir, 'Uninstall.exe')
setup_cs = os.path.join(launcher_dir, 'SetupInstaller.cs')
app_manifest = os.path.join(launcher_dir, 'app.manifest')
assembly_info = os.path.join(launcher_dir, 'AssemblyInfo.cs')
installer_assembly_info = os.path.join(launcher_dir, 'InstallerAssemblyInfo.cs')

target_app_exe = os.path.join(root_dir, 'GPT-TYPE.exe')
target_setup_exe = os.path.join(root_dir, 'GPT-TYPE-Setup.exe')

print("1. Compiling GPT-TYPE.exe...")
subprocess.run([
    csc, '/nologo', '/target:winexe', f'/win32icon:{ico}',
    f'/win32manifest:{app_manifest}',
    f'/resource:{html_file},index.html',
    f'/resource:{ico},favicon.ico',
    f'/out:{target_app_exe}',
    app_launcher_cs, assembly_info
], check=True)

print("2. Compiling Uninstall.exe...")
subprocess.run([
    csc, '/nologo', '/target:winexe', f'/win32icon:{ico}',
    f'/win32manifest:{app_manifest}',
    f'/out:{un_exe}',
    un_cs, assembly_info
], check=True)

print("3. Compiling GPT-TYPE-Setup.exe...")
subprocess.run([
    csc, '/nologo', '/target:winexe', f'/win32icon:{ico}',
    f'/win32manifest:{app_manifest}',
    f'/resource:{target_app_exe},GPT-TYPE.exe',
    f'/resource:{ico},favicon.ico',
    f'/resource:{un_exe},Uninstall.exe',
    f'/resource:{html_file},index.html',
    f'/out:{target_setup_exe}',
    setup_cs, installer_assembly_info
], check=True)

# Copy to windows-app folder
shutil.copy2(target_app_exe, os.path.join(windows_app_dir, 'GPT-TYPE.exe'))
shutil.copy2(target_setup_exe, os.path.join(windows_app_dir, 'GPT-TYPE-Setup.exe'))

# Package into GPT-TYPE-Downloads
downloads_dir = os.path.join(root_dir, 'GPT-TYPE-Downloads')
if not os.path.exists(downloads_dir):
    os.makedirs(downloads_dir, exist_ok=True)

shutil.copy2(target_app_exe, os.path.join(downloads_dir, 'GPT-TYPE.exe'))
shutil.copy2(target_setup_exe, os.path.join(downloads_dir, 'GPT-TYPE-Setup.exe'))

with zipfile.ZipFile(os.path.join(downloads_dir, 'GPT-TYPE-Portable.zip'), 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.write(target_app_exe, 'GPT-TYPE.exe')
    bat = os.path.join(downloads_dir, 'Install-GPT-TYPE.bat')
    if os.path.exists(bat):
        zf.write(bat, 'Install-GPT-TYPE.bat')

with zipfile.ZipFile(os.path.join(downloads_dir, 'GPT-TYPE-Windows-Setup.zip'), 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.write(target_setup_exe, 'GPT-TYPE-Setup.exe')
    bat = os.path.join(downloads_dir, 'Install-GPT-TYPE.bat')
    if os.path.exists(bat):
        zf.write(bat, 'Install-GPT-TYPE.bat')

with zipfile.ZipFile(os.path.join(downloads_dir, 'GPT-TYPE-Windows.zip'), 'w', zipfile.ZIP_DEFLATED) as zf:
    zf.write(target_setup_exe, 'GPT-TYPE-Setup.exe')
    zf.write(target_app_exe, 'GPT-TYPE.exe')
    bat = os.path.join(downloads_dir, 'Install-GPT-TYPE.bat')
    if os.path.exists(bat):
        zf.write(bat, 'Install-GPT-TYPE.bat')
    info = os.path.join(downloads_dir, 'HOW_TO_SHARE_THESE_FILES.txt')
    if os.path.exists(info):
        zf.write(info, 'HOW_TO_SHARE_THESE_FILES.txt')

# Update installed version if present
local_app_dir = os.path.expandvars(r'%LocalAppData%\Programs\GPT-TYPE')
if os.path.exists(local_app_dir):
    shutil.copy2(target_app_exe, os.path.join(local_app_dir, 'GPT-TYPE.exe'))
    shutil.copy2(html_file, os.path.join(local_app_dir, 'index.html'))

# Copy theme to Desktop and Downloads
desktop_theme = os.path.join(os.path.expanduser('~'), 'Desktop', 'typeshala-blogger-theme.xml')
downloads_theme = os.path.join(os.path.expanduser('~'), 'Downloads', 'typeshala-blogger-theme.xml')
try:
    shutil.copy2(theme_path, desktop_theme)
except Exception:
    pass
try:
    shutil.copy2(theme_path, downloads_theme)
except Exception:
    pass

print("Build complete! Binaries, ZIPs, and local install updated successfully.")
