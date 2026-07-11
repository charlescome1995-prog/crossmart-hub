#!/usr/bin/env python3
"""Rebuild data/hub.json aggregating counts + asin_to_sources index."""
from __future__ import annotations
import json, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

def load(name: str) -> dict:
    p = DATA / name
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"warn: parse {name} failed: {e}")
        return {}

def now_iso() -> str:
    return datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(timespec="seconds")

def main() -> None:
    sel = load("selection.json")
    mon = load("monitor.json")
    lst = load("listing.json")
    ops = load("ops.json")
    sim = load("predictions.json")

    # station summaries
    stations = {
        "selector": {
            "last_push": sel.get("generated_at"),
            "items_count": len(sel.get("items", []) or []),
            "url": "https://charlescome1995-prog.github.io/crossmart-selector/frontend/selection.html",
        },
        "monitor": {
            "last_push": mon.get("generated_at"),
            "asins_count": _count_monitor_asins(mon),
            "url": "https://charlescome1995-prog.github.io/crossmart-monitor/monitor.html",
        },
        "listing": {
            "last_push": lst.get("generated_at"),
            "drafts_count": len(lst.get("drafts", []) or []),
            "url": None,
        },
        "ops": {
            "last_push": ops.get("generated_at"),
            "last_date": ops.get("date"),
            "url": None,
        },
        "simulator": {
            "last_push": sim.get("generated_at"),
            "predictions_count": len(sim.get("predictions", []) or []),
            "calibrated_count": sum(
                1 for p in (sim.get("predictions") or [])
                if p.get("calibration_status") == "calibrated"
            ),
            "url": None,
        },
    }

    # asin cross-index
    idx: dict[str, dict] = {}

    for it in sel.get("items", []) or []:
        for a in it.get("top_asins", []) or []:
            idx.setdefault(a, {})["selector_score"] = it.get("score")

    for a in _iter_monitor_asins(mon):
        cur = idx.setdefault(a, {})
        cur["monitor_snapshots"] = cur.get("monitor_snapshots", 0) + 1

    for d in lst.get("drafts", []) or []:
        a = d.get("asin")
        if a: idx.setdefault(a, {})["listing_generated"] = True

    for p in sim.get("predictions", []) or []:
        a = p.get("asin")
        if not a: continue
        cur = idx.setdefault(a, {})
        cur["simulator_predicted"] = True
        cur["simulator_calibrated"] = p.get("calibration_status") == "calibrated"

    hub = {
        "schema_version": "v1",
        "generated_at": now_iso(),
        "source": "crossmart-hub-actions",
        "stations": stations,
        "asin_to_sources": idx,
    }

    (DATA / "hub.json").write_text(
        json.dumps(hub, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"hub.json rebuilt · {len(idx)} asins indexed")

def _iter_monitor_asins(mon: dict):
    seen = set()
    for kw in mon.get("keywords", []) or []:
        for t in kw.get("top_asins", []) or []:
            a = t.get("asin") if isinstance(t, dict) else t
            if a and a not in seen:
                seen.add(a); yield a
    for a in (mon.get("asins") or {}).keys():
        if a not in seen:
            seen.add(a); yield a

def _count_monitor_asins(mon: dict) -> int:
    return sum(1 for _ in _iter_monitor_asins(mon))

if __name__ == "__main__":
    main()
