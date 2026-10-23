# Auto Next Deck

[English](README.md) | 简体中文

Anki 插件。学完一个牌组后，在「恭喜」页面按一个键即可进入下一个牌组，不必回到牌组列表手动选择。

## 功能

- 在「恭喜」页面按 <kbd>Space</kbd> 或 <kbd>Enter</kbd>，打开下一个有待学卡片的牌组。
- 不会自动跳转：只有按键后才会切换牌组。
- 支持通过 [Contanki](https://ankiweb.net/shared/info/1898790263) 使用游戏手柄。
- 无需配置，不添加额外界面。

## 安装

### AnkiWeb（推荐）

1. 在 Anki 中打开 **工具 → 插件 → 获取插件...**
2. 输入代码 `1855134110`。
3. 重启 Anki。

插件页面：<https://ankiweb.net/shared/info/1855134110>

### 从文件安装

1. 从 [最新 Release](https://github.com/DDowl51/anki-auto-next-deck/releases/latest) 下载 `Auto_Next_Deck-<版本号>.ankiaddon`。
2. 在 Anki 中打开 **工具 → 插件 → 从文件安装...**，选择下载的文件。
3. 重启 Anki。

### 从源码安装

将本仓库克隆到 Anki 插件目录，然后重启 Anki：

| 系统    | 插件目录                                        |
| ------- | ----------------------------------------------- |
| Windows | `%APPDATA%\Anki2\addons21\`                     |
| macOS   | `~/Library/Application Support/Anki2/addons21/` |
| Linux   | `~/.local/share/Anki2/addons21/`                |

```sh
cd ~/.local/share/Anki2/addons21
git clone https://github.com/DDowl51/anki-auto-next-deck.git
```

通过文件或源码安装时，如果已安装 AnkiWeb 版本，请先将其停用，避免两份同时运行。

## 使用

1. 正常学习一个牌组，直到出现「恭喜」页面。
2. 按 <kbd>Space</kbd>，进入下一个牌组的概览页。
3. 再按 <kbd>Space</kbd>，开始学习该牌组。

如果后面没有待学的牌组，<kbd>Space</kbd> 保持 Anki 的默认行为。

### 下一个牌组的确定规则

- 按牌组全名（如 `Parent::Child`）排序，不区分大小写。
- 从刚学完的牌组之后开始查找，不会回到开头。
- 跳过筛选牌组和没有待学卡片的牌组。

### 游戏手柄

使用 Contanki 时，在「恭喜」页面触发 **Select** 或 **Enter** 动作（默认配置中为 A 键），效果与 <kbd>Space</kbd> 相同。

暂不支持 Contanki 的 **Forward** 动作。

## 兼容性

- Anki 2.1.45 及以上，已在 Anki 26.09 上测试。
- 在牌组概览页，<kbd>Space</kbd> 和 <kbd>Enter</kbd> 由插件在 Qt 层处理，即使页面没有键盘焦点也能开始学习。其他在概览页绑定这两个键的插件可能与本插件冲突。

## 实现原理

- 通过 `gui_hooks.state_will_change` 检测从复习切换到概览页，记录刚学完的牌组。
- 通过 `gui_hooks.state_shortcuts_will_change` 注册 <kbd>Space</kbd> 和 <kbd>Enter</kbd>。按键时，只有当前牌组仍是刚学完的牌组才切换，否则开始学习。
- Contanki 向页面发送的是点击，而不是按键。插件在「恭喜」页面注入监听器，捕获落在 `<body>` 上的非用户触发点击（`isTrusted === false`），并通过 `pycmd` 交给同一处理逻辑。真实的鼠标点击不受影响。

## 更新日志

### 1.1.0

- 新增对 Contanki 手柄 Select / Enter 动作的支持。
- 修复：在「恭喜」页面通过其他方式（如 Contanki 的 Next Due Deck）切换牌组后，按 <kbd>Space</kbd> 会跳过该牌组，而不是开始学习。

### 1.0.0

- 首次发布。

## 许可证

[AGPL-3.0-only](LICENSE)
