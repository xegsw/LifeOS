#!/usr/bin/env python3
import json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
contract = json.loads((ROOT / "tests/visual_contract.json").read_text())
rows = []
for page, anchors in contract["pages"].items():
    text = (ROOT / "ui" / page).read_text()
    for anchor in contract["shared"] + anchors:
        ok = anchor["selector"] in text
        rows.append({"result_id": f"{anchor['id']}-{page}", "page": page, "anchor_id": anchor["id"], "description": anchor["description"], "status": "PASS" if ok else "FAIL"})
payload = {"contract_id": contract["contract_id"], "viewport": contract["viewport"], "total": len(rows), "pass": sum(r["status"]=="PASS" for r in rows), "fail": sum(r["status"]=="FAIL" for r in rows), "results": rows}
(ROOT / "evidence/visual_contract_results.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({k: payload[k] for k in ["contract_id","total","pass","fail"]}, ensure_ascii=False))
sys.exit(1 if payload["fail"] else 0)
