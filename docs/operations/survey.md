# Surveys（survey）操作清单

分组：productivity · 替代 SurveyMonkey, Google Forms, Typeform · 许可证 MIT · 页面标题「Surveys」

共 28 个操作，全部有语义命令（`foxos survey <资源> <动词>`，MCP 工具 `survey.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `folders.select` | `foxos survey folders select` | 主界面 > Folders > all # | `target`（必填） | 点击名称匹配的「all #」项（link） | 不适用（只读） |
| `describe-survey.select` | `foxos survey describe-survey select` | 主界面 > describe your survey for * | `target`（必填） | 点击名称匹配的「describe your survey for *」项（textbox） | 不适用（只读） |
| `content.dismiss` | `foxos survey content dismiss` | 主界面 > Skip to content | — | 点击「Skip to content」（link） | 不适用（只读） |
| `surveys-home.show` | `foxos survey surveys-home show` | 主界面 > Surveys home | — | 点击「Surveys home」（link），切换到该视图 | 不适用（只读） |
| `source-code-github-opens-tab.show` | `foxos survey source-code-github-opens-tab show` | 主界面 > Source code on GitHub (opens in a new tab) | — | 点击「Source code on GitHub (opens in a new tab)」（link），切换到该视图 | 不适用（只读） |
| `account-settings.activate` | `foxos survey account-settings activate` | 主界面 > Account and settings | — | 点击「Account and settings」（button） | 否（应用没有撤销入口） |
| `folder.create` | `foxos survey folder create` | 主界面 > New folder | — | 点击「New folder」（button） | 否（应用没有撤销入口） |
| `source-github.open` | `foxos survey source-github open` | 主界面 > Folders > Open source on GitHub | — | 点击「Open source on GitHub」（link） | 不适用（只读） |
| `powered-by-puter.show` | `foxos survey powered-by-puter show` | 主界面 > Folders > Powered by Puter | — | 点击「Powered by Puter」（link），切换到该视图 | 不适用（只读） |
| `survey.create` | `foxos survey survey create` | 主界面 > main > Create survey | — | 点击「Create survey」（button） | 否（应用没有撤销入口） |
| `from-scratcha-blank-survey.start` | `foxos survey from-scratcha-blank-survey start` | 主界面 > main > Start from scratchA blank survey | — | 点击「Start from scratchA blank survey」（button） | 否（应用没有撤销入口） |
| `use-templateready-made-fully-editable.activate` | `foxos survey use-templateready-made-fully-editable activate` | 主界面 > main > Use a templateReady-made, fully editable | — | 点击「Use a templateReady-made, fully editable」（button） | 否（应用没有撤销入口） |
| `questionspaste-list-or-open-file.import` | `foxos survey questionspaste-list-or-open-file import` | 主界面 > main > Import questionsPaste a list or open a file | — | 点击「Import questionsPaste a list or open a file」（button） | 否（应用没有撤销入口） |
| `generate.run` | `foxos survey generate run` | 主界面 > main > Generate | — | 点击「Generate」（button） | 否（应用没有撤销入口） |
| `search-surveys.set` | `foxos survey search-surveys set` | 主界面 > Search surveys | `value`（必填）, `submit` | 把「Search surveys」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `filter-by-status.set` | `foxos survey filter-by-status set` | 主界面 > Filter by status | `value`（必填）, `submit` | 把「Filter by status」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `sort-by.set` | `foxos survey sort-by set` | 主界面 > Sort by | `value`（必填）, `submit` | 把「Sort by」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `survey-2.create` | `foxos survey survey-2 create` | 主界面 > main > Create a survey | — | 点击「Create a survey」（button） | 否（应用没有撤销入口） |
| `it.dismiss` | `foxos survey it dismiss` | 主界面 > Got it | — | 点击「Got it」（button） | 不适用（只读） |
| `system.activate` | `foxos survey system activate` | Account and settings > Account > System | — | 点击「System」（menuitemradio） | 否（应用没有撤销入口） |
| `light.activate` | `foxos survey light activate` | Account and settings > Account > Light | — | 点击「Light」（menuitemradio） | 否（应用没有撤销入口） |
| `dark.activate` | `foxos survey dark activate` | Account and settings > Account > Dark | — | 点击「Dark」（menuitemradio） | 否（应用没有撤销入口） |
| `keyboard-shortcuts.activate` | `foxos survey keyboard-shortcuts activate` | Account and settings > Account > Keyboard shortcuts? | — | 点击「Keyboard shortcuts?」（menuitem） | 否（应用没有撤销入口） |
| `surveys.show` | `foxos survey surveys show` | Account and settings > Account > About Surveys | — | 点击「About Surveys」（menuitem），切换到该视图 | 不适用（只读） |
| `from-scratch.start` | `foxos survey from-scratch start` | Create survey > Create survey > Start from scratch | — | 点击「Start from scratch」（menuitem） | 否（应用没有撤销入口） |
| `use-template.activate` | `foxos survey use-template activate` | Create survey > Create survey > Use a template | — | 点击「Use a template」（menuitem） | 否（应用没有撤销入口） |
| `ai.run` | `foxos survey ai run` | Create survey > Create survey > Generate with AI | — | 点击「Generate with AI」（menuitem） | 否（应用没有撤销入口） |
| `questions.import` | `foxos survey questions import` | Create survey > Create survey > Import questions | — | 点击「Import questions」（menuitem） | 否（应用没有撤销入口） |
