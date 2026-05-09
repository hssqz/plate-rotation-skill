#!/usr/bin/env python3
# ==================================================================
# plate-rotation 统一调用器
#
#   姿势 1 (form/query 简单参数):
#       fetch.py main /api/getPlateRotatData from=ths days=20
#   姿势 2 (复杂参数走 JSON):
#       fetch.py main /api/getLongByPlate -p '{"platecode":"886084","days":20}'
#   姿势 3 (探测/自检 URL):
#       fetch.py main /api/getPlateRotatData from=ths days=20 -v
#
# host alias: main | data | x | ext
#   ext = 完整 URL (path 已含 host); 其余 alias 在 HOSTS 字典内部决议。
#
# Cookie 通常无需配置, 后端只校验 Referer (本调用器自动注入)。
# 如需 cookie, 优先读环境变量 PR_COOKIE, 其次 ~/.plate_rotation_cookie。
# ==================================================================
import argparse, json, os, sys, urllib.parse, urllib.request, urllib.error
from pathlib import Path

HOSTS = {
    "main": "https://duanxianxia.com",
    "data": "https://ds.duanxianxia.com",
    "x":    "https://x.duanxianxia.cn",
}
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
      "(KHTML, like Gecko) Version/17.0 Safari/605.1.15")
COOKIE_FILE = Path.home() / ".plate_rotation_cookie"

# ------------------------------------------------------------------
def load_cookie(host_alias: str) -> str:
    """读取 cookie。文件格式: 一行 'domain=cookie_string'。"""
    if env := os.environ.get("PR_COOKIE"):
        return env
    if not COOKIE_FILE.exists():
        return ""
    for line in COOKIE_FILE.read_text().splitlines():
        if "=" not in line: continue
        _, _, cookie = line.partition("=")
        return cookie.strip()
    return ""

# ------------------------------------------------------------------
def build_url(host_alias: str, path: str) -> str:
    if host_alias == "ext" or path.startswith("http"):
        return path
    base = HOSTS.get(host_alias)
    if base is None:
        sys.exit(f"[fetch] ERROR: unknown host alias '{host_alias}'. valid: main|data|x|ext")
    if not path.startswith("/"):
        path = "/" + path
    return base + path

# ------------------------------------------------------------------
def parse_kv_args(kv_args):
    out = {}
    for a in kv_args:
        if "=" not in a:
            sys.exit(f"[fetch] ERROR: invalid kv arg '{a}', expected key=value")
        k, v = a.split("=", 1)
        out[k] = v
    return out

# ------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="plate-rotation 统一调用器")
    ap.add_argument("host", help="host alias: main | data | x | ext")
    ap.add_argument("path", help="endpoint path (or full URL when host=ext)")
    ap.add_argument("kv", nargs="*", help="form/query: key=value …")
    ap.add_argument("-p", "--params-json", help="JSON 形式的参数 (优先级 > kv)")
    ap.add_argument("-X", "--method", default="POST", choices=["GET", "POST"], help="HTTP method (default: POST)")
    ap.add_argument("-v", "--verbose", action="store_true", help="打印 URL+body 自检")
    ap.add_argument("--no-cookie", action="store_true", help="不发 cookie")
    ap.add_argument("--timeout", type=int, default=15)
    ap.add_argument("--raw", action="store_true", help="输出原始字符串（不格式化 JSON）")
    args = ap.parse_args()

    # 解析参数 -p > kv
    if args.params_json:
        try:
            params = json.loads(args.params_json)
        except json.JSONDecodeError as e:
            sys.exit(f"[fetch] ERROR: invalid JSON in -p: {e}")
        if args.kv:
            sys.exit("[fetch] ERROR: 不能同时使用 -p 和 key=value，二选一")
    else:
        params = parse_kv_args(args.kv)

    url = build_url(args.host, args.path)
    cookie = "" if args.no_cookie else load_cookie(args.host)

    headers = {
        "User-Agent": UA,
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://duanxianxia.com/web/main",
        "Origin": "https://duanxianxia.com",
        "X-Requested-With": "XMLHttpRequest",
    }
    if cookie:
        headers["Cookie"] = cookie

    body = None
    if args.method == "GET":
        if params:
            qs = urllib.parse.urlencode(params, doseq=True)
            sep = "&" if "?" in url else "?"
            url = url + sep + qs
    else:  # POST
        if params:
            body = urllib.parse.urlencode(params, doseq=True).encode("utf-8")
            headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"

    if args.verbose:
        print(f"[fetch] {args.method} {url}", file=sys.stderr)
        if body:
            print(f"[fetch] body: {body.decode('utf-8')[:300]}", file=sys.stderr)
        if cookie:
            print(f"[fetch] cookie: {cookie[:60]}... ({len(cookie)} chars)", file=sys.stderr)

    req = urllib.request.Request(url, data=body, headers=headers, method=args.method)
    try:
        with urllib.request.urlopen(req, timeout=args.timeout) as r:
            txt = r.read().decode("utf-8", errors="replace")
            status = r.status
    except urllib.error.HTTPError as e:
        body_err = e.read().decode("utf-8", errors="replace")
        print(f"[fetch] HTTP {e.code}: {body_err[:400]}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"[fetch] FAIL: {e}", file=sys.stderr)
        sys.exit(2)

    if args.raw:
        sys.stdout.write(txt)
        return
    # 尝试 JSON 美化, 失败回退到 raw
    try:
        obj = json.loads(txt)
        print(json.dumps(obj, ensure_ascii=False, indent=2))
    except Exception:
        sys.stdout.write(txt)

if __name__ == "__main__":
    main()
