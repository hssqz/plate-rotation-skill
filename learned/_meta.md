# learned/_meta.md — 跨源经验沉淀

> 不属于单一数据源的通用经验。源专属经验放 `ths.md` / `kaipan.md`。

---

## 沉淀机制

每次完成一个 plate-rotation 任务,主动总结新发现追加到本文件。
格式: `### YYYY-MM-DD <一句话标题>` + 现象 / 根因 / 应对。
接口改版导致沉淀失效时,删除条目并更新 `references/stock-facts.md`。

---

## 2026-05-09 parse_plate_long_heads 对"全无领涨"板块的 bug

**现象**: 近 20 日 F5G 概念 (886084) 调 `getLongByPlate` 后 heads 列表完全为空,
违背 "heads 长度 = dates 长度" 的不变量。

**根因**: 服务端对"当日无领涨"的 td 用了
`text-align:center;color:#bbb;...` 样式 + `</div>` 闭合,
与有领涨 td 的 `text-align:left;padding-bottom:5px;` + `</td>` 不同。
原正则只匹配后者。

**应对**: 正则同时匹配两种 style + 用 `(?=<td|$)` lookahead 兜底错位闭合。
**这是测试集替代 code review 的典型案例** — 没有在线集成测试集,这个 bug 不可能被发现。

**教训**: 任何 parsers 改动后必须跑 `tests/test_plate_rotation.py`,
覆盖率不能只看正常路径,要包含"全空 / 部分空 / 跨日空"三档边界。

---

## 2026-05-12 fetch 层增加 retry + cache 后的副作用清单

**变更**: fetch.py 加入指数退避重试 (1s/2s/4s) + 1h 落盘缓存。

**新副作用**:
1. 同一参数请求 1 小时内的"今日"数据不会刷新 — 盘中实时分析要 `--no-cache`
2. 缓存路径 `~/.cache/plate-rotation/` 长期不清理会膨胀 — 跑 `python3 scripts/cache.py clear --older 604800` 定期清理
3. retry 在 4xx (除 429) 直接失败,不退避 — 与 5xx/429 区分是为了不浪费时间撞参数错误

**教训**: 任何"鲁棒性升级"都要明示新的失败模式,否则用户拿到旧数据会以为接口在骗他。

---

[PROTOCOL]: 变更时更新此头部,然后检查 CLAUDE.md
