# plate-rotation/
> L2 | 父级: ~/.claude/skills/CLAUDE.md（如不存在则视 SKILL.md 为根契约）

A 股板块轮动 & 强势板块识别 skill。封装 4 个公开市场行情接口
(`getPlateRotatData` / `getPlateRotatChart` / `getLongByPlate` / `getPlateDayChart`),
在 4 个底层接口之上再封装 4 个高级 helper + CLI,
**让 Agent 一行命令出"今日 Top / 妖王榜 / 排名变化 / 板块强度"**。

## 成员清单

`SKILL.md`: skill 根契约 + Claude 加载时的 system prompt。
- 上半部分: **顶尖 A 股板块轮动分析师人格** (混合龙虎榜游资 + 学院分析师双视角) +
  核心方法论 (双源对照 / 转折信号优先 / 持续性 vs 当日爆发 / 产业链传导 / 真主线-伪主线-妖板-卫星四象限) +
  必守纪律 (硬约束工具规则, 13 条, 数据真实性 / 工具优先级 / 双源不可比 / 风险声明等) +
  分析输出风格 (事实表→关键解读→一句话总结→下一步建议) + 风险声明嵌入。
- 下半部分: 工具弹药库 (CLI 速查 / Python 用法 / 4 高级 helper / 底层接口 / 已知陷阱 / 文件清单)。
- frontmatter 触发关键词 (板块轮动 / 龙头股 / 板块强度 / F5G概念 / 算力 / 886084 / 801807 等)。

`README.md`: GitHub 访客导览。项目定位 + 安装 (clone / submodule) + 依赖 (Python 3.9+ stdlib only) +
触发关键词 + CLI 速查 demo + Python API + 项目结构 + 测试方法 + 重要声明 + License + 贡献指引。
**面向 GitHub 访客与首次使用者, 不是 Claude 自身**。

`CLAUDE.md`: 本文件, L2 模块地图。

`DISCLAIMER.md`: 数据使用免责 + 不构成投资建议 + 责任限制 + 频率建议 + 用户责任。
独立成页便于法律出面引用; SKILL.md 与 README.md 都引用本文件。**Claude 输出继承本声明**。

`LICENSE`: MIT License, Copyright (c) 2026 hssqz1998。

`references/`: 4 个 endpoint reference + 1 路由总表 + 1 领域事实手册。
- `_INDEX.md`: 4 接口路由 + 双源差异表 (ths 涨幅% / kaipan 强度分) + 板块代码前缀强语义 (88x 同花顺 / 80x 开盘啦) + days/dates 入参约定 + 指向 stock-facts.md。
- `stock-facts.md`: A 股 11 条领域惰性知识 (双源单位 / 前缀语义 / HTML in JSON / 当日无领涨语义 / 鉴权 / 交易日 / 涨跌停板规则 / T+1 / 数据延迟 / 复权 / 本 skill 不覆盖的相关常识)。从 SKILL.md 已知陷阱节抽离, 集中托管, 便于跨 stock skill 引用。
- `api_getplaterotatdata.md`: 主表 (HTML in JSON, response.first 字段是当日 Top1 板块代码)。
- `api_getplaterotatchart.md`: Top5 板块 N 日排名变化 ECharts (legend / date / name / 1..5 series, value=10.5+wu.png 表示当日未上榜)。
- `api_getlongbyplate.md`: 单板块龙头矩阵 (每天 5 个 div.kline, 平台返回 td 序列与 dates 对齐)。
- `api_getplatedaychart.md`: 单板块强度+量能 ECharts (legend=null 表示当日未活跃)。

`learned/`: 经验沉淀通道 (2026-05-12 新增)。每完成一个任务,把新发现追加到对应文件,
按 `### YYYY-MM-DD <标题>` + 现象/根因/应对/教训 格式书写。
- `_meta.md`: 跨源通用经验,目前种子条目 = 2026-05-09 parse_plate_long_heads td bug + 2026-05-12 fetch retry/cache 副作用清单。
- `ths.md`: 同花顺源专属 (`from=ths` 涨幅字段单位 / 仅认 88x 前缀板块)。
- `kaipan.md`: 开盘啦源专属 (`from=kaipan` 强度分单位 / 仅认 80x-803x 前缀 / 强度分 vs 涨幅% 哲学差异)。

`tests/`: 在线集成测试集 (stdlib unittest, 无第三方依赖)。
- `__init__.py`: 空, 让 unittest discover 能识别 tests 包。
- `test_plate_rotation.py`: 5 个 TestCase 共 31 个用例, 全部走真实在线接口验证。覆盖:
  - TestFetchEndpoints: 4 个底层 endpoint 健康度
  - TestParsers: 5 个 parsers helper 在真实 HTML in JSON 上的解析正确性 (双源 value_type 区分、dates 格式与排序、matrix 与 dates 对齐、kings 降序与 positions 格式)
  - TestHighLevelHelpers: 4 个高级 helper 签名 + 返回结构
  - TestSourceAutoPick: 88x→ths / 80x→kaipan 自动路由验证 (find_dragon_kings 关键设计)
  - TestCLI: 4 子命令 × text+json 双模 + 错误路径 (无子命令 / 非法 source)
  共享 `_Fixtures._cache` 跨 TestCase 缓存接口响应, 降低网络开销。
  运行: `python3 tests/test_plate_rotation.py` 或 `python3 -m unittest tests.test_plate_rotation -v`。

`scripts/`: 全 stdlib 实现, 无第三方依赖。
- `fetch.py`: 统一调用器, 保留 main+data+x+ext 全部 host alias。
  自动注入 Referer + cookie + UA + X-Requested-With, 三种参数姿势 (key=value / -p JSON / -X GET|POST)。
  **2026-05-12 升级**: 引入指数退避重试 (429/5xx/网络异常 1s/2s/4s, 最多 3 次, 4xx 直接抛) +
  落盘缓存层 (默认 1h TTL, `--no-cache` / `PR_CACHE_DISABLE=1` 关闭, `--cache-ttl SEC` 自定)。
  retry 与 cache 透明插入, 上游 platerotat.py 无需感知。
- `cache.py`: 本地缓存原子层 (2026-05-12 新增)。key = sha1(host+path+sorted_params),
  落盘 `~/.cache/plate-rotation/{key[:2]}/{key}.json`, 原子写 (tmp + os.replace) 防半写文件。
  对外 API: `cache_get` / `cache_put` / `cache_clear` / `cache_stats` / `cache_disabled`。
  自带 CLI: `cache.py stats | clear [--older SEC]`。环境变量 `PR_CACHE_DIR` / `PR_CACHE_TTL` 可调。
- `parsers.py`: 5 个板块轮动专用解析器。把 HTML in JSON 模板归纳为结构化 dict:
  - `parse_plate_rotat(data, source)`: 今日 Top N
  - `parse_plate_rotat_matrix(data, dates)`: N×天矩阵
  - `parse_plate_rotat_dates(data)`: 表头日期列
  - `parse_plate_long_heads(data, dates)`: 每天龙头清单
  - `rank_plate_long_persistence(data, dates, top_n)`: 跨天频次 (找妖王)
  自带 self-test 子命令 (plate_rotat_ths / plate_rotat_kaipan / plate_long_<code>)。
- `platerotat.py`: 4 个高级 helper + CLI 入口。底层调 fetch.py, 组合 parsers.py,
  对外暴露 `today_top / find_dragon_kings / top1_curve / plate_strength` 4 个高级函数,
  CLI 子命令 `today / wangking / curve / strength` 一一对应。
  `find_dragon_kings` 自动按 platecode 前缀 (88x→ths / 其他→kaipan) 选 source, Agent 不用关心。
  **2026-05-12 升级**: 每个 helper 解析完成后做运行时校验, 检测到空数据 / 跨源错传 / 节假日时
  通过 stderr 输出 `PR-EMPTY` / `PR-WARN` 标签, 帮助下游 Agent 与"凭印象编造"明确划清边界。
  `_hint_for_empty()` 内置周末判定 + 前缀-source 一致性检查, stdlib only, 不依赖交易日历。

## 架构原则

1. **Reference-first**: 调用前必读 `references/_INDEX.md` (双源差异 / 板块代码前缀语义)。
2. **三层 API 分级**: 用户面向 (CLI / Python helper) → 解析层 (parsers.py) → 调用层 (fetch.py)。每一层都可单独使用。
3. **No-mock 验证**: 4 个 reference 的 frontmatter 都标注 `last_verified` 日期, 样例数据来自真实响应。
4. **Stdlib only**: 无第三方依赖, 开箱即用。
5. **官方无承诺**: 上游接口未文档化, 可能随时变更或失效。失效时需重新归纳响应结构。
6. **裸调即可**: 后端只校验 Referer (fetch.py 已自动注入), 无需 cookie。

## 关键设计决策

### 为何 CLI 入口走 platerotat.py 而非 SKILL.md 里贴一堆 oneliner?
SKILL.md 是给 Agent / 人看的导览文档, **不应该承载逻辑**。把"自动按 platecode 选 source"
"CLI 输出格式化"等逻辑放进可执行文件, SKILL.md 只是引导。**逻辑与文档分离** 是 GEB 协议的精神。

### 为何 find_dragon_kings 内部自动判 source?
用户的真实意图是"我想知道这个板块谁是龙头", **他不应该被迫记住"88x 走 ths / 80x 走 kaipan"**。
让代码 own 这个 mapping, 用户只传 platecode 即可。这是消除特殊情况的"好品味"实践。

### 为何保留 fetch.py 的 4 个 host alias 而不只留 main?
未来可能需要扩展 (例如同板块的资金流向接口在不同子域), 保留 fetch.py 完整能力等于
保留向上扩展的"接口位"。删 30 行省不了多少, 但削掉了未来增量价值。

### 为何 cache TTL 默认 1 小时, 而不是"交易日级"?
"交易日级"听起来语义最准, 但 stdlib 无法知道当下是不是交易日 (没有 trade_cal 依赖)。
更重要的是: 盘中"今日"数据每分钟都在变, 锁到交易日级 = 上午 9:30 拉的数据下午 3:00 还在用,
误导分析师。1 小时是"够新鲜 + 够节流"的折衷; 极端实时场景显式 `--no-cache` 即可。
真正的不变量是: **任何"鲁棒性升级"都要明示新的失败模式**, 这条已在 learned/_meta.md 沉淀。

### 为何 PR-EMPTY / PR-WARN 走 stderr 而不抛异常?
抛异常会击穿整条分析流水线, 对"扫 5 个板块, 其中 1 个跨源错传"的场景过于激进 —
正确做法是其余 4 个继续分析, 错传那个明确告知 Agent "这条数据空, 自己判断". 用 stderr 标签
而非 exit code, 让上层既能监听又能选择性忽略, 与 retry 的"软失败"哲学保持一致。

## 关键修复历史

- **2026-05-09 (test driven fix)**: 编写在线集成测试集时, 捕捉到 `parse_plate_long_heads` 的真实 bug:
  服务端对"当日无领涨"的 td 用了 `text-align:center;color:#bbb;...` 样式 (闭合用 `</div>`,
  与有领涨 td 的 `text-align:left;padding-bottom:5px;` + `</td>` 不同),
  原正则只匹配后者, 导致**整段全无领涨的板块** (如近 20 日的 886084 F5G概念) 解析结果为空列表,
  违背了 "heads 长度 = dates 长度" 的不变量。修复: 正则同时匹配两种 style + 用 `(?=<td|$)`
  lookahead 兜底错位闭合。这是测试集替代了一次 code review 的典型案例。

- **2026-05-12 (stock-skill-design 体检后批量补强)**: 用元方法论体检自己的 skill, 发现
  上层卓越 (分析师人格 / 四象限 / 13 条必守纪律) 但下层薄 (fetch 只有 timeout 没有 retry,
  无缓存, 无领域事实独立文件, 无 learned/ 沉淀通道, 无 sub-agent 分发协议)。
  6 项补强一次性落地: ① fetch.py 加 retry + 429 backoff ② 新增 cache.py 1h TTL 落盘
  ③ 抽出 references/stock-facts.md 11 条领域事实 ④ 创建 learned/ 三件套 ⑤ platerotat.py
  四个 helper 加 PR-EMPTY / PR-WARN 运行时校验 ⑥ SKILL.md 增加扫多板块时的 sub-agent
  分发协议 (含污染用词对照表)。设计哲学: "上层卓越下层薄"的剖面最危险, 顶配人格遇脏数据
  会更自信地错 — 基础设施层必须与人格层同步顶配。

[PROTOCOL]: 变更时更新此头部, 然后检查 CLAUDE.md
