using System;
using System.Diagnostics;
using System.IO;
using System.Windows.Forms;
using Microsoft.Win32;

namespace GptType
{
    static class Uninstaller
    {
        [STAThread]
        static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);

            DialogResult confirm = MessageBox.Show(
                "Are you sure you want to completely remove GPT-TYPE and all of its components?",
                "GPT-TYPE Uninstall",
                MessageBoxButtons.YesNo,
                MessageBoxIcon.Question
            );

            if (confirm != DialogResult.Yes)
            {
                return;
            }

            try
            {
                // 1. Remove Desktop Shortcut
                string desktop = Environment.GetFolderPath(Environment.SpecialFolder.Desktop);
                string desktopShortcut = Path.Combine(desktop, "GPT-TYPE.lnk");
                if (File.Exists(desktopShortcut))
                {
                    try { File.Delete(desktopShortcut); } catch { }
                }

                // 2. Remove Start Menu Shortcut
                string programs = Environment.GetFolderPath(Environment.SpecialFolder.Programs);
                string startShortcut = Path.Combine(programs, "GPT-TYPE.lnk");
                if (File.Exists(startShortcut))
                {
                    try { File.Delete(startShortcut); } catch { }
                }

                // 3. Remove Registry Entry
                try
                {
                    using (RegistryKey key = Registry.CurrentUser.OpenSubKey(@"Software\Microsoft\Windows\CurrentVersion\Uninstall", true))
                    {
                        if (key != null)
                        {
                            key.DeleteSubKeyTree("GPT-TYPE", false);
                        }
                    }
                }
                catch { }

                // 4. Clean up installation directory
                string appDir = AppDomain.CurrentDomain.BaseDirectory.TrimEnd('\\', '/');

                MessageBox.Show(
                    "GPT-TYPE was successfully removed from your computer.",
                    "Uninstall Complete",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Information
                );

                // Spawn background cleanup to delete directory after process exit
                ProcessStartInfo psi = new ProcessStartInfo();
                psi.FileName = "cmd.exe";
                psi.Arguments = string.Format("/C ping 127.0.0.1 -n 2 > nul & rmdir /s /q \"{0}\"", appDir);
                psi.WindowStyle = ProcessWindowStyle.Hidden;
                psi.CreateNoWindow = true;
                Process.Start(psi);
            }
            catch (Exception ex)
            {
                MessageBox.Show("Error during uninstall: " + ex.Message, "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }
    }
}
