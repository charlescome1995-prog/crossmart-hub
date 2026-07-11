# crossmart-hub

CrossMart 五站（Selector / Monitor / Listing / Ops / Simulator）**共享数据层**。

## 定位

一个极薄的"影子副本"仓库：
- 5 站 push 各自的产物 JSON 到 `data/`
- 5 站 pull 别人的 JSON 做交叉引用
- GitHub Pages 提供静态只读访问

**不做**：微服务、消息队列、数据库。**要做**：JSON 契约 + GitHub Pages。

## 目录

```
data/
  selection.json    ← Selector 每周推
  monitor.json      ← Monitor 每次抓取推
  listing.json      ← Listing 生成后推
  ops.json          ← Ops 每日 06:06 推
  predictions.json  ← Simulator 每次预测推
  hub.json          ← 五站总览 + 交叉索引（由 Actions 生成）
dashboard.html      ← 五站总览首页
schemas/            ← 每个 JSON 的 schema 说明 (未来接入 jsonschema 校验)
```

## 数据契约（当前 v1）

见 `schemas/`。每个 JSON 必带：
- `schema_version`（字符串，如 `"v1"`）
- `generated_at`（ISO8601 时间戳）
- `source`（推送方站名，如 `"crossmart-selector"`）

## 使用

### 站点端 push

在各站的每日/每周脚本末尾追加 `scripts/push_to_hub.sh`（模板见 hub 仓库根 `docs/`）。

### 站点端 pull

前端：`fetch("https://charlescome1995-prog.github.io/crossmart-hub/data/monitor.json?v=" + Date.now())`

后端脚本：
```python
import urllib.request, json
url = "https://charlescome1995-prog.github.io/crossmart-hub/data/selection.json"
data = json.loads(urllib.request.urlopen(url).read())
```

## 部署

GitHub Pages 从 `main` 分支根目录 serve。首次开启：
Settings → Pages → Source: Deploy from a branch → Branch: main / (root)

访问：`https://charlescome1995-prog.github.io/crossmart-hub/`

## 版本

- `v1`（2026-07-11）：MVP，5 个数据文件占位 + dashboard 骨架
