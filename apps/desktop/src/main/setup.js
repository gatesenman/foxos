'use strict';
const { t } = require('./i18n');
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
  const r = planBase();
  // Everything 应用：每个分组一条安装命令（从上游源码在本机构建）
  const py = kernel.pythonPath();
  const q = IS_WIN ? `& "${py}"` : `'${py.replace(/'/g, "'\\''")}'`;
  for (const g of ['office', 'collaboration', 'creative', 'engineering', 'productivity', 'finance', 'business', 'developer', 'games']) r.components[`everything:${g}`] = `${q} -m foxos everything install --group ${g}`;
  return r;
}

function planBase() {
  const py = kernel.pythonPath();
  const quote = (s) => (IS_WIN ? `"${s}"` : `'${s.replace(/'/g, "'\\''")}'`);
  // Windows 的命令在 PowerShell 里执行：带引号的程序路径前要加调用运算符 &
  const exe = (s) => (IS_WIN ? `& ${quote(s)}` : quote(s));
  const pyDeps = `${exe(py)} -m pip install --upgrade "openpyxl>=3.1,<4" "python-docx>=1.1,<2" "python-pptx>=1.0,<2" "zstandard>=0.22"`;
  const fx = `${exe(py)} -m foxos`;
  // 环境组件：Linux 检查用户命名空间并预下载 Alpine 镜像；Windows 启用 WSL2；macOS 编译 Virtualization.framework 辅助程序
  const envLinux = `unshare -U true && ${fx} env pull alpine-3.20`;
  const vz = require('node:path').join(require('./paths').corePath(), 'foxos', 'data', 'macos', 'FoxVZ.swift');
  const envMac = `mkdir -p "$HOME/Library/Application Support/FoxOS/bin" && swiftc -O ${quote(vz)} -framework Virtualization -o "$HOME/Library/Application Support/FoxOS/bin/foxvz"`;
  if (IS_WIN) {
    const wg = (id) => `winget install --id ${id} -e --accept-package-agreements --accept-source-agreements`;
    const path = require('node:path');
    const loPs = path.join(require('./paths').corePath(), 'foxos', 'data', 'windows', 'install-libreoffice.ps1');
    // 安装包自带 Python（embeddable 版 + 办公库）；只有开发模式下才需要单独安装
    const bundled = kernel.bundledPython && kernel.bundledPython();
    const check = t('setup.c_import_foxos_openpyxl_docx_pptx', exe(py));
    return {
      platform: 'windows', packageManager: which('winget') ? 'winget' : null,
      components: {
        libreoffice: `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ${quote(loPs)}`,
        python: bundled ? check : wg('Python.Python.3.12'),
        'python-deps': bundled ? check : pyDeps,
        node: wg('OpenJS.NodeJS.LTS'),
        git: wg('Git.Git'),
        environments: 'wsl --install --no-distribution',
      },
    };
  }
  if (process.platform === 'darwin') {
    return {
      platform: 'macos', packageManager: which('brew') ? 'brew' : null,
      components: {
        libreoffice: 'brew install --cask libreoffice', python: 'brew install python', 'python-deps': pyDeps,
        node: 'brew install node', git: 'brew install git', environments: envMac,
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
      environments: envLinux,
    },
  };
}

module.exports = { plan };
