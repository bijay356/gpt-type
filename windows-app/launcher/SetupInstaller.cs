using System;
using System.ComponentModel;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Reflection;
using System.Threading;
using System.Windows.Forms;
using Microsoft.Win32;

namespace GptTypeInstaller
{
    static class Program
    {
        [STAThread]
        static void Main(string[] args)
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);

            bool isSilent = false;
            foreach (string arg in args)
            {
                if (arg.Equals("/S", StringComparison.OrdinalIgnoreCase) || 
                    arg.Equals("/silent", StringComparison.OrdinalIgnoreCase) ||
                    arg.Equals("-s", StringComparison.OrdinalIgnoreCase))
                {
                    isSilent = true;
                }
            }

            if (isSilent)
            {
                InstallerEngine.InstallSync(true, false);
                return;
            }

            Application.Run(new InstallerForm());
        }
    }

    public static class InstallerEngine
    {
        public static string GetInstallDir()
        {
            string localApp = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
            return Path.Combine(localApp, "Programs", "GPT-TYPE");
        }

        public static void InstallSync(bool createDesktopShortcut, bool launchAfter)
        {
            PerformInstallCore(null, createDesktopShortcut, launchAfter);
        }

        public static void PerformInstallCore(Action<int, string> progress, bool createDesktopShortcut, bool launchAfter)
        {
            try
            {
                if (progress != null) progress(10, "Closing existing instances...");
                KillRunningInstances();

                if (progress != null) progress(20, "Preparing installation directory...");
                string installDir = GetInstallDir();
                if (!Directory.Exists(installDir))
                {
                    Directory.CreateDirectory(installDir);
                }

                // Clean up old legacy files if present
                string oldElectronUninstall = Path.Combine(installDir, "Uninstall-GPT-TYPE.exe");
                if (File.Exists(oldElectronUninstall))
                {
                    try { File.Delete(oldElectronUninstall); } catch { }
                }

                if (progress != null) progress(40, "Extracting application components...");
                Assembly asm = Assembly.GetExecutingAssembly();
                
                string exePath = Path.Combine(installDir, "GPT-TYPE.exe");
                ExtractResource(asm, "GPT-TYPE.exe", exePath);

                string htmlPath = Path.Combine(installDir, "index.html");
                ExtractResource(asm, "index.html", htmlPath);

                string uninstallPath = Path.Combine(installDir, "Uninstall.exe");
                ExtractResource(asm, "Uninstall.exe", uninstallPath);

                string icoPath = Path.Combine(installDir, "favicon.ico");
                ExtractResource(asm, "favicon.ico", icoPath);

                if (progress != null) progress(70, "Configuring Windows shortcuts...");

                // Desktop shortcut
                if (createDesktopShortcut)
                {
                    string desktop = Environment.GetFolderPath(Environment.SpecialFolder.Desktop);
                    
                    // Remove old raw exe from Desktop so it never shows .exe
                    string oldDesktopExe = Path.Combine(desktop, "GPT-TYPE.exe");
                    if (File.Exists(oldDesktopExe))
                    {
                        try { File.Delete(oldDesktopExe); } catch { }
                    }

                    string desktopLnk = Path.Combine(desktop, "GPT-TYPE.lnk");
                    CreateShortcut(desktopLnk, exePath, installDir, "GPT-TYPE - 123+ Languages Typing & Typeshala");
                }

                // Start Menu shortcut
                string programs = Environment.GetFolderPath(Environment.SpecialFolder.Programs);
                string startMenuLnk = Path.Combine(programs, "GPT-TYPE.lnk");
                CreateShortcut(startMenuLnk, exePath, installDir, "GPT-TYPE - 123+ Languages Typing & Typeshala");

                if (progress != null) progress(90, "Registering application in Windows...");
                RegisterUninstall(installDir, exePath, uninstallPath);

                if (progress != null) progress(100, "Installation completed successfully!");

                if (launchAfter)
                {
                    try
                    {
                        Process.Start(exePath);
                    }
                    catch { }
                }
            }
            catch (Exception ex)
            {
                if (progress != null) progress(-1, "Installation Error: " + ex.Message);
                throw;
            }
        }

        private static void KillRunningInstances()
        {
            try
            {
                int currentId = Process.GetCurrentProcess().Id;
                foreach (Process p in Process.GetProcessesByName("GPT-TYPE"))
                {
                    if (p.Id != currentId)
                    {
                        try { p.Kill(); p.WaitForExit(1500); } catch { }
                    }
                }
            }
            catch { }
        }

        private static void ExtractResource(Assembly asm, string resName, string targetPath)
        {
            using (Stream s = asm.GetManifestResourceStream(resName))
            {
                if (s != null)
                {
                    // If target file exists, remove it first to avoid locks or truncated files
                    if (File.Exists(targetPath))
                    {
                        try { File.Delete(targetPath); } catch { }
                    }
                    using (FileStream fs = new FileStream(targetPath, FileMode.Create, FileAccess.Write, FileShare.None))
                    {
                        s.CopyTo(fs);
                    }
                }
            }
        }

        public static void CreateShortcut(string shortcutPath, string targetExe, string workingDir, string desc)
        {
            try
            {
                Type shellType = Type.GetTypeFromProgID("WScript.Shell");
                if (shellType != null)
                {
                    dynamic shell = Activator.CreateInstance(shellType);
                    dynamic sc = shell.CreateShortcut(shortcutPath);
                    sc.TargetPath = targetExe;
                    sc.WorkingDirectory = workingDir;
                    sc.Description = desc;
                    sc.IconLocation = targetExe + ",0";
                    sc.Save();
                }
            }
            catch { }
        }

        private static void RegisterUninstall(string installDir, string exePath, string uninstallPath)
        {
            try
            {
                using (RegistryKey parent = Registry.CurrentUser.OpenSubKey(@"Software\Microsoft\Windows\CurrentVersion\Uninstall", true))
                {
                    if (parent != null)
                    {
                        using (RegistryKey appKey = parent.CreateSubKey("GPT-TYPE"))
                        {
                            if (appKey != null)
                            {
                                appKey.SetValue("DisplayName", "GPT-TYPE");
                                appKey.SetValue("DisplayVersion", "2.0.0");
                                appKey.SetValue("Publisher", "GPT-TYPE");
                                appKey.SetValue("InstallLocation", installDir);
                                appKey.SetValue("DisplayIcon", exePath + ",0");
                                appKey.SetValue("UninstallString", "\"" + uninstallPath + "\"");
                                appKey.SetValue("EstimatedSize", 3600, RegistryValueKind.DWord);
                                appKey.SetValue("NoModify", 1, RegistryValueKind.DWord);
                                appKey.SetValue("NoRepair", 1, RegistryValueKind.DWord);
                            }
                        }
                    }
                }
            }
            catch { }
        }
    }

    public class InstallerForm : Form
    {
        private ProgressBar progressBar;
        private Label lblStatus;
        private Label lblPath;
        private CheckBox chkDesktop;
        private CheckBox chkLaunch;
        private Button btnAction;
        private Button btnCancel;
        private bool isFinished = false;

        public InstallerForm()
        {
            InitializeComponent();
        }

        private void InitializeComponent()
        {
            this.Text = "GPT-TYPE Setup";
            this.Size = new Size(540, 390);
            this.StartPosition = FormStartPosition.CenterScreen;
            this.FormBorderStyle = FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;
            this.BackColor = Color.FromArgb(15, 23, 42); // Slate 900
            this.ForeColor = Color.White;
            this.Font = new Font("Segoe UI", 9F);

            try
            {
                this.Icon = Icon.ExtractAssociatedIcon(Assembly.GetExecutingAssembly().Location);
            }
            catch { }

            // Header
            Panel pnlHeader = new Panel();
            pnlHeader.Dock = DockStyle.Top;
            pnlHeader.Height = 85;
            pnlHeader.BackColor = Color.FromArgb(30, 41, 59);

            PictureBox picLogo = new PictureBox();
            picLogo.Location = new Point(20, 16);
            picLogo.Size = new Size(52, 52);
            picLogo.SizeMode = PictureBoxSizeMode.Zoom;
            try
            {
                if (this.Icon != null) picLogo.Image = this.Icon.ToBitmap();
            }
            catch { }
            pnlHeader.Controls.Add(picLogo);

            Label lblTitle = new Label();
            lblTitle.Text = "GPT-TYPE Setup";
            lblTitle.Font = new Font("Segoe UI", 15F, FontStyle.Bold);
            lblTitle.ForeColor = Color.White;
            lblTitle.Location = new Point(85, 16);
            lblTitle.AutoSize = true;
            pnlHeader.Controls.Add(lblTitle);

            Label lblSub = new Label();
            lblSub.Text = "123+ Languages Typing Speed Test, Typeshala & Ramayan Battle";
            lblSub.Font = new Font("Segoe UI", 9F);
            lblSub.ForeColor = Color.FromArgb(148, 163, 184);
            lblSub.Location = new Point(87, 47);
            lblSub.AutoSize = true;
            pnlHeader.Controls.Add(lblSub);

            this.Controls.Add(pnlHeader);

            // Body
            Label lblWelcome = new Label();
            lblWelcome.Text = "Click Install to set up GPT-TYPE on your computer.";
            lblWelcome.Font = new Font("Segoe UI", 10F, FontStyle.Regular);
            lblWelcome.Location = new Point(30, 105);
            lblWelcome.AutoSize = true;
            this.Controls.Add(lblWelcome);

            lblPath = new Label();
            lblPath.Text = "Destination: " + InstallerEngine.GetInstallDir();
            lblPath.Font = new Font("Segoe UI", 8.5F);
            lblPath.ForeColor = Color.FromArgb(148, 163, 184);
            lblPath.Location = new Point(30, 133);
            lblPath.Size = new Size(470, 20);
            this.Controls.Add(lblPath);

            progressBar = new ProgressBar();
            progressBar.Location = new Point(30, 165);
            progressBar.Size = new Size(465, 22);
            progressBar.Style = ProgressBarStyle.Continuous;
            this.Controls.Add(progressBar);

            lblStatus = new Label();
            lblStatus.Text = "Ready to install";
            lblStatus.ForeColor = Color.FromArgb(56, 189, 248);
            lblStatus.Location = new Point(30, 195);
            lblStatus.Size = new Size(465, 22);
            this.Controls.Add(lblStatus);

            chkDesktop = new CheckBox();
            chkDesktop.Text = "Create Desktop Shortcut (GPT-TYPE)";
            chkDesktop.Checked = true;
            chkDesktop.Location = new Point(30, 230);
            chkDesktop.AutoSize = true;
            this.Controls.Add(chkDesktop);

            chkLaunch = new CheckBox();
            chkLaunch.Text = "Launch GPT-TYPE after installation";
            chkLaunch.Checked = true;
            chkLaunch.Location = new Point(30, 258);
            chkLaunch.AutoSize = true;
            this.Controls.Add(chkLaunch);

            // Bottom Panel
            Panel pnlBottom = new Panel();
            pnlBottom.Dock = DockStyle.Bottom;
            pnlBottom.Height = 58;
            pnlBottom.BackColor = Color.FromArgb(30, 41, 59);

            btnAction = new Button();
            btnAction.Text = "Install";
            btnAction.Font = new Font("Segoe UI", 9.5F, FontStyle.Bold);
            btnAction.Size = new Size(100, 36);
            btnAction.Location = new Point(300, 11);
            btnAction.BackColor = Color.FromArgb(37, 99, 235);
            btnAction.ForeColor = Color.White;
            btnAction.FlatStyle = FlatStyle.Flat;
            btnAction.FlatAppearance.BorderSize = 0;
            btnAction.Click += BtnAction_Click;
            pnlBottom.Controls.Add(btnAction);

            btnCancel = new Button();
            btnCancel.Text = "Cancel";
            btnCancel.Font = new Font("Segoe UI", 9F);
            btnCancel.Size = new Size(85, 36);
            btnCancel.Location = new Point(410, 11);
            btnCancel.BackColor = Color.FromArgb(71, 85, 105);
            btnCancel.ForeColor = Color.White;
            btnCancel.FlatStyle = FlatStyle.Flat;
            btnCancel.FlatAppearance.BorderSize = 0;
            btnCancel.Click += (s, e) => this.Close();
            pnlBottom.Controls.Add(btnCancel);

            this.Controls.Add(pnlBottom);
        }

        private void BtnAction_Click(object sender, EventArgs e)
        {
            if (isFinished)
            {
                if (chkLaunch.Checked)
                {
                    string exe = Path.Combine(InstallerEngine.GetInstallDir(), "GPT-TYPE.exe");
                    try { Process.Start(exe); } catch { }
                }
                this.Close();
                return;
            }

            btnAction.Enabled = false;
            btnCancel.Enabled = false;
            chkDesktop.Enabled = false;
            chkLaunch.Enabled = false;

            Thread worker = new Thread(() =>
            {
                try
                {
                    InstallerEngine.PerformInstallCore(
                        (progress, status) =>
                        {
                            if (this.IsDisposed) return;
                            this.BeginInvoke(new Action(() =>
                            {
                                if (progress >= 0)
                                {
                                    progressBar.Value = Math.Min(100, Math.Max(0, progress));
                                    lblStatus.Text = status;
                                }
                                else
                                {
                                    lblStatus.ForeColor = Color.FromArgb(248, 113, 113);
                                    lblStatus.Text = status;
                                    btnAction.Text = "Close";
                                    btnAction.Enabled = true;
                                    isFinished = true;
                                }
                            }));
                        },
                        chkDesktop.Checked,
                        false
                    );

                    if (this.IsDisposed) return;
                    this.BeginInvoke(new Action(() =>
                    {
                        progressBar.Value = 100;
                        lblStatus.ForeColor = Color.FromArgb(74, 222, 128);
                        lblStatus.Text = "GPT-TYPE has been successfully installed!";
                        btnAction.Text = "Finish";
                        btnAction.BackColor = Color.FromArgb(34, 197, 94);
                        btnAction.Enabled = true;
                        btnCancel.Visible = false;
                        btnAction.Location = new Point(400, 11);
                        isFinished = true;
                    }));
                }
                catch
                {
                    // Already reported via progress callback
                }
            });
            worker.IsBackground = true;
            worker.Start();
        }
    }
}
