# learned/ths.md — 同花顺源专属经验

> from=ths 路径下踩过的坑。
> 跨源通用经验放 `_meta.md`,开盘啦经验放 `kaipan.md`。

---

## 字段陷阱

### 2026-05-09 ths 涨幅字段单位

- `getPlateRotatData` `from=ths` 返回的数值是**带 `%` 的字符串**: `"4.94%"`
- 不是 float 也不是百分比 *100 的整数
- parsers 已用 `value_type='pct'` 标注
- **写下游分析时不要 `float(value)` 直接转,会 ValueError**

### ths 源仅认 88x 前缀板块

- 试图传 80x 板块代码到 `from=ths` 路径的接口会返回空数据 / 非预期错位
- 86 类板块 (例如 `886084` F5G) 是同花顺概念板块体系
- 80x 类板块 (例如 `801807` 算力) 是开盘啦独有的强度榜

---

## 路由速记

| 任务 | from | 板块前缀 |
|---|---|---|
| 看当日涨幅 % 排序的 Top 板块 | `ths` | 88x |
| 看当日强度分排序的 Top 板块 | `kaipan` | 80x / 803x |
| 看 88x 板块的龙头矩阵 | (`getLongByPlate` 自动识别) | 88x |

---

[PROTOCOL]: 变更时更新此头部,然后检查 CLAUDE.md
