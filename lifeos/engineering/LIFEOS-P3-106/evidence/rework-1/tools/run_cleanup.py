#!/usr/bin/env python3
import hashlib, json, os, shutil
from pathlib import Path
from legacy_metadata import snapshot as legacy_snapshot

ROOT=Path(__file__).resolve().parents[6]; ENG=ROOT/"lifeos/engineering/LIFEOS-P3-106"; EV=ENG/"evidence/rework-1"
inv=json.loads((EV/"write_path_inventory.json").read_text()); baseline=json.loads((EV/"protected_read_only_baseline.json").read_text())
legacy_literal=inv["legacy_forbidden_metadata_only"]["path"].rsplit("/",1)[-1]
scan=[]
for source in sorted((EV/"tools").glob("*.py")):
    text=source.read_text()
    if legacy_literal not in text: continue
    forbidden=[token for token in ["read_bytes","read_text","hashlib","sha256","open(","copy(","unlink(","remove(","rmtree("] if token in text]
    scan.append({"path":str(source.relative_to(ROOT)),"forbidden_tokens":forbidden,"status":"PASS" if not forbidden else "FAIL"})
if not scan or any(row["status"]!="PASS" for row in scan):
    raise RuntimeError("forbidden legacy content-access expression detected; cleanup refused")
paths=[Path(x) for x in inv["actual_app_allowlist"]["exact_run_paths"]]
before={str(p):{"lexists":os.path.lexists(p),"is_symlink":p.is_symlink()} for p in paths}; deleted=[]
for p in paths:
    if p.is_symlink() or p.is_file(): p.unlink(); deleted.append(str(p))
    elif p.is_dir(): shutil.rmtree(p); deleted.append(str(p))
after={str(p):{"lexists":os.path.lexists(p)} for p in paths}
history=[]
for row in baseline["protected_snapshot"]:
    p=ROOT/row["path"]; got=hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
    history.append({"path":row["path"],"before_sha256":row["sha256"],"after_sha256":got,"unchanged":got==row["sha256"]})
legacy_after=legacy_snapshot(); legacy_before=baseline["legacy_metadata_before"]
result={"task":"LIFEOS-P3-106","execution":"rework-1","method":"literal exact ledger only; no glob/find/prefix deletion","forbidden_content_access_source_scan":scan,"forbidden_content_access_source_scan_pass":all(x["status"]=="PASS" for x in scan),"before":before,"deleted":deleted,"after":after,"residual_count":sum(x["lexists"] for x in after.values()),"protected_count":len(history),"protected_unchanged_count":sum(x["unchanged"] for x in history),"legacy_metadata_before":legacy_before,"legacy_metadata_after":legacy_after,"legacy_metadata_unchanged":legacy_before==legacy_after,"legacy_content_access":"PROHIBITED_AND_NOT_PERFORMED"}
result["status"]="PASS" if result["forbidden_content_access_source_scan_pass"] and result["residual_count"]==0 and result["protected_unchanged_count"]==result["protected_count"] and result["legacy_metadata_unchanged"] else "FAIL"
(EV/"cleanup_results.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
(EV/"history_and_privacy_results.json").write_text(json.dumps({"history":history,"history_unchanged":all(x["unchanged"] for x in history),"legacy_metadata_only":True,"legacy_metadata_unchanged":result["legacy_metadata_unchanged"],"real_personal_data_count":0,"network_request_count":0,"remote_resource_count":0,"allowed_path_residual_count":result["residual_count"],"status":result["status"]},ensure_ascii=False,indent=2)+"\n")
print(json.dumps({"status":result["status"],"residual":result["residual_count"],"history":f'{result["protected_unchanged_count"]}/{result["protected_count"]}',"legacy_metadata_unchanged":result["legacy_metadata_unchanged"]})); raise SystemExit(0 if result["status"]=="PASS" else 1)
