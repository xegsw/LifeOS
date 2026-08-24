#!/usr/bin/env python3
import hashlib, importlib.util, json, os, re, stat
from pathlib import Path
from legacy_metadata import snapshot as legacy_snapshot

ROOT=Path(__file__).resolve().parents[6]
ENG=ROOT/"lifeos/engineering/LIFEOS-P3-106"
EV=ENG/"evidence/rework-1"
ABF=ROOT/"lifeos/tasks/LIFEOS-P3-106_three_frozen_stitch_pages_high_fidelity_tauri_ui_path_contract_successor_acceptance_basis_freeze.md"
INV=json.loads((EV/"write_path_inventory.json").read_text())

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def meta(p):
    try:
        s=p.lstat(); return {"exists":True,"type":stat.filemode(s.st_mode)[0],"size":s.st_size,"mtime_ns":s.st_mtime_ns,"ctime_ns":s.st_ctime_ns}
    except FileNotFoundError: return {"exists":False}
def emit(name,data): (EV/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")

spec=importlib.util.spec_from_file_location("frozen_preflight",ENG/"tests/verify_preflight.py")
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
fixed=[]
for label,(p,want) in mod.FIXED.items():
    got=sha(p) if p.is_file() else None
    fixed.append({"id":f"FIXED-{label}","path":str(p.relative_to(ROOT)),"expected":want,"actual":got,"status":"PASS" if got==want else "FAIL"})
abf_got=sha(ABF)
fixed.append({"id":"FIXED-ABF","path":str(ABF.relative_to(ROOT)),"expected":INV["abf_sha256"],"actual":abf_got,"status":"PASS" if abf_got==INV["abf_sha256"] else "FAIL"})

protected=[]
roots=[ENG/"evidence",ROOT/"lifeos/reviews/LIFEOS-P3-106/pm_evidence/initial",ROOT/"lifeos/reviews/LIFEOS-P3-106/pm_evidence/resume-1"]
files=[ROOT/"lifeos/reviews/LIFEOS-P3-106_pm_review.md",ROOT/"lifeos/deliverables/LIFEOS-P3-106_three_frozen_stitch_pages_high_fidelity_tauri_ui_path_contract_successor.md",ROOT/"lifeos/deliverables/LIFEOS-P3-106_three_frozen_stitch_pages_high_fidelity_tauri_ui_path_contract_successor_resume_1.md"]
for base in roots:
    for p in sorted(base.rglob("*")):
        if p.is_file() and EV not in p.parents: protected.append({"path":str(p.relative_to(ROOT)),"sha256":sha(p),"metadata":meta(p)})
for p in files:
    if p.is_file(): protected.append({"path":str(p.relative_to(ROOT)),"sha256":sha(p),"metadata":meta(p)})

run_paths=[Path(x) for x in INV["actual_app_allowlist"]["exact_run_paths"]]
unit_pat=re.compile(r"lifeos-p3-104-unit-(?:lifecycle|failure|arguments|links|dangling-final|dangling-sidecars|tamper|sidecar)-[0-9]+|lifeos-p3-104-unit-link-target-[0-9]+|lifeos-p3-104-unit-link-[0-9]+")
unit=[str(p) for p in Path("/private/tmp").iterdir() if unit_pat.fullmatch(p.name)]
paths=[{"path":str(p),"metadata":meta(p)} for p in run_paths]

source_scan=[]
legacy_literal=INV["legacy_forbidden_metadata_only"]["path"].rsplit("/",1)[-1]
for p in sorted((EV/"tools").glob("*.py")):
    text=p.read_text()
    if legacy_literal not in text: continue
    forbidden=[token for token in ["read_bytes","read_text","hashlib","sha256","open(","copy(","unlink(","remove(","rmtree("] if token in text]
    source_scan.append({"path":str(p.relative_to(ROOT)),"forbidden_tokens":forbidden,"status":"PASS" if not forbidden else "FAIL"})

pre={"task":"LIFEOS-P3-106","execution":"rework-1","protected_snapshot":protected,"legacy_metadata_before":legacy_snapshot(),"authorized_paths_before":paths,"unit_residuals_before":unit,"forbidden_content_access_source_scan":source_scan}
emit("fixed_input_hashes.json",fixed); emit("protected_read_only_baseline.json",pre)
checks={"fixed_23_of_23":len(fixed)==23 and all(x["status"]=="PASS" for x in fixed),"authorized_paths_absent":all(not x["metadata"]["exists"] for x in paths),"unit_residuals_zero":not unit,"legacy_source_scan_pass":bool(source_scan) and all(x["status"]=="PASS" for x in source_scan),"inventory_precedes_actions":INV["created_before_rework_build_test_fixture_or_app_action"] is True}
emit("preflight_results.json",{"checks":checks,"counts":{"fixed":len(fixed),"protected":len(protected),"source_scanned":len(source_scan)},"status":"PASS" if all(checks.values()) else "FAIL"})
print(json.dumps({"checks":checks,"protected":len(protected)})); raise SystemExit(0 if all(checks.values()) else 1)
