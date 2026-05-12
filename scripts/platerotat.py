#!/usr/bin/env python3
"""
[INPUT]: 依赖同目录 fetch.py (subprocess 调用) + parsers.py (5 个 helper)
[OUTPUT]: 对外暴露 today_top / find_dragon_kings / top1_curve / plate_strength 4 个高级函数 + CLI
[POS]: scripts/ 的最高层封装,组合 fetch+parsers,给 Agent / 用户提供 "一个意图一个函数" 入口
[PROTOCOL]: 变更时更新此头部,然后检查 CLAUDE.md
"""
# ==================================================================
# plate-rotation 高级 API + CLI
#
# 把 4 个底层接口 (getPlateRotatData / getPlateRotatChart /
# getLongByPlate / getPlateDayChart) 组合成"一个意图一个函数"的高级
# helper, 让 Agent 不用自己拼接。
#
# 用作 import:
#     from platerotat import today_top, find_dragon_kings, top1_curve, plate_strength
#     today_top(source='kaipan', n=10)
#     find_dragon_kings(platecode='886084', days=20, top_n=10)
#
# 用作 CLI:
#     platerotat.py today                         # 今日 Top10 (默认开盘啦)
#     platerotat.py today --from ths --n 20       # 切同花顺,看前 20
#     platerotat.py wangking 886084 --days 20     # 板块妖王榜
#     platerotat.py curve --from kaipan           # Top5 板块 N 日排名变化
#     platerotat.py strength 886084               # 板块强度+量能时序
#
# 运行时校验 (2026-05-12):
#   每个高级 helper 在解析完成后做一次 sanity check, 命中空数据 / 缺关键字段
#   时通过 stderr 输出明确的 "PR-EMPTY: ..." 警告, 帮助下游 Agent 区分:
#     - 节假日 / 参数 days 超前 → 接口正常但当日无数据
#     - 板块代码跨源错传 → 88x 传到 kaipan 源会拿到空
#     - 上游接口异常 → response 非 dict 或缺顶层字段
# ==================================================================
import argparse, datetime, json, os, subprocess, sys
from typing import Literal, Optional

HERE = os.path.dirname(os.path.abspath(__file__))
FETCH = os.path.join(HERE, "fetch.py")

# 让 import 形式也能找到 parsers
sys.path.insert(0, HERE)
from parsers import (
    parse_plate_rotat,
    parse_plate_rotat_matrix,
    parse_plate_rotat_dates,
    parse_plate_long_heads,
    rank_plate_long_persistence,
)

Source = Literal["ths", "kaipan"]


# ============== 底层调用封装 ====================================

def _call(host: str, path: str, *kv: str) -> dict:
    """Thin wrapper over scripts/fetch.py。--raw 拿原始 JSON 字符串再 parse。"""
    r = subprocess.run(
        ["python3", FETCH, host, path, *kv, "--raw"],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        sys.stderr.write(r.stderr)
        sys.exit(r.returncode)
    txt = r.stdout.strip()
    if not txt:
        sys.exit(f"[platerotat] empty response from {path}")
    try:
        return json.loads(txt)
    except json.JSONDecodeError as e:
        sys.exit(f"[platerotat] non-JSON from {path}: {e}\n{txt[:300]}")


# ============== 运行时校验工具 ==================================

def _warn(tag: str, msg: str) -> None:
    """统一警告通道。下游 Agent 可 grep 'PR-EMPTY' / 'PR-WARN' 识别。"""
    print(f"[platerotat] {tag}: {msg}", file=sys.stderr)


def _is_weekend(d: Optional[datetime.date] = None) -> bool:
    d = d or datetime.date.today()
    return d.weekday() >= 5  # 5=Sat, 6=Sun


def _hint_for_empty(source: Optional[str], platecode: Optional[str]) -> str:
    """对空数据给出最可能的 3 类原因提示。stdlib only, 不查交易日历,只给方向。"""
    parts = []
    if _is_weekend():
        parts.append("今天是周末")
    if platecode and source:
        prefix_ok = (platecode.startswith("88") and source == "ths") \
                    or (platecode.startswith(("80", "803")) and source == "kaipan")
        if not prefix_ok:
            parts.append(f"板块前缀 {platecode[:3]} 与 source={source} 可能不匹配")
    if not parts:
        parts.append("可能是节假日 / 参数 days 超前 / 上游接口临时异常")
    return ";".join(parts)


# ============== 高级 helper #1: today_top ========================

def today_top(source: Source = "kaipan", n: int = 10, days: int = 20) -> list[dict]:
    """
    今日 Top N 板块 (基于 /api/getPlateRotatData)。

    Args:
        source: 'ths' (同花顺,值=涨幅%) 或 'kaipan' (开盘啦,值=强度分)
        n:      返回前几名
        days:   回溯天数 (10|20|30|50,影响主表的列宽,但当日 Top 只看第一列)

    Returns:
        [{rank, code, name, value, value_type, color}, ...]
        其中 value_type='pct' 时 value 形如 '4.94%',='score' 时形如 '15199'。
    """
    data = _call("main", "/api/getPlateRotatData", f"from={source}", f"days={days}")
    rows = parse_plate_rotat(data, source=source)[:n]
    if not rows:
        _warn("PR-EMPTY",
              f"today_top(source={source}) 返回空 → {_hint_for_empty(source, None)}")
    return rows


# ============== 高级 helper #2: find_dragon_kings ================

def find_dragon_kings(platecode: str, days: int = 20, top_n: int = 10) -> dict:
    """
    板块妖王榜: 该板块过去 N 天里,哪些股票最频繁地当过龙头?
    依赖 getPlateRotatData (拿日期) + getLongByPlate (拿龙头矩阵)。

    Args:
        platecode: 板块代码,如 '886084' (F5G概念) / '801807' (算力)
                   88x = 同花顺;80x/803x = 开盘啦
        days:      回溯天数
        top_n:     妖王榜返回前几名

    Returns:
        {
          'platecode': '886084',
          'days': 20,
          'dates': ['2026-05-07', ...],
          'kings': [{code, name, count, positions:['2026-04-28/龙三',...]}, ...],
          'daily_heads': [{date, heads:[{rank,code,name},...]}, ...],
        }
    """
    # 推断板块 source 仅用于决定 main 表查询的 from 参数 (拿 dates 不区分,
    # 但响应内容会因 from 不同而稍异;这里默认开盘啦,因为 80x/803x 板块在
    # 同花顺源里查不到,而 88x 在两源都可)。
    source: Source = "ths" if platecode.startswith("88") else "kaipan"
    prd = _call("main", "/api/getPlateRotatData", f"from={source}", f"days={days}")
    lng = _call("main", "/api/getLongByPlate", f"platecode={platecode}", f"days={days}")
    dates = parse_plate_rotat_dates(prd)
    kings = rank_plate_long_persistence(lng, dates, top_n=top_n)
    heads = parse_plate_long_heads(lng, dates)

    # ---- 运行时校验: dates 空 / kings 空 / heads 全空 ----
    if not dates:
        _warn("PR-EMPTY",
              f"find_dragon_kings({platecode}) dates 为空 → 上游主表无回退,"
              f"{_hint_for_empty(source, platecode)}")
    elif not kings and all(not h.get("heads") for h in heads):
        _warn("PR-EMPTY",
              f"find_dragon_kings({platecode}) 近 {days} 天均无领涨 → "
              f"该板块持续未活跃,或 platecode 跨源错传 ({_hint_for_empty(source, platecode)})")

    return {
        "platecode": platecode,
        "source": source,  # 透出实际使用的 source, 方便下游断言
        "days": days,
        "dates": dates,
        "kings": kings,
        "daily_heads": heads,
    }


# ============== 高级 helper #3: top1_curve =======================

def top1_curve(source: Source = "kaipan", days: int = 20) -> dict:
    """
    Top5 板块 N 日排名变化曲线 (ECharts 数据)。

    底层走 /api/getPlateRotatChart, 返回原始 ECharts 结构,但补上一些方便
    Agent 直接吞的字段:
      legend: ['F5G概念(6次上榜)', ...]  # 括号里是过去 N 日总上榜次数
      date:   ['05-07', '05-06', ...]    # MM-DD,newest first
      series_1..5: 每名板块的 N 日排名序列;value=10.5 + symbol=wu.png 表示当日未上榜

    Returns: 原 JSON 透传 + 加 'top5_names' 便利字段。
    """
    data = _call("main", "/api/getPlateRotatChart", f"from={source}", f"days={days}")
    # 'name' 字段是 {1: 'xxx', 2: 'xxx'}, 提取成有序 list 方便用
    name_dict = data.get("name") or {}
    data["top5_names"] = [name_dict.get(str(i)) for i in range(1, 6) if str(i) in name_dict]
    if not data["top5_names"]:
        _warn("PR-EMPTY",
              f"top1_curve(source={source}) 缺 name 字段 → {_hint_for_empty(source, None)}")
    return data


# ============== 高级 helper #4: plate_strength ===================

def plate_strength(platecode: str, days: int = 20) -> dict:
    """
    单板块的 N 日强度+量能 ECharts 数据。
    底层走 /api/getPlateDayChart。

    板块当日"未活跃"时整张图的 legend 字段为 null,前端不渲染。

    Returns: 原 JSON 透传 (legend, date, ...);上层应用按需读 series。
    """
    data = _call("main", "/api/getPlateDayChart", f"platecode={platecode}", f"days={days}")
    # legend=null 表示当日板块未活跃;date 为空 = 上游接口异常
    if not data.get("date"):
        _warn("PR-EMPTY",
              f"plate_strength({platecode}) date 列为空 → 板块代码可能无效或上游异常")
    elif data.get("legend") is None:
        _warn("PR-WARN",
              f"plate_strength({platecode}) legend=null → 该板块近 {days} 天均未活跃")
    return data


# ============== CLI ==============================================

def _print_json(obj):
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def _cli_today(args):
    rows = today_top(source=args.source, n=args.n, days=args.days)
    if args.json:
        _print_json(rows)
        return
    # 表格输出
    print(f"=== Top {args.n} 板块 (source={args.source}, days={args.days}) ===")
    for r in rows:
        arrow = "↑" if r["color"] == "red" else "↓"
        print(f"  #{r['rank']:>2}  {r['code']}  {r['name']:<16}  {arrow} {r['value']}")


def _cli_wangking(args):
    res = find_dragon_kings(platecode=args.platecode, days=args.days, top_n=args.n)
    if args.json:
        _print_json(res)
        return
    print(f"=== 板块 {args.platecode} 妖王榜 (近 {args.days} 天, dates {len(res['dates'])} 列) ===")
    for k in res["kings"]:
        pos = " | ".join(k["positions"][:5])
        more = "" if len(k["positions"]) <= 5 else f" +{len(k['positions'])-5}更多"
        print(f"  {k['code']}  {k['name']:<10}  上榜 {k['count']} 次   [{pos}]{more}")


def _cli_curve(args):
    data = top1_curve(source=args.source, days=args.days)
    if args.json:
        _print_json(data)
        return
    print(f"=== Top5 板块 {args.days} 日排名变化 (source={args.source}) ===")
    print("  日期序列 (newest first):", " ".join(data.get("date", [])))
    for i, name in enumerate(data.get("top5_names", []), start=1):
        series = data.get(str(i), [])
        ranks = [str(p.get("value")) for p in series]
        print(f"  #{i} {name}")
        print(f"     {' '.join(ranks)}")


def _cli_strength(args):
    data = plate_strength(platecode=args.platecode, days=args.days)
    if args.json:
        _print_json(data)
        return
    print(f"=== 板块 {args.platecode} 强度时序 ===")
    print(f"  legend: {data.get('legend')}")
    print(f"  date:   {data.get('date')}")
    extra = {k: v for k, v in data.items() if k not in ("legend", "date")}
    if extra:
        print(f"  series keys: {list(extra.keys())}")


def main():
    ap = argparse.ArgumentParser(prog="platerotat",
        description="板块轮动 4 件套 (today / wangking / curve / strength)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_today = sub.add_parser("today", help="今日 Top N 板块")
    p_today.add_argument("--source", choices=["ths", "kaipan"], default="kaipan")
    p_today.add_argument("--n", type=int, default=10)
    p_today.add_argument("--days", type=int, default=20)
    p_today.add_argument("--json", action="store_true")
    p_today.set_defaults(func=_cli_today)

    p_wk = sub.add_parser("wangking", help="板块妖王榜 (跨天上榜次数 Top N)")
    p_wk.add_argument("platecode", help="板块代码,如 886084 (F5G概念) / 801807 (算力)")
    p_wk.add_argument("--days", type=int, default=20)
    p_wk.add_argument("--n", type=int, default=10)
    p_wk.add_argument("--json", action="store_true")
    p_wk.set_defaults(func=_cli_wangking)

    p_cv = sub.add_parser("curve", help="Top5 板块 N 日排名变化曲线")
    p_cv.add_argument("--source", choices=["ths", "kaipan"], default="kaipan")
    p_cv.add_argument("--days", type=int, default=20)
    p_cv.add_argument("--json", action="store_true")
    p_cv.set_defaults(func=_cli_curve)

    p_st = sub.add_parser("strength", help="单板块 N 日强度+量能时序")
    p_st.add_argument("platecode")
    p_st.add_argument("--days", type=int, default=20)
    p_st.add_argument("--json", action="store_true")
    p_st.set_defaults(func=_cli_strength)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
