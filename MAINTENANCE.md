# freesub-cron 维护手册

这套系统让 YouTube 节点订阅**全自动维护在 GitHub 上**，你的电脑 0 参与。

## 架构

```
GitHub 免费 runner（每 6 小时自动，schedule: 0 */6 * * * UTC）
  └─ 本仓 workflow: .github/workflows/freesub-autosync.yml
  └─ 拉上游 hezhanleiok/freesub 最新 main_v2.py
  └─ 套定制：节点后缀 -github + 你自己的订阅源（custom-sources.txt）
  └─ 经 Contents API 推到你 fork: tthhjkk/freesub-
  └─ 触发 fork 的构建 workflow (id 361298492)
       └─ 测活 1000+ 节点 → 生成 clash/singbox/v2ray 订阅 → 刷 CDN
```

## 订阅地址（直接导入客户端）

- Clash: `https://cdn.jsdelivr.net/gh/tthhjkk/freesub-@main/output/clash.yaml`
- sing-box: `https://cdn.jsdelivr.net/gh/tthhjkk/freesub-@main/output/singbox.json`
- V2Ray: `https://cdn.jsdelivr.net/gh/tthhjkk/freesub-@main/output/v2ray.txt`

## 常用维护（都不需要电脑跑任务，手机/任何设备开 GitHub 网页即可）

| 需求 | 操作 |
|---|---|
| 加你自己的订阅源 | 编辑本仓 `custom-sources.txt`（每行一个链接，# 注释），保存即 6h 内生效 |
| 换节点后缀 | 编辑 `.github/workflows/freesub-autosync.yml` 里的 `SUFFIX` |
| 手动跑一轮 | 本仓 Actions 页 → fre
