'use strict';
// 执行策略：Windows（以及 macOS / 普通 Linux）上的桌面程序是“狐狸OS 电脑”的客户端——
// 智能体和桌面上的一切动作（应用中心安装、打开 Word、终端、文件操作、Everything 应用、电脑操作）都在狐狸OS 虚拟机 / 远程狐狸OS 里执行，
// 不碰用户自己的电脑。只有两种情况在本机执行：
//   native  本机就是狐狸OS（/etc/os-release 的 ID=foxos），或开发 / 测试时显式设置 FOXOS_HOST_EXECUTION=1
//   host    用户在设置里打开了“允许在本机执行”，且每一次动作都在原生对话框里确认
// 纯函数部分（mode / classify）不依赖 Electron，单元测试直接 require。
const fs = require('node:fs');

// 这些 foxos 命令管理的是本机上的虚拟机 / 配对登记本身（创建、启动、连接狐狸OS 电脑），不是在“操作电脑”
const LIFECYCLE_APPS = new Set(['env', 'machine', 'help', 'version']);

function isFoxosOs(osRelease = '/etc/os-release') {
  try { return /^ID=("?)foxos\1$/m.test(fs.readFileSync(osRelease, 'utf8')); } catch { return false; }
}

// env: process.env；packaged: app.isPackaged
function mode({ env = process.env, packaged = true, osRelease } = {}) {
  if (env.FOXOS_CLIENT_MODE === '1') return 'client';
  if (env.FOXOS_HOST_EXECUTION === '1') return 'native';
  if (process.platform === 'linux' && isFoxosOs(osRelease)) return 'native';
  if (!packaged) return 'native';          // 开发模式（npm start）沿用原来的本机行为
  return 'client';
}

// 一条 foxos 命令在客户端模式下去哪儿执行：'local'（虚拟机生命周期、配对）或 'guest'
function routeKernel(args) {
  return LIFECYCLE_APPS.has(String((args || [])[0] || '')) ? 'local' : 'guest';
}

module.exports = { mode, routeKernel, isFoxosOs, LIFECYCLE_APPS };
