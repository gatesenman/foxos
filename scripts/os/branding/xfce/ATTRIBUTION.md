# 狐狸OS 桌面外观的来源与许可

- **壁纸**（`scripts/os/branding/wallpaper.png`，安装后为 `/usr/share/backgrounds/foxos/default.png`）：狐狸OS 项目自制，由 `scripts/os/branding/xfce/gen-wallpaper.py` 生成——暖色渐变、柔和山脊、居中的狐狸OS 图标与「狐狸OS」字样。图标是本项目的 `assets/icons/icon-512.png`；字样用 Noto Sans CJK（SIL Open Font License 1.1）。
- **FoxOS 窗口装饰**（`xfwm4` 主题）与面板 / 开始菜单样式：为本项目编写。
- **GTK 控件样式**：建立在 GTK 自带的 [Adwaita](https://gitlab.gnome.org/GNOME/gtk) 主题之上（LGPL-2.1），通过 `@import` 引用系统副本，不把源码拷进本仓库。
- **图标主题**：[Papirus](https://github.com/PapirusDevelopmentTeam/papirus-icon-theme)（GPL-3.0），以 Ubuntu 软件包 `papirus-icon-theme` 安装；开始菜单分类、应用、面板状态图标都来自它。没有 Papirus 时依次退回 Yaru（CC-BY-SA-4.0 / GPL-3）和 Adwaita。均不把源码拷进本仓库。各应用自己的图标（Firefox、终端、Thunar 等）仍是应用本身提供的。
- **字体**：界面 Noto Sans CJK SC，终端 Noto Sans Mono CJK SC（`fonts-noto-cjk`，SIL OFL 1.1）。
- **终端配色**：狐狸OS 暖色深色配色，为本项目编写（`xfconf/xfce4-terminal.xml`）。
- **XFCE**（xfce4-session、xfwm4、xfce4-panel、Whisker Menu、genmon 等）：以 Ubuntu 软件包安装，许可以各软件包为准（主要为 GPL-2.0 或以上）。
