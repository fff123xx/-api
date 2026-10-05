#!/usr/bin/env bash
# 换源：从 sources.txt 里从上往下取第一个能下通的，覆盖 output/result.m3u
# 用法： bash scripts/fetch.sh
set -u
cd "$(dirname "$0")/.."

SRC_LIST="sources.txt"
OUT="output/result.m3u"

[ -f "$SRC_LIST" ] || { echo "找不到 $SRC_LIST"; exit 1; }
[ -f "$OUT" ] && cp "$OUT" "$OUT.bak"

ok=0
while IFS= read -r line; do
  case "$line" in ''|\#*) continue ;; esac
  printf '尝试 %s ... ' "$line"
  code=$(curl -sL -m 40 -o "$OUT" -w '%{http_code}' "$line")
  size=$(wc -c < "$OUT" 2>/dev/null || echo 0)
  if [ "${code:0:1}" = "2" ] && [ "$size" -gt 1024 ]; then
    echo "成功（${size} 字节）"
    ok=1
    break
  fi
  echo "失败 code=$code size=$size"
  rm -f "$OUT"
done < "$SRC_LIST"

if [ "$ok" = "1" ]; then
  echo "已写入 $OUT"
  echo "接着可以跑： python scripts/health.py --limit 50  先小范围试"
else
  echo "全部源都失败了，已回滚（原文件在 $OUT.bak）"
  [ -f "$OUT.bak" ] && mv "$OUT.bak" "$OUT"
  exit 1
fi
