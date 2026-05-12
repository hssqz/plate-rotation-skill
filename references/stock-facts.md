# stock-facts.md — A 股领域惰性知识手册

> 模型"知道"但任务中"想不起来"的 A 股事实清单。
> 调用任何 plate-rotation 接口前请先扫一遍。
> 摘自 stock-skill-design 元方法论第三节 + 本 skill 在生产环境踩过的坑。

---

## 一、接口层陷阱 (本 skill 高频)

### 1. 双源数值语义不同 — 不可直接比较

| from | 数值含义 | 单位示例 | 适用板块前缀 |
|---|---|---|---|
| `ths` (同花顺) | 当日**板块涨幅 %** | `4.94%` (带 `%`) | `88x` |
| `kaipan` (开盘啦) | 当日**板块强度分** | `15199` (纯整数) | `80x` / `803x` |

**铁律**: 两套数值各自排序,不能跨源说"A 比 B 强多少"。
**正则陷阱**: `[\d.\-]+%` 会漏开盘啦数据,parsers 已用 `[\d.\-]+%?` 兼容。

### 2. 板块代码前缀强语义 — 不可乱传

| 前缀 | 来源 | 例 |
|---|---|---|
| `88x` | 同花顺 | `886084` F5G概念 / `885998` 光纤概念 / `886033` 共封装光学 |
| `80x` / `803x` | 开盘啦 | `801807` 算力 / `801660` 通信 / `803023` AI 应用 |

`getLongByPlate` / `getPlateDayChart` 的 `platecode=` **不能跨源传**:
- 同花顺 88x 板块在开盘啦里查不到,反之亦然
- `find_dragon_kings()` 已内置自动判别 (`88x → ths` / 其他 → `kaipan`)
- **底层调 fetch.py 手动传 platecode 时必须自检**
- 运行时若跨源错传,`platerotat.py` 会通过 stderr 输出 `PR-EMPTY: 板块前缀 xxx 与 source=yyy 可能不匹配`

### 3. HTML in JSON — 用 parsers,不要重新逆向

`getPlateRotatData` / `getLongByPlate` 的 `html` 字段是 jQuery innerHTML 模板,
不是结构化 JSON。**走 `parsers.py`,不要重复正则逆向**。

### 4. 当日无领涨 = 合法返回值

- `getLongByPlate` 某天 td 文本可能是 `当日无领涨` 而非 `<div class='kline'>`
- parsers 已用双 style + lookahead 兜底解析
- 这意味该板块当时确实没活跃个股 → **直接告诉用户,不要把这当 bug**

### 5. `value=10.5 + symbol=wu.png` = 当日未上榜

- `getPlateRotatChart` 的 Top5 排名曲线里出现 `value=10.5` 必须解读为"空白"
- **不是排名 10.5 名**,不要参与排名平均
- 看 `top1_curve` 数据时眼睛盯断点,不要盯位次

### 6. 鉴权: 后端只校验 Referer

- fetch.py 已自动注入 `Referer: https://duanxianxia.com/web/main`
- **裸调即可,无需 cookie**
- 如服务端策略升级,优先读 `PR_COOKIE` 环境变量,其次 `~/.plate_rotation_cookie`

---

## 二、A 股领域通用事实 (跨 skill 共享)

### 7. 交易日 ≠ 自然日

- 节假日 / 周末 / 临时休市 → 接口返回**上一交易日**数据,不抛错
- 周末调"今日 Top 板块"会拿到上周五的快照
- 本 skill 在周末时会输出 `PR-EMPTY: 今天是周末` 提示
- 真要查交易日,看 tushare `trade_cal` 接口 (本 skill 不依赖,故未集成)

### 8. 涨跌停板规则 (板块龙头分析时常用)

| 板块 | 涨停幅度 | 备注 |
|---|---|---|
| 主板 | ±10% | 上证 60 / 深圳 00 |
| 创业板 | ±20% | 30 开头 |
| 科创板 | ±20% | 688 开头 |
| 北交所 | ±30% | 8 开头 (注意与同花顺板块代码 88x 区别) |
| ST 股 | ±5% | *ST 一样 |
| 新股 | 上市首日不设涨跌幅,N+1 起 ±20% (主板)/30% (北交) |

判断龙头股是否"封板/烂板"时,涨幅一定要对照本规则,不能一律用 ±10%。

### 9. T+1 结算 — 板块切换分析的隐藏维度

- 当日买入次日才能卖,资金 T+1 到账
- 影响"板块龙头进出"类计算: 今天的龙头是昨天买入的资金 → 看龙头变化时窗口要前移 1 天
- 跨板块轮动节奏判断时,真正的资金切换信号比表象延后 1 天

### 10. 数据延迟语义

- "实时" API 通常 **3 秒 ~ 1 分钟** 延迟
- 真正 tick 级要 L2 行情 (本 skill 不提供)
- 本 skill 的 4 个接口属于**日级 / 多日级聚合**,盘中刷新粒度 ≈ 5 分钟
- 缓存 TTL 默认 1 小时,盘中需要分钟级实时请用 `--no-cache` 或 `--cache-ttl 60`

### 11. 复权语义 (板块层面不涉及,但子板块的成分股要注意)

- 板块涨幅是成分股的市值加权,通常**不复权**
- 单看个股 K 线时:不复权看真实价,前复权看趋势,后复权算收益率
- 三者结论可能不同,讲数据时必须标注复权方式

---

## 三、本 skill 不覆盖的相关常识

避免下游 Agent 误用 plate-rotation 解决以下问题:

| 问题 | 该用什么 |
|---|---|
| 涨停股池 / 炸板池 | duanxianxia / xuangutong / tushare `limit_list` |
| 个股 K 线 | tushare `daily` / `pro_bar` |
| 财务三表 | tushare `income` / `balancesheet` / `cashflow` |
| 主力资金流向 | tushare `moneyflow_*` |
| 龙虎榜 | tushare `top_list` / duanxianxia 龙虎 |
| 实时 WebSocket 推送 | xuangutong 实时频道 |

---

[PROTOCOL]: 变更时更新此头部,然后检查 CLAUDE.md
