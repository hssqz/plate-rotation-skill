#!/usr/bin/env python3
"""
[INPUT]: 依赖 stdlib (argparse/json/os/sys/urllib);依赖同目录 cache.py 的 cache_get/cache_put
[OUTPUT]: 对外提供 CLI 入口 (3 种参数姿势) + main() 函数;打印 response 到 stdout
[POS]: scripts/ 的网络调用原子层,统一 cookie/Referer/UA + retry + cache;
       上游被 platerotat.py 的 _call() subprocess 调用,与 parsers.py 解耦
[PROTOCOL]: 变更时更新此头部,然后检查 CLAUDE.md
"""
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
#
# 鲁棒性升级 (2026-05-12):
#   - retry: 429 / 5xx / 网络异常 自动指数退避 (最多 3 次,1s/2s/4s)
#   - cache: POST 请求默认走 ~/.cache/plate-rotation/ 落盘缓存,TTL=1h
#     - --no-cache / PR_CACHE_DISABLE=1 关闭
#     - --cache-ttl SEC 调整新鲜度阈值
# ==================================================================
import argparse, json, os, sys, time, urllib.parse, urllib.request, urllib.error
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from cache import cache_get, cache_put, DEFAULT_TTL  # noqa: E402

HOSTS = {
    "main": "https://duanxianxia.com",
    "data": "https://ds.duanxianxia.com",
    "x":    "https://x.duanxianxia.cn",
}
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
      "(KHTML, like Gecko) Version/17.0 Safari/605.1.15")
COOKIE_FILE = Path.home() / ".plate_rotation_cookie"

# retry 策略: 429/502/503/504 + 任何网络层异常 → 指数退避;4xx 其余直接抛
RETRY_HTTP_CODES = {429, 500, 502, 503, 504}
DEFAULT_MAX_RETRIES = 3
RETRY_BASE_SLEEP = 1.0  # 1s, 2s, 4s


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
def do_request(req: urllib.request.Request,
               timeout: int,
               max_retries: int = DEFAULT_MAX_RETRIES,
               verbose: bool = False) -> str:
    """
    带指数退避的 HTTP 请求执行器。

    返回 decode 后的 response body。
    抛 RuntimeError 表示最终失败(含详细原因)。
    """
    last_err = None
    for attempt in range(max_retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as e:
            body_err = e.read().decode("utf-8", errors="replace")
            last_err = f"HTTP {e.code}: {body_err[:300]}"
            if e.code not in RETRY_HTTP_CODES:
                raise RuntimeError(last_err)  # 4xx 等非重试码,直接退出
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            last_err = f"network: {e}"
        except Exception as e:  # noqa: BLE001
            last_err = f"unexpected: {e}"
            raise RuntimeError(last_err)

        if attempt >= max_retries:
            break
        sleep_s = RETRY_BASE_SLEEP * (2 ** attempt)
        if verbose:
            print(f"[fetch] retry {attempt + 1}/{max_retries} after {sleep_s}s "
                  f"({last_err})", file=sys.stderr)
        time.sleep(sleep_s)
    raise RuntimeError(f"[fetch] all retries failed: {last_err}")


# ------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="plate-rotation 统一调用器")
    ap.add_argument("host", help="host alias: main | data | x | ext")
    ap.add_argument("path", help="endpoint path (or full URL when host=ext)")
    ap.add_argument("kv", nargs="*", help="form/query: key=value …")
    ap.add_argument("-p", "--params-json", help="JSON 形式的参数 (优先级 > kv)")
    ap.add_argument("-X", "--method", default="POST", choices=["GET", "POST"], help="HTTP method (default: POST)")
    ap.add_argument("-v", "--verbose", action="store_true", help="打印 URL+body+retry 自检")
    ap.add_argument("--no-cookie", action="store_true", help="不发 cookie")
    ap.add_argument("--no-cache", action="store_true", help="禁用本次请求的缓存读写")
    ap.add_argument("--cache-ttl", type=int, default=DEFAULT_TTL,
                    help=f"缓存新鲜度阈值(秒),默认 {DEFAULT_TTL}")
    ap.add_argument("--max-retries", type=int, default=DEFAULT_MAX_RETRIES)
    ap.add_argument("--timeout", type=int, default=15)
    ap.add_argument("--raw", action="store_true", help="输出原始字符串（不格式化 JSON）")
    args = ap.parse_args()

    # ------------------ 解析参数 -p > kv ------------------
    if args.params_json:
        try:
            params = json.loads(args.params_json)
        except json.JSONDecodeError as e:
            sys.exit(f"[fetch] ERROR: invalid JSON in -p: {e}")
        if args.kv:
            sys.exit("[fetch] ERROR: 不能同时使用 -p 和 key=value,二选一")
    else:
        params = parse_kv_args(args.kv)

    url = build_url(args.host, args.path)
    cookie = "" if args.no_cookie else load_cookie(args.host)

    # ------------------ 缓存命中分支 ------------------
    cache_enabled = (not args.no_cache) and args.method == "POST"
    if cache_enabled:
        hit = cache_get(args.host, args.path, params, ttl=args.cache_ttl)
        if hit is not None:
            if args.verbose:
                print(f"[fetch] cache HIT {args.host}{args.path} {params}",
                      file=sys.stderr)
            _output(hit, raw=args.raw)
            return

    # ------------------ 构造请求 ------------------
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

    # ------------------ 执行请求 (含 retry) ------------------
    req = urllib.request.Request(url, data=body, headers=headers, method=args.method)
    try:
        txt = do_request(req, timeout=args.timeout,
                         max_retries=args.max_retries, verbose=args.verbose)
    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        sys.exit(2)

    # ------------------ 写缓存 + 输出 ------------------
    if cache_enabled:
        cache_put(args.host, args.path, params, txt)
    _output(txt, raw=args.raw)


# ------------------------------------------------------------------
def _output(txt: str, raw: bool):
    if raw:
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
