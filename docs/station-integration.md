# 站点端接入指南

每个站点（Selector / Monitor / Listing / Ops / Simulator）都通过下面两步接入：

## 1. 拷贝 helper

把 `crossmart-hub/scripts/push_to_hub.py` 拷贝到本站的 `backend/` 或 `scripts/` 目录。
它零依赖（只用 stdlib）。

## 2. 在生成完自家数据后，调用它

```python
from push_to_hub import push_to_hub
import datetime

payload = {
    "schema_version": "v1",
    "generated_at": datetime.datetime.now(
        datetime.timezone(datetime.timedelta(hours=8))
    ).isoformat(timespec="seconds"),
    "source": "crossmart-selector",   # <- 换成本站
    # ... 本站独有字段（items / drafts / predictions / ...）
}

push_to_hub("selection.json", payload)   # 或 monitor.json / listing.json / ops.json / predictions.json
```

## 3. Token

`push_to_hub` 优先读 `GITHUB_TOKEN_HUB` 环境变量。
本地开发：`setx GITHUB_TOKEN_HUB "<PAT>"`
GitHub Actions：在 secrets 里加 `HUB_TOKEN`，job env `GITHUB_TOKEN_HUB: ${{ secrets.HUB_TOKEN }}`

## 4. Pull 别人数据（无需 token）

前端：
```js
fetch(`https://charlescome1995-prog.github.io/crossmart-hub/data/monitor.json?v=${Date.now()}`)
```

后端脚本：
```python
import urllib.request, json
url = "https://charlescome1995-prog.github.io/crossmart-hub/data/selection.json"
data = json.loads(urllib.request.urlopen(url).read())
```

## 各站建议的推送时机

| 站点 | 时机 |
|---|---|
| Selector  | 每周选品脚本结束 |
| Monitor   | `sync_monitor_data.py` 推 rawData.json 后同步推一份到 hub |
| Listing   | 生成完 Listing 草稿并入库后 |
| Ops       | 每日 06:06 广告词雷达跑完后 |
| Simulator | 跑完预测/校准后 |
