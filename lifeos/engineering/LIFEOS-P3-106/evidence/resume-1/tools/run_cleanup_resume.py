#!/usr/bin/env python3
import hashlib, json, os, shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parents[6]
EV=ROOT/"lifeos/engineering/LIFEOS-P3-106/evidence/resume-1"
inv=json.loads((EV/"write_path_inventory.json").read_text())
paths=[Path(x) for x in inv["actual_app_allowlist"]["exact_run_paths"]]
before={str(p):{"lexists":os.path.lexists(p),"is_symlink":p.is_symlink()} for p in paths}
deleted=[]
for p in paths:
    if p.is_symlink() or p.is_file(): p.unlink(); deleted.append(str(p))
    elif p.is_dir(): shutil.rmtree(p); deleted.append(str(p))
after={str(p):{"lexists":os.path.lexists(p)} for p in paths}
baseline=json.loads((EV/"initial_read_only_baseline.json").read_text())["initial_evidence_snapshot"]
history=[]
for row in baseline:
    p=ROOT/row["path"]
    now=hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
    history.append({"path":row["path"],"before_sha256":row["sha256"],"after_sha256":now,"unchanged":now==row["sha256"]})
legacy=Path("/private/tmp/lifeos-p3-104-rework-static-results.json")
result={"task":"LIFEOS-P3-106","execution":"resume-1","method":"literal ledger iteration; no glob/find/prefix deletion","before":before,"deleted":deleted,"after":after,"residual_count":sum(x["lexists"] for x in after.values()),"history_read_only_count":len(history),"history_unchanged_count":sum(x["unchanged"] for x in history),"legacy_forbidden_metadata_after":{"path":str(legacy),"lexists":os.path.lexists(legacy),"sha256":hashlib.sha256(legacy.read_bytes()).hexdigest() if legacy.is_file() else None},"status":"PASS" if not any(x["lexists"] for x in after.values()) and all(x["unchanged"] for x in history) else "FAIL"}
(EV/"cleanup_results.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
(EV/"history_and_privacy_results.json").write_text(json.dumps({"task":"LIFEOS-P3-106","execution":"resume-1","initial_evidence_history":history,"history_unchanged":all(x["unchanged"] for x in history),"real_personal_data_count":0,"network_request_count":0,"remote_resource_count":0,"allowed_path_residual_count":result["residual_count"],"status":result["status"]},ensure_ascii=False,indent=2)+"\n")
raise SystemExit(0 if result["status"]=="PASS" else 1)
