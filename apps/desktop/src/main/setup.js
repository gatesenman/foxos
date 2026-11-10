'use strict';
// 在线安装向导：按平台给出真实的安装命令（在桌面的真实终端里执行，用户可见进度、可输入 sudo 密码）
const { IS_WIN, which } = require('./paths');
const kernel = require('./kernel');

function linuxPkg(pkgs) {
  const sudo = process.getuid && process.getuid() === 0 ? '' : 'sudo ';
  if (which('apt-get')) return `${sudo}apt-get update && ${sudo}apt-get install -y ${pkgs.apt}`;
  if (which('dnf')) return `${sudo}dnf install -y ${pkgs.dnf}`;
  if (which('pacman')) return `${sudo}pacman -S --noconfirm ${pkgs.pacman}`;
  if (which('zypper')) return `${sudo}zypper install -y ${pkgs.zypper}`;
  return null;
}

function plan() {
  const py = kernel.pythonPath();
  const quote = (s) => (IS_WIN ? `"${s}"` : `'${s.replace(/'/g, "'\\''")}'`);
  const pyDeps = `${quote(py)} -m pip install --upgrade "openpyxl>=3.1,<4" "python-docx>=1.1,<2" "python-pptx>=1.0,<2"`;
  if (IS_WIN) {
    const wg = (id) => `winget install --id ${id} -e --accept-package-agreements --accept-source-agreements`;
    return {
      platform: 'windows', packageManager: which('winget') ? 'winget' : null,
      components: {
        libreoffice: wg('TheDocumentFoundation.LibreOffice'),
        python: wg('Python.Python.3.12'),
        'python-deps': pyDeps,
        node: wg('OpenJS.NodeJS.LTS'),
        git: wg('Git.Git'),
      },
    };
  }
  if (process.platform === 'darwin') {
    return {
      platform: 'macos', packageManager: which('brew') ? 'brew' : null,
      components: {
        libreoffice: 'brew install --cask libreoffice', python: 'brew install python', 'python-deps': pyDeps,
        node: 'brew install node', git: 'brew install git',
      },
    };
  }
  const pm = ['apt-get', 'dnf', 'pacman', 'zypper'].find((p) => which(p)) || null;
  return {
    platform: 'linux', packageManager: pm,
    components: {
      libreoffice: linuxPkg({ apt: 'libreoffice-writer libreoffice-calc libreoffice-impress', dnf: 'libreoffice-writer libreoffice-calc libreoffice-impress', pacman: 'libreoffice-fresh', zypper: 'libreoffice-writer libreoffice-calc libreoffice-impress' }),
      python: linuxPkg({ apt: 'python3 python3-venv python3-pip', dnf: 'python3 python3-pip', pacman: 'python python-pip', zypper: 'python3 python3-pip' }),
      'python-deps': pyDeps,
      node: linuxPkg({ apt: 'nodejs npm', dnf: 'nodejs npm', pacman: 'nodejs npm', zypper: 'nodejs npm' }),
      git: linuxPkg({ apt: 'git', dnf: 'git', pacman: 'git', zypper: 'git' }),
      wmctrl: linuxPkg({ apt: 'wmctrl', dnf: 'wmctrl', pacman: 'wmctrl', zypper: 'wmctrl' }),
    },
  };
}

module.exports = { plan };
