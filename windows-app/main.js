const { app, BrowserWindow, Menu, globalShortcut } = require('electron');
const path = require('path');

let mainWindow = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1320,
    height: 860,
    minWidth: 980,
    minHeight: 650,
    title: 'GPT-TYPE 123+ Languages Speed Test, Typeshala & Ramayan Archery Battle',
    icon: path.join(__dirname, 'favicon.ico'),
    backgroundColor: '#090d16',
    autoHideMenuBar: false,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      webSecurity: true
    }
  });

  // Load the standalone, 100% offline index.html
  const indexPath = path.join(__dirname, 'index.html');
  mainWindow.loadFile(indexPath);

  // Native Menu
  const menuTemplate = [
    {
      label: 'File',
      submenu: [
        {
          label: 'Restart / Reset Game',
          accelerator: 'CmdOrCtrl+R',
          click: () => { mainWindow.reload(); }
        },
        { type: 'separator' },
        {
          label: 'Exit',
          accelerator: 'CmdOrCtrl+Q',
          click: () => { app.quit(); }
        }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { type: 'separator' },
        { role: 'togglefullscreen' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' }
      ]
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'About GPT-TYPE Desktop',
          click: async () => {
            const { dialog } = require('electron');
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'About GPT-TYPE Desktop',
              message: 'GPT-TYPE Desktop v2.0\n\n123+ Languages Typing Platform\nAuthentic Nepali Typeshala (Preeti & Unicode)\nRamayan Archery Typing Battle Game\n100% Offline Client-Side Engine.',
              buttons: ['OK']
            });
          }
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(menuTemplate);
  Menu.setApplicationMenu(menu);

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
