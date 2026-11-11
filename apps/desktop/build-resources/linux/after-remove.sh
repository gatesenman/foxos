#!/bin/bash

# 升级时（deb: upgrade；rpm: $1 >= 1）不删链接，新版本已经装好
case "${1:-}" in upgrade|failed-upgrade|1|2) exit 0 ;; esac

# Delete the link to the binary
# update-alternatives --remove <name> <path>: 'path' must be the registered alternative binary,
# not the generic symlink — see https://man7.org/linux/man-pages/man1/update-alternatives.1.html
if type update-alternatives >/dev/null 2>&1; then
    update-alternatives --remove '${executable}' '/opt/${sanitizedProductName}/${executable}'
else
    rm -f '/usr/bin/${executable}'
fi

APPARMOR_PROFILE_DEST='/etc/apparmor.d/${executable}'

# Remove and unload apparmor profile.
if [ -f "$APPARMOR_PROFILE_DEST" ]; then
  # Unload the profile from the running kernel before deleting the file so the
  # policy is not left enforced until the next reboot.  Mirror the chroot guard
  # used in the after-install script — live AppArmor operations are not
  # meaningful inside a chroot.
  # https://wiki.debian.org/AppArmor/HowToUse
  if apparmor_status --enabled > /dev/null 2>&1; then
    if ! { [ -x '/usr/bin/ischroot' ] && /usr/bin/ischroot; } && hash apparmor_parser 2>/dev/null; then
      apparmor_parser --remove "$APPARMOR_PROFILE_DEST" || true
    fi
  fi
  rm -f "$APPARMOR_PROFILE_DEST"
fi
# 狐狸OS：命令行 foxos
if [ -L /usr/bin/foxos ] && [ "$(readlink /usr/bin/foxos)" = '/opt/${sanitizedProductName}/resources/bin/foxos' ]; then
  rm -f /usr/bin/foxos
fi

# 卸载后 /opt/${sanitizedProductName} 里只剩运行时生成的缓存（例如以 root 启动桌面时的 __pycache__），一并删掉
rm -rf '/opt/${sanitizedProductName}'
