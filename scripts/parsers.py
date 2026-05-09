#!/usr/bin/env python3
# ==================================================================
# plate-rotation 响应解析 helpers
#
# 4 个板块轮动接口大量返回 "HTML 片段嵌在 JSON 的 html 字段里" —
# 前端直接 innerHTML 渲染。所以拿到 JSON 后必须再做一次 HTML 抽取。
# 本模块沉淀板块轮动相关的解析函数。
#
# 用法:
#   from parsers import parse_plate_rotat, parse_plate_long_heads
#   data = json.load(open('xxx.json'))   # fetch.py 输出
#   plates = parse_plate_rotat(data, source='ths')
# ==================================================================
import re
from collections import defaultdict
from typing import Optional

# ============== 板块轮动主表 (api_getplaterotatdata) ==============

def parse_plate_rotat(data: dict, source: str = "ths") -> list[dict]:
    """
    解析 /api/getPlateRotatData 响应,返回今日 Top N 板块清单。

    `source` 决定数值字段的语义：
      - 'ths'    (同花顺) → 数值是【今日板块涨幅 %】(带 % 符号, 如 '4.94%')
      - 'kaipan' (开盘啦) → 数值是【板块强度分】(纯数字, 如 '15199',
                            综合上榜次数+涨速+龙头数等多因子)

    返回结构:
      [{'rank': 1, 'code': '886084', 'name': '光纤概念',
        'value': '4.94%' | '15199', 'value_type': 'pct'|'score',
        'color': 'red'|'green'}, ...]

    HTML 模板 (基于响应正则归纳):
      <span class='rank' style='...'>N</span>            ← 排名
      <td class='plate plate{code}' code='{code}' name='{name}' style='...'>
          <span>...{name}</span><br>
          <span style='color:red|green;'>{value}</span>  ← 第 1 个 td 是今天的
      </td>
    """
    html = data.get("html", "")
    out = []
    rows = re.split(r"<span class='rank'[^>]*>(\d+)</span>", html)
    for i in range(1, len(rows), 2):
        rank = int(rows[i])
        rest = rows[i + 1] if i + 1 < len(rows) else ""
        # 当日数据是 split 后第一个 td.plate
        # 注意 ths 带 %, kaipan 无 %  → [\d.\-]+%? 兼容
        m = re.search(
            r"<td class='plate plate\d+'\s*code='(\d+)'\s*name='([^']+)'[^>]*>"
            r".*?<span style='color:(red|green);'>([\d.\-]+%?)</span>",
            rest, re.S
        )
        if not m:
            continue
        code, name, color, value = m.groups()
        out.append({
            "rank": rank,
            "code": code,
            "name": name,
            "value": value,
            "value_type": "pct" if value.endswith("%") else "score",
            "color": color,
        })
    return out


def parse_plate_rotat_matrix(data: dict, dates: list[str]) -> list[dict]:
    """
    把 getPlateRotatData 还原成 N×天 矩阵, 方便分析"某板块何时上榜"或者
    "某天的整列 Top10"。

    `dates` 是日期序列 (从 getPlateRotatData 同一份响应的表头解析得到,
    或独立调用一次取 dates = parse_plate_rotat_dates(data))。

    返回:
      [{'rank': 1, 'cells': [{'date': '2026-05-07', 'code': '886084',
                              'name': '光纤概念', 'value': '4.94%',
                              'color': 'red'}, ...]}, ...]
    """
    html = data.get("html", "")
    out = []
    rows = re.split(r"<span class='rank'[^>]*>(\d+)</span>", html)
    cell_re = re.compile(
        r"<td class='plate plate\d+'\s*code='(\d+)'\s*name='([^']+)'[^>]*>"
        r".*?<span style='color:(red|green);'>([\d.\-]+%?)</span>",
        re.S
    )
    for i in range(1, len(rows), 2):
        rank = int(rows[i])
        rest = rows[i + 1] if i + 1 < len(rows) else ""
        cells = []
        for di, m in enumerate(cell_re.finditer(rest)):
            code, name, color, value = m.groups()
            cells.append({
                "date": dates[di] if di < len(dates) else None,
                "code": code, "name": name, "value": value, "color": color,
            })
            if di + 1 >= len(dates):
                break
        out.append({"rank": rank, "cells": cells})
    return out


def parse_plate_rotat_dates(data: dict) -> list[str]:
    """从 getPlateRotatData 的表头抽日期数组 (按 newest→oldest 排列)."""
    html = data.get("html", "")
    return re.findall(r"line-height:160%;'>(\d{4}-\d{2}-\d{2})", html)


# ============== 板块龙头 (api_getlongbyplate) ====================

def parse_plate_long_heads(data: dict, dates: list[str]) -> list[dict]:
    """
    解析 /api/getLongByPlate 响应,返回每天的龙头股清单。

    结构特点:
      - 每个 <td> 代表【一天】, 但服务端用两种 style 区分:
        · 有领涨: style='text-align:left;padding-bottom:5px;'  → 含 5 个 div.kline
        · 无领涨: style='text-align:center;color:#bbb;...'     → 文本"当日无领涨"
      - tds 顺序 = dates 顺序 (newest first, 跟 getPlateRotatData 的 dates 对齐)
      - 注意: 无领涨 td 的闭合是 </div> 不是 </td> (服务端 HTML 错位),
        所以用 lookahead `(?=<td|$)` 而非 `</td>` 兜底。

    返回:
      [{'date': '2026-05-07',
        'heads': [{'rank': '龙一', 'code': '603045', 'name': '福达合金'}, ...]},
       ...]
    """
    html = data.get("html", "")
    # 双 style 兼容: 有领涨 (text-align:left) + 无领涨 (text-align:center;color:#bbb)
    tds = re.findall(
        r"<td style='(?:text-align:left;padding-bottom:5px;"
        r"|text-align:center;color:#bbb[^']*)'>(.*?)(?=<td|$)",
        html, re.S
    )
    out = []
    for di, td in enumerate(tds):
        if "当日无领涨" in td:
            heads = []
        else:
            heads = [
                {"rank": rank, "code": code, "name": name}
                for code, rank, name in re.findall(
                    r"<div class='kline' code='(\d{6})'><span>([^<]+)</span>([^<]+)</div>",
                    td
                )
            ]
        out.append({
            "date": dates[di] if di < len(dates) else None,
            "heads": heads,
        })
    return out


def rank_plate_long_persistence(data: dict, dates: list[str], top_n: int = 15) -> list[dict]:
    """
    跨天统计某板块"哪些股票多次当过龙头"。
    用途: 找"妖王/真核心"——上榜次数越多说明持续性越强。

    返回:
      [{'code': '000889', 'name': '中嘉博创', 'count': 6,
        'positions': ['2026-04-28/龙三', '2026-04-24/龙二', ...]}, ...]
    """
    days = parse_plate_long_heads(data, dates)
    bag = defaultdict(lambda: {"count": 0, "name": "", "positions": []})
    for d in days:
        for h in d["heads"]:
            slot = bag[h["code"]]
            slot["count"] += 1
            slot["name"] = h["name"]
            slot["positions"].append(f"{d['date']}/{h['rank']}")
    ranked = sorted(bag.items(), key=lambda x: -x[1]["count"])
    return [{"code": c, **info} for c, info in ranked[:top_n]]


# ============== self-test ========================================
if __name__ == "__main__":
    import sys, subprocess, os, json
    if len(sys.argv) < 2:
        print("usage: parsers.py <demo>", file=sys.stderr)
        print("  demo: plate_rotat_ths | plate_rotat_kaipan | plate_long_<code>", file=sys.stderr)
        sys.exit(1)
    demo = sys.argv[1]
    here = os.path.dirname(os.path.abspath(__file__))
    fetch = os.path.join(here, "fetch.py")

    def run(*args):
        r = subprocess.run(["python3", fetch, *args, "--raw"],
                           capture_output=True, text=True)
        return json.loads(r.stdout) if r.stdout.strip().startswith(("{", "[")) else None

    if demo == "plate_rotat_ths":
        d = run("main", "/api/getPlateRotatData", "from=ths", "days=20")
        for p in parse_plate_rotat(d, source="ths")[:10]:
            print(p)
    elif demo == "plate_rotat_kaipan":
        d = run("main", "/api/getPlateRotatData", "from=kaipan", "days=20")
        for p in parse_plate_rotat(d, source="kaipan")[:10]:
            print(p)
    elif demo.startswith("plate_long_"):
        platecode = demo.split("_", 2)[-1]
        prd = run("main", "/api/getPlateRotatData", "from=kaipan", "days=20")
        lng = run("main", "/api/getLongByPlate", f"platecode={platecode}", "days=20")
        dates = parse_plate_rotat_dates(prd)
        print(f"=== {platecode} 持续性 Top ===")
        for x in rank_plate_long_persistence(lng, dates, top_n=10):
            print(x)
    else:
        print(f"unknown demo: {demo}", file=sys.stderr)
        sys.exit(1)
