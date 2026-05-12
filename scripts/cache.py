#!/usr/bin/env python3
"""
[INPUT]: 依赖 stdlib (hashlib/json/os/time/pathlib);无第三方依赖
[OUTPUT]: 对外提供 cache_get / cache_put / cache_clear / cache_stats / cache_disabled
[POS]: scripts/ 的缓存原子层,被 fetch.py 在 POST 请求前后调用;
       与 fetch.py 平级,与 parsers.py / platerotat.py 解耦
[PROTOCOL]: 变更时更新此头部,然后检查 CLAUDE.md
"""
# ==================================================================
# plate-rotation 本地缓存层
#
# 设计目标:
#   - 节流: 同一参数组合在 TTL 内只发一次网络请求
#   - 解耦: fetch.py 调用层不感知 cache 实现细节
#   - 可关: 环境变量 PR_CACHE_DISABLE=1 全局关闭
#
# 落盘路径: ~/.cache/plate-rotation/{key[:2]}/{key}.json
# Key 构成: sha1(host + "\n" + path + "\n" + sorted_form_kv)
# TTL 策略: 默认 3600s (1 小时)
#   - 盘中"今日"数据 → 1 小时足够新鲜,又能避免重复请求
#   - 历史 N 日数据 → 一小时内不会变化,缓存命中率高
#   - 用户需要强刷新 → 传 ttl=0 或 export PR_CACHE_DISABLE=1
#
# 文件格式 (JSON):
#   {"ts": 1715414400, "host": "...", "path": "...",
#    "params": {...}, "body": "raw response text"}
# ==================================================================
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Optional

CACHE_ROOT = Path(os.environ.get("PR_CACHE_DIR",
                                 str(Path.home() / ".cache" / "plate-rotation")))
DEFAULT_TTL = int(os.environ.get("PR_CACHE_TTL", "3600"))


# ------------------------------------------------------------------
def cache_disabled() -> bool:
    """全局开关。环境变量 PR_CACHE_DISABLE=1 时返回 True。"""
    return os.environ.get("PR_CACHE_DISABLE", "").strip() in ("1", "true", "yes")


# ------------------------------------------------------------------
def _key(host: str, path: str, params: dict) -> str:
    """稳定哈希: 参数按 key 排序后拼接,保证 days=20&from=ths 与 from=ths&days=20 同 key。"""
    kv = "&".join(f"{k}={params[k]}" for k in sorted(params.keys()))
    raw = f"{host}\n{path}\n{kv}".encode("utf-8")
    return hashlib.sha1(raw).hexdigest()


def _path_of(key: str) -> Path:
    return CACHE_ROOT / key[:2] / f"{key}.json"


# ------------------------------------------------------------------
def cache_get(host: str, path: str, params: dict,
              ttl: int = DEFAULT_TTL) -> Optional[str]:
    """命中返回原始 response body 字符串;未命中 / 过期 / 禁用返回 None。"""
    if cache_disabled() or ttl <= 0:
        return None
    fp = _path_of(_key(host, path, params))
    if not fp.exists():
        return None
    try:
        obj = json.loads(fp.read_text("utf-8"))
    except Exception:
        # 损坏文件 → 删除并 miss
        try: fp.unlink()
        except OSError: pass
        return None
    if (time.time() - obj.get("ts", 0)) > ttl:
        return None  # 过期 (保留文件,下次 put 会覆盖)
    return obj.get("body")


def cache_put(host: str, path: str, params: dict, body: str) -> None:
    """落盘 response body。禁用时 no-op。"""
    if cache_disabled():
        return
    fp = _path_of(_key(host, path, params))
    fp.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "ts": int(time.time()),
        "host": host,
        "path": path,
        "params": params,
        "body": body,
    }
    tmp = fp.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, fp)  # 原子写,避免半写文件


# ------------------------------------------------------------------
def cache_clear(older_than: int = 0) -> int:
    """清理缓存。older_than>0 时只清超过 N 秒的;返回删除文件数。"""
    if not CACHE_ROOT.exists():
        return 0
    now = time.time()
    n = 0
    for fp in CACHE_ROOT.rglob("*.json"):
        if older_than > 0:
            try:
                obj = json.loads(fp.read_text("utf-8"))
                if (now - obj.get("ts", 0)) <= older_than:
                    continue
            except Exception:
                pass
        try:
            fp.unlink(); n += 1
        except OSError:
            pass
    return n


def cache_stats() -> dict:
    """诊断用: 返回 {count, total_bytes, root}。"""
    if not CACHE_ROOT.exists():
        return {"count": 0, "total_bytes": 0, "root": str(CACHE_ROOT)}
    files = list(CACHE_ROOT.rglob("*.json"))
    return {
        "count": len(files),
        "total_bytes": sum(f.stat().st_size for f in files),
        "root": str(CACHE_ROOT),
    }


# ------------------------------------------------------------------
if __name__ == "__main__":
    # 简易自检 CLI: python3 cache.py stats | clear | clear --older 86400
    import sys
    if len(sys.argv) < 2 or sys.argv[1] == "stats":
        print(json.dumps(cache_stats(), ensure_ascii=False, indent=2))
    elif sys.argv[1] == "clear":
        older = 0
        if "--older" in sys.argv:
            older = int(sys.argv[sys.argv.index("--older") + 1])
        n = cache_clear(older_than=older)
        print(f"[cache] removed {n} files")
    else:
        sys.exit(f"usage: cache.py stats | clear [--older SEC]")
