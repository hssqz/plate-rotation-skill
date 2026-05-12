# plate-rotation 路由表

板块轮动 4 接口。**全部 host=`main`**, 全部 POST, 后端只校验 Referer (fetch.py 已自动注入)。

| ID | Path | 用途 | 关键入参 |
|----|------|------|--------|
| ✅ [api_getplaterotatdata](api_getplaterotatdata.md) | `/api/getPlateRotatData` | 板块 N 日轮动主表 (HTML in JSON) | `from`, `days` |
| ✅ [api_getplaterotatchart](api_getplaterotatchart.md) | `/api/getPlateRotatChart` | Top5 板块 N 日排名变化 ECharts | `from`, `days` |
| ✅ [api_getlongbyplate](api_getlongbyplate.md) | `/api/getLongByPlate` | 单板块 N 日龙头股矩阵 | `platecode`, `days` |
| ✅ [api_getplatedaychart](api_getplatedaychart.md) | `/api/getPlateDayChart` | 单板块 N 日强度+量能 ECharts | `platecode`, `days` |

## 领域知识附录

- 📖 [stock-facts.md](stock-facts.md) — A 股 11 条惰性事实 (双源/前缀/T+1/复权/数据延迟等),调用前先扫一遍

## 双源差异 (from 入参)

| from | 数值字段含义 | 单位 | 适用板块 |
|------|------------|------|--------|
| `ths` (同花顺) | 当日**板块涨幅 %** | `4.94%` (带 `%` 符号) | 88x 板块 |
| `kaipan` (开盘啦) | 当日**板块强度分** | `15199` (纯整数,无 `%`) | 80x/803x 板块 |

数字越大越强。**两套数值不可直接比较**,正则 `[\d.\-]+%` 会漏开盘啦数据。

## 板块代码前缀强语义

| 前缀 | 来源 | 例 |
|------|------|---|
| `88x` | 同花顺 | `886084` F5G概念, `885998` 光纤概念, `886033` 共封装光学 |
| `80x` / `803x` | 开盘啦 | `801807` 算力, `801660` 通信, `803023` AI 应用 |

`getLongByPlate` / `getPlateDayChart` 的 `platecode=` 不能跨源乱传 — 同花顺 88x 板块在开盘啦里查不到, 反之亦然。

## days 入参

`10 | 20 | 30 | 50` 四档, 影响主表的列宽和 chart 的回溯长度。**默认建议 20**, 既能看出趋势又不会被假突破带跑。

## dates 入参 (可选)

不传则按 days 自动回溯。要查指定日期窗口时传 `YYYY-MM-DD,YYYY-MM-DD,...` 逗号分隔。

[PROTOCOL]: 变更时更新此头部, 然后检查 CLAUDE.md
