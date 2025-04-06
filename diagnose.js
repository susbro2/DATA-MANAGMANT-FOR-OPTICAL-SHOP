// Simple diagnostic script
const fs = require('fs');
const path = require('path');

console.log('=== SHIVAM OPTICAL APP DIAGNOSTICS ===');
console.log('Node.js version:', process.version);
console.log('Operating system:', process.platform, process.arch);
console.log('Current directory:', process.cwd());

// Check if critical files exist
const requiredFiles = [
    'package.json',
    'electron.js',
    'server.js',
    'index.html',
    'script.js',
    'styles.css',
    'icon.svg'
];

console.log('\nChecking required files:');
let missingFiles = false;
requiredFiles.forEach(file => {
    const exists = fs.existsSync(path.join(process.cwd(), file));
    console.log(`${file}: ${exists ? 'Found ✓' : 'MISSING ✗'}`);
    if (!exists) missingFiles = true;
});

// Check package.json
try {
    const packageJson = require('./package.json');
    console.log('\nPackage information:');
    console.log('Name:', packageJson.name);
    console.log('Main:', packageJson.main);
    console.log('Dependencies:', Object.keys(packageJson.dependencies).length);
    console.log('DevDependencies:', Object.keys(packageJson.devDependencies).length);
    
    // Check if key dependencies are installed
    console.log('\nChecking node_modules:');
    const nodeModulesExists = fs.existsSync(path.join(process.cwd(), 'node_modules'));
    console.log(`node_modules directory: ${nodeModulesExists ? 'Found ✓' : 'MISSING ✗'}`);
    
    if (nodeModulesExists) {
        const criticalDeps = ['electron', 'express', 'sqlite3'];
        criticalDeps.forEach(dep => {
            const depExists = fs.existsSync(path.join(process.cwd(), 'node_modules', dep));
            console.log(`${dep}: ${depExists ? 'Installed ✓' : 'NOT INSTALLED ✗'}`);
        });
    }
} catch (e) {
    console.log('\nError reading package.json:', e.message);
}

console.log('\n=== END OF DIAGNOSTICS ===');
console.log('Run this report to identify issues with your setup.'); 