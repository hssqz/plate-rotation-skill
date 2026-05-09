#!/usr/bin/env python3
# ==================================================================
# plate-rotation skill 完整测试集 (在线集成测试)
#
# 目标: 验证 skill 在真实在线接口下完整工作 ——
#   1. 4 个底层 endpoint 健康
#   2. 5 个 parsers 函数对真实 HTML in JSON 的解析正确
#   3. 4 个高级 helper (today_top / find_dragon_kings /
#      top1_curve / plate_strength) 签名 + 返回结构
#   4. find_dragon_kings 的 88x→ths / 80x→kaipan 自动路由
#   5. CLI 4 个子命令 (today/wangking/curve/strength) text + json 双模
#
# 运行:
#   python3 tests/test_plate_rotation.py            # 直接跑
#   python3 -m unittest tests.test_plate_rotation -v
#
# 依赖: 网络在线, Python 3.9+ stdlib only
# ==================================================================
import json
import os
import re
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(HERE)
SCRIPTS = os.path.join(SKILL_DIR, "scripts")
FETCH = os.path.join(SCRIPTS, "fetch.py")
PLATEROTAT = os.path.join(SCRIPTS, "platerotat.py")

sys.path.insert(0, SCRIPTS)
from parsers import (
    parse_plate_rotat,
    parse_plate_rotat_matrix,
    parse_plate_rotat_dates,
    parse_plate_long_heads,
    rank_plate_long_persistence,
)
from platerotat import (
    today_top,
    find_dragon_kings,
    top1_curve,
    plate_strength,
)


# ============== 共享 fixture (跨 TestCase 缓存,避免重复打网络) ====
class _Fixtures:
    """用 fetch.py --raw 拉一次接口数据,后续测试直接复用。"""
    _cache: dict = {}

    @classmethod
    def get(cls, key: str, host: str, path: str, *kv: str) -> dict:
        if key in cls._cache:
            return cls._cache[key]
        r = subprocess.run(
            ["python3", FETCH, host, path, *kv, "--raw"],
            capture_output=True, text=True, timeout=30,
        )
        if r.returncode != 0:
            raise RuntimeError(
                f"fetch.py {path} failed (code={r.returncode}):\n{r.stderr}"
            )
        try:
            cls._cache[key] = json.loads(r.stdout)
        except json.JSONDecodeError as e:
            raise RuntimeError(
                f"fetch.py {path} returned non-JSON: {e}\n{r.stdout[:300]}"
            )
        return cls._cache[key]


# ============== 1. 底层 endpoint 健康度 ==========================
class TestFetchEndpoints(unittest.TestCase):
    """验证 4 个底层 endpoint 都能正常响应、返回带核心字段的 JSON。"""

    def test_01_getplaterotatdata_ths(self):
        d = _Fixtures.get("prd_ths", "main",
                          "/api/getPlateRotatData", "from=ths", "days=20")
        self.assertIsInstance(d, dict)
        self.assertIn("html", d, "getPlateRotatData 必须返回 html 字段")
        self.assertGreater(len(d["html"]), 100, "html 字段必须有真实内容")
        self.assertIn("plate", d["html"], "html 应包含 plate 标签")

    def test_02_getplaterotatdata_kaipan(self):
        d = _Fixtures.get("prd_kaipan", "main",
                          "/api/getPlateRotatData", "from=kaipan", "days=20")
        self.assertIn("html", d)
        self.assertGreater(len(d["html"]), 100)
        self.assertIn("plate", d["html"])

    def test_03_getplaterotatchart(self):
        d = _Fixtures.get("prc", "main",
                          "/api/getPlateRotatChart", "from=kaipan", "days=20")
        self.assertIsInstance(d, dict)
        # ECharts 数据结构: name(1..5 字典) + date(列表) + 1..5 series
        self.assertIn("name", d, "getPlateRotatChart 必须返回 name 字典")
        self.assertIn("date", d, "getPlateRotatChart 必须返回 date 列表")
        self.assertIsInstance(d["name"], dict)
        self.assertIsInstance(d["date"], list)

    def test_04_getlongbyplate_88x(self):
        d = _Fixtures.get("long_886084", "main",
                          "/api/getLongByPlate",
                          "platecode=886084", "days=20")
        self.assertIsInstance(d, dict)
        self.assertIn("html", d)

    def test_05_getplatedaychart_88x(self):
        d = _Fixtures.get("daychart_886084", "main",
                          "/api/getPlateDayChart",
                          "platecode=886084", "days=20")
        self.assertIsInstance(d, dict)
        self.assertIn("date", d)
        # legend 可能为 null (板块当日未活跃),但 key 必须存在
        self.assertIn("legend", d)


# ============== 2. parsers.py 5 个 helper 解析正确性 ============
class TestParsers(unittest.TestCase):
    """parsers.py 在真实 HTML in JSON 数据上的解析正确性。"""

    # ---------- parse_plate_rotat (双源数值语义) -----------------
    def test_parse_plate_rotat_ths_value_has_pct(self):
        d = _Fixtures.get("prd_ths", "main",
                          "/api/getPlateRotatData", "from=ths", "days=20")
        rows = parse_plate_rotat(d, source="ths")
        self.assertGreater(len(rows), 0, "ths 源应返回非空板块列表")
        # rank 单调递增, 起点 = 1
        self.assertEqual(rows[0]["rank"], 1, "首行 rank 必须 = 1")
        ranks = [r["rank"] for r in rows]
        self.assertEqual(ranks, sorted(ranks), "rank 必须按升序排列")
        # 字段完整 + 双源差异: ths 必带 %
        for r in rows:
            self.assertIn("code", r)
            self.assertIn("name", r)
            self.assertIn("color", r)
            self.assertIn(r["color"], ("red", "green"))
            self.assertEqual(r["value_type"], "pct",
                             "ths 源 value_type 必须 = pct")
            self.assertTrue(r["value"].endswith("%"),
                            f"ths value 必带 %: got {r['value']!r}")

    def test_parse_plate_rotat_kaipan_value_no_pct(self):
        """已知陷阱: 正则 `[\\d.\\-]+%` 会漏开盘啦数据,这里反向验证。"""
        d = _Fixtures.get("prd_kaipan", "main",
                          "/api/getPlateRotatData", "from=kaipan", "days=20")
        rows = parse_plate_rotat(d, source="kaipan")
        self.assertGreater(len(rows), 0, "kaipan 源应返回非空板块列表")
        for r in rows:
            self.assertEqual(r["value_type"], "score",
                             "kaipan 源 value_type 必须 = score")
            self.assertFalse(r["value"].endswith("%"),
                             f"kaipan value 不应带 %: got {r['value']!r}")
            self.assertRegex(r["value"], r"^[\d.\-]+$",
                             "kaipan value 必须是纯数字")

    # ---------- parse_plate_rotat_dates --------------------------
    def test_parse_plate_rotat_dates_format_and_order(self):
        d = _Fixtures.get("prd_ths", "main",
                          "/api/getPlateRotatData", "from=ths", "days=20")
        dates = parse_plate_rotat_dates(d)
        self.assertGreater(len(dates), 0, "dates 列必须非空")
        # 每条都是 YYYY-MM-DD
        for s in dates:
            self.assertRegex(s, r"^\d{4}-\d{2}-\d{2}$",
                             f"dates 必须为 YYYY-MM-DD: {s!r}")
        # newest first → 第一个 >= 最后一个
        self.assertGreaterEqual(dates[0], dates[-1],
                                "dates 应按 newest-first 排列")
        # 无重复
        self.assertEqual(len(dates), len(set(dates)),
                         "dates 不应有重复日期")

    # ---------- parse_plate_rotat_matrix -------------------------
    def test_parse_plate_rotat_matrix_aligned_with_dates(self):
        d = _Fixtures.get("prd_ths", "main",
                          "/api/getPlateRotatData", "from=ths", "days=20")
        dates = parse_plate_rotat_dates(d)
        matrix = parse_plate_rotat_matrix(d, dates)
        self.assertGreater(len(matrix), 0, "matrix 必须非空")
        for row in matrix:
            self.assertIn("rank", row)
            self.assertIn("cells", row)
            self.assertGreater(len(row["cells"]), 0,
                               "每行至少要有一格")
            # cells 数量不应超过 dates 长度
            self.assertLessEqual(len(row["cells"]), len(dates),
                                 "cells 不应多于 dates 列数")
            for cell in row["cells"]:
                self.assertIn(cell["date"], dates,
                              "cell.date 必须落在 dates 集合内")
                self.assertRegex(cell["code"], r"^\d+$")
                self.assertIn(cell["color"], ("red", "green"))

    # ---------- parse_plate_long_heads ---------------------------
    def test_parse_plate_long_heads_structure(self):
        prd = _Fixtures.get("prd_kaipan", "main",
                            "/api/getPlateRotatData",
                            "from=kaipan", "days=20")
        lng = _Fixtures.get("long_886084", "main",
                            "/api/getLongByPlate",
                            "platecode=886084", "days=20")
        dates = parse_plate_rotat_dates(prd)
        heads = parse_plate_long_heads(lng, dates)
        self.assertGreater(len(heads), 0, "heads 列表必须非空")
        for entry in heads:
            self.assertIn("date", entry)
            self.assertIn("heads", entry)
            self.assertIsInstance(entry["heads"], list)
            for h in entry["heads"]:
                self.assertRegex(h["code"], r"^\d{6}$",
                                 f"龙头 code 必须 6 位数字: {h['code']!r}")
                self.assertIn(h["rank"],
                              ("龙一", "龙二", "龙三", "龙四", "龙五"),
                              f"未知 rank: {h['rank']!r}")
                self.assertGreater(len(h["name"]), 0)

    # ---------- rank_plate_long_persistence ----------------------
    def test_rank_plate_long_persistence_sorted_desc(self):
        prd = _Fixtures.get("prd_kaipan", "main",
                            "/api/getPlateRotatData",
                            "from=kaipan", "days=20")
        lng = _Fixtures.get("long_886084", "main",
                            "/api/getLongByPlate",
                            "platecode=886084", "days=20")
        dates = parse_plate_rotat_dates(prd)
        kings = rank_plate_long_persistence(lng, dates, top_n=10)
        self.assertLessEqual(len(kings), 10, "top_n 限制必须生效")
        # 真实数据通常会有龙头, 但极端情况(板块完全无龙头)也容错
        if kings:
            counts = [k["count"] for k in kings]
            self.assertEqual(counts, sorted(counts, reverse=True),
                             "妖王榜须按 count 降序")
            self.assertGreaterEqual(kings[0]["count"], 1)
            for k in kings:
                self.assertEqual(len(k["positions"]), k["count"],
                                 "positions 数量必须 = count")
                # positions 形如 'YYYY-MM-DD/龙X'
                for p in k["positions"]:
                    self.assertRegex(p, r"^\d{4}-\d{2}-\d{2}/龙[一二三四五]$",
                                     f"position 格式错误: {p!r}")


# ============== 3. 4 个高级 helper (import 形式) =================
class TestHighLevelHelpers(unittest.TestCase):
    """4 个高级 helper 的返回结构、签名约束、双源 value_type 区分。"""

    def test_today_top_kaipan_default(self):
        rows = today_top(source="kaipan", n=10, days=20)
        self.assertIsInstance(rows, list)
        self.assertGreater(len(rows), 0, "kaipan Top 应非空")
        self.assertLessEqual(len(rows), 10, "n 限制必须生效")
        self.assertEqual(rows[0]["rank"], 1)
        for r in rows:
            self.assertEqual(r["value_type"], "score")

    def test_today_top_ths_with_pct(self):
        rows = today_top(source="ths", n=5, days=20)
        self.assertLessEqual(len(rows), 5)
        self.assertGreater(len(rows), 0, "ths Top 应非空")
        for r in rows:
            self.assertTrue(r["value"].endswith("%"),
                            f"ths value 必带 %: got {r['value']!r}")

    def test_today_top_n_clamps(self):
        """n=3 必须严格 ≤ 3 (可能更少, 不会更多)。"""
        rows = today_top(source="kaipan", n=3, days=20)
        self.assertLessEqual(len(rows), 3)

    def test_find_dragon_kings_returns_full_dict(self):
        res = find_dragon_kings(platecode="886084", days=20, top_n=10)
        for k in ("platecode", "days", "dates", "kings", "daily_heads"):
            self.assertIn(k, res, f"find_dragon_kings 返回应含 {k}")
        self.assertEqual(res["platecode"], "886084")
        self.assertEqual(res["days"], 20)
        self.assertGreater(len(res["dates"]), 0)
        self.assertLessEqual(len(res["kings"]), 10, "top_n 限制必须生效")
        # daily_heads 与 dates 大致对齐 (允许极端日 td 缺失)
        self.assertGreater(len(res["daily_heads"]), 0)

    def test_top1_curve_has_top5_names(self):
        data = top1_curve(source="kaipan", days=20)
        self.assertIn("top5_names", data,
                      "top5_names 是 helper 加的便利字段")
        self.assertIsInstance(data["top5_names"], list)
        self.assertLessEqual(len(data["top5_names"]), 5)
        # 每个 name 都不为 None (helper 已用 if str(i) in name_dict 过滤)
        for n in data["top5_names"]:
            self.assertIsNotNone(n, "top5_names 不应包含 None")
        self.assertIn("date", data)
        self.assertIn("name", data)

    def test_plate_strength_returns_echarts_dict(self):
        data = plate_strength(platecode="886084", days=20)
        self.assertIsInstance(data, dict)
        self.assertIn("date", data)
        self.assertIn("legend", data,
                      "legend key 必须存在 (即使值为 null)")
        self.assertIsInstance(data["date"], list)


# ============== 4. find_dragon_kings 自动路由 source =============
class TestSourceAutoPick(unittest.TestCase):
    """find_dragon_kings 内部按板块代码前缀自动选 source — 关键设计:
       88x → ths (同花顺)
       80x/803x → kaipan (开盘啦)
       用户不需关心,直接传 platecode。
    """

    def test_88x_routes_to_ths(self):
        # 886084 = F5G概念; 88x 走 ths, 应能拿到 dates
        res = find_dragon_kings(platecode="886084", days=20, top_n=5)
        self.assertGreater(len(res["dates"]), 0,
                           "886084 (88x→ths) 必须能拿到 dates")

    def test_80x_routes_to_kaipan(self):
        # 801807 = 算力; 80x 必须走 kaipan, 否则同花顺源里查不到
        res = find_dragon_kings(platecode="801807", days=20, top_n=5)
        self.assertGreater(len(res["dates"]), 0,
                           "801807 (80x→kaipan) 必须能拿到 dates")
        # daily_heads 必须有内容 (算力是热门板块, 20 天必有龙头)
        total_heads = sum(len(d["heads"]) for d in res["daily_heads"])
        self.assertGreater(total_heads, 0,
                           "801807 算力板块 20 天累计龙头数不应为 0 — "
                           "若为 0 极可能是 source 选错路由失败")


# ============== 5. CLI 4 个子命令 (subprocess) ==================
class TestCLI(unittest.TestCase):
    """4 个 CLI 子命令的 text + json 双模式输出健康度。"""

    def _run_cli(self, *args, timeout=45):
        r = subprocess.run(
            ["python3", PLATEROTAT, *args],
            capture_output=True, text=True, timeout=timeout,
        )
        self.assertEqual(r.returncode, 0,
                         f"CLI 失败 (args={args}):\n"
                         f"STDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}")
        return r.stdout

    # --- today ---
    def test_cli_today_text_default(self):
        out = self._run_cli("today", "--source", "kaipan",
                            "--n", "3", "--days", "20")
        self.assertIn("Top", out, "text 输出应有 Top 标题")
        self.assertIn("板块", out, "text 输出应有 '板块' 字样")
        # 至少出现一次 # 排名标记
        self.assertRegex(out, r"#\s*\d+", "text 输出应含 #N 排名行")

    def test_cli_today_json_kaipan(self):
        out = self._run_cli("today", "--source", "kaipan",
                            "--n", "3", "--days", "20", "--json")
        rows = json.loads(out)
        self.assertIsInstance(rows, list)
        self.assertLessEqual(len(rows), 3)
        if rows:
            for r in rows:
                self.assertIn("code", r)
                self.assertIn("rank", r)
                self.assertEqual(r["value_type"], "score")

    def test_cli_today_json_ths_pct(self):
        out = self._run_cli("today", "--source", "ths",
                            "--n", "3", "--days", "20", "--json")
        rows = json.loads(out)
        for r in rows:
            self.assertEqual(r["value_type"], "pct")
            self.assertTrue(r["value"].endswith("%"))

    # --- wangking ---
    def test_cli_wangking_json_88x(self):
        out = self._run_cli("wangking", "886084",
                            "--days", "20", "--n", "5", "--json")
        d = json.loads(out)
        self.assertEqual(d["platecode"], "886084")
        self.assertIn("kings", d)
        self.assertIn("daily_heads", d)
        self.assertIn("dates", d)
        self.assertLessEqual(len(d["kings"]), 5)

    def test_cli_wangking_text_88x(self):
        out = self._run_cli("wangking", "886084",
                            "--days", "20", "--n", "3")
        self.assertIn("妖王榜", out)
        self.assertIn("886084", out)

    def test_cli_wangking_json_80x(self):
        """覆盖 80x→kaipan 自动路由的 CLI 路径。"""
        out = self._run_cli("wangking", "801807",
                            "--days", "20", "--n", "5", "--json")
        d = json.loads(out)
        self.assertEqual(d["platecode"], "801807")
        self.assertGreater(len(d["dates"]), 0)

    # --- curve ---
    def test_cli_curve_json(self):
        out = self._run_cli("curve", "--source", "kaipan",
                            "--days", "20", "--json")
        d = json.loads(out)
        self.assertIn("top5_names", d)
        self.assertIn("date", d)
        self.assertIn("name", d)

    def test_cli_curve_text(self):
        out = self._run_cli("curve", "--source", "kaipan", "--days", "20")
        self.assertIn("Top5 板块", out)
        self.assertIn("日期序列", out)

    # --- strength ---
    def test_cli_strength_json(self):
        out = self._run_cli("strength", "886084", "--days", "20", "--json")
        d = json.loads(out)
        self.assertIn("date", d)
        self.assertIn("legend", d)

    def test_cli_strength_text(self):
        out = self._run_cli("strength", "886084", "--days", "20")
        self.assertIn("886084", out)
        self.assertIn("强度时序", out)

    # --- 错误路径: 缺参/非法参数应明确报错 ---
    def test_cli_no_subcommand_exits_nonzero(self):
        r = subprocess.run(
            ["python3", PLATEROTAT],
            capture_output=True, text=True, timeout=10,
        )
        self.assertNotEqual(r.returncode, 0,
                            "无子命令时 argparse 应报错 (required=True)")

    def test_cli_bad_source_rejected(self):
        r = subprocess.run(
            ["python3", PLATEROTAT, "today", "--source", "xxx"],
            capture_output=True, text=True, timeout=10,
        )
        self.assertNotEqual(r.returncode, 0,
                            "非法 --source 必须被 argparse choices 拒绝")


if __name__ == "__main__":
    unittest.main(verbosity=2)
