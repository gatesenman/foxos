# Music Studio（music-studio）操作清单

分组：creative · 替代 FL Studio, Ableton Live, Logic Pro · 许可证 MIT (root LICENSE) · 页面标题「Demo Song - Music Studio」

共 266 个操作，全部有语义命令（`foxos music-studio <资源> <动词>`，MCP 工具 `music-studio.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `pattern-mode.select` | `foxos music-studio pattern-mode select` | 主界面 > Playback mode > pattern mode: * | `target`（必填） | 点击名称匹配的「pattern mode: *」项（radio） | 不适用（只读） |
| `song-mode.select` | `foxos music-studio song-mode select` | 主界面 > Playback mode > song mode: * | `target`（必填） | 点击名称匹配的「song mode: *」项（radio） | 不适用（只读） |
| `pattern.select` | `foxos music-studio pattern select` | 主界面 > pattern: * | `target`（必填） | 点击名称匹配的「pattern: *」项（button） | 不适用（只读） |
| `project.select` | `foxos music-studio project select` | 主界面 > project: * | `target`（必填） | 点击名称匹配的「project: *」项（button） | 不适用（只读） |
| `account.select` | `foxos music-studio account select` | 主界面 > account: * | `target`（必填） | 点击名称匹配的「account: *」项（button） | 不适用（只读） |
| `one-synthesized-drum-voice.select` | `foxos music-studio one-synthesized-drum-voice select` | 主界面 > Browser > one synthesized drum voice: * | `target`（必填） | 点击名称匹配的「one synthesized drum voice: *」项（treeitem） | 不适用（只读） |
| `browser.select` | `foxos music-studio browser select` | 主界面 > Browser > # | `target`（必填） | 点击名称匹配的「#」项（treeitem） | 不适用（只读） |
| `beat-clips.select` | `foxos music-studio beat-clips select` | 主界面 > beat, # clips | `target`（必填） | 点击名称匹配的「beat, # clips」项（option） | 不适用（只读） |
| `bassline-clips.select` | `foxos music-studio bassline-clips select` | 主界面 > bassline, # clips | `target`（必填） | 点击名称匹配的「bassline, # clips」项（option） | 不适用（只读） |
| `chords-clips.select` | `foxos music-studio chords-clips select` | 主界面 > chords, # clips | `target`（必填） | 点击名称匹配的「chords, # clips」项（option） | 不适用（只读） |
| `lead-clip.select` | `foxos music-studio lead-clip select` | 主界面 > lead, # clip | `target`（必填） | 点击名称匹配的「lead, # clip」项（option） | 不适用（只读） |
| `track-1.select` | `foxos music-studio track-1 select` | 主界面 > track 1: * | `target`（必填） | 点击名称匹配的「track 1: *」项（button） | 不适用（只读） |
| `track-2.select` | `foxos music-studio track-2 select` | 主界面 > track 2: * | `target`（必填） | 点击名称匹配的「track 2: *」项（button） | 不适用（只读） |
| `track-3.select` | `foxos music-studio track-3 select` | 主界面 > track 3: * | `target`（必填） | 点击名称匹配的「track 3: *」项（button） | 不适用（只读） |
| `track-4.select` | `foxos music-studio track-4 select` | 主界面 > track 4: * | `target`（必填） | 点击名称匹配的「track 4: *」项（button） | 不适用（只读） |
| `track-5.select` | `foxos music-studio track-5 select` | 主界面 > track 5: * | `target`（必填） | 点击名称匹配的「track 5: *」项（button） | 不适用（只读） |
| `mute-track.select` | `foxos music-studio mute-track select` | 主界面 > mute track # | `target`（必填） | 点击名称匹配的「mute track #」项（button） | 不适用（只读） |
| `solo-track.select` | `foxos music-studio solo-track select` | 主界面 > solo track # | `target`（必填） | 点击名称匹配的「solo track #」项（button） | 不适用（只读） |
| `track-6.select` | `foxos music-studio track-6 select` | 主界面 > track 6: * | `target`（必填） | 点击名称匹配的「track 6: *」项（button） | 不适用（只读） |
| `track-7.select` | `foxos music-studio track-7 select` | 主界面 > track 7: * | `target`（必填） | 点击名称匹配的「track 7: *」项（button） | 不适用（只读） |
| `track-8.select` | `foxos music-studio track-8 select` | 主界面 > track 8: * | `target`（必填） | 点击名称匹配的「track 8: *」项（button） | 不适用（只读） |
| `track-9.select` | `foxos music-studio track-9 select` | 主界面 > track 9: * | `target`（必填） | 点击名称匹配的「track 9: *」项（button） | 不适用（只读） |
| `track-10.select` | `foxos music-studio track-10 select` | 主界面 > track 10: * | `target`（必填） | 点击名称匹配的「track 10: *」项（button） | 不适用（只读） |
| `track-11.select` | `foxos music-studio track-11 select` | 主界面 > track 11: * | `target`（必填） | 点击名称匹配的「track 11: *」项（button） | 不适用（只读） |
| `track-12.select` | `foxos music-studio track-12 select` | 主界面 > track 12: * | `target`（必填） | 点击名称匹配的「track 12: *」项（button） | 不适用（只读） |
| `track-13.select` | `foxos music-studio track-13 select` | 主界面 > track 13: * | `target`（必填） | 点击名称匹配的「track 13: *」项（button） | 不适用（只读） |
| `track-14.select` | `foxos music-studio track-14 select` | 主界面 > track 14: * | `target`（必填） | 点击名称匹配的「track 14: *」项（button） | 不适用（只读） |
| `track-15.select` | `foxos music-studio track-15 select` | 主界面 > track 15: * | `target`（必填） | 点击名称匹配的「track 15: *」项（button） | 不适用（只读） |
| `track-16.select` | `foxos music-studio track-16 select` | 主界面 > track 16: * | `target`（必填） | 点击名称匹配的「track 16: *」项（button） | 不适用（只读） |
| `kick.select` | `foxos music-studio kick select` | 主界面 > kick: * | `target`（必填） | 点击名称匹配的「kick: *」项（button） | 不适用（只读） |
| `channel-rack-beat.select` | `foxos music-studio channel-rack-beat select` | 主界面 > Channel rack, Beat > # | `target`（必填） | 点击名称匹配的「#」项（gridcell） | 不适用（只读） |
| `kick-2.select` | `foxos music-studio kick-2 select` | 主界面 > Channel rack, Beat > kick: * | `target`（必填） | 点击名称匹配的「kick: *」项（button） | 不适用（只读） |
| `step-velocity.select` | `foxos music-studio step-velocity select` | 主界面 > step #, on, velocity #% | `target`（必填） | 点击名称匹配的「step #, on, velocity #%」项（gridcell） | 不适用（只读） |
| `step-off.select` | `foxos music-studio step-off select` | 主界面 > step #, off | `target`（必填） | 点击名称匹配的「step #, off」项（gridcell） | 不适用（只读） |
| `clap.select` | `foxos music-studio clap select` | 主界面 > clap: * | `target`（必填） | 点击名称匹配的「clap: *」项（button） | 不适用（只读） |
| `clap-2.select` | `foxos music-studio clap-2 select` | 主界面 > Channel rack, Beat > clap: * | `target`（必填） | 点击名称匹配的「clap: *」项（button） | 不适用（只读） |
| `closed-hat.select` | `foxos music-studio closed-hat select` | 主界面 > closed hat: * | `target`（必填） | 点击名称匹配的「closed hat: *」项（button） | 不适用（只读） |
| `closed-hat-2.select` | `foxos music-studio closed-hat-2 select` | 主界面 > Channel rack, Beat > closed hat: * | `target`（必填） | 点击名称匹配的「closed hat: *」项（button） | 不适用（只读） |
| `hat.open` | `foxos music-studio hat open` | 主界面 > open hat: * | `target`（必填） | 点击名称匹配的「open hat: *」项（button） | 不适用（只读） |
| `hat-2.open` | `foxos music-studio hat-2 open` | 主界面 > Channel rack, Beat > open hat: * | `target`（必填） | 点击名称匹配的「open hat: *」项（button） | 不适用（只读） |
| `bass.select` | `foxos music-studio bass select` | 主界面 > bass: * | `target`（必填） | 点击名称匹配的「bass: *」项（button） | 不适用（只读） |
| `bass-2.select` | `foxos music-studio bass-2 select` | 主界面 > Channel rack, Beat > bass: * | `target`（必填） | 点击名称匹配的「bass: *」项（button） | 不适用（只读） |
| `chords.select` | `foxos music-studio chords select` | 主界面 > chords: * | `target`（必填） | 点击名称匹配的「chords: *」项（button） | 不适用（只读） |
| `chords-2.select` | `foxos music-studio chords-2 select` | 主界面 > Channel rack, Beat > chords: * | `target`（必填） | 点击名称匹配的「chords: *」项（button） | 不适用（只读） |
| `lead.select` | `foxos music-studio lead select` | 主界面 > lead: * | `target`（必填） | 点击名称匹配的「lead: *」项（button） | 不适用（只读） |
| `lead-2.select` | `foxos music-studio lead-2 select` | 主界面 > Channel rack, Beat > lead: * | `target`（必填） | 点击名称匹配的「lead: *」项（button） | 不适用（只读） |
| `master-double-click-or-rename.select` | `foxos music-studio master-double-click-or-rename select` | 主界面 > Master > master. double-click or # to rename. | `target`（必填） | 点击名称匹配的「master. double-click or # to rename.」项（button） | 不适用（只读） |
| `kick-master.send` | `foxos music-studio kick-master send` | 主界面 > send # kick to master | `target`（必填） | 点击名称匹配的「send # kick to master」项（button） | 否（应用没有撤销入口） |
| `inputs.select` | `foxos music-studio inputs select` | 主界面 > inputs: * | `target`（必填） | 点击名称匹配的「inputs: *」项（button） | 不适用（只读） |
| `kick-double-click-or-rename.select` | `foxos music-studio kick-double-click-or-rename select` | 主界面 > Insert 1, Kick > kick. double-click or # to rename. | `target`（必填） | 点击名称匹配的「kick. double-click or # to rename.」项（button） | 不适用（只读） |
| `clap-double-click-or-rename.select` | `foxos music-studio clap-double-click-or-rename select` | 主界面 > Insert 2, Clap > clap. double-click or # to rename. | `target`（必填） | 点击名称匹配的「clap. double-click or # to rename.」项（button） | 不适用（只读） |
| `kick-clap.send` | `foxos music-studio kick-clap send` | 主界面 > send # kick to # clap | `target`（必填） | 点击名称匹配的「send # kick to # clap」项（button） | 否（应用没有撤销入口） |
| `hats-double-click-or-rename.select` | `foxos music-studio hats-double-click-or-rename select` | 主界面 > Insert 3, Hats > hats. double-click or # to rename. | `target`（必填） | 点击名称匹配的「hats. double-click or # to rename.」项（button） | 不适用（只读） |
| `kick-hats.send` | `foxos music-studio kick-hats send` | 主界面 > send # kick to # hats | `target`（必填） | 点击名称匹配的「send # kick to # hats」项（button） | 否（应用没有撤销入口） |
| `bass-double-click-or-rename.select` | `foxos music-studio bass-double-click-or-rename select` | 主界面 > Insert 4, Bass > bass. double-click or # to rename. | `target`（必填） | 点击名称匹配的「bass. double-click or # to rename.」项（button） | 不适用（只读） |
| `kick-bass.send` | `foxos music-studio kick-bass send` | 主界面 > send # kick to # bass | `target`（必填） | 点击名称匹配的「send # kick to # bass」项（button） | 否（应用没有撤销入口） |
| `chords-double-click-or-rename.select` | `foxos music-studio chords-double-click-or-rename select` | 主界面 > Insert 5, Chords > chords. double-click or # to rename. | `target`（必填） | 点击名称匹配的「chords. double-click or # to rename.」项（button） | 不适用（只读） |
| `kick-chords.send` | `foxos music-studio kick-chords send` | 主界面 > send # kick to # chords | `target`（必填） | 点击名称匹配的「send # kick to # chords」项（button） | 否（应用没有撤销入口） |
| `lead-double-click-or-rename.select` | `foxos music-studio lead-double-click-or-rename select` | 主界面 > Insert 6, Lead > lead. double-click or # to rename. | `target`（必填） | 点击名称匹配的「lead. double-click or # to rename.」项（button） | 不适用（只读） |
| `kick-lead.send` | `foxos music-studio kick-lead send` | 主界面 > send # kick to # lead | `target`（必填） | 点击名称匹配的「send # kick to # lead」项（button） | 否（应用没有撤销入口） |
| `double-click-or-rename.create` | `foxos music-studio double-click-or-rename create` | 主界面 > Insert 7, Insert 7 > insert # double-click or # to rename. | `target`（必填） | 点击名称匹配的「insert # double-click or # to rename.」项（button） | 否（应用没有撤销入口） |
| `mute-insert.select` | `foxos music-studio mute-insert select` | 主界面 > mute insert # | `target`（必填） | 点击名称匹配的「mute insert #」项（button） | 不适用（只读） |
| `solo-insert.select` | `foxos music-studio solo-insert select` | 主界面 > solo insert # | `target`（必填） | 点击名称匹配的「solo insert #」项（button） | 不适用（只读） |
| `kick-insert.send` | `foxos music-studio kick-insert send` | 主界面 > send # kick to insert # | `target`（必填） | 点击名称匹配的「send # kick to insert #」项（button） | 否（应用没有撤销入口） |
| `double-click-or-rename-2.create` | `foxos music-studio double-click-or-rename-2 create` | 主界面 > Insert 8, Insert 8 > insert # double-click or # to rename. | `target`（必填） | 点击名称匹配的「insert # double-click or # to rename.」项（button） | 否（应用没有撤销入口） |
| `double-click-or-rename-3.create` | `foxos music-studio double-click-or-rename-3 create` | 主界面 > Insert 9, Insert 9 > insert # double-click or # to rename. | `target`（必填） | 点击名称匹配的「insert # double-click or # to rename.」项（button） | 否（应用没有撤销入口） |
| `double-click-or-rename-4.create` | `foxos music-studio double-click-or-rename-4 create` | 主界面 > Insert 10, Insert 10 > insert # double-click or # to rename. | `target`（必填） | 点击名称匹配的「insert # double-click or # to rename.」项（button） | 否（应用没有撤销入口） |
| `double-click-or-rename-5.create` | `foxos music-studio double-click-or-rename-5 create` | 主界面 > Insert 11, Insert 11 > insert # double-click or # to rename. | `target`（必填） | 点击名称匹配的「insert # double-click or # to rename.」项（button） | 否（应用没有撤销入口） |
| `double-click-or-rename-6.create` | `foxos music-studio double-click-or-rename-6 create` | 主界面 > Insert 12, Insert 12 > insert # double-click or # to rename. | `target`（必填） | 点击名称匹配的「insert # double-click or # to rename.」项（button） | 否（应用没有撤销入口） |
| `double-click-or-rename-7.create` | `foxos music-studio double-click-or-rename-7 create` | 主界面 > Insert 13, Insert 13 > insert # double-click or # to rename. | `target`（必填） | 点击名称匹配的「insert # double-click or # to rename.」项（button） | 否（应用没有撤销入口） |
| `double-click-or-rename-8.create` | `foxos music-studio double-click-or-rename-8 create` | 主界面 > Insert 14, Insert 14 > insert # double-click or # to rename. | `target`（必填） | 点击名称匹配的「insert # double-click or # to rename.」项（button） | 否（应用没有撤销入口） |
| `double-click-or-rename-9.create` | `foxos music-studio double-click-or-rename-9 create` | 主界面 > Insert 15, Insert 15 > insert # double-click or # to rename. | `target`（必填） | 点击名称匹配的「insert # double-click or # to rename.」项（button） | 否（应用没有撤销入口） |
| `double-click-or-rename-10.create` | `foxos music-studio double-click-or-rename-10 create` | 主界面 > Insert 16, Insert 16 > insert # double-click or # to rename. | `target`（必填） | 点击名称匹配的「insert # double-click or # to rename.」项（button） | 否（应用没有撤销入口） |
| `effect.select` | `foxos music-studio effect select` | 主界面 > Effect slots > # effect | `target`（必填） | 点击名称匹配的「# effect」项（button） | 不适用（只读） |
| `beat.select` | `foxos music-studio beat select` | Pattern: Beat. Select pattern > Patterns > # beat | `target`（必填） | 点击名称匹配的「# beat」项（menuitemradio） | 不适用（只读） |
| `bassline.select` | `foxos music-studio bassline select` | Pattern: Beat. Select pattern > Patterns > # bassline | `target`（必填） | 点击名称匹配的「# bassline」项（menuitemradio） | 不适用（只读） |
| `pattern-beat-select-pattern-chords.select` | `foxos music-studio pattern-beat-select-pattern-chords select` | Pattern: Beat. Select pattern > Patterns > # chords | `target`（必填） | 点击名称匹配的「# chords」项（menuitemradio） | 不适用（只读） |
| `pattern-beat-select-pattern-lead.select` | `foxos music-studio pattern-beat-select-pattern-lead select` | Pattern: Beat. Select pattern > Patterns > # lead | `target`（必填） | 点击名称匹配的「# lead」项（menuitemradio） | 不适用（只读） |
| `pattern.rename` | `foxos music-studio pattern rename` | Pattern: Beat. Select pattern > Patterns > rename pattern...# | `target`（必填） | 点击名称匹配的「rename pattern...#」项（menuitem） | 否（应用没有撤销入口） |
| `clap-master.send` | `foxos music-studio clap-master send` | Clap: click to select, double-click or Enter for the editor, right-click for options > send # clap to master | `target`（必填） | 点击名称匹配的「send # clap to master」项（button） | 否（应用没有撤销入口） |
| `clap-kick.send` | `foxos music-studio clap-kick send` | Clap: click to select, double-click or Enter for the editor, right-click for options > send # clap to # kick | `target`（必填） | 点击名称匹配的「send # clap to # kick」项（button） | 否（应用没有撤销入口） |
| `clap-hats.send` | `foxos music-studio clap-hats send` | Clap: click to select, double-click or Enter for the editor, right-click for options > send # clap to # hats | `target`（必填） | 点击名称匹配的「send # clap to # hats」项（button） | 否（应用没有撤销入口） |
| `clap-bass.send` | `foxos music-studio clap-bass send` | Clap: click to select, double-click or Enter for the editor, right-click for options > send # clap to # bass | `target`（必填） | 点击名称匹配的「send # clap to # bass」项（button） | 否（应用没有撤销入口） |
| `clap-chords.send` | `foxos music-studio clap-chords send` | Clap: click to select, double-click or Enter for the editor, right-click for options > send # clap to # chords | `target`（必填） | 点击名称匹配的「send # clap to # chords」项（button） | 否（应用没有撤销入口） |
| `clap-lead.send` | `foxos music-studio clap-lead send` | Clap: click to select, double-click or Enter for the editor, right-click for options > send # clap to # lead | `target`（必填） | 点击名称匹配的「send # clap to # lead」项（button） | 否（应用没有撤销入口） |
| `clap-insert.send` | `foxos music-studio clap-insert send` | Clap: click to select, double-click or Enter for the editor, right-click for options > send # clap to insert # | `target`（必填） | 点击名称匹配的「send # clap to insert #」项（button） | 否（应用没有撤销入口） |
| `hats-master.send` | `foxos music-studio hats-master send` | Open Hat: click to select, double-click or Enter for the editor, right-click for options > send # hats to master | `target`（必填） | 点击名称匹配的「send # hats to master」项（button） | 否（应用没有撤销入口） |
| `hats-kick.send` | `foxos music-studio hats-kick send` | Open Hat: click to select, double-click or Enter for the editor, right-click for options > send # hats to # kick | `target`（必填） | 点击名称匹配的「send # hats to # kick」项（button） | 否（应用没有撤销入口） |
| `hats-clap.send` | `foxos music-studio hats-clap send` | Open Hat: click to select, double-click or Enter for the editor, right-click for options > send # hats to # clap | `target`（必填） | 点击名称匹配的「send # hats to # clap」项（button） | 否（应用没有撤销入口） |
| `hats-bass.send` | `foxos music-studio hats-bass send` | Open Hat: click to select, double-click or Enter for the editor, right-click for options > send # hats to # bass | `target`（必填） | 点击名称匹配的「send # hats to # bass」项（button） | 否（应用没有撤销入口） |
| `hats-chords.send` | `foxos music-studio hats-chords send` | Open Hat: click to select, double-click or Enter for the editor, right-click for options > send # hats to # chords | `target`（必填） | 点击名称匹配的「send # hats to # chords」项（button） | 否（应用没有撤销入口） |
| `hats-lead.send` | `foxos music-studio hats-lead send` | Open Hat: click to select, double-click or Enter for the editor, right-click for options > send # hats to # lead | `target`（必填） | 点击名称匹配的「send # hats to # lead」项（button） | 否（应用没有撤销入口） |
| `hats-insert.send` | `foxos music-studio hats-insert send` | Open Hat: click to select, double-click or Enter for the editor, right-click for options > send # hats to insert # | `target`（必填） | 点击名称匹配的「send # hats to insert #」项（button） | 否（应用没有撤销入口） |
| `bass-master.send` | `foxos music-studio bass-master send` | Bass: click to select, double-click or Enter for the editor, right-click for options > send # bass to master | `target`（必填） | 点击名称匹配的「send # bass to master」项（button） | 否（应用没有撤销入口） |
| `bass-kick.send` | `foxos music-studio bass-kick send` | Bass: click to select, double-click or Enter for the editor, right-click for options > send # bass to # kick | `target`（必填） | 点击名称匹配的「send # bass to # kick」项（button） | 否（应用没有撤销入口） |
| `bass-clap.send` | `foxos music-studio bass-clap send` | Bass: click to select, double-click or Enter for the editor, right-click for options > send # bass to # clap | `target`（必填） | 点击名称匹配的「send # bass to # clap」项（button） | 否（应用没有撤销入口） |
| `bass-hats.send` | `foxos music-studio bass-hats send` | Bass: click to select, double-click or Enter for the editor, right-click for options > send # bass to # hats | `target`（必填） | 点击名称匹配的「send # bass to # hats」项（button） | 否（应用没有撤销入口） |
| `bass-chords.send` | `foxos music-studio bass-chords send` | Bass: click to select, double-click or Enter for the editor, right-click for options > send # bass to # chords | `target`（必填） | 点击名称匹配的「send # bass to # chords」项（button） | 否（应用没有撤销入口） |
| `bass-lead.send` | `foxos music-studio bass-lead send` | Bass: click to select, double-click or Enter for the editor, right-click for options > send # bass to # lead | `target`（必填） | 点击名称匹配的「send # bass to # lead」项（button） | 否（应用没有撤销入口） |
| `bass-insert.send` | `foxos music-studio bass-insert send` | Bass: click to select, double-click or Enter for the editor, right-click for options > send # bass to insert # | `target`（必填） | 点击名称匹配的「send # bass to insert #」项（button） | 否（应用没有撤销入口） |
| `chords-master.send` | `foxos music-studio chords-master send` | Chords: click to select, double-click or Enter for the editor, right-click for options > send # chords to master | `target`（必填） | 点击名称匹配的「send # chords to master」项（button） | 否（应用没有撤销入口） |
| `chords-kick.send` | `foxos music-studio chords-kick send` | Chords: click to select, double-click or Enter for the editor, right-click for options > send # chords to # kick | `target`（必填） | 点击名称匹配的「send # chords to # kick」项（button） | 否（应用没有撤销入口） |
| `chords-clap.send` | `foxos music-studio chords-clap send` | Chords: click to select, double-click or Enter for the editor, right-click for options > send # chords to # clap | `target`（必填） | 点击名称匹配的「send # chords to # clap」项（button） | 否（应用没有撤销入口） |
| `chords-hats.send` | `foxos music-studio chords-hats send` | Chords: click to select, double-click or Enter for the editor, right-click for options > send # chords to # hats | `target`（必填） | 点击名称匹配的「send # chords to # hats」项（button） | 否（应用没有撤销入口） |
| `chords-bass.send` | `foxos music-studio chords-bass send` | Chords: click to select, double-click or Enter for the editor, right-click for options > send # chords to # bass | `target`（必填） | 点击名称匹配的「send # chords to # bass」项（button） | 否（应用没有撤销入口） |
| `chords-lead.send` | `foxos music-studio chords-lead send` | Chords: click to select, double-click or Enter for the editor, right-click for options > send # chords to # lead | `target`（必填） | 点击名称匹配的「send # chords to # lead」项（button） | 否（应用没有撤销入口） |
| `chords-insert.send` | `foxos music-studio chords-insert send` | Chords: click to select, double-click or Enter for the editor, right-click for options > send # chords to insert # | `target`（必填） | 点击名称匹配的「send # chords to insert #」项（button） | 否（应用没有撤销入口） |
| `reverb-slot-open-editor.select` | `foxos music-studio reverb-slot-open-editor select` | Chords: click to select, double-click or Enter for the editor, right-click for options > reverb, slot # open editor | `target`（必填） | 点击名称匹配的「reverb, slot # open editor」项（button） | 不适用（只读） |
| `lead-master.send` | `foxos music-studio lead-master send` | Lead: click to select, double-click or Enter for the editor, right-click for options > send # lead to master | `target`（必填） | 点击名称匹配的「send # lead to master」项（button） | 否（应用没有撤销入口） |
| `lead-kick.send` | `foxos music-studio lead-kick send` | Lead: click to select, double-click or Enter for the editor, right-click for options > send # lead to # kick | `target`（必填） | 点击名称匹配的「send # lead to # kick」项（button） | 否（应用没有撤销入口） |
| `lead-clap.send` | `foxos music-studio lead-clap send` | Lead: click to select, double-click or Enter for the editor, right-click for options > send # lead to # clap | `target`（必填） | 点击名称匹配的「send # lead to # clap」项（button） | 否（应用没有撤销入口） |
| `lead-hats.send` | `foxos music-studio lead-hats send` | Lead: click to select, double-click or Enter for the editor, right-click for options > send # lead to # hats | `target`（必填） | 点击名称匹配的「send # lead to # hats」项（button） | 否（应用没有撤销入口） |
| `lead-bass.send` | `foxos music-studio lead-bass send` | Lead: click to select, double-click or Enter for the editor, right-click for options > send # lead to # bass | `target`（必填） | 点击名称匹配的「send # lead to # bass」项（button） | 否（应用没有撤销入口） |
| `lead-chords.send` | `foxos music-studio lead-chords send` | Lead: click to select, double-click or Enter for the editor, right-click for options > send # lead to # chords | `target`（必填） | 点击名称匹配的「send # lead to # chords」项（button） | 否（应用没有撤销入口） |
| `lead-insert.send` | `foxos music-studio lead-insert send` | Lead: click to select, double-click or Enter for the editor, right-click for options > send # lead to insert # | `target`（必填） | 点击名称匹配的「send # lead to insert #」项（button） | 否（应用没有撤销入口） |
| `delay-slot-open-editor.select` | `foxos music-studio delay-slot-open-editor select` | Lead: click to select, double-click or Enter for the editor, right-click for options > delay, slot # open editor | `target`（必填） | 点击名称匹配的「delay, slot # open editor」项（button） | 不适用（只读） |
| `lead-click-select-double-click-or-enter-reverb-s.select` | `foxos music-studio lead-click-select-double-click-or-enter-reverb-s select` | Lead: click to select, double-click or Enter for the editor, right-click for options > reverb, slot # open editor | `target`（必填） | 点击名称匹配的「reverb, slot # open editor」项（button） | 不适用（只读） |
| `add-mixer-insert-project.select` | `foxos music-studio add-mixer-insert-project select` | Add mixer insert > project: * | `target`（必填） | 点击名称匹配的「project: *」项（button） | 不适用（只读） |
| `insert-master.send` | `foxos music-studio insert-master send` | Add mixer insert > send insert # to master | `target`（必填） | 点击名称匹配的「send insert # to master」项（button） | 否（应用没有撤销入口） |
| `insert-kick.send` | `foxos music-studio insert-kick send` | Add mixer insert > send insert # to # kick | `target`（必填） | 点击名称匹配的「send insert # to # kick」项（button） | 否（应用没有撤销入口） |
| `insert-clap.send` | `foxos music-studio insert-clap send` | Add mixer insert > send insert # to # clap | `target`（必填） | 点击名称匹配的「send insert # to # clap」项（button） | 否（应用没有撤销入口） |
| `insert-hats.send` | `foxos music-studio insert-hats send` | Add mixer insert > send insert # to # hats | `target`（必填） | 点击名称匹配的「send insert # to # hats」项（button） | 否（应用没有撤销入口） |
| `insert-bass.send` | `foxos music-studio insert-bass send` | Add mixer insert > send insert # to # bass | `target`（必填） | 点击名称匹配的「send insert # to # bass」项（button） | 否（应用没有撤销入口） |
| `insert-chords.send` | `foxos music-studio insert-chords send` | Add mixer insert > send insert # to # chords | `target`（必填） | 点击名称匹配的「send insert # to # chords」项（button） | 否（应用没有撤销入口） |
| `insert-lead.send` | `foxos music-studio insert-lead send` | Add mixer insert > send insert # to # lead | `target`（必填） | 点击名称匹配的「send insert # to # lead」项（button） | 否（应用没有撤销入口） |
| `insert-insert.send` | `foxos music-studio insert-insert send` | Add mixer insert > send insert # to insert # | `target`（必填） | 点击名称匹配的「send insert # to insert #」项（button） | 否（应用没有撤销入口） |
| `add-mixer-insert-double-click-or-rename.create` | `foxos music-studio add-mixer-insert-double-click-or-rename create` | Add mixer insert > Insert 17, Insert 17 > insert # double-click or # to rename. | `target`（必填） | 点击名称匹配的「insert # double-click or # to rename.」项（button） | 否（应用没有撤销入口） |
| `volume.create` | `foxos music-studio volume create` | Add mixer insert > insert # volume | `target`（必填） | 点击名称匹配的「insert # volume」项（slider） | 否（应用没有撤销入口） |
| `add-mixer-insert-mute-insert.select` | `foxos music-studio add-mixer-insert-mute-insert select` | Add mixer insert > mute insert # | `target`（必填） | 点击名称匹配的「mute insert #」项（button） | 不适用（只读） |
| `add-mixer-insert-solo-insert.select` | `foxos music-studio add-mixer-insert-solo-insert select` | Add mixer insert > solo insert # | `target`（必填） | 点击名称匹配的「solo insert #」项（button） | 不适用（只读） |
| `workspace.dismiss` | `foxos music-studio workspace dismiss` | 主界面 > Skip to workspace | — | 点击「Skip to workspace」（link） | 不适用（只读） |
| `file.activate` | `foxos music-studio file activate` | 主界面 > Main menu > File | — | 点击「File」（menuitem） | 否（应用没有撤销入口） |
| `edit.update` | `foxos music-studio edit update` | 主界面 > Main menu > Edit | — | 点击「Edit」（menuitem） | 否（应用没有撤销入口） |
| `add.create` | `foxos music-studio add create` | 主界面 > Main menu > Add | — | 点击「Add」（menuitem） | 否（应用没有撤销入口） |
| `patterns.activate` | `foxos music-studio patterns activate` | 主界面 > Main menu > Patterns | — | 点击「Patterns」（menuitem） | 否（应用没有撤销入口） |
| `view.show` | `foxos music-studio view show` | 主界面 > Main menu > View | — | 点击「View」（menuitem），切换到该视图 | 不适用（只读） |
| `options.activate` | `foxos music-studio options activate` | 主界面 > Main menu > Options | — | 点击「Options」（menuitem） | 否（应用没有撤销入口） |
| `tools.activate` | `foxos music-studio tools activate` | 主界面 > Main menu > Tools | — | 点击「Tools」（menuitem） | 否（应用没有撤销入口） |
| `help.show` | `foxos music-studio help show` | 主界面 > Main menu > Help | — | 点击「Help」（menuitem），切换到该视图 | 不适用（只读） |
| `play.play` | `foxos music-studio play play` | 主界面 > Play | — | 点击「Play」（button） | 否（应用没有撤销入口） |
| `stop.stop` | `foxos music-studio stop stop` | 主界面 > Stop | — | 点击「Stop」（button） | 否（应用没有撤销入口） |
| `record.record` | `foxos music-studio record record` | 主界面 > Record | — | 点击「Record」（button） | 否（应用没有撤销入口） |
| `tempo-beats-per-minute.set` | `foxos music-studio tempo-beats-per-minute set` | 主界面 > Tempo in beats per minute | `value`（必填）, `submit` | 把「Tempo in beats per minute」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `metronome.activate` | `foxos music-studio metronome activate` | 主界面 > Metronome | — | 点击「Metronome」（button） | 否（应用没有撤销入口） |
| `count-in-before-recording.activate` | `foxos music-studio count-in-before-recording activate` | 主界面 > Count-in before recording | — | 点击「Count-in before recording」（button） | 否（应用没有撤销入口） |
| `typing-keyboard-piano.activate` | `foxos music-studio typing-keyboard-piano activate` | 主界面 > Typing keyboard to piano | — | 点击「Typing keyboard to piano」（button） | 否（应用没有撤销入口） |
| `pattern.previous` | `foxos music-studio pattern previous` | 主界面 > Previous pattern | — | 点击「Previous pattern」（button） | 不适用（只读） |
| `pattern.next` | `foxos music-studio pattern next` | 主界面 > Next pattern | — | 点击「Next pattern」（button） | 不适用（只读） |
| `pattern.create` | `foxos music-studio pattern create` | 主界面 > New pattern | — | 点击「New pattern」（button） | 否（应用没有撤销入口） |
| `playlist.activate` | `foxos music-studio playlist activate` | 主界面 > Playlist | — | 点击「Playlist」（button） | 否（应用没有撤销入口） |
| `channel-rack.activate` | `foxos music-studio channel-rack activate` | 主界面 > Channel rack | — | 点击「Channel rack」（button） | 否（应用没有撤销入口） |
| `piano-roll.activate` | `foxos music-studio piano-roll activate` | 主界面 > Piano roll | — | 点击「Piano roll」（button） | 否（应用没有撤销入口） |
| `mixer.activate` | `foxos music-studio mixer activate` | 主界面 > Mixer | — | 点击「Mixer」（button） | 否（应用没有撤销入口） |
| `browser.activate` | `foxos music-studio browser activate` | 主界面 > Browser | — | 点击「Browser」（button） | 否（应用没有撤销入口） |
| `master-volume.set` | `foxos music-studio master-volume set` | 主界面 > Master volume | `value`（必填）, `submit` | 把「Master volume」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `source-code-github-opens-tab.show` | `foxos music-studio source-code-github-opens-tab show` | 主界面 > Source code on GitHub (opens in a new tab) | — | 点击「Source code on GitHub (opens in a new tab)」（link），切换到该视图 | 不适用（只读） |
| `audio.import` | `foxos music-studio audio import` | 主界面 > Import audio | — | 点击「Import audio」（button） | 否（应用没有撤销入口） |
| `collapse.collapse` | `foxos music-studio collapse collapse` | 主界面 > Collapse all | — | 点击「Collapse all」（button） | 不适用（只读） |
| `browser.close` | `foxos music-studio browser close` | 主界面 > Close Browser | — | 点击「Close Browser」（button） | 不适用（只读） |
| `search-browser.set` | `foxos music-studio search-browser set` | 主界面 > Search the browser | `value`（必填）, `submit` | 把「Search the browser」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `instruments.activate` | `foxos music-studio instruments activate` | 主界面 > Browser > Instruments | — | 点击「Instruments」（treeitem） | 否（应用没有撤销入口） |
| `synth-presets.activate` | `foxos music-studio synth-presets activate` | 主界面 > Browser > Synth presets | — | 点击「Synth presets」（treeitem） | 否（应用没有撤销入口） |
| `drum-presets.activate` | `foxos music-studio drum-presets activate` | 主界面 > Browser > Drum presets | — | 点击「Drum presets」（treeitem） | 否（应用没有撤销入口） |
| `effects.activate` | `foxos music-studio effects activate` | 主界面 > Browser > Effects | — | 点击「Effects」（treeitem） | 否（应用没有撤销入口） |
| `project.activate` | `foxos music-studio project activate` | 主界面 > Browser > Project | — | 点击「Project」（treeitem） | 否（应用没有撤销入口） |
| `files.activate` | `foxos music-studio files activate` | 主界面 > Browser > My files | — | 点击「My files」（treeitem） | 否（应用没有撤销入口） |
| `music-studio-files.activate` | `foxos music-studio music-studio-files activate` | 主界面 > Browser > Music Studio files | — | 点击「Music Studio files」（treeitem） | 否（应用没有撤销入口） |
| `browse-another-folder.activate` | `foxos music-studio browse-another-folder activate` | 主界面 > Browser > Browse another folder... | — | 点击「Browse another folder...」（treeitem） | 否（应用没有撤销入口） |
| `audio-from-device.import` | `foxos music-studio audio-from-device import` | 主界面 > Browser > Import audio from this device... | — | 点击「Import audio from this device...」（treeitem） | 否（应用没有撤销入口） |
| `device.activate` | `foxos music-studio device activate` | 主界面 > Browser > This device | — | 点击「This device」（treeitem） | 否（应用没有撤销入口） |
| `browser.resize` | `foxos music-studio browser resize` | 主界面 > Resize browser | — | 点击「Resize browser」（separator） | 否（应用没有撤销入口） |
| `clip-sources.show` | `foxos music-studio clip-sources show` | 主界面 > Show clip sources | — | 点击「Show clip sources」（button），切换到该视图 | 不适用（只读） |
| `tool.draw` | `foxos music-studio tool draw` | 主界面 > Draw tool | — | 点击「Draw tool」（button） | 否（应用没有撤销入口） |
| `paint-tool.activate` | `foxos music-studio paint-tool activate` | 主界面 > Paint tool | — | 点击「Paint tool」（button） | 否（应用没有撤销入口） |
| `tool.delete` | `foxos music-studio tool delete` | 主界面 > Delete tool | — | 点击「Delete tool」（button） | 否（应用没有撤销入口） |
| `mute-tool.activate` | `foxos music-studio mute-tool activate` | 主界面 > Mute tool | — | 点击「Mute tool」（button） | 否（应用没有撤销入口） |
| `slice-tool.activate` | `foxos music-studio slice-tool activate` | 主界面 > Slice tool | — | 点击「Slice tool」（button） | 否（应用没有撤销入口） |
| `tool.select` | `foxos music-studio tool select` | 主界面 > Select tool | — | 点击「Select tool」（button） | 不适用（只读） |
| `view.zoom-tool` | `foxos music-studio view zoom-tool` | 主界面 > Zoom tool | — | 点击「Zoom tool」（button） | 否（应用没有撤销入口） |
| `playback-tool.activate` | `foxos music-studio playback-tool activate` | 主界面 > Playback tool | — | 点击「Playback tool」（button） | 否（应用没有撤销入口） |
| `snap.set` | `foxos music-studio snap set` | 主界面 > Snap | `value`（必填）, `submit` | 把「Snap」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `follow-playhead.activate` | `foxos music-studio follow-playhead activate` | 主界面 > Follow playhead | — | 点击「Follow playhead」（button） | 否（应用没有撤销入口） |
| `follow-options.activate` | `foxos music-studio follow-options activate` | 主界面 > Follow options | — | 点击「Follow options」（button） | 否（应用没有撤销入口） |
| `view.zoom-out` | `foxos music-studio view zoom-out` | 主界面 > Zoom out | — | 点击「Zoom out」（button） | 否（应用没有撤销入口） |
| `view.zoom-` | `foxos music-studio view zoom-` | 主界面 > Zoom in | — | 点击「Zoom in」（button） | 否（应用没有撤销入口） |
| `view-2.zoom-` | `foxos music-studio view-2 zoom-` | 主界面 > Zoom to fit song | — | 点击「Zoom to fit song」（button） | 否（应用没有撤销入口） |
| `maximize-playlist.activate` | `foxos music-studio maximize-playlist activate` | 主界面 > Maximize Playlist | — | 点击「Maximize Playlist」（button） | 否（应用没有撤销入口） |
| `playlist.close` | `foxos music-studio playlist close` | 主界面 > Close Playlist | — | 点击「Close Playlist」（button） | 不适用（只读） |
| `automation-clip.create` | `foxos music-studio automation-clip create` | 主界面 > Add automation clip | — | 点击「Add automation clip」（button） | 否（应用没有撤销入口） |
| `clip-source-list.resize` | `foxos music-studio clip-source-list resize` | 主界面 > Resize clip source list | — | 点击「Resize clip source list」（separator） | 否（应用没有撤销入口） |
| `track.create` | `foxos music-studio track create` | 主界面 > Add track | — | 点击「Add track」（button） | 否（应用没有撤销入口） |
| `song-position.set` | `foxos music-studio song-position set` | 主界面 > Song position | `value`（必填）, `submit` | 把「Song position」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `mute-drums.activate` | `foxos music-studio mute-drums activate` | 主界面 > Mute Drums | — | 点击「Mute Drums」（button） | 否（应用没有撤销入口） |
| `solo-drums.activate` | `foxos music-studio solo-drums activate` | 主界面 > Solo Drums | — | 点击「Solo Drums」（button） | 否（应用没有撤销入口） |
| `mute-bass.activate` | `foxos music-studio mute-bass activate` | 主界面 > Mute Bass | — | 点击「Mute Bass」（button） | 否（应用没有撤销入口） |
| `solo-bass.activate` | `foxos music-studio solo-bass activate` | 主界面 > Solo Bass | — | 点击「Solo Bass」（button） | 否（应用没有撤销入口） |
| `mute-chords.activate` | `foxos music-studio mute-chords activate` | 主界面 > Mute Chords | — | 点击「Mute Chords」（button） | 否（应用没有撤销入口） |
| `solo-chords.activate` | `foxos music-studio solo-chords activate` | 主界面 > Solo Chords | — | 点击「Solo Chords」（button） | 否（应用没有撤销入口） |
| `mute-lead.activate` | `foxos music-studio mute-lead activate` | 主界面 > Mute Lead | — | 点击「Mute Lead」（button） | 否（应用没有撤销入口） |
| `solo-lead.activate` | `foxos music-studio solo-lead activate` | 主界面 > Solo Lead | — | 点击「Solo Lead」（button） | 否（应用没有撤销入口） |
| `playlist-arrangement.activate` | `foxos music-studio playlist-arrangement activate` | 主界面 > Playlist arrangement | — | 点击「Playlist arrangement」（application） | 否（应用没有撤销入口） |
| `editors.resize` | `foxos music-studio editors resize` | 主界面 > Resize editors | — | 点击「Resize editors」（separator） | 否（应用没有撤销入口） |
| `bar.delete` | `foxos music-studio bar delete` | 主界面 > Remove a bar | — | 点击「Remove a bar」（button） | 否（应用没有撤销入口） |
| `bar.create` | `foxos music-studio bar create` | 主界面 > Add a bar | — | 点击「Add a bar」（button） | 否（应用没有撤销入口） |
| `swing.set` | `foxos music-studio swing set` | 主界面 > Swing | `value`（必填）, `submit` | 把「Swing」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `velocity-lane.activate` | `foxos music-studio velocity-lane activate` | 主界面 > Velocity lane | — | 点击「Velocity lane」（button） | 否（应用没有撤销入口） |
| `channel.create` | `foxos music-studio channel create` | 主界面 > header > Add a channel | — | 点击「Add a channel」（button） | 否（应用没有撤销入口） |
| `maximize-channel-rack.activate` | `foxos music-studio maximize-channel-rack activate` | 主界面 > Maximize Channel rack | — | 点击「Maximize Channel rack」（button） | 否（应用没有撤销入口） |
| `channel-rack.close` | `foxos music-studio channel-rack close` | 主界面 > Close Channel rack | — | 点击「Close Channel rack」（button） | 不适用（只读） |
| `kick-3.select` | `foxos music-studio kick-3 select` | 主界面 > Select Kick | — | 点击「Select Kick」（button） | 不适用（只读） |
| `clap-3.select` | `foxos music-studio clap-3 select` | 主界面 > Select Clap | — | 点击「Select Clap」（button） | 不适用（只读） |
| `closed-hat-3.select` | `foxos music-studio closed-hat-3 select` | 主界面 > Select Closed Hat | — | 点击「Select Closed Hat」（button） | 不适用（只读） |
| `open-hat.select` | `foxos music-studio open-hat select` | 主界面 > Select Open Hat | — | 点击「Select Open Hat」（button） | 不适用（只读） |
| `bass-3.select` | `foxos music-studio bass-3 select` | 主界面 > Select Bass | — | 点击「Select Bass」（button） | 不适用（只读） |
| `chords-3.select` | `foxos music-studio chords-3 select` | 主界面 > Select Chords | — | 点击「Select Chords」（button） | 不适用（只读） |
| `lead-3.select` | `foxos music-studio lead-3 select` | 主界面 > Select Lead | — | 点击「Select Lead」（button） | 不适用（只读） |
| `channel-2.create` | `foxos music-studio channel-2 create` | 主界面 > main > Add a channel | — | 点击「Add a channel」（button） | 否（应用没有撤销入口） |
| `panels.resize` | `foxos music-studio panels resize` | 主界面 > Resize panels | — | 点击「Resize panels」（separator） | 否（应用没有撤销入口） |
| `mixer-insert.create` | `foxos music-studio mixer-insert create` | 主界面 > Add mixer insert | — | 点击「Add mixer insert」（button） | 否（应用没有撤销入口） |
| `effects-routing-panel.activate` | `foxos music-studio effects-routing-panel activate` | 主界面 > Effects and routing panel | — | 点击「Effects and routing panel」（button） | 否（应用没有撤销入口） |
| `maximize-mixer.activate` | `foxos music-studio maximize-mixer activate` | 主界面 > Maximize Mixer | — | 点击「Maximize Mixer」（button） | 否（应用没有撤销入口） |
| `mixer.close` | `foxos music-studio mixer close` | 主界面 > Close Mixer | — | 点击「Close Mixer」（button） | 不适用（只读） |
| `mute-master.activate` | `foxos music-studio mute-master activate` | 主界面 > Mute Master | — | 点击「Mute Master」（button） | 否（应用没有撤销入口） |
| `pan.set` | `foxos music-studio pan set` | 主界面 > Pan | `value`（必填）, `submit` | 把「Pan」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `width.set` | `foxos music-studio width set` | 主界面 > Width | `value`（必填）, `submit` | 把「Width」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `kick-volume.set` | `foxos music-studio kick-volume set` | 主界面 > Kick volume | `value`（必填）, `submit` | 把「Kick volume」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `mute-kick.activate` | `foxos music-studio mute-kick activate` | 主界面 > Mute Kick | — | 点击「Mute Kick」（button） | 否（应用没有撤销入口） |
| `solo-kick.activate` | `foxos music-studio solo-kick activate` | 主界面 > Solo Kick | — | 点击「Solo Kick」（button） | 否（应用没有撤销入口） |
| `mute-clap.activate` | `foxos music-studio mute-clap activate` | 主界面 > Mute Clap | — | 点击「Mute Clap」（button） | 否（应用没有撤销入口） |
| `solo-clap.activate` | `foxos music-studio solo-clap activate` | 主界面 > Solo Clap | — | 点击「Solo Clap」（button） | 否（应用没有撤销入口） |
| `mute-hats.activate` | `foxos music-studio mute-hats activate` | 主界面 > Mute Hats | — | 点击「Mute Hats」（button） | 否（应用没有撤销入口） |
| `solo-hats.activate` | `foxos music-studio solo-hats activate` | 主界面 > Solo Hats | — | 点击「Solo Hats」（button） | 否（应用没有撤销入口） |
| `options.create` | `foxos music-studio options create` | 主界面 > Insert options | — | 点击「Insert options」（button） | 否（应用没有撤销入口） |
| `insert.select` | `foxos music-studio insert select` | 主界面 > Sends > Select this insert | — | 点击「Select this insert」（button） | 不适用（只读） |
| `send-level-master.set` | `foxos music-studio send-level-master set` | 主界面 > Send level to Master | `value`（必填）, `submit` | 把「Send level to Master」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `send-master.delete` | `foxos music-studio send-master delete` | 主界面 > Remove send to Master | — | 点击「Remove send to Master」（button） | 否（应用没有撤销入口） |
| `send.create` | `foxos music-studio send create` | 主界面 > Routing > Add send | — | 点击「Add send」（button） | 否（应用没有撤销入口） |
| `channel-rack.select` | `foxos music-studio channel-rack select` | 主界面 > Channels > Select in the channel rack | — | 点击「Select in the channel rack」（button） | 不适用（只读） |
| `music-studio-is-open-source.show` | `foxos music-studio music-studio-is-open-source show` | 主界面 > contentinfo > Music Studio is open source | — | 点击「Music Studio is open source」（link），切换到该视图 | 不适用（只读） |
| `take-tour.activate` | `foxos music-studio take-tour activate` | 主界面 > status > Take the tour | — | 点击「Take the tour」（button） | 否（应用没有撤销入口） |
| `it.dismiss` | `foxos music-studio it dismiss` | 主界面 > status > Got it | — | 点击「Got it」（button） | 不适用（只读） |
| `pattern-beat-select-pattern-pattern.create` | `foxos music-studio pattern-beat-select-pattern-pattern create` | Pattern: Beat. Select pattern > Patterns > New pattern | — | 点击「New pattern」（menuitem） | 否（应用没有撤销入口） |
| `clone-pattern.activate` | `foxos music-studio clone-pattern activate` | Pattern: Beat. Select pattern > Patterns > Clone pattern | — | 点击「Clone pattern」（menuitem） | 否（应用没有撤销入口） |
| `signed-as-local.activate` | `foxos music-studio signed-as-local activate` | Account: local > Account > Signed in as local | — | 点击「Signed in as local」（menuitem） | 否（应用没有撤销入口） |
| `follow-options-follow-playhead.activate` | `foxos music-studio follow-options-follow-playhead activate` | Follow options > Follow options > Follow playhead | — | 点击「Follow playhead」（menuitemcheckbox） | 否（应用没有撤销入口） |
| `page-by-page.activate` | `foxos music-studio page-by-page activate` | Follow options > Follow options > Page by page | — | 点击「Page by page」（menuitemradio） | 否（应用没有撤销入口） |
| `continuous.activate` | `foxos music-studio continuous activate` | Follow options > Follow options > Continuous | — | 点击「Continuous」（menuitemradio） | 否（应用没有撤销入口） |
| `poly-synth.activate` | `foxos music-studio poly-synth activate` | Add a channel > Add channel > Poly Synth | — | 点击「Poly Synth」（menuitem） | 否（应用没有撤销入口） |
| `drum-synth.activate` | `foxos music-studio drum-synth activate` | Add a channel > Add channel > Drum Synth | — | 点击「Drum Synth」（menuitem） | 否（应用没有撤销入口） |
| `sampler.activate` | `foxos music-studio sampler activate` | Add a channel > Add channel > Sampler | — | 点击「Sampler」（menuitem） | 否（应用没有撤销入口） |
| `add-channel-synth-presets.activate` | `foxos music-studio add-channel-synth-presets activate` | Add a channel > Add channel > Synth presets | — | 点击「Synth presets」（menuitem） | 否（应用没有撤销入口） |
| `add-channel-drum-presets.activate` | `foxos music-studio add-channel-drum-presets activate` | Add a channel > Add channel > Drum presets | — | 点击「Drum presets」（menuitem） | 否（应用没有撤销入口） |
| `sampler-from-audio-file.activate` | `foxos music-studio sampler-from-audio-file activate` | Add a channel > Add channel > Sampler from audio file... | — | 点击「Sampler from audio file...」（menuitem） | 否（应用没有撤销入口） |
| `clap-volume.set` | `foxos music-studio clap-volume set` | Clap: click to select, double-click or Enter for the editor, right-click for options > Clap volume | `value`（必填）, `submit` | 把「Clap volume」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `hats-volume.set` | `foxos music-studio hats-volume set` | Open Hat: click to select, double-click or Enter for the editor, right-click for options > Hats volume | `value`（必填）, `submit` | 把「Hats volume」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `bass-volume.set` | `foxos music-studio bass-volume set` | Bass: click to select, double-click or Enter for the editor, right-click for options > Bass volume | `value`（必填）, `submit` | 把「Bass volume」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `chords-volume.set` | `foxos music-studio chords-volume set` | Chords: click to select, double-click or Enter for the editor, right-click for options > Chords volume | `value`（必填）, `submit` | 把「Chords volume」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `drag-reorder-ctrlup-down.activate` | `foxos music-studio drag-reorder-ctrlup-down activate` | Chords: click to select, double-click or Enter for the editor, right-click for options > Effect slots > Drag to reorder (Ctrl+Up/Down) | — | 点击「Drag to reorder (Ctrl+Up/Down)」（button） | 否（应用没有撤销入口） |
| `reverb.activate` | `foxos music-studio reverb activate` | Chords: click to select, double-click or Enter for the editor, right-click for options > Reverb on | — | 点击「Reverb on」（button） | 否（应用没有撤销入口） |
| `reverb-mix.set` | `foxos music-studio reverb-mix set` | Chords: click to select, double-click or Enter for the editor, right-click for options > Reverb mix | `value`（必填）, `submit` | 把「Reverb mix」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `reverb-options.activate` | `foxos music-studio reverb-options activate` | Chords: click to select, double-click or Enter for the editor, right-click for options > Reverb options | — | 点击「Reverb options」（button） | 否（应用没有撤销入口） |
| `lead-volume.set` | `foxos music-studio lead-volume set` | Lead: click to select, double-click or Enter for the editor, right-click for options > Lead volume | `value`（必填）, `submit` | 把「Lead volume」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `delay.activate` | `foxos music-studio delay activate` | Lead: click to select, double-click or Enter for the editor, right-click for options > Delay on | — | 点击「Delay on」（button） | 否（应用没有撤销入口） |
| `delay-mix.set` | `foxos music-studio delay-mix set` | Lead: click to select, double-click or Enter for the editor, right-click for options > Delay mix | `value`（必填）, `submit` | 把「Delay mix」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `delay-options.activate` | `foxos music-studio delay-options activate` | Lead: click to select, double-click or Enter for the editor, right-click for options > Delay options | — | 点击「Delay options」（button） | 否（应用没有撤销入口） |
| `shortcut.key-t` | `foxos music-studio shortcut key-t` | 键盘 mod+t | — | 在当前焦点上按 mod+t（src/dialogs/tools.js 中定义） | 否（应用没有撤销入口） |
