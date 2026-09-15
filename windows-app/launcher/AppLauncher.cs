using System;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Threading;
using System.Windows.Forms;

namespace GptType
{
    static class AppLauncher
    {
        static string logFile = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "GPT-TYPE", "launcher.log");

        static void Log(string msg)
        {
            try
            {
                File.AppendAllText(logFile, string.Format("[{0:HH:mm:ss.fff}] {1}\r\n", DateTime.Now, msg));
            }
            catch { }
        }

        [STAThread]
        static void Main(string[] args)
        {
            try
            {
                File.WriteAllText(logFile, "=== GPT-TYPE Launch Log ===\r\n");
                Log("BaseDirectory: " + AppDomain.CurrentDomain.BaseDirectory);
                // 1. Determine base working directory & target index.html
                string appDir = AppDomain.CurrentDomain.BaseDirectory;
                string localHtml = Path.Combine(appDir, "index.html");
                string targetHtml = localHtml;

                // If local index.html does not exist, extract from embedded resource to %LocalAppData%\GPT-TYPE
                if (!File.Exists(localHtml))
                {
                    string userDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "GPT-TYPE");
                    if (!Directory.Exists(userDir))
                    {
                        Directory.CreateDirectory(userDir);
                    }
                    targetHtml = Path.Combine(userDir, "index.html");

                    try
                    {
                        Assembly asm = Assembly.GetExecutingAssembly();
                        using (Stream resStream = asm.GetManifestResourceStream("index.html"))
                        {
                            if (resStream != null)
                            {
                                using (FileStream fs = new FileStream(targetHtml, FileMode.Create, FileAccess.Write, FileShare.ReadWrite))
                                {
                                    resStream.CopyTo(fs);
                                }
                            }
                        }
                    }
                    catch
                    {
                        // If extraction fails because the file is in use, proceed if it already exists
                        if (!File.Exists(targetHtml))
                        {
                            MessageBox.Show("Could not extract index.html for GPT-TYPE.", "GPT-TYPE Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                            return;
                        }
                    }
                }

                if (!File.Exists(targetHtml))
                {
                    MessageBox.Show("Could not find index.html for GPT-TYPE.", "GPT-TYPE Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                    return;
                }

                string fileUri = "file:///" + targetHtml.Replace('\\', '/');

                // 2. Clean up any stale locks or orphaned zombie Edge processes for GPT-TYPE
                CleanupZombieBrowserInstances();

                // 3. Locate Browsers
                string edgePath = LocateEdge();
                string chromePath = LocateChrome();
                string userDataDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "GPT-TYPE", "EdgeProfile");

                // Tier 1: Try Edge in App Mode with Profile (dedicated app window, native desktop look)
                if (!string.IsNullOrEmpty(edgePath) && File.Exists(edgePath))
                {
                    string args1 = string.Format("--app=\"{0}\" --user-data-dir=\"{1}\" --window-size=1280,850 --no-first-run", fileUri, userDataDir);
                    if (TryLaunchBrowser(edgePath, args1))
                    {
                        return;
                    }

                    // Tier 2: Try Edge in App Mode without custom profile
                    string args2 = string.Format("--app=\"{0}\" --window-size=1280,850", fileUri);
                    if (TryLaunchBrowser(edgePath, args2))
                    {
                        return;
                    }
                }

                // Tier 3: Try Chrome in App Mode with Profile
                if (!string.IsNullOrEmpty(chromePath) && File.Exists(chromePath))
                {
                    string chromeProfile = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "GPT-TYPE", "ChromeProfile");
                    string args3 = string.Format("--app=\"{0}\" --user-data-dir=\"{1}\" --window-size=1280,850 --no-first-run", fileUri, chromeProfile);
                    if (TryLaunchBrowser(chromePath, args3))
                    {
                        return;
                    }

                    // Tier 4: Try Chrome in App Mode without profile
                    string args4 = string.Format("--app=\"{0}\" --window-size=1280,850", fileUri);
                    if (TryLaunchBrowser(chromePath, args4))
                    {
                        return;
                    }
                }

                // Tier 5: Try Default Browser via File URI
                try
                {
                    ProcessStartInfo psi = new ProcessStartInfo(fileUri);
                    psi.UseShellExecute = true;
                    Process.Start(psi);
                    return;
                }
                catch { }

                // Tier 6: Try Shell Open on the target HTML file
                try
                {
                    ProcessStartInfo psi = new ProcessStartInfo(targetHtml);
                    psi.UseShellExecute = true;
                    Process.Start(psi);
                    return;
                }
                catch (Exception ex)
                {
                    MessageBox.Show("Failed to launch GPT-TYPE: " + ex.Message, "GPT-TYPE Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show("Fatal Error launching GPT-TYPE: " + ex.Message, "GPT-TYPE Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private static bool TryLaunchBrowser(string exePath, string args)
        {
            try
            {
                Log("TryLaunchBrowser: " + exePath + " " + args);
                ProcessStartInfo psi = new ProcessStartInfo();
                psi.FileName = exePath;
                psi.Arguments = args;
                psi.UseShellExecute = true;
                psi.WindowStyle = ProcessWindowStyle.Normal;

                Process p = Process.Start(psi);
                if (p == null)
                {
                    Log("Process.Start returned null");
                    return false;
                }

                Log("Process.Start returned Id=" + p.Id);

                // Check if it exited immediately with an error code (e.g. exit code 21, crash, etc.)
                if (p.WaitForExit(1200))
                {
                    Log("Process exited within 1200ms with ExitCode=" + p.ExitCode);
                    return p.ExitCode == 0;
                }

                // Still running after 1200ms -> successfully launched!
                Log("Process still running after 1200ms -> SUCCESS");
                return true;
            }
            catch (Exception ex)
            {
                Log("TryLaunchBrowser Exception: " + ex.Message);
                return false;
            }
        }

        private static void CleanupZombieBrowserInstances()
        {
            try
            {
                string profileDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "GPT-TYPE", "EdgeProfile");
                string lockPath = Path.Combine(profileDir, "lockfile");

                if (File.Exists(lockPath))
                {
                    bool isLocked = false;
                    try
                    {
                        using (FileStream fs = new FileStream(lockPath, FileMode.Open, FileAccess.ReadWrite, FileShare.None))
                        {
                            // Stale lock file not locked by any process
                        }
                    }
                    catch
                    {
                        isLocked = true;
                    }

                    if (isLocked)
                    {
                        // Check if any msedge process exists without a main window
                        foreach (Process p in Process.GetProcessesByName("msedge"))
                        {
                            try
                            {
                                if (p.MainWindowHandle == IntPtr.Zero)
                                {
                                    // Could be an orphaned headless process from a previous crash
                                }
                            }
                            catch { }
                        }
                    }
                    else
                    {
                        try { File.Delete(lockPath); } catch { }
                    }
                }
            }
            catch { }
        }

        private static string LocateEdge()
        {
            string[] candidates = new string[]
            {
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFilesX86), @"Microsoft\Edge\Application\msedge.exe"),
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles), @"Microsoft\Edge\Application\msedge.exe"),
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), @"Microsoft\Edge\Application\msedge.exe")
            };

            foreach (string p in candidates)
            {
                if (File.Exists(p)) return p;
            }
            return null;
        }

        private static string LocateChrome()
        {
            string[] candidates = new string[]
            {
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles), @"Google\Chrome\Application\chrome.exe"),
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.ProgramFilesX86), @"Google\Chrome\Application\chrome.exe"),
                Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), @"Google\Chrome\Application\chrome.exe")
            };

            foreach (string p in candidates)
            {
                if (File.Exists(p)) return p;
            }
            return null;
        }
    }
}
