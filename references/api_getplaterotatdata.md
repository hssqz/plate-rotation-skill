---
id: api_getplaterotatdata
host: main
path: /api/getPlateRotatData
method: POST
category: 板块轮动
tier: data
last_verified: 2026-05-07
found_in_pages: platerotat
---

# ✅ api_getplaterotatdata

**分类**: 板块轮动　|　**Host**: `main`　|　**Method**: `POST`　|　**Tier**: ✅ `data`

## 调用方式

```bash
python3 ~/.claude/skills/plate-rotation/scripts/fetch.py main /api/getPlateRotatData -v
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
| first | string | "886084" — (从 body_head 正则抽取) |
| html | string | "<tr><td style='width:50px;vertical-align: middle;'>\u6392\u540d<\/td><td style= — (从 body_head 正则抽取) |

## 数据样例

```
{"first":"886084","html":"<tr><td style='width:50px;vertical-align: middle;'>排名<\/td><td style='vertical-align: middle;line-height:160%;'>2026-05-07<\/td><td style='vertical-align: middle;line-height:160%;'>2026-05-06<\/td><td style='vertical-align: middle;line-height:160%;'>2026-04-30<\/td><td style='vertical-align: middle;line-height:160%;'>2026-04-29<\/td><td style='vertical-align: middle;line-height:160%;'>2026-04-28<\/td><td style='vertical-align: middle;line-height:160%;'>2026-04-27<\/td><td style='vertical-align: middle;line-height:160%;'>2026-04-24<\/td><td style='vertical-align: middle;line-height:160%;'>2026-04-23<\/td><td style='vertical-align: middle;line-height:160%;'>2026-04-22<\/td><td style='vertical-align: middle;line-height:160%;'>2026-04-21<\/td><td style='vert
```

## 解析提示 / 字段语义

**输出双重语义** (取决于入参 `from`):
| from | 数值字段含义 | 单位 | 排序方向 |
| --- | --- | --- | --- |
| `ths` (同花顺) | 当日**板块涨幅 %** | `4.94%` (带 `%` 符号) | 数值越大越强 |
| `kaipan` (开盘啦) | 当日**板块强度分** | `15199` (纯整数,无 `%`) | 综合上榜次数+涨速+龙头数等多因子,数字越大越强 |

**板块代码前缀含义**:
- `80x` / `803x` 开头 → 开盘啦板块 (如 `801807`=算力, `801660`=通信, `803023`=AI 应用)
- `88x` 开头 → 同花顺板块 (如 `886084`=F5G概念, `885998`=光纤概念, `886033`=共封装光学)

**HTML 解析模板** (`response.html` 字段):
```
<span class='rank' style='...'>{N}</span>          ← 排名 1..N
<td class='plate plate{code}' code='{code}' name='{name}' style='...'>
    <span>...{name}</span><br>
    <span style='color:red|green;'>{value}</span>  ← 第 1 个 td 是【今天】的数值
</td>
... (后续 td = 第 2 天 / 第 3 天 ... 倒序)
```

**直接调 helper 推荐**:
```python
import sys; sys.path.insert(0, '~/.claude/skills/plate-rotation/scripts')
from parsers import parse_plate_rotat
top = parse_plate_rotat(data, source='ths')      # [{rank, code, name, value, value_type, color}]
```

`response.first` 字段 = 当日 Top1 板块代码,可直接传给 `getLongByPlate` 拿龙头股。

