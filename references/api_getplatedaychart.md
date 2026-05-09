---
id: api_getplatedaychart
host: main
path: /api/getPlateDayChart
method: POST
category: 板块轮动
tier: data
last_verified: 2026-05-07
found_in_pages: platerotat
---

# ✅ api_getplatedaychart

**分类**: 板块轮动　|　**Host**: `main`　|　**Method**: `POST`　|　**Tier**: ✅ `data`

## 调用方式

```bash
python3 ~/.claude/skills/plate-rotation/scripts/fetch.py main /api/getPlateDayChart -v
```

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
| --- | --- | --- | --- |
| platecode | string | 是 | 板块代码,如 886084(F5G概念);可从 getPlateRotatData 响应的 first 字段拿 |
| days | int | 是 | 回溯天数: 10 | 20 | 30 | 50 |
| dates | string | 否 | 自定义日期,空则按 days 回溯 |

## 输出字段

| 字段 | 类型 | 样例值 / 备注 |
| --- | --- | --- |
| legend | null | null |
| date | list | ["05-07", "05-06", "04-30", "04-29", "04-28", "04-27", "04-24", "04-23", "04-22"… |

## 数据样例

```
{"legend":null,"date":["05-07","05-06","04-30","04-29","04-28","04-27","04-24","04-23","04-22","04-21","04-20","04-17","04-16","04-15","04-14","04-13","04-10","04-09","04-08","04-07"]}
```

## 解析提示 / 字段语义

**与 `getLongByPlate` 配套**: 同一个 `platecode + days` 入参,返回该板块 N 日的强度+量能 ECharts 数据。
板块当日"未活跃"时 `legend` 字段为 null,前端不渲染图表。

