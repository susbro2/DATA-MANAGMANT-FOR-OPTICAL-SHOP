const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

console.log('Converting icon to Windows ICO format...');

// Check if svg-to-ico module is installed
exec('npm list svg-to-ico -g', (error, stdout) => {
  if (stdout.includes('empty')) {
    console.log('Installing svg-to-ico module...');
    exec('npm install -g svg-to-ico', (err) => {
      if (err) {
        console.error('Error installing svg-to-ico:', err);
        return;
      }
      convertIcon();
    });
  } else {
    convertIcon();
  }
});

function convertIcon() {
  exec('svg-to-ico icon.svg -o icon.ico', (error) => {
    if (error) {
      console.error('Error converting icon:', error);
      console.log('Alternative method: Please use an online converter to convert icon.svg to icon.ico');
      return;
    }
    console.log('Icon converted successfully to icon.ico');
  });
} 