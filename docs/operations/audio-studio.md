# Audio Studio（audio-studio）操作清单

分组：creative · 替代 Adobe Audition, Sound Forge · 许可证 MIT (root LICENSE) · 页面标题「Audio Studio」

共 148 个操作，全部有语义命令（`foxos audio-studio <资源> <动词>`，MCP 工具 `audio-studio.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `account.select` | `foxos audio-studio account select` | 主界面 > account: * | `target`（必填） | 点击名称匹配的「account: *」项（button） | 不适用（只读） |
| `waveform.select` | `foxos audio-studio waveform select` | 主界面 > Editor > waveform (#) | `target`（必填） | 点击名称匹配的「waveform (#)」项（radio） | 不适用（只读） |
| `multitrack.select` | `foxos audio-studio multitrack select` | 主界面 > Editor > multitrack (#) | `target`（必填） | 点击名称匹配的「multitrack (#)」项（radio） | 不适用（只读） |
| `selection-tool-e.select` | `foxos audio-studio selection-tool-e select` | 主界面 > # selection tool (e) | `target`（必填） | 点击名称匹配的「# selection tool (e)」项（button） | 不适用（只读） |
| `file.activate` | `foxos audio-studio file activate` | 主界面 > Application menu > File | — | 点击「File」（menuitem） | 否（应用没有撤销入口） |
| `edit.update` | `foxos audio-studio edit update` | 主界面 > Application menu > Edit | — | 点击「Edit」（menuitem） | 否（应用没有撤销入口） |
| `multitrack.activate` | `foxos audio-studio multitrack activate` | 主界面 > Application menu > Multitrack | — | 点击「Multitrack」（menuitem） | 否（应用没有撤销入口） |
| `clip.activate` | `foxos audio-studio clip activate` | 主界面 > Application menu > Clip | — | 点击「Clip」（menuitem） | 否（应用没有撤销入口） |
| `effects.activate` | `foxos audio-studio effects activate` | 主界面 > Application menu > Effects | — | 点击「Effects」（menuitem） | 否（应用没有撤销入口） |
| `favorites.activate` | `foxos audio-studio favorites activate` | 主界面 > Application menu > Favorites | — | 点击「Favorites」（menuitem） | 否（应用没有撤销入口） |
| `view.show` | `foxos audio-studio view show` | 主界面 > Application menu > View | — | 点击「View」（menuitem），切换到该视图 | 不适用（只读） |
| `window.activate` | `foxos audio-studio window activate` | 主界面 > Application menu > Window | — | 点击「Window」（menuitem） | 否（应用没有撤销入口） |
| `help.show` | `foxos audio-studio help show` | 主界面 > Application menu > Help | — | 点击「Help」（menuitem），切换到该视图 | 不适用（只读） |
| `spectral-frequency-display-shiftd.show` | `foxos audio-studio spectral-frequency-display-shiftd show` | 主界面 > Show Spectral Frequency Display (Shift+D) | — | 点击「Show Spectral Frequency Display (Shift+D)」（button），切换到该视图 | 不适用（只读） |
| `spectral-pitch-display.show` | `foxos audio-studio spectral-pitch-display show` | 主界面 > Show Spectral Pitch Display | — | 点击「Show Spectral Pitch Display」（button），切换到该视图 | 不适用（只读） |
| `tool-v.move` | `foxos audio-studio tool-v move` | 主界面 > Move Tool (V) | — | 点击「Move Tool (V)」（button） | 否（应用没有撤销入口） |
| `razor-tool-r.activate` | `foxos audio-studio razor-tool-r activate` | 主界面 > Razor Tool (R) | — | 点击「Razor Tool (R)」（button） | 否（应用没有撤销入口） |
| `slip-tool-y.activate` | `foxos audio-studio slip-tool-y activate` | 主界面 > Slip Tool (Y) | — | 点击「Slip Tool (Y)」（button） | 否（应用没有撤销入口） |
| `time-selection-tool-t.activate` | `foxos audio-studio time-selection-tool-t activate` | 主界面 > Time Selection Tool (T) | — | 点击「Time Selection Tool (T)」（button） | 否（应用没有撤销入口） |
| `lasso-selection-tool-d.activate` | `foxos audio-studio lasso-selection-tool-d activate` | 主界面 > Lasso Selection Tool (D) | — | 点击「Lasso Selection Tool (D)」（button） | 否（应用没有撤销入口） |
| `paintbrush-selection-tool-p.activate` | `foxos audio-studio paintbrush-selection-tool-p activate` | 主界面 > Paintbrush Selection Tool (P) | — | 点击「Paintbrush Selection Tool (P)」（button） | 否（应用没有撤销入口） |
| `spot-healing-brush-tool-b.activate` | `foxos audio-studio spot-healing-brush-tool-b activate` | 主界面 > Spot Healing Brush Tool (B) | — | 点击「Spot Healing Brush Tool (B)」（button） | 否（应用没有撤销入口） |
| `workspaces.activate` | `foxos audio-studio workspaces activate` | 主界面 > All workspaces | — | 点击「All workspaces」（button） | 否（应用没有撤销入口） |
| `search-commands.set` | `foxos audio-studio search-commands set` | 主界面 > Search commands | `value`（必填）, `submit` | 把「Search commands」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `files.show` | `foxos audio-studio files show` | 主界面 > Panels > Files | — | 点击「Files」（tab），切换到该视图 | 不适用（只读） |
| `files-panel-menu.activate` | `foxos audio-studio files-panel-menu activate` | 主界面 > Files panel menu | — | 点击「Files panel menu」（button） | 否（应用没有撤销入口） |
| `favorites.show` | `foxos audio-studio favorites show` | 主界面 > Panels > Favorites | — | 点击「Favorites」（tab），切换到该视图 | 不适用（只读） |
| `open.open` | `foxos audio-studio open open` | 主界面 > Open | — | 点击「Open」（button） | 不适用（只读） |
| `import.import` | `foxos audio-studio import import` | 主界面 > Import | — | 点击「Import」（button） | 否（应用没有撤销入口） |
| `audio-file.create` | `foxos audio-studio audio-file create` | 主界面 > New Audio File | — | 点击「New Audio File」（button） | 否（应用没有撤销入口） |
| `into-multitrack.create` | `foxos audio-studio into-multitrack create` | 主界面 > Insert into Multitrack | — | 点击「Insert into Multitrack」（button） | 否（应用没有撤销入口） |
| `close.close` | `foxos audio-studio close close` | 主界面 > Close | — | 点击「Close」（button） | 不适用（只读） |
| `search-files.set` | `foxos audio-studio search-files set` | 主界面 > Search files | `value`（必填）, `submit` | 把「Search files」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `name.activate` | `foxos audio-studio name activate` | 主界面 > Open files > Name | — | 点击「Name」（button） | 否（应用没有撤销入口） |
| `status.activate` | `foxos audio-studio status activate` | 主界面 > Open files > Status | — | 点击「Status」（button） | 否（应用没有撤销入口） |
| `duration.activate` | `foxos audio-studio duration activate` | 主界面 > Open files > Duration | — | 点击「Duration」（button） | 否（应用没有撤销入口） |
| `sample-rate.activate` | `foxos audio-studio sample-rate activate` | 主界面 > Open files > Sample Rate | — | 点击「Sample Rate」（button） | 否（应用没有撤销入口） |
| `channels.activate` | `foxos audio-studio channels activate` | 主界面 > Open files > Channels | — | 点击「Channels」（button） | 否（应用没有撤销入口） |
| `bit-depth.activate` | `foxos audio-studio bit-depth activate` | 主界面 > Open files > Bit Depth | — | 点击「Bit Depth」（button） | 否（应用没有撤销入口） |
| `format.activate` | `foxos audio-studio format activate` | 主界面 > Open files > Format | — | 点击「Format」（button） | 否（应用没有撤销入口） |
| `from-start.play` | `foxos audio-studio from-start play` | 主界面 > Play from Start | — | 点击「Play from Start」（button） | 否（应用没有撤销入口） |
| `loop-playback.activate` | `foxos audio-studio loop-playback activate` | 主界面 > Loop Playback | — | 点击「Loop Playback」（button） | 否（应用没有撤销入口） |
| `auto-play.toggle` | `foxos audio-studio auto-play toggle` | 主界面 > Files panel group > Auto-play | — | 切换「Auto-play」 | 否（应用没有撤销入口） |
| `panels.resize` | `foxos audio-studio panels resize` | 主界面 > Resize panels | — | 点击「Resize panels」（separator） | 否（应用没有撤销入口） |
| `media-browser.show` | `foxos audio-studio media-browser show` | 主界面 > Panels > Media Browser | — | 点击「Media Browser」（tab），切换到该视图 | 不适用（只读） |
| `media-browser-panel-menu.activate` | `foxos audio-studio media-browser-panel-menu activate` | 主界面 > Media Browser panel menu | — | 点击「Media Browser panel menu」（button） | 否（应用没有撤销入口） |
| `effects-rack.show` | `foxos audio-studio effects-rack show` | 主界面 > Panels > Effects Rack | — | 点击「Effects Rack」（tab），切换到该视图 | 不适用（只读） |
| `markers.show` | `foxos audio-studio markers show` | 主界面 > Panels > Markers | — | 点击「Markers」（tab），切换到该视图 | 不适用（只读） |
| `properties.show` | `foxos audio-studio properties show` | 主界面 > Panels > Properties | — | 点击「Properties」（tab），切换到该视图 | 不适用（只读） |
| `panels-group.activate` | `foxos audio-studio panels-group activate` | 主界面 > All panels in this group | — | 点击「All panels in this group」（button） | 否（应用没有撤销入口） |
| `up-one-level.activate` | `foxos audio-studio up-one-level activate` | 主界面 > Up One Level | — | 点击「Up One Level」（button） | 否（应用没有撤销入口） |
| `refresh.activate` | `foxos audio-studio refresh activate` | 主界面 > Refresh | — | 点击「Refresh」（button） | 否（应用没有撤销入口） |
| `folder-from-device.create` | `foxos audio-studio folder-from-device create` | 主界面 > Add a Folder from This Device | — | 点击「Add a Folder from This Device」（button） | 否（应用没有撤销入口） |
| `home.activate` | `foxos audio-studio home activate` | 主界面 > Folder path > Home | — | 点击「Home」（button） | 否（应用没有撤销入口） |
| `search-folder.set` | `foxos audio-studio search-folder set` | 主界面 > Search this folder | `value`（必填）, `submit` | 把「Search this folder」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `only-audio-files.show` | `foxos audio-studio only-audio-files show` | 主界面 > Show only audio files | — | 点击「Show only audio files」（button），切换到该视图 | 不适用（只读） |
| `homeappdata.activate` | `foxos audio-studio homeappdata activate` | 主界面 > Folders > HomeAppData | — | 点击「HomeAppData」（treeitem） | 否（应用没有撤销入口） |
| `appdata.activate` | `foxos audio-studio appdata activate` | 主界面 > Folders > AppData | — | 点击「AppData」（treeitem） | 否（应用没有撤销入口） |
| `folder.create` | `foxos audio-studio folder create` | 主界面 > Folders > Add Folder... | — | 点击「Add Folder...」（treeitem） | 否（应用没有撤销入口） |
| `appdatafolder.activate` | `foxos audio-studio appdatafolder activate` | 主界面 > Files > AppDataFolder | — | 点击「AppDataFolder」（generic） | 否（应用没有撤销入口） |
| `preview.play` | `foxos audio-studio preview play` | 主界面 > Play Preview | — | 点击「Play Preview」（button） | 否（应用没有撤销入口） |
| `preview.stop` | `foxos audio-studio preview stop` | 主界面 > Stop Preview | — | 点击「Stop Preview」（button） | 否（应用没有撤销入口） |
| `loop-preview.activate` | `foxos audio-studio loop-preview activate` | 主界面 > Loop Preview | — | 点击「Loop Preview」（button） | 否（应用没有撤销入口） |
| `preview-position.set` | `foxos audio-studio preview-position set` | 主界面 > Preview position | `value`（必填）, `submit` | 把「Preview position」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `auto-play-2.toggle` | `foxos audio-studio auto-play-2 toggle` | 主界面 > Media Browser panel group > Auto-play | — | 切换「Auto-play」 | 否（应用没有撤销入口） |
| `open-2.open` | `foxos audio-studio open-2 open` | 主界面 > Media Browser panel group > Open | — | 点击「Open」（button） | 不适用（只读） |
| `into-multitrack-2.create` | `foxos audio-studio into-multitrack-2 create` | 主界面 > Media Browser panel group > Insert into Multitrack | — | 点击「Insert into Multitrack」（button） | 否（应用没有撤销入口） |
| `history.show` | `foxos audio-studio history show` | 主界面 > Panels > History | — | 点击「History」（tab），切换到该视图 | 不适用（只读） |
| `history-panel-menu.activate` | `foxos audio-studio history-panel-menu activate` | 主界面 > History panel menu | — | 点击「History panel menu」（button） | 否（应用没有撤销入口） |
| `video.show` | `foxos audio-studio video show` | 主界面 > Panels > Video | — | 点击「Video」（tab），切换到该视图 | 不适用（只读） |
| `history.clear` | `foxos audio-studio history clear` | 主界面 > Clear history | — | 点击「Clear history」（button） | 否（应用没有撤销入口） |
| `editor.show` | `foxos audio-studio editor show` | 主界面 > Panels > Editor | — | 点击「Editor」（tab），切换到该视图 | 不适用（只读） |
| `editor-panel-menu.activate` | `foxos audio-studio editor-panel-menu activate` | 主界面 > Editor panel menu | — | 点击「Editor panel menu」（button） | 否（应用没有撤销入口） |
| `mixer.show` | `foxos audio-studio mixer show` | 主界面 > Panels > Mixer | — | 点击「Mixer」（tab），切换到该视图 | 不适用（只读） |
| `open-3.open` | `foxos audio-studio open-3 open` | 主界面 > Editor panel group > Open | — | 点击「Open」（button） | 不适用（只读） |
| `audio-file-2.create` | `foxos audio-studio audio-file-2 create` | 主界面 > Editor panel group > New Audio File | — | 点击「New Audio File」（button） | 否（应用没有撤销入口） |
| `multitrack-session.create` | `foxos audio-studio multitrack-session create` | 主界面 > Editor panel group > New Multitrack Session | — | 点击「New Multitrack Session」（button） | 否（应用没有撤销入口） |
| `record.record` | `foxos audio-studio record record` | 主界面 > Editor panel group > Record | — | 点击「Record」（button） | 否（应用没有撤销入口） |
| `playhead-time.activate` | `foxos audio-studio playhead-time activate` | 主界面 > Playhead time | — | 点击「Playhead time」（button） | 否（应用没有撤销入口） |
| `stop.stop` | `foxos audio-studio stop stop` | 主界面 > Stop | — | 点击「Stop」（button） | 否（应用没有撤销入口） |
| `space.play` | `foxos audio-studio space play` | 主界面 > Play (Space) | — | 点击「Play (Space)」（button） | 否（应用没有撤销入口） |
| `pause.pause` | `foxos audio-studio pause pause` | 主界面 > Pause | — | 点击「Pause」（button） | 否（应用没有撤销入口） |
| `playhead-previous.move` | `foxos audio-studio playhead-previous move` | 主界面 > Move Playhead to Previous | — | 点击「Move Playhead to Previous」（button） | 否（应用没有撤销入口） |
| `rewind.activate` | `foxos audio-studio rewind activate` | 主界面 > Rewind | — | 点击「Rewind」（button） | 否（应用没有撤销入口） |
| `fast-forward.activate` | `foxos audio-studio fast-forward activate` | 主界面 > Fast Forward | — | 点击「Fast Forward」（button） | 否（应用没有撤销入口） |
| `playhead-next.move` | `foxos audio-studio playhead-next move` | 主界面 > Move Playhead to Next | — | 点击「Move Playhead to Next」（button） | 否（应用没有撤销入口） |
| `shiftspace.record` | `foxos audio-studio shiftspace record` | 主界面 > Record (Shift+Space) | — | 点击「Record (Shift+Space)」（button） | 否（应用没有撤销入口） |
| `selection.dismiss` | `foxos audio-studio selection dismiss` | 主界面 > Skip Selection | — | 点击「Skip Selection」（button） | 不适用（只读） |
| `view.zoom-` | `foxos audio-studio view zoom-` | 主界面 > Zoom In (Amplitude) | — | 点击「Zoom In (Amplitude)」（button） | 否（应用没有撤销入口） |
| `view.zoom-out` | `foxos audio-studio view zoom-out` | 主界面 > Zoom Out (Amplitude) | — | 点击「Zoom Out (Amplitude)」（button） | 否（应用没有撤销入口） |
| `view-2.zoom-` | `foxos audio-studio view-2 zoom-` | 主界面 > Zoom In (Time) | — | 点击「Zoom In (Time)」（button） | 否（应用没有撤销入口） |
| `view-2.zoom-out` | `foxos audio-studio view-2 zoom-out` | 主界面 > Zoom Out (Time) | — | 点击「Zoom Out (Time)」（button） | 否（应用没有撤销入口） |
| `view-3.zoom-out` | `foxos audio-studio view-3 zoom-out` | 主界面 > Zoom Out Full (All Axes) | — | 点击「Zoom Out Full (All Axes)」（button） | 否（应用没有撤销入口） |
| `view-3.zoom-` | `foxos audio-studio view-3 zoom-` | 主界面 > Zoom In at In Point | — | 点击「Zoom In at In Point」（button） | 否（应用没有撤销入口） |
| `view-4.zoom-` | `foxos audio-studio view-4 zoom-` | 主界面 > Zoom In at Out Point | — | 点击「Zoom In at Out Point」（button） | 否（应用没有撤销入口） |
| `view-5.zoom-` | `foxos audio-studio view-5 zoom-` | 主界面 > Zoom to Selection | — | 点击「Zoom to Selection」（button） | 否（应用没有撤销入口） |
| `view.zoom-reset` | `foxos audio-studio view zoom-reset` | 主界面 > Zoom Reset (Time) | — | 点击「Zoom Reset (Time)」（button） | 否（应用没有撤销入口） |
| `view-6.zoom-` | `foxos audio-studio view-6 zoom-` | 主界面 > Zoom In Full (Selected Track) | — | 点击「Zoom In Full (Selected Track)」（button） | 否（应用没有撤销入口） |
| `sound-assistant.show` | `foxos audio-studio sound-assistant show` | 主界面 > Panels > Sound Assistant | — | 点击「Sound Assistant」（tab），切换到该视图 | 不适用（只读） |
| `sound-assistant-panel-menu.activate` | `foxos audio-studio sound-assistant-panel-menu activate` | 主界面 > Sound Assistant panel menu | — | 点击「Sound Assistant panel menu」（button） | 否（应用没有撤销入口） |
| `levels.show` | `foxos audio-studio levels show` | 主界面 > Panels > Levels | — | 点击「Levels」（tab），切换到该视图 | 不适用（只读） |
| `levels-panel-menu.activate` | `foxos audio-studio levels-panel-menu activate` | 主界面 > Levels panel menu | — | 点击「Levels panel menu」（button） | 否（应用没有撤销入口） |
| `left-channel-clip-indicator-click-reset.activate` | `foxos audio-studio left-channel-clip-indicator-click-reset activate` | 主界面 > Left channel clip indicator. Click to reset. | — | 点击「Left channel clip indicator. Click to reset.」（button） | 否（应用没有撤销入口） |
| `right-channel-clip-indicator-click-reset.activate` | `foxos audio-studio right-channel-clip-indicator-click-reset activate` | 主界面 > Right channel clip indicator. Click to reset. | — | 点击「Right channel clip indicator. Click to reset.」（button） | 否（应用没有撤销入口） |
| `selection-view.show` | `foxos audio-studio selection-view show` | 主界面 > Panels > Selection/View | — | 点击「Selection/View」（tab），切换到该视图 | 不适用（只读） |
| `selection-view-panel-menu.activate` | `foxos audio-studio selection-view-panel-menu activate` | 主界面 > Selection/View panel menu | — | 点击「Selection/View panel menu」（button） | 否（应用没有撤销入口） |
| `selection-start.set` | `foxos audio-studio selection-start set` | 主界面 > Selection start | `value`（必填）, `submit` | 把「Selection start」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `selection-end.set` | `foxos audio-studio selection-end set` | 主界面 > Selection end | `value`（必填）, `submit` | 把「Selection end」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `selection-duration.set` | `foxos audio-studio selection-duration set` | 主界面 > Selection duration | `value`（必填）, `submit` | 把「Selection duration」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `view-start.set` | `foxos audio-studio view-start set` | 主界面 > View start | `value`（必填）, `submit` | 把「View start」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `view-end.set` | `foxos audio-studio view-end set` | 主界面 > View end | `value`（必填）, `submit` | 把「View end」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `view-duration.set` | `foxos audio-studio view-duration set` | 主界面 > View duration | `value`（必填）, `submit` | 把「View duration」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `signed-as-local.activate` | `foxos audio-studio signed-as-local activate` | Account: local > Account > Signed in as local | — | 点击「Signed in as local」（menuitem） | 否（应用没有撤销入口） |
| `saved-layout.reset` | `foxos audio-studio saved-layout reset` | All workspaces > Workspaces > Reset to Saved Layout | — | 点击「Reset to Saved Layout」（menuitem） | 否（应用没有撤销入口） |
| `changes-workspace.save` | `foxos audio-studio changes-workspace save` | All workspaces > Workspaces > Save Changes to this Workspace | — | 点击「Save Changes to this Workspace」（menuitem） | 否（应用没有撤销入口） |
| `as-workspace.save` | `foxos audio-studio as-workspace save` | All workspaces > Workspaces > Save as New Workspace... | — | 点击「Save as New Workspace...」（menuitem） | 否（应用没有撤销入口） |
| `workspaces.update` | `foxos audio-studio workspaces update` | All workspaces > Workspaces > Edit Workspaces... | — | 点击「Edit Workspaces...」（menuitem） | 否（应用没有撤销入口） |
| `ctrlo.open` | `foxos audio-studio ctrlo open` | Files panel menu > Files panel menu > Open...Ctrl+O | — | 点击「Open...Ctrl+O」（menuitem） | 不适用（只读） |
| `file-ctrli.import` | `foxos audio-studio file-ctrli import` | Files panel menu > Files panel menu > Import File...Ctrl+I | — | 点击「Import File...Ctrl+I」（menuitem） | 否（应用没有撤销入口） |
| `audio-file-altshiftn.create` | `foxos audio-studio audio-file-altshiftn create` | Files panel menu > Files panel menu > New Audio File...Alt+Shift+N | — | 点击「New Audio File...Alt+Shift+N」（menuitem） | 否（应用没有撤销入口） |
| `into-multitrack-session.create` | `foxos audio-studio into-multitrack-session create` | Files panel menu > Files panel menu > Insert into Multitrack Session | — | 点击「Insert into Multitrack Session」（menuitem） | 否（应用没有撤销入口） |
| `closealtw.activate` | `foxos audio-studio closealtw activate` | Files panel menu > Files panel menu > CloseAlt+W | — | 点击「CloseAlt+W」（menuitem） | 否（应用没有撤销入口） |
| `allaltshiftw.close` | `foxos audio-studio allaltshiftw close` | Files panel menu > Files panel menu > Close AllAlt+Shift+W | — | 点击「Close AllAlt+Shift+W」（menuitem） | 不适用（只读） |
| `columns.activate` | `foxos audio-studio columns activate` | Files panel menu > Files panel menu > Columns | — | 点击「Columns」（menuitem） | 否（应用没有撤销入口） |
| `by-open-order.sort` | `foxos audio-studio by-open-order sort` | Files panel menu > Files panel menu > Sort by Open Order | — | 点击「Sort by Open Order」（menuitem） | 不适用（只读） |
| `panel.close` | `foxos audio-studio panel close` | Files panel menu > Files panel menu > Close Panel | — | 点击「Close Panel」（menuitem） | 不适用（只读） |
| `other-panels-group.close` | `foxos audio-studio other-panels-group close` | Files panel menu > Files panel menu > Close Other Panels in Group | — | 点击「Close Other Panels in Group」（menuitem） | 不适用（只读） |
| `panel-group.close` | `foxos audio-studio panel-group close` | Files panel menu > Files panel menu > Close Panel Group | — | 点击「Close Panel Group」（menuitem） | 不适用（只读） |
| `maximize-frame.activate` | `foxos audio-studio maximize-frame activate` | Files panel menu > Files panel menu > Maximize Frame` | — | 点击「Maximize Frame`」（menuitem） | 否（应用没有撤销入口） |
| `file-name.set` | `foxos audio-studio file-name set` | New Audio File > File name | `value`（必填）, `submit` | 把「File name」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `sample-rate.set` | `foxos audio-studio sample-rate set` | New Audio File > Sample rate | `value`（必填）, `submit` | 把「Sample rate」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `channels.set` | `foxos audio-studio channels set` | New Audio File > Channels | `value`（必填）, `submit` | 把「Channels」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `bit-depth.set` | `foxos audio-studio bit-depth set` | New Audio File > Bit depth | `value`（必填）, `submit` | 把「Bit depth」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `cancel.cancel` | `foxos audio-studio cancel cancel` | New Audio File > dialog > Cancel | — | 点击「Cancel」（button） | 不适用（只读） |
| `ok.confirm` | `foxos audio-studio ok confirm` | New Audio File > dialog > OK | — | 点击「OK」（button） | 否（应用没有撤销入口） |
| `media-browser-panel-menu-panel.close` | `foxos audio-studio media-browser-panel-menu-panel close` | Media Browser panel menu > Media Browser panel menu > Close Panel | — | 点击「Close Panel」（menuitem） | 不适用（只读） |
| `media-browser-panel-menu-other-panels-group.close` | `foxos audio-studio media-browser-panel-menu-other-panels-group close` | Media Browser panel menu > Media Browser panel menu > Close Other Panels in Group | — | 点击「Close Other Panels in Group」（menuitem） | 不适用（只读） |
| `media-browser-panel-menu-panel-group.close` | `foxos audio-studio media-browser-panel-menu-panel-group close` | Media Browser panel menu > Media Browser panel menu > Close Panel Group | — | 点击「Close Panel Group」（menuitem） | 不适用（只读） |
| `media-browser-panel-menu-maximize-frame.activate` | `foxos audio-studio media-browser-panel-menu-maximize-frame activate` | Media Browser panel menu > Media Browser panel menu > Maximize Frame` | — | 点击「Maximize Frame`」（menuitem） | 否（应用没有撤销入口） |
| `undoctrlz.activate` | `foxos audio-studio undoctrlz activate` | History panel menu > History panel menu > UndoCtrl+Z | — | 点击「UndoCtrl+Z」（menuitem） | 否（应用没有撤销入口） |
| `redoctrlshiftz.activate` | `foxos audio-studio redoctrlshiftz activate` | History panel menu > History panel menu > RedoCtrl+Shift+Z | — | 点击「RedoCtrl+Shift+Z」（menuitem） | 否（应用没有撤销入口） |
| `later-states.delete` | `foxos audio-studio later-states delete` | History panel menu > History panel menu > Delete Later States | — | 点击「Delete Later States」（menuitem） | 否（应用没有撤销入口） |
| `history-panel-menu-history.clear` | `foxos audio-studio history-panel-menu-history clear` | History panel menu > History panel menu > Clear History... | — | 点击「Clear History...」（menuitem） | 否（应用没有撤销入口） |
| `history-panel-menu-panel.close` | `foxos audio-studio history-panel-menu-panel close` | History panel menu > History panel menu > Close Panel | — | 点击「Close Panel」（menuitem） | 不适用（只读） |
| `history-panel-menu-other-panels-group.close` | `foxos audio-studio history-panel-menu-other-panels-group close` | History panel menu > History panel menu > Close Other Panels in Group | — | 点击「Close Other Panels in Group」（menuitem） | 不适用（只读） |
| `history-panel-menu-panel-group.close` | `foxos audio-studio history-panel-menu-panel-group close` | History panel menu > History panel menu > Close Panel Group | — | 点击「Close Panel Group」（menuitem） | 不适用（只读） |
| `history-panel-menu-maximize-frame.activate` | `foxos audio-studio history-panel-menu-maximize-frame activate` | History panel menu > History panel menu > Maximize Frame` | — | 点击「Maximize Frame`」（menuitem） | 否（应用没有撤销入口） |
| `selection.select-all` | `foxos audio-studio selection select-all` | 键盘 mod+a | — | 在当前焦点上按 mod+a（src/batch/panel.js 中定义） | 否（应用没有撤销入口） |
