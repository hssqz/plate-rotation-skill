---
id: api_getplaterotatchart
host: main
path: /api/getPlateRotatChart
method: POST
category: 板块轮动
tier: data
last_verified: 2026-05-07
found_in_pages: platerotat
---

# ✅ api_getplaterotatchart

**分类**: 板块轮动　|　**Host**: `main`　|　**Method**: `POST`　|　**Tier**: ✅ `data`

## 调用方式

```bash
python3 ~/.claude/skills/plate-rotation/scripts/fetch.py main /api/getPlateRotatChart -v
```

## 输入参数

| 名称 | 类型 | 必选 | 描述 |
| --- | --- | --- | --- |
| from | string | 是 | 板块来源: ths(同花顺) | kaipan(开盘啦) |
| days | int | 是 | 回溯天数: 10 | 20 | 30 | 50 |
| dates | string | 否 | 自定义日期(YYYY-MM-DD,逗号分隔),空则按 days 回溯 |

## 输出字段

| 字段 | 类型 | 样例值 / 备注 |
| --- | --- | --- |
| date | list | ["05-07" — (从 body_head 正则抽取) |
| legend | list | ["F5G概念(6次上榜)" — (从 body_head 正则抽取) |
| name | object | {"1":"F5G概念(6次上榜)" — (从 body_head 正则抽取) |
| value | string | "2" — (从 body_head 正则抽取) |
| symbol | string | "image:///static/img/rank2.png"} — (从 body_head 正则抽取) |

## 数据样例

```
{"date":["05-07","05-06","04-30","04-29","04-28","04-27","04-24","04-23","04-22","04-21","04-20","04-17","04-16","04-15","04-14","04-13","04-10","04-09","04-08","04-07"],"legend":["F5Gæ¦å¿µ(6æ¬¡ä¸æ¦)","ç§åæ¬¡æ°è¡(6æ¬¡ä¸æ¦)","å½å®¶å¤§åºéæè¡(5æ¬¡ä¸æ¦)","PETéç®(5æ¬¡ä¸æ¦)","å±å°è£åå­¦(CPO)(5æ¬¡ä¸æ¦)"],"name":{"1":"F5Gæ¦å¿µ(6æ¬¡ä¸æ¦)","2":"ç§åæ¬¡æ°è¡(6æ¬¡ä¸æ¦)","3":"å½å®¶å¤§åºéæè¡(5æ¬¡ä¸æ¦)","4":"PETéç®(5æ¬¡ä¸æ¦)","5":"å±å°è£åå­¦(CPO)(5æ¬¡ä¸æ¦)"},"1":[{"value":"2","symbol":"image:///static/img/rank2.png"},{"value":"8","symbol":"image:///static/img/rank8.png"},{"value":10.5,"symbol":"image:///static/img/wu.png"},{"value":10.5,"symbol":"image:///static/img/wu.png"},{"value":10.5,"symbol":"image:///static/img/wu.png"},{"value":10.5,"symbol":"image:///static/img/wu.png"},{"value":10.5,"symbol":"image:///static/img/wu.png"},{"value":10.5,"symbol":"image:///static/img/wu.png"},{"v
```

## 解析提示 / 字段语义

**输出**: ECharts 数据，结构 `{date:[最近N日], legend:[Top5板块名(N次上榜)], name:{1..5:名}, 1..5:[{value, symbol}*N]}`。
- `legend[i]` 形如 "F5G概念(6次上榜)" — 括号内是该板块过去 N 日总上榜次数
- `1..5` 各是 Top5 中第 i 名板块的【N 日排名变化序列】，每点 `{value: '排名', symbol: 'image:///static/img/rankN.png'}`
- value 为 `10.5` 时图标 `wu.png` 表示当日未上榜

