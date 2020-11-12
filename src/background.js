'use strict'

import { app, protocol, BrowserWindow } from 'electron'
import { createProtocol } from 'vue-cli-plugin-electron-builder/lib'
import installExtension, { VUEJS_DEVTOOLS } from 'electron-devtools-installer'

const { ipcMain } = require('electron')

const path = require("path");
const isDevelopment = process.env.NODE_ENV !== 'production'
const PY_DIST_FOLDER = "../dist"
const PY_MODULE = "main"
let subpy = null;
var loadingwindow = null

// Get command options
var port = (app.commandLine.getSwitchValue("port") || "5000")
var onion_port = (app.commandLine.getSwitchValue("onion_port") || "80")
var onion_control_port = (app.commandLine.getSwitchValue("onion_control_port") || "9051")
var onion_socks_port = (app.commandLine.getSwitchValue("onion_socks_port") || "9050")
var tor_browser = (app.commandLine.hasSwitch('tor_browser'))

if (tor_browser) {
  onion_control_port = "9151"
  onion_socks_port = "9150"
}

var folder = (app.commandLine.getSwitchValue("folder") || "~/calsotchat")

// Scheme must be registered before the app is ready
protocol.registerSchemesAsPrivileged([
  { scheme: 'app', privileges: { secure: true, standard: true } }
])

const getPythonScriptPath = () => {
  if (process.platform === "win32") {
    return path.join(
      __dirname,
      PY_DIST_FOLDER,
      PY_MODULE + ".exe"
    );
  }
  return path.join(__dirname, PY_DIST_FOLDER, PY_MODULE);
};

const startPythonSubprocess = () => {
  let script = getPythonScriptPath();
  subpy = require("child_process").execFile(script, [
    "--port", port, 
    "--onion-port", onion_port, 
    "--folder", folder,
    "--onion_control_port", onion_control_port,
    "--onion_socks_port", onion_socks_port
  ]);
};

async function createWindow() {
  var default_width = 800;
  if (isDevelopment && !process.env.IS_TEST) {
    default_width = 1200
  }
  // Create the browser window.
  loadingwindow.hide()
  const win = new BrowserWindow({
    width: default_width,
    height: 600,
    'minHeight': 600,
    'minWidth': 750,
    icon: path.join(__static, 'icon.png'),
    webPreferences: {
      // Use pluginOptions.nodeIntegration, leave this alone
      // See nklayman.github.io/vue-cli-plugin-electron-builder/guide/security.html#node-integration for more info
      nodeIntegration: process.env.ELECTRON_NODE_INTEGRATION
    }
  })
  
  if (process.env.WEBPACK_DEV_SERVER_URL) {
    // Load the url of the dev server if in development mode
    await win.loadURL(process.env.WEBPACK_DEV_SERVER_URL)
    if (!process.env.IS_TEST) win.webContents.openDevTools()
  } else {
    // win.webContents.openDevTools()
    createProtocol('app')
    // Load the index.html when not in development
    win.loadURL('app://./index.html')
  }
  loadingwindow.close()
}

// Quit when all windows are closed.
app.on('window-all-closed', () => {
  // On macOS it is common for applications and their menu bar
  // to stay active until the user quits explicitly with Cmd + Q
  if (process.platform !== 'darwin') {
    app.quit();
  }
})

app.on('quit', async () => {
  subpy.kill('SIGINT')
  subpy = null
})

app.on('activate', () => {
  // On macOS it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (BrowserWindow.getAllWindows().length === 0) createWindow()
})

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.on('ready', async () => {
  loadingwindow = new BrowserWindow({
    frame : false,
    width: 175,
    height: 175,
    movable : false,
    icon: path.join(__static, 'icon.png')
  })
  if (process.env.WEBPACK_DEV_SERVER_URL) {
    // Load the url of the dev server if in development mode
    await loadingwindow.loadURL(process.env.WEBPACK_DEV_SERVER_URL+"/loading.html")
  } else {
    createProtocol('app')
    // Load the index.html when not in development
    loadingwindow.loadURL('app://./loading.html')
  }

  if (isDevelopment && !process.env.IS_TEST) {
    // Install Vue Devtools
    try {
      await installExtension(VUEJS_DEVTOOLS)
    } catch (e) {
      console.error('Vue Devtools failed to install:', e.toString())
    }
  }

  if(isDevelopment){
    createWindow()
  }else{
    startPythonSubprocess()
    setTimeout(() => {  createWindow() }, 3000); // wait until python process starts (TODO: make loading more precise)
  }
})

// Exit cleanly on request from parent process in development mode.
if (isDevelopment) {
  if (process.platform === 'win32') {
    process.on('message', (data) => {
      if (data === 'graceful-exit') {
        app.quit()
      }
    })
  } else {
    process.on('SIGTERM', () => {
      app.quit()
    })
  }
}

ipcMain.on('get-api-url', (event) => {
  const result = "http://localhost:" + port + "/api"
  event.returnValue = result
})
