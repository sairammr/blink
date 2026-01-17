const { spawnSync } = require('child_process');
const path = require('path');

const isWin = process.platform === 'win32';
const scriptPath = path.join(__dirname, isWin ? 'build_py.ps1' : 'build_py.sh');

if (isWin) {
  const ps = spawnSync('powershell', ['-ExecutionPolicy', 'Bypass', '-File', scriptPath], { stdio: 'inherit' });
  process.exit(ps.status);
} else {
  const sh = spawnSync('bash', [scriptPath], { stdio: 'inherit' });
  process.exit(sh.status);
}
