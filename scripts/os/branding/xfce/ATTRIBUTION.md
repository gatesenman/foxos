# 狐狸OS 桌面外观的来源与许可

- **壁纸**（`scripts/os/branding/wallpaper.png`，安装后为 `/usr/share/backgrounds/foxos/default.png`）：狐狸OS 项目自制，狐狸标志配暖色光晕。
- **FoxOS 窗口装饰**（`xfwm4` 主题）与面板/开始菜单样式：为本项目编写。
- **GTK 控件样式**：建立在 GTK 自带的 [Adwaita](https://gitlab.gnome.org/GNOME/gtk) 主题之上（LGPL-2.1），通过 `@import` 引用系统副本，不把源码拷进本仓库。
- **图标主题**：优先使用发行版中的 Yaru（Canonical，CC-BY-SA-4.0 / GPL-3），没有 Yaru 时使用 Adwaita。二者均以 Ubuntu / 系统软件包安装，不把源码拷进本仓库。
- **XFCE**（xfce4-session、xfwm4、xfce4-panel、Whisker Menu 等）：以 Ubuntu 软件包安装，许可以各软件包为准（主要为 GPL-2.0 或以上）。
