#!/usr/bin/env python3
"""直播源巡检：并发探测每个播放地址，剔除失效行。零第三方依赖，只调系统自带的 curl。

用法：
    python scripts/health.py --limit 50            # 只测前 50 个频道（试跑）
    python scripts/health.py                       # 全量巡检，原地改写 result.m3u
    python scripts/health.py --dry-run             # 只看会删哪些，不写文件

注意：只支持 m3u 格式（一个 #EXTINF 行 + 其后的播放地址行）。txt 格式请先转成 m3u。
"""

import argparse
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

TIMEOUT = 8
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


def probe(url):
    """返回 True 表示这个地址还能播。用 Range 取前 2KB 就够，比整首下快得多。"""
    cmd = [
        "curl", "-sL", "-m", str(TIMEOUT),
        "-r", "0-2048", "-o", os.devnull,
        "-w", "%{http_code}", "-A", UA,
        url,
    ]
    try:
        r = subprocess.run(
            cmd, capture_output=True, text=True, timeout=TIMEOUT + 6
        )
    except Exception:
        return False
    code = (r.stdout or "").strip().split()[-1] if r.stdout else ""
    return code.startswith("2")


def parse(text):
    """把 m3u 拆成若干个频道块，各块的第一行是 #EXTINF。"""
    blocks, cur = [], []
    for ln in text.splitlines():
        if ln.startswith("#EXTINF"):
            if cur:
                blocks.append(cur)
            cur = [ln]
        elif cur:
            cur.append(ln)
    if cur:
        blocks.append(cur)
    return blocks


def urls_of(block):
    """取出块里的播放地址行（非空、不是 # 注释）。"""
    return [
        ln.strip() for ln in block[1:]
        if ln.strip() and not ln.strip().startswith("#")
    ]


def strip_leading_comments(text):
    """捞文件头（#EXTM3U 那一行及它之前的注释），这些要原样保留。"""
    head = []
    for ln in text.splitlines():
        if ln.startswith("#EXTINF"):
            break
        head.append(ln)
    return head


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", default="output/result.m3u")
    ap.add_argument("--workers", type=int, default=24)
    ap.add_argument("--limit", type=int, default=0, help="只测前 N 个频道，0 表示全部")
    ap.add_argument("--dry-run", action="store_true", help="只报告不落盘")
    args = ap.parse_args()

    if not os.path.exists(args.file):
        sys.exit("找不到文件：%s" % args.file)

    with open(args.file, "r", encoding="utf-8", errors="ignore") as f:
        raw = f.read()

    head = strip_leading_comments(raw)
    blocks = parse(raw)
    if not blocks:
        sys.exit("这个文件里没解析到 #EXTINF，可能不是 m3u 格式")

    if args.limit:
        blocks = blocks[: args.limit]

    print("共 %d 个频道，并发 %d 路探测 ..." % (len(blocks), args.workers))

    keep, dead = [], []

    def do(block):
        live = [u for u in urls_of(block) if probe(u)]
        return block, live

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for block, live in pool.map(do, blocks):
            if live:
                keep.append([block[0]] + live)
            else:
                dead.append(block[0])

    total_urls = sum(len(urls_of(b)) for b in blocks)
    dead_urls = sum(len(urls_of(b)) for b in blocks) - sum(len(k) - 1 for k in keep)
    print("结果：保留 %d 台，剔除 %d 台（%d 个地址不通）"
          % (len(keep), len(dead), dead_urls))
    if dead:
        print("--- 被剔除的频道 ---")
        for b in dead[:20]:
            name = b.split(",", 1)[-1].strip() if "," in b else b
            print("  -", name[:40])
        if len(dead) > 20:
            print("  ... 其余 %d 条省略" % (len(dead) - 20))

    if args.dry_run:
        print("（dry-run，未写文件）")
        return

    out = "\n".join(head + [ln for b in keep for ln in b]) + "\n"
    bak = args.file + ".bak"
    if not os.path.exists(bak):
        with open(bak, "w", encoding="utf-8") as f:
            f.write(raw)
    with open(args.file, "w", encoding="utf-8") as f:
        f.write(out)
    print("已写回 %s（原文件备份到 %s）" % (args.file, bak))


if __name__ == "__main__":
    main()
