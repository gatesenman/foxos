# Signatures（signatures）操作清单

分组：collaboration · 替代 DocuSign, Adobe Acrobat Sign, Dropbox Sign · 许可证 MIT (root LICENSE) · 页面标题「Signatures」

共 29 个操作，全部有语义命令（`foxos signatures <资源> <动词>`，MCP 工具 `signatures.<资源>.<动词>`）。绑定方式为 ui：命令在应用的真实界面上执行与人相同的点击 / 输入 / 按键，界面实时更新。

由 `python scripts/inventory_ops.py` 从运行中的应用生成，不要手工编辑。

| 操作 ID | CLI | 界面路径 / 快捷键 | 参数 | 效果 | 可撤销（推断） |
|---|---|---|---|---|---|
| `0out.select` | `foxos signatures 0out select` | 主界面 > main > 0out for * | `target`（必填） | 点击名称匹配的「0out for *」项（button） | 不适用（只读） |
| `0waiting.select` | `foxos signatures 0waiting select` | 主界面 > main > 0waiting for * | `target`（必填） | 点击名称匹配的「0waiting for *」项（button） | 不适用（只读） |
| `main.select` | `foxos signatures main select` | 主界面 > main > # | `target`（必填） | 点击名称匹配的「#」项（button） | 不适用（只读） |
| `out.select` | `foxos signatures out select` | 主界面 > Filter documents > out for * | `target`（必填） | 点击名称匹配的「out for *」项（button） | 不适用（只读） |
| `waiting.select` | `foxos signatures waiting select` | 主界面 > Filter documents > waiting for * | `target`（必填） | 点击名称匹配的「waiting for *」项（button） | 不适用（只读） |
| `skip.dismiss` | `foxos signatures skip dismiss` | 主界面 > Welcome > skip for * | `target`（必填） | 点击名称匹配的「skip for *」项（button） | 不适用（只读） |
| `signer-declinessigning-closes.select` | `foxos signatures signer-declinessigning-closes select` | Settings > main > a signer declinessigning closes for * | `target`（必填） | 点击名称匹配的「a signer declinessigning closes for *」项（checkbox） | 不适用（只读） |
| `signatures-githubsend-documents.select` | `foxos signatures signatures-githubsend-documents select` | Settings > main > signatures on githubsend documents for * | `target`（必填） | 点击名称匹配的「signatures on githubsend documents for *」项（link） | 不适用（只读） |
| `documents.show` | `foxos signatures documents show` | 主界面 > Main navigation > Documents | — | 点击「Documents」（link），切换到该视图 | 不适用（只读） |
| `settings.show` | `foxos signatures settings show` | 主界面 > Main navigation > Settings | — | 点击「Settings」（link），切换到该视图 | 不适用（只读） |
| `document.create` | `foxos signatures document create` | 主界面 > Main navigation > New document | — | 点击「New document」（button） | 否（应用没有撤销入口） |
| `document-2.create` | `foxos signatures document-2 create` | 主界面 > main > New document | — | 点击「New document」（button） | 否（应用没有撤销入口） |
| `search-documents.set` | `foxos signatures search-documents set` | 主界面 > Search documents | `value`（必填）, `submit` | 把「Search documents」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `drafts.activate` | `foxos signatures drafts activate` | 主界面 > Filter documents > Drafts | — | 点击「Drafts」（button） | 否（应用没有撤销入口） |
| `completed.activate` | `foxos signatures completed activate` | 主界面 > Filter documents > Completed | — | 点击「Completed」（button） | 否（应用没有撤销入口） |
| `closed.activate` | `foxos signatures closed activate` | 主界面 > Filter documents > Closed | — | 点击「Closed」（button） | 否（应用没有撤销入口） |
| `pdf.import` | `foxos signatures pdf import` | 主界面 > main > Upload a PDF | — | 点击「Upload a PDF」（button） | 否（应用没有撤销入口） |
| `close.close` | `foxos signatures close close` | 主界面 > Close | — | 点击「Close」（button） | 不适用（只读） |
| `set-up-account.activate` | `foxos signatures set-up-account activate` | 主界面 > Welcome > Set up my account | — | 点击「Set up my account」（button） | 否（应用没有撤销入口） |
| `explore-sample-documents.activate` | `foxos signatures explore-sample-documents activate` | 主界面 > Welcome > Explore with sample documents | — | 点击「Explore with sample documents」（button） | 否（应用没有撤销入口） |
| `name-shown-signers.set` | `foxos signatures name-shown-signers set` | Settings > main > Name shown to signers | `value`（必填）, `submit` | 把「Name shown to signers」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `system.activate` | `foxos signatures system activate` | Settings > Theme > System | — | 点击「System」（button） | 否（应用没有撤销入口） |
| `light.activate` | `foxos signatures light activate` | Settings > Theme > Light | — | 点击「Light」（button） | 否（应用没有撤销入口） |
| `dark.activate` | `foxos signatures dark activate` | Settings > Theme > Dark | — | 点击「Dark」（button） | 否（应用没有撤销入口） |
| `documents-expire.set` | `foxos signatures documents-expire set` | Settings > main > Documents expire | `value`（必填）, `submit` | 把「Documents expire」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `remind-signers.set` | `foxos signatures remind-signers set` | Settings > main > Remind signers | `value`（必填）, `submit` | 把「Remind signers」设为给定值（触发 input / change 事件） | 否（应用没有撤销入口） |
| `any-signer-signsone-email-per-signature.toggle` | `foxos signatures any-signer-signsone-email-per-signature toggle` | Settings > main > Any signer signsOne email per signature | — | 切换「Any signer signsOne email per signature」 | 否（应用没有撤销入口） |
| `signature.create` | `foxos signatures signature create` | Settings > main > Create signature | — | 点击「Create signature」（button） | 否（应用没有撤销入口） |
| `puteryour-documents-live-own-puter-cloud.show` | `foxos signatures puteryour-documents-live-own-puter-cloud show` | Settings > main > PuterYour documents live in your own Puter cloud | — | 点击「PuterYour documents live in your own Puter cloud」（link），切换到该视图 | 不适用（只读） |
