const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

// Enable Electron app to be started from any directory
if (process.env.ELECTRON_RUN_AS_NODE !== '1') {
  // We need to change the current working directory to the app directory
  process.chdir(path.dirname(app.getAppPath()));
}

let mainWindow;
let serverProcess;
const PORT = 3000;
let serverRunning = false;
let serverStartAttempts = 0;
const MAX_SERVER_START_ATTEMPTS = 5;

function createWindow() {
  console.log('Creating browser window...');
  
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true
    },
    icon: path.join(__dirname, 'icon.ico')
  });

  // Wait for server to start before loading the app
  const loadApp = () => {
    console.log('Loading app URL...');
    mainWindow.loadURL(`http://localhost:${PORT}`);
  };

  // Start the server
  startServer();

  // Poll for server availability
  const serverCheckInterval = setInterval(() => {
    if (serverRunning) {
      loadApp();
      clearInterval(serverCheckInterval);
    } else if (serverStartAttempts >= MAX_SERVER_START_ATTEMPTS) {
      clearInterval(serverCheckInterval);
      const errorMessage = 'Failed to start the server after multiple attempts. Please try again.';
      console.error(errorMessage);
      showErrorAndExit(errorMessage);
    }
    serverStartAttempts++;
  }, 1000);

  // Handle window close
  mainWindow.on('closed', () => {
    mainWindow = null;
    // Kill the server process when the window is closed
    if (serverProcess) {
      try {
        const isWindows = process.platform === 'win32';
        if (isWindows) {
          spawn('taskkill', ['/pid', serverProcess.pid, '/f', '/t']);
        } else {
          serverProcess.kill('SIGINT');
        }
      } catch(e) {
        console.error('Error stopping server:', e);
      }
      serverProcess = null;
    }
  });
}

function startServer() {
  console.log('Starting server...');
  
  // Check if server.js exists
  if (!fs.existsSync(path.join(__dirname, 'server.js'))) {
    console.error('ERROR: server.js file not found!');
    return;
  }
  
  // Execute the server.js file using Node
  try {
    serverProcess = spawn(process.execPath, [path.join(__dirname, 'server.js')]);
    
    // Log server output
    serverProcess.stdout.on('data', (data) => {
      console.log(`Server: ${data}`);
      if (data.toString().includes('Server running on port')) {
        console.log('Server is running!');
        serverRunning = true;
      }
    });
    
    serverProcess.stderr.on('data', (data) => {
      console.error(`Server error: ${data}`);
    });
    
    serverProcess.on('close', (code) => {
      console.log(`Server process exited with code ${code}`);
      serverRunning = false;
    });
  } catch (error) {
    console.error('Error starting server:', error);
  }
}

function showErrorAndExit(message) {
  const { dialog } = require('electron');
  dialog.showErrorBox('Shivam Opticals Error', message);
  app.exit(1);
}

// Create window when Electron is ready
app.whenReady().then(() => {
  console.log('Electron app is ready');
  createWindow();
  
  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

// Quit app when all windows are closed (except on macOS)
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// On macOS, recreate window when dock icon is clicked
app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
}); 