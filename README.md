<div align="center">

# plate-rotation

### A 股板块轮动分析师 · Claude Code Skill

**双源对照 · 妖王识别 · 转折信号 · 终端风格**

[![Claude Code](https://img.shields.io/badge/Claude_Code-Skill-C53030?style=for-the-badge&logo=anthropic&logoColor=white)](https://docs.claude.com/en/docs/claude-code/overview)
[![Python](https://img.shields.io/badge/Python-3.9+-15803D?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Dependencies](https://img.shields.io/badge/Deps-stdlib_only-EAB308?style=for-the-badge)](https://docs.python.org/3/library/)
[![License](https://img.shields.io/badge/License-MIT-0F172A?style=for-the-badge)](LICENSE)
[![Market](https://img.shields.io/badge/Market-A--Share-DC2626?style=for-the-badge)](#)
[![Style](https://img.shields.io/badge/Style-Wind_Terminal-EAB308?style=for-the-badge&logo=tradingview&logoColor=black)](#)

</div>

```text
╔══════════════════════════════════════════════════════════════════╗
║   PLATE ROTATION TERMINAL  ·  双源对照  ·  v1.0                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║   [+] 算力        +5.23%   ████████░░   ▲  LEAD     · 真主线    ║
║   [+] F5G概念     +3.87%   ██████░░░░   ▲  HOT      · 妖板      ║
║   [-] 光纤        -1.42%   ███░░░░░░░   ▼  COLD     · 退潮      ║
║   [+] 通信        +2.15%   █████░░░░░   ▲  ACTIVE   · 接棒      ║
║   [-] 芯片        -0.83%   ████░░░░░░   ▼  FADING   · 让位      ║
║                                                                  ║
║   SRC: 同花顺(THS) × 开盘啦(KAIPAN)  ·  CROSS-VALIDATED          ║
╚══════════════════════════════════════════════════════════════════╝
```

> **一行命令出结论** — 把 4 个公开行情接口封装成 4 个高级 helper + 1 个 CLI, 配套一个**顶尖板块轮动分析师人格** (龙虎榜游资盘感 + 学院派结构框架双视角), 让 Claude / Claude Code 加载后用自然语言就能完成"今日 Top / 妖王榜 / 排名变化 / 板块强度"四件套。

---

## Quick Start · 60 秒上手

### ◉ Step 1 — Install

```bash
# ── 方式 A · 推荐 ── npx skills (兼容 40+ AI agent) ────────────
npx skills add hssqz/plate-rotation-skill

# ── 方式 B ── 直接 clone 到 Claude skills 目录 ─────────────────
git clone https://github.com/hssqz/plate-rotation-skill.git \
  ~/.claude/skills/plate-rotation
```

### ◉ Step 2 — Verify

```bash
python3 ~/.claude/skills/plate-rotation/scripts/platerotat.py today --n 5
```

看到类似下方的当日 Top5 板块表格即安装成功:

```text
┌───────┬──────────────────┬─────────┬──────────────┐
│  RANK │  CODE   NAME     │  VALUE  │  TYPE        │
├───────┼──────────────────┼─────────┼──────────────┤
│   #1  │  801807 算力     │  87.42  │  strength    │
│   #2  │  801660 通信     │  76.31  │  strength    │
│   #3  │  886084 F5G概念  │  68.55  │  strength    │
│   #4  │  803023 AI 应用  │  61.20  │  strength    │
│   #5  │  885998 光纤     │  54.83  │  strength    │
└───────┴──────────────────┴─────────┴──────────────┘
```

### ◉ Step 3 — Talk to Claude

打开 Claude Code, 直接问:

> 「**今天最强板块前 10**」<br>
> 「**算力这 20 天谁是真龙头?**」

skill 会自动加载, 分析师人格立即上岗。

### ◉ 依赖

| 项 | 要求 | 说明 |
|---|---|---|
| Python | `3.9+` | 用了 PEP 585 类型语法 (`dict[str]` / `list[dict]`) |
| 第三方包 | **无** | stdlib only, 不需要 `pip install` |
| 网络 | 公网直连 | 国内无需特殊配置, 后端只校验 Referer (已自动注入) |

---

## Capabilities · 能力四件套

<table align="center">
<tr>
<td align="center" width="25%">

### 今日 Top N
**`today_top()`**

双源对照排行榜<br>
THS 涨幅% / KAIPAN 强度

**看赛道当下**

</td>
<td align="center" width="25%">

### 妖王榜
**`find_dragon_kings()`**

跨 N 天龙头持续性<br>
找真核心 / 接力 / 妖股

**找真核心**

</td>
<td align="center" width="25%">

### 排名曲线
**`top1_curve()`**

Top5 板块 N 日轨迹<br>
看赛道切换断点

**抓转折信号**

</td>
<td align="center" width="25%">

### 板块强度
**`plate_strength()`**

单板块强度+量能时序<br>
ECharts 数据流

**看板块健康**

</td>
</tr>
</table>

```text
─── 方法论核心 ─────────────────────────────────────────────────────
  KAIPAN  →  "这条赛道还在不在跑"   (强度分 = 持续性)
  THS     →  "今天谁在爆发"          (涨幅% = 当日资金集中度)
  双源同时上榜 = 真主线  ·  仅 KAIPAN = 退潮中  ·  仅 THS = 偶发热点
─────────────────────────────────────────────────────────────────────
```

加载到 Claude / Claude Code 后, 直接用自然语言就能调度上面四件套:

> 「今天最强板块前 10」<br>
> 「算力板块这 20 天谁是真龙头?」<br>
> 「Top5 板块这 20 天的排名变化趋势」<br>
> 「通信和芯片现在谁在接棒?」

---

## Live Data · 拿到的数据形态

skill 直接对接 **同花顺 (THS) + 开盘啦 (KAIPAN)** 双源板块轮动接口,
**裸调即可** (后端只校验 Referer, fetch.py 已自动注入)。
一行命令就能拉到下面这种粒度的原始数据:

### 1. 双源 N 日板块排名矩阵

<div align="center">

<table>
<thead>
<tr>
  <th rowspan="2" align="center">排名</th>
  <th colspan="3" align="center">开盘啦 (KAIPAN) · 强度分</th>
  <th colspan="3" align="center">同花顺 (THS) · 涨幅%</th>
</tr>
<tr>
  <th align="center">05-06</th>
  <th align="center">05-07</th>
  <th align="center">05-08</th>
  <th align="center">05-06</th>
  <th align="center">05-07</th>
  <th align="center">05-08</th>
</tr>
</thead>
<tbody>
<tr>
  <td align="center"><b>#1</b></td>
  <td align="center">算力<br><sub>21132</sub></td>
  <td align="center">算力<br><sub>15199</sub></td>
  <td align="center">机器人<br><sub>16304</sub></td>
  <td align="center">芯片<br><sub>+5.2%</sub></td>
  <td align="center">通信<br><sub>+4.8%</sub></td>
  <td align="center">机器人<br><sub>+6.3%</sub></td>
</tr>
<tr>
  <td align="center"><b>#2</b></td>
  <td align="center">芯片<br><sub>20799</sub></td>
  <td align="center">通信<br><sub>14020</sub></td>
  <td align="center">通信<br><sub>9084</sub></td>
  <td align="center">算力<br><sub>+4.1%</sub></td>
  <td align="center">芯片<br><sub>+3.5%</sub></td>
  <td align="center">通信<br><sub>+3.9%</sub></td>
</tr>
<tr>
  <td align="center"><b>#3</b></td>
  <td align="center">一季报增长<br><sub>17808</sub></td>
  <td align="center">机器人<br><sub>11635</sub></td>
  <td align="center">商业航天<br><sub>7296</sub></td>
  <td align="center">机器人<br><sub>+3.8%</sub></td>
  <td align="center">商业航天<br><sub>+2.9%</sub></td>
  <td align="center">商业航天<br><sub>+2.4%</sub></td>
</tr>
<tr>
  <td align="center"><b>#4</b></td>
  <td align="center">通信<br><sub>8950</sub></td>
  <td align="center">芯片<br><sub>10732</sub></td>
  <td align="center">ST板块<br><sub>7096</sub></td>
  <td align="center">一季报增长<br><sub>+3.2%</sub></td>
  <td align="center">机器人<br><sub>+2.7%</sub></td>
  <td align="center">芯片<br><sub>+2.1%</sub></td>
</tr>
<tr>
  <td align="center"><b>#5</b></td>
  <td align="center">ST板块<br><sub>5838</sub></td>
  <td align="center">ST板块<br><sub>6673</sub></td>
  <td align="center">算力<br><sub>6217</sub></td>
  <td align="center">通信<br><sub>+2.8%</sub></td>
  <td align="center">一季报增长<br><sub>+2.5%</sub></td>
  <td align="center">ST板块<br><sub>+1.9%</sub></td>
</tr>
</tbody>
</table>

</div>

> 同一天双源对照看: **双源同时上榜 = 真主线** · **仅 KAIPAN = 老热点退潮中** · **仅 THS = 偶发热点**

### 2. 单板块强度时序 + 量能 (近 5 日)

```text
板块强度  (开盘啦 KAIPAN · getPlateDayChart)

   1500 │
   1000 │                                       ●  1032
    500 │                  ●  960
        │
      0 ┼─────────────────────────────────────────────────
        │
   -500 │  ●  -660
        │
  -1000 │                              ●  -1203
        │
  -1500 │              ●  -1472
        └─────────────────────────────────────────────────
            04-21    04-22    04-23    04-24    04-25


板块量能  (亿元)

   8000 │  ████  8120
   7500 │  ████        ████  7614
   7000 │  ████        ████        ████  7733
   6500 │  ████        ████        ████
   6000 │  ████        ████        ████        ████  6443        ████  6071
        └────────────────────────────────────────────────────────────────
            04-21        04-22        04-23        04-24        04-25
```

> 完整数据为 **ECharts JSON** 格式, 直接喂给前端 ECharts / Highcharts 即可绘制双轴图。

### 3. Top 板块 N 日排名变化 (近 20 日)

<div align="center">

| 板块 | 04-14 | 04-17 | 04-21 | 04-25 | 04-29 | 05-05 | 05-08 | 上榜次数 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **芯片** | #3 | #7 | #4 | — | #3 | #2 | #9 | `20` |
| **算力** | #1 | #3 | #2 | #6 | #5 | #1 | #5 | `19` |
| **一季报增长** | — | #3 | #3 | — | #1 | #6 | #6 | `17` |
| **通信** | #5 | #2 | #2 | #4 | #4 | #4 | #2 | `15` |

</div>

> 看 4 条曲线**哪条在升、哪条在降, 资金切换信号一目了然**。`—` 表示当日未上榜 (服务端用 `value=10.5 + symbol=wu.png` 标记, parsers 已处理为可读形态)。

---

## 触发关键词 · Trigger Keywords

skill 会在 Claude / Claude Code 检测到下列关键词时**自动加载**:

<div align="center">

![板块轮动](https://img.shields.io/badge/板块轮动-C53030?style=flat-square)
![强势板块](https://img.shields.io/badge/强势板块-C53030?style=flat-square)
![龙头股](https://img.shields.io/badge/龙头股-C53030?style=flat-square)
![妖王](https://img.shields.io/badge/妖王-C53030?style=flat-square)
![龙一龙二](https://img.shields.io/badge/龙一龙二-C53030?style=flat-square)
![领涨股](https://img.shields.io/badge/领涨股-C53030?style=flat-square)
![Top板块](https://img.shields.io/badge/Top板块-DC2626?style=flat-square)

![板块强度](https://img.shields.io/badge/板块强度-15803D?style=flat-square)
![板块切换](https://img.shields.io/badge/板块切换-15803D?style=flat-square)
![轮动节奏](https://img.shields.io/badge/轮动节奏-15803D?style=flat-square)
![热点板块](https://img.shields.io/badge/热点板块-15803D?style=flat-square)
![板块代码](https://img.shields.io/badge/板块代码-15803D?style=flat-square)

![算力](https://img.shields.io/badge/算力-EAB308?style=flat-square&labelColor=0F172A)
![CPO](https://img.shields.io/badge/CPO-EAB308?style=flat-square&labelColor=0F172A)
![PCB](https://img.shields.io/badge/PCB-EAB308?style=flat-square&labelColor=0F172A)
![F5G概念](https://img.shields.io/badge/F5G概念-EAB308?style=flat-square&labelColor=0F172A)
![886084](https://img.shields.io/badge/886084-EAB308?style=flat-square&labelColor=0F172A)
![801807](https://img.shields.io/badge/801807-EAB308?style=flat-square&labelColor=0F172A)

![getPlateRotatData](https://img.shields.io/badge/getPlateRotatData-0F172A?style=flat-square)
![getLongByPlate](https://img.shields.io/badge/getLongByPlate-0F172A?style=flat-square)

</div>

> 也可以**显式调用**: 直接在对话里说 `用 plate-rotation skill 看看 ...`

---

## 终端输出示例 · Terminal Output

> 以下为**示例数据** (illustrative), 用于展示输出风格。真实接口数据每日不同。

### ① CLI 原生输出

```text
$ python3 platerotat.py today --source kaipan --n 8
═══════════════════════════════════════════════════════════════════
  TODAY · KAIPAN STRENGTH RANKING                     8 sectors
═══════════════════════════════════════════════════════════════════
  #1   801807  算力          ▲  87.42   ████████░░   LEAD
  #2   801660  通信          ▲  76.31   ███████░░░   ACTIVE
  #3   886084  F5G概念       ▲  68.55   ██████░░░░   HOT
  #4   803023  AI 应用       ▲  61.20   █████░░░░░   ACTIVE
  #5   885998  光纤          ▲  54.83   █████░░░░░   ACTIVE
  #6   801580  机器人        ▼  42.10   ████░░░░░░   FADING
  #7   886037  减速器        ▲  39.85   ███░░░░░░░   COLD
  #8   885502  芯片          ▼  31.20   ███░░░░░░░   COLD
═══════════════════════════════════════════════════════════════════
```

### ② Claude 分析师人格叙述

> 你: 「今天最强板块前 8, 给我看下双源对照, 找妖板」

<table>
<tr><td>

**plate-rotation 分析师**

**事实层** (KAIPAN 强度 + THS 涨幅% 双源对照)

| 板块 | KAIPAN | THS | 形态 |
|---|---|---|---|
| 算力 (801807) | `#1` | `+5.23%` | ✓ 真主线 |
| 通信 (801660) | `#2` | `+2.15%` | ✓ 接棒 |
| F5G (886084) | `#3` | `+3.87%` | ✦ 妖板 |
| 芯片 (885502) | `#8` | `-0.83%` | ✗ 让位 |

**关键转折信号**

- **算力**连续 13 天稳居 Top3, 今日 #1 — 主线**没断**
- **F5G** 过去 10 天 7 天未上榜, 今日突然 #3 + 涨幅榜 #2 — **典型妖板形态** (一致性预期 + 流动性溢价)
- **芯片**从昨天 #4 掉到 #8, 资金切换信号弹 — 留意是否承接到通信
- 通信 #2 + F5G #3 + 光纤 #5 三层产业链共振, **健康轮动**

**一句话总结**: 今天的真相是 — **算力主线还在跑, 通信接棒, F5G 是细分妖板, 芯片让位**。

**下一步建议**:
```bash
python3 platerotat.py wangking 801807   # 看算力龙头持续性
python3 platerotat.py strength 886084   # 看 F5G 量能健康度
```

</td></tr>
</table>

---

## DISCLAIMER · 重要声明

```text
╔══════════════════════════════════════════════════════════════════╗
║  ⚠  RISK NOTICE  ·  请仔细阅读                                   ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  ▸ 数据来源: 第三方公开市场行情接口                              ║
║    接口稳定性由上游决定, 不做任何承诺                            ║
║                                                                  ║
║  ▸ 用途定位: 仅供复盘与量化研究                                  ║
║    本工具不构成任何投资建议                                      ║
║                                                                  ║
║  ▸ 责任归属: 用户基于本工具做出的交易决策                        ║
║    由用户自行承担盈亏责任                                        ║
║                                                                  ║
║  ▸ 合规底线: 不绕过任何加密接口 / 不做高频压测 / 不反爬          ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

完整声明详见 [`DISCLAIMER.md`](DISCLAIMER.md)。

---

## License & Contributing

<table>
<tr>
<td width="50%" valign="top">

### License

[MIT](LICENSE) © 2026 [@hssqz1998](https://github.com/hssqz)

可商用 · 可修改 · 可再分发<br>
保留版权与许可证声明即可。

</td>
<td width="50%" valign="top">

### Contributing

**欢迎提 issue / PR**:
- 接口失效 / 数据异常 → 附 `fetch.py -v` 输出
- 新增分析维度 → 先在 issue 讨论范围
- 文档/typo → 直接 PR

**不接受**:
- 任何引入第三方依赖的改动 (stdlib only 原则)
- 加密接口逆向 / 高频压测 / 反爬绕过

</td>
</tr>
</table>

---

<div align="center">

**by [@hssqz1998](https://github.com/hssqz1998)** · A-share rhythm only

```text
─────  双源对照 · 妖王识别 · 转折信号  ─────
  the map IS the terrain · GEB protocol
─────────────────────────────────────────────
```

[![Stars](https://img.shields.io/github/stars/hssqz/plate-rotation-skill?style=social)](https://github.com/hssqz/plate-rotation-skill)
[![Issues](https://img.shields.io/github/issues/hssqz/plate-rotation-skill?color=DC2626)](https://github.com/hssqz/plate-rotation-skill/issues)
[![Last Commit](https://img.shields.io/github/last-commit/hssqz/plate-rotation-skill?color=15803D)](https://github.com/hssqz/plate-rotation-skill/commits)

</div>
