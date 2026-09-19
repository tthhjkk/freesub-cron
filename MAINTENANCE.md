# freesub-cron 维护手册

这套系统让 YouTube 节点订阅**全自动维护在 GitHub 上**，电脑 0 参与（无本地 cron、无代理、关机不影响）。

## 架构

```
GitHub 免费 runner（每 6 小时 schedule: 0 */6 * * * UTC + 手动 dispatch）
  └─ 本仓 workflow: .github/workflows/freesub-autosync.yml
  └─ 拉上游 hezhanleiok/freesub 最新 scripts/main_v2.py
  └─ 套定制：节点后缀 -github（SUFFIX）+ 你自己的订阅源（custom-sources.txt）
  └─ 经 Contents API 推到你 fork: tthhjkk/freesub- 的 main_v2.py
  └─ 触发 fork 构建 workflow (id 361298492)
       └─ 测活 1000+ 节点 → 生成 clash/singbox/v2ray 订阅 → 刷新 jsDelivr CDN
```

## 仓库分工

| 仓库 | 作用 |
|---|---|
| `tthhjkk/freesub-` | 主力 fork：构建 + 订阅产出（CDN 吃它） |
| `tthhjkk/freesub-cron` | 调度器：6h 定时器 + 自动同步上游 + 本手册 |
| `hezhanleiok/freesub` | 上游作者仓（自动跟随，无需手动操作） |

## 订阅地址（直接导入 Clash / sing-box / V2RayN）

- Clash: `https://cdn.jsdelivr.net/gh/tthhjkk/freesub-@main/output/clash.yaml`
- sing-box: `https://cdn.jsdelivr.net/gh/tthhjkk/freesub-@main/output/singbox.json`
- V2Ray: `https://cdn.jsdelivr.net/gh/tthhjkk/freesub-@main/output/v2ray.txt`
- 家宽专区: `.../output/residential-by-country/TW.txt`（TW/US/GB/JP/DE）

## 常用维护（手机开 GitHub 网页即可，全程不用电脑）

| 需求 | 操作 |
|---|---|
| 加你自己的订阅源 | 编辑本仓 `custom-sources.txt`（每行一个链接，`#` 注释），保存后 6h 内自动注入并重建 |
| 换节点后缀 | 编辑 `.github/workflows/freesub-autosync.yml` 里的 `SUFFIX: github` |
| 手动跑一轮 | 本仓 Actions 页 → `freesub-autosync` → Run workflow → main |
| 看运行状态 | 本仓 Actions 页；fork 构建在 `tthhjkk/freesub-` 的 Actions 页 |

## token / secret（唯一钥匙，无过期）

- 名字：`freesub-cron`（classic PAT，repo + workflow，No expiration）
- 存放：本仓 Actions secret `SYNC_TOKEN`（加密存储，仅本仓 runner 可解密）；本地备份在维护机 `~/.hermes/freesub_gh_token`
- **修改/撤销路径**（注意：secret 修改必须走网页 UI，本机 API 环境的 public-key 端点是桩）：
  - 改 secret：`github.com/tthhjkk/freesub-cron/settings/secrets/actions/SYNC_TOKEN` → Edit
  - 撤 token：`github.com/settings/tokens`（删除后需同步换掉 secret + 本地备份，否则全链断）

## 故障排查

| 症状 | 原因/处理 |
|---|---|
| 调度仓 run 403 rate limit | runner 共享 IP 撞限流；脚本已全程带 token 请求，若复发看是否 token 被撤 |
| fork 构建失败 | 上游 pipeline 变更或节点源失效；看 `freesub-` Actions 日志，必要时手动同步上游代码 |
| 订阅不更新 | 依次查：调度仓 schedule 是否在跑 → fork 构建是否 success → CDN 5 分钟缓存 |
| 整个系统不动 | token 是否被误撤（secret 失效会全链 401）→ 重建 token + 换 secret |

## 历史

- 2026-09-18：fork 部署 + 本机 cron 触发
- 2026-09-19：迁移为 GitHub 原生 schedule（本仓），本机 cron 已删；token 改无过期；本手册上线
