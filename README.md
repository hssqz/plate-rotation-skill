# plate-rotation

**A 股板块轮动 & 强势板块识别 — Claude Code Skill**

A 股板块轮动数据接口的封装工具集, 配套一个**顶尖 A 股板块轮动分析师**人格, 让 Claude / Claude Code 加载后能直接用游资 + 学院双视角做轮动分析。一行命令出结论。

---

## 这个 skill 能做什么

- **今日 Top N 板块** — 双源对照 (开盘啦持续强度 vs 同花顺当日涨幅)
- **板块妖王榜** — 跨 N 天龙头持续性排名, 找真核心 / 接力者 / 妖股
- **Top5 板块 N 日排名变化** — 看赛道切换的转折信号
- **单板块强度+量能时序** — 板块自身的健康度曲线

加载到 Claude / Claude Code 后, 直接用自然语言提问即可, 例如:
- "今天最强板块前 10"
- "算力板块这 20 天谁是真龙头?"
- "Top5 板块这 20 天的排名变化趋势"
- "通信和芯片现在谁在接棒?"

---

## 安装

### 方式 1: 直接 clone 到 Claude skills 目录

```bash
git clone https://github.com/hssqz1998/plate-rotation.git \
  ~/.claude/skills/plate-rotation
```

### 方式 2: git submodule (项目内)

```bash
cd <your-project>
git submodule add https://github.com/hssqz1998/plate-rotation.git \
  .claude/skills/plate-rotation
```

### 验证安装

```bash
python3 ~/.claude/skills/plate-rotation/scripts/platerotat.py today --n 5
```

看到当日 Top5 板块表格即安装成功。

---

## 依赖

- **Python 3.9+** (使用 `dict[str]` / `list[dict]` PEP 585 语法)
- **stdlib only** — 无第三方依赖, 不需要 pip install
- **网络** — 能访问公网 (国内直连即可, 无需 cookie 配置)

---

## 触发方式

skill 安装后, Claude / Claude Code 会根据用户消息**自动触发**, 当出现以下关键词时:

> 板块轮动 / 强势板块 / 龙头股 / 板块强度 / Top 板块 / 妖王 / 龙一 / 龙二 / 领涨股 / 板块切换 / 轮动节奏 / 概念板块走势 / F5G概念 / 算力 / CPO / PCB / 886084 / 801807 / getPlateRotatData / getLongByPlate

也可以手动让 Claude 加载: 直接说"用 plate-rotation skill"。

---

## CLI 速查

```bash
SKILL=~/.claude/skills/plate-rotation
PR=$SKILL/scripts/platerotat.py

# 今日 Top10 (开盘啦强度分)
python3 $PR today

# 切同花顺源
python3 $PR today --source ths

# 板块妖王榜 (该板块过去 20 天谁最常当龙头)
python3 $PR wangking 801807

# Top5 板块 20 日排名变化
python3 $PR curve --source kaipan --days 20

# 单板块强度+量能 ECharts JSON
python3 $PR strength 886084 --json
```

子命令全部支持 `--days 10|20|30|50` 和 `--json`。

---

## Python API

```python
import sys
sys.path.insert(0, '/path/to/plate-rotation/scripts')
from platerotat import today_top, find_dragon_kings, top1_curve, plate_strength

today_top(source='kaipan', n=10)                          # 今日 Top10
find_dragon_kings(platecode='801807', days=20, top_n=10)  # 妖王榜
top1_curve(source='kaipan', days=20)                      # Top5 排名曲线
plate_strength(platecode='801807', days=20)               # 板块强度时序
```

---

## 项目结构

```
plate-rotation/
├── SKILL.md           人格 + 方法论 + 工具弹药 (Claude 加载时读这个)
├── CLAUDE.md          L2 模块地图 (GEB 文档协议)
├── README.md          本文件
├── DISCLAIMER.md      数据使用免责 + 不构成投资建议
├── LICENSE            MIT
├── references/        4 接口规格 + 路由表
│   ├── _INDEX.md
│   ├── api_getplaterotatdata.md
│   ├── api_getplaterotatchart.md
│   ├── api_getlongbyplate.md
│   └── api_getplatedaychart.md
├── scripts/
│   ├── fetch.py        统一调用器 (3 host alias + 自动 Referer)
│   ├── parsers.py      5 个 HTML→dict 解析器
│   └── platerotat.py   4 个高级 helper + CLI
└── tests/              在线集成测试 (stdlib unittest)
    └── test_plate_rotation.py
```

---

## 测试

```bash
cd ~/.claude/skills/plate-rotation
python3 -m unittest tests.test_plate_rotation -v
```

走真实接口验证 5 个 TestCase 共 31 个用例 (覆盖底层接口 / parsers / 高级 helper / 自动路由 / CLI)。

---

## 重要声明

**数据来自第三方公开市场行情接口**, 接口稳定性由上游决定, 不做承诺。

**所有数据与分析仅供复盘与研究, 不构成任何投资建议。** 用户基于本工具做出的交易决策由用户自行承担盈亏责任。

详见 [DISCLAIMER.md](DISCLAIMER.md)。

---

## License

[MIT](LICENSE) © 2026 hssqz1998

---

## 贡献

欢迎 issue / PR:
- 接口失效 / 数据异常 → 提供 `fetch.py -v` 输出 + 期望值
- 新增分析维度 (例: 资金流向 / 北向持仓) → 先在 issue 讨论范围
- 文档/typo 修复 → 直接 PR

不接受:
- 任何引入第三方依赖的改动 (stdlib only 原则)
- 加密接口的逆向 (合规底线)
- 高频压测 / 反爬绕过相关 PR

---

