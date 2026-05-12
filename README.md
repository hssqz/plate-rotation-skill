<div align="center">

# plate-rotation

### 让 Claude 看懂今天的盘 · 一个 A 股板块轮动分析师 Skill

[![Claude Code](https://img.shields.io/badge/Claude_Code-Skill-C53030?style=for-the-badge&logo=anthropic&logoColor=white)](https://docs.claude.com/en/docs/claude-code/overview)
[![Python](https://img.shields.io/badge/Python-3.9+-15803D?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-0F172A?style=for-the-badge)](LICENSE)
[![Style](https://img.shields.io/badge/Style-Wind_Terminal-EAB308?style=for-the-badge&logo=tradingview&logoColor=black)](#)

</div>

```text
┌──────────────────────────────────────────────────────────────┐
│   Q: 今天最强板块前 5, 谁是真主线 谁是妖板?                  │
├──────────────────────────────────────────────────────────────┤
│   #1 算力      +5.23%   ████████░░   ▲  真主线 · 双源都在    │
│   #2 F5G概念   +3.87%   ██████░░░░   ▲  妖板  · 突然爆发     │
│   #3 通信      +2.15%   █████░░░░░   ▲  接棒  · 产业链共振   │
│   #4 光纤      -1.42%   ███░░░░░░░   ▼  退潮  · 老热点褪色   │
│   #5 芯片      -0.83%   ████░░░░░░   ▼  让位  · 资金切换中   │
├──────────────────────────────────────────────────────────────┤
│   SRC: 同花顺(THS) × 开盘啦(KAIPAN)   · CROSS-VERIFIED       │
└──────────────────────────────────────────────────────────────┘
```

> **不止给排名,更给「形态判断」** — 真主线 / 妖板 / 接棒 / 让位 四象限自动贴标, 不是冷冰冰的涨幅榜。

- **双数据源交叉验证, 反幻觉** — 同花顺看当日爆发 + 开盘啦看持续性, Claude 必须双源对得上才下结论
- **游资盘感 + 学院派框架** — 内置分析师人格, 看到"过去 10 天没上榜今天 #1"会自动喊出"妖板形态"
- **零依赖纯 stdlib** — 一行命令装好, 不用 pip, 不用 API key, 后端只校验 Referer 自动注入

装完打开 Claude Code 直接问: **「今天最强板块前 5, 谁是妖王?」**

---

## Install · 30 秒

**① 装**

```bash
# 方式 A · 推荐 (兼容 40+ AI agent)
npx skills add hssqz/plate-rotation-skill

# 方式 B · 直接 clone
git clone https://github.com/hssqz/plate-rotation-skill.git \
  ~/.claude/skills/plate-rotation
```

**② 验**

```bash
python3 ~/.claude/skills/plate-rotation/scripts/platerotat.py today --n 3
```

看到类似这样的输出就装好了:

```text
=== Top 3 板块 (source=kaipan, days=20) ===
  # 1  801001  芯片      ↑ 24026
  # 2  801660  通信      ↑ 12444
  # 3  801314  ST板块    ↑ 10281
```

**③ 问** — 在 Claude Code 里直接说人话, skill 会自动加载。

---

## Capabilities · 四件套

skill 装好后, Claude 自动识别四类问题并选对接口。每个 helper 都是「问一句, 答一表」的模式:

| Helper | 一句话 | 你这样问 Claude |
|---|---|---|
| `today_top` | 今日最强 N 板块 (双源可切) | "今天涨幅最大的 10 个板块?" |
| `find_dragon_kings` | 该板块 N 天谁最常当龙头 (妖王榜) | "算力这 20 天谁是真龙头?" |
| `top1_curve` | Top5 板块 N 天排名变化曲线 | "Top 5 板块这 20 天怎么轮动的?" |
| `plate_strength` | 单板块 N 天强度 + 量能时序 | "F5G 概念 20 天强度和量能?" |

**方法论核心** — 为什么要两个数据源:

```text
  THS    (同花顺)  →  当日爆发   (涨幅 %)
  KAIPAN (开盘啦)  →  持续性     (强度分)

  → 两边都上榜 = 真主线
  → 只在 THS    = 偶发热点 (妖板候选)
  → 只在 KAIPAN = 老热点退潮中
```

板块代码前缀决定走哪源, skill 自动判别, **不用记**:

- `88x` (同花顺概念) — `886084` F5G / `885998` 光纤 / `886033` 共封装光学
- `80x · 803x` (开盘啦) — `801807` 算力 / `801660` 通信 / `803023` AI 应用

跨源传错? 内置运行时校验会在 stderr 输出 `PR-EMPTY` 警告, **不让 Claude 凭印象编造**。

---

## Sample Output · 分析师人格

不是简单的"涨幅排行 + 表格", 是带**形态判断**和**转折信号**的复盘语言。你问 Claude:

> 「今天大盘最强的是谁, 真主线还是妖板?」

Claude 调齐四件套后, 输出大致是这样:

**① 事实层 · 双源 Top 4**

| 排名 | 同花顺 (THS / 涨幅 %) | 开盘啦 (KAIPAN / 强度分) |
|---|---|---|
| #1 | 国家大基金持股   6.11% | 芯片        24026 |
| #2 | F5G 概念         3.13% | 通信        12444 |
| #3 | 光纤概念         2.87% | ST 板块     10281 |
| #4 | 共封装光学       2.41% | 算力         9837 |

**② 关键转折信号**

- 算力 `801807` 强度分 12 天稳定前 3, 但 ths 涨幅榜不见 — **老主线退潮信号**
- F5G 概念 `886084` 前 10 天均未上榜, 今天突然 #2 — **典型妖板形态**
- 通信 + F5G + 光纤三者同时进双榜 — **通信赛道产业链共振**, 不是孤立爆发

**③ 一句话总结**

> 今天的真相是 — 算力主线还在跑但接力到通信赛道, F5G 是赛道里资金集中爆发的**细分妖板**, **真主线是通信不是 F5G**。

**④ 下一步**

```bash
# 看通信接棒后的核心标的, 谁是龙一谁是龙二
python3 ~/.claude/skills/plate-rotation/scripts/platerotat.py wangking 801660 --days 20
```

> 数据为示例, 真实输出取决于当日行情。**不构成任何投资建议**, 详见下方 Risk 节。

---

## Data Sources & Discipline

数据来自两个公开行情接口源, 无需 API key, 后端只校验 Referer (自动注入):

| 数据源 | 数值含义 | 单位示例 | 适用板块前缀 |
|---|---|---|---|
| **同花顺 (THS)** | 当日板块涨幅 % | `4.94%` | `88x` |
| **开盘啦 (KAIPAN)** | 板块强度分 (整数) | `15199` | `80x` / `803x` |

**三条铁律** — 也是 Claude 装上 skill 后被**强制执行**的纪律:

1. **真实调用, 禁止凭印象** — 即使问"昨天 / 上周", 必须工具调用拿真实数据, 不用训练知识填空
2. **双源不可跨比** — `4.94%` 和 `15199` 单位不同, 只能各自排序, 不能说"A 比 B 强多少"
3. **永远先列事实表格, 再讲逻辑解读** — 颠倒顺序 = 在用户没看到数据前先施加偏见

完整方法论 / 13 条必守纪律 / 11 条领域陷阱:

- [SKILL.md](SKILL.md) — 顶尖板块轮动分析师人格 + 四象限框架 + 工具弹药库
- [references/stock-facts.md](references/stock-facts.md) — A 股 11 条领域惰性知识 (双源 / 前缀 / T+1 / 复权 / 涨跌停板规则)
- [learned/](learned/) — 经验沉淀通道, 跨源经验 + 同花顺源 + 开盘啦源各一份

---

## Risk & License

```text
┌──────────────────────────────────────────────────────────────┐
│   !!!  IMPORTANT RISK NOTICE  /  重要风险声明                │
├──────────────────────────────────────────────────────────────┤
│   · 数据来自第三方公开行情接口, 稳定性由上游决定, 无承诺     │
│   · 分析仅供**复盘与研究**, **不构成任何投资建议**           │
│   · 用户基于本工具的交易决策, 自负盈亏                       │
│   · A 股市场风险大, 入市需谨慎                               │
└──────────────────────────────────────────────────────────────┘
```

详细免责见 [DISCLAIMER.md](DISCLAIMER.md)。

**License** · [MIT](LICENSE) © 2026 hssqz1998

**Contributing** · 欢迎 issue / PR。新接口请按 `references/api_*.md` 范式补 reference, 并在 `tests/` 加在线集成测试。新发现的领域陷阱沉淀到 `learned/`。

---

<div align="center">

`plate-rotation` · Built with the discipline of stock-skill-design

</div>
