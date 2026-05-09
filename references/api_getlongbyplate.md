---
id: api_getlongbyplate
host: main
path: /api/getLongByPlate
method: POST
category: 板块轮动
tier: data
last_verified: 2026-05-07
found_in_pages: platerotat
---

# ✅ api_getlongbyplate

**分类**: 板块轮动　|　**Host**: `main`　|　**Method**: `POST`　|　**Tier**: ✅ `data`

> platecode 例: 886084=F5G概念, 从 getPlateRotatData.first 拿

## 调用方式

```bash
python3 ~/.claude/skills/plate-rotation/scripts/fetch.py main /api/getLongByPlate -v
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
| html | string | "<td style='width:50px;vertical-align: middle;height:99px;'><b style='box-shadow — (从 body_head 正则抽取) |

## 数据样例

```
{"html":"<td style='width:50px;vertical-align: middle;height:99px;'><b style='box-shadow: 0 1px 6px rgba(0, 0, 0, .06);font-weight:normal;padding:2px 3px;border:1px solid #f5f5f5;'>é¢æ¶¨</b></td><td style='text-align:center;color:#bbb;vertical-align: middle;font-size:90%:'>å½æ¥æ é¢æ¶¨</div><td style='text-align:center;color:#bbb;vertical-align: middle;font-size:90%:'>å½æ¥æ é¢æ¶¨</div><td style='text-align:center;color:#bbb;vertical-align: middle;font-size:90%:'>å½æ¥æ é¢æ¶¨</div><td style='text-align:center;color:#bbb;vertical-align: middle;font-size:90%:'>å½æ¥æ é¢æ¶¨</div><td style='text-align:center;color:#bbb;vertical-align: middle;font-size:90%:'>å½æ¥æ é¢æ¶¨</div><td style='text-align:center;color:#bbb;vertical-align: middle;font-size:90%:'>å½æ¥æ é¢æ¶¨</div><td style='text-align:center;color:#bbb;vertical-align: middle;font-
```

## 解析提示 / 字段语义

**HTML 结构**: 顶层是 `<table>`，每个 `<td style='text-align:left;padding-bottom:5px;'>` = **一天**，
里面 1~5 个 `<div class='kline' code='{code}'><span>{rank}</span>{name}</div>` (rank=龙一/龙二/.../龙五)。

- td 顺序 = `getPlateRotatData` 同期 days 入参的日期表头顺序 (newest first)
- 当日无领涨股时 td 文本为 `当日无领涨` (无 `<div class='kline'>`)
- 第 1 个 td 是 `<td>领涨</td>` 标签头,**不是数据**,需跳过 (parse_plate_long_heads 已自动处理)

**入参 `platecode` 必填**,从 `getPlateRotatData.first` 拿当日 Top1,或从 `<td class='plate plate{code}'>` 提取任意板块。

**helper 推荐**:
```python
from parsers import parse_plate_long_heads, rank_plate_long_persistence, parse_plate_rotat_dates
prd = json.load(...)   # getPlateRotatData 响应
lng = json.load(...)   # getLongByPlate 响应
dates = parse_plate_rotat_dates(prd)
days   = parse_plate_long_heads(lng, dates)         # 每天的 5 个龙头
top    = rank_plate_long_persistence(lng, dates)    # 跨天频次 Top 15 (找妖王)
```

