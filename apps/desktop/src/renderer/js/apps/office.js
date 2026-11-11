// LibreOffice Writer / Calc / Impress：以真实的原生窗口启动，任务栏跟踪（未嵌入桌面窗口）
'use strict';
(() => {
  const NAMES = { writer: 'LibreOffice Writer', calc: 'LibreOffice Calc', impress: 'LibreOffice Impress' };

  FX.launchOffice = async (app, rel = null) => {
    const info = FX.apps && FX.apps.office.find((o) => o.id === app);
    if (info && !info.installed) {
      const go = await FX.confirm(FX.t('office.is_not_installed', NAMES[app]), FX.t('office.open_the_setup_wizard_now', info.hint || ''), { okText: FX.t('common.open_setup_wizard') });
      if (go) FX.openWindow('setup', {});
      return null;
    }
    try {
      const rec = await window.foxos.office.launch(app, rel);
      FX.toast(FX.t('office.starting_native_window', NAMES[app], rel ? FX.t('office.file_suffix', FX.basename(rel)) : ''));
      if (FX.env.mode === 'client') FX.openWindow('computer', {});
      FX.refreshNative();
      setTimeout(FX.refreshNative, 2500);
      setTimeout(FX.refreshNative, 6000);
      return rec;
    } catch (e) { FX.toast(e.message, 'error'); return null; }
  };

  FX.refreshNative = async () => {
    try {
      const r = await window.foxos.office.list();
      FX.nativeWindows = r.windows;
      FX.officeProcesses = r.processes;
      FX.renderTaskbar();
    } catch { /* 忽略 */ }
  };
  window.foxos.office.onChanged(() => FX.refreshNative());
  setInterval(FX.refreshNative, 4000);
})();
