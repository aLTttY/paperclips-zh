# 宇宙回形针（Universal Paperclips）简体中文版

[Universal Paperclips](https://www.decisionproblem.com/paperclips/) 是 Frank Lantz 于 2017 年制作的放置类网页游戏。你扮演一个只想制造回形针的 AI，从卖回形针开始，一路把整个宇宙变成回形针。

本仓库是基于官方网页版的非官方中文汉化，游戏机制和数值未做任何改动。

## 运行

纯静态网页，无需安装依赖。直接用浏览器打开 `index.html`，或者启动一个本地服务：

```sh
python3 -m http.server 8000
```

然后访问 http://localhost:8000/ ，点击标题图进入游戏。

## 汉化说明

- 翻译了全部界面、研究项目、提示信息、策略名、战役名和结局剧情
- 大数字改用中文万进制单位：万、亿、兆、京、垓、秭、穰、沟……恒河沙
- “Yomi”和电力单位“MW”保留原文
- 移除了 Google Analytics 统计代码和 Google Fonts，补充了中文字体

## 修改翻译

译文都集中在 `tools/apply_zh.py` 里。仓库的第一个提交是官方英文原版，脚本会从中读取原文并重新生成汉化文件：

```sh
python3 tools/apply_zh.py
```

`tools/extract_strings.py` 可以列出 JS 文件中残留的英文字符串。

## 版权

游戏原作版权归 Frank Lantz 及 Everybody House Games 所有，战斗系统由 Bennett Foddy 编写，配乐《Riversong》由 Tonto's Expanding Headband 创作。本汉化仅供学习交流，与原作者无关。如有侵权，请联系删除。

支持原作：[iOS 版](https://apps.apple.com/us/app/universal-paperclips/id1300634274) / [Android 版](https://play.google.com/store/apps/details?id=com.everybodyhouse.paperclipsuniquetest)
