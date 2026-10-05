# 2905273808qq-hue/-api

自己的电视盒子（影视TV / TVBox）直播配置仓库。直播源放在这里，**地址永远受你自己控制**，上游作者闭站、删文件、改源都影响不到你。

对应仓库：https://github.com/2905273808qq-hue/-api

---

## 1. 目录结构（上传后仓库里应该长这样）

```
2905273808qq-hue/-api
├── tvbox.json                     ← 配置入口（影视TV「配置地址」填这个）
├── README.md
├── .gitignore
├── output/
│   ├── result.m3u                 ← 主直播源（1432 个频道，约 398KB）
│   └── result.txt                 ← 备用源（txt 格式，约 145KB）
├── sources.txt                    ← 上游轮换清单，换源时改这里
├── scripts/
│   ├── health.py                  ← 巡检脚本（零第三方依赖）
│   └── fetch.sh                   ← 换源脚本
└── .github/workflows/
    └── health.yml                 ← 每日自动养源
```

## 2. 三个地址前缀（实测结论）

仓库名以 `-` 开头（`-api`），已实测三种前缀都能正常取到文件：

| 前缀 | 格式 | 实测 | 说明 |
| --- | --- | --- | --- |
| **Pages（推荐）** | `2905273808qq-hue.github.io/-api/文件` | 未开（404） | 不限大小，走 Cloudflare 国内能开。**大 EPG 只能走它** |
| **jsDelivr** | `cdn.jsdelivr.net/gh/2905273808qq-hue/-api@main/文件` | ✅ 200 / 511B 真实内容 | 整包超 50MB 会 403，只适合小文件 |
| **raw** | `raw.githubusercontent.com/2905273808qq-hue/-api/main/文件` | ✅ 200 / 511B 真实内容 | 不限大小，国内常超时，可拼 `gh-proxy.com/` 前缀 |

## 3. 影视TV 里怎么填

| 想做什么 | 填这一条 |
| --- | --- |
| 完整配置（推荐） | `https://2905273808qq-hue.github.io/-api/tvbox.json` |
| 只要直播源 | `https://2905273808qq-hue.github.io/-api/output/result.m3u` |
| 必须要能连（raw 备用） | `https://gh-proxy.com/https://raw.githubusercontent.com/2905273808qq-hue/-api/main/output/result.m3u` |

路径：影视TV → **设置 → 配置地址**（或设置 → 直播源 → 远程）。

## 4. 本地巡检：手动剔除失效源

```bash
python scripts/health.py --limit 50      # 先试 50 台，看耗时和准确率
python scripts/health.py --dry-run       # 只看会删哪些，不落盘
python scripts/health.py --workers 32    # 全量 1432 台，约 1-3 分钟
```

只调系统自带的 `curl`，不用装任何 Python 包。第一次运行会把原文件备份成 `result.m3u.bak`。

## 5. 自动巡检：每天两次

`.github/workflows/health.yml` 每 12 小时跑一次，并发探测全部播放地址，把失效行删掉后自动提交回 main；没变化就不动仓库。

首次看效果：**Actions** 页签 → 右边 `直播源每日巡检` → **Run workflow**，手动跑一次。

改频率就编辑 `cron: '0 */12 * * *'`，用的是 **UTC**——`0 */12 * * *` 对应北京时间 08:00 和 20:00。

## 6. 换源

**改 `sources.txt`**（一行一个上游，从上往下取第一个能下通的），然后：

```bash
bash scripts/fetch.sh
```

常用上游（已带镜像前缀，`raw.githubusercontent.com` 国内不稳）：

```
https://lightconer.github.io/iptv-api/result.m3u
https://gh-proxy.com/https://raw.githubusercontent.com/CCSH/IPTV/refs/heads/main/live.m3u
https://gh-proxy.com/https://raw.githubusercontent.com/zilong7728/Collect-IPTV/refs/heads/main/best_sorted.m3u
```

## 7. 踩过的坑

- 仓库必须 **Public**，Private 的 Pages 要付费。
- 文件名、目录名只用英文小写——jsDelivr 区分大小写。
- Pages 首次发布要 1–2 分钟，还 404 别慌。改动后 Pages 同样有延迟；jsDelivr 缓存更久，必要时在地址后加 `?v=` 时间戳强制刷新。
- 改坏了一步就能回退：仓库主页 **History** → 选上一个提交 → **Revert**。
- 直播源里的台标和 EPG 地址是上游作者写死的（指向他的 CDN），换源后台标会变。想彻底自控得把 `epg.gz` 也传上来再改 `x-tvg-url`。
- 版权提醒：这类源多是公开测试地址，自用可以，别拿去分发。
