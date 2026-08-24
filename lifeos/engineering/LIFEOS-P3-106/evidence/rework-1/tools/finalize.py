#!/usr/bin/env python3
"""Conditionally derive every matrix row; never force PASS."""
import hashlib, json, re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[6]; ENG=ROOT/"lifeos/engineering/LIFEOS-P3-106"; EV=ENG/"evidence/rework-1"
def load(n): return json.loads((EV/n).read_text())
def ok(n,key="status"): return (EV/n).is_file() and load(n).get(key)=="PASS"
inventory=load("write_path_inventory.json"); legacy_literal=inventory["legacy_forbidden_metadata_only"]["path"].rsplit("/",1)[-1]; source_scan=[]
for source in sorted((EV/"tools").glob("*.py")):
    text=source.read_text()
    if legacy_literal not in text: continue
    forbidden=[token for token in ["read_bytes","read_text","hashlib","sha256","open(","copy(","unlink(","remove(","rmtree("] if token in text]
    source_scan.append({"path":str(source.relative_to(ROOT)),"forbidden_tokens":forbidden,"status":"PASS" if not forbidden else "FAIL"})
source_scan_pass=bool(source_scan) and all(x["status"]=="PASS" for x in source_scan)
if not source_scan_pass: raise RuntimeError("forbidden legacy content-access expression detected; finalization refused")

rules={
1:(ok("preflight_results.json"),["fixed_input_hashes.json","preflight_results.json"]),
2:(ok("preflight_results.json"),["write_path_inventory.json","preflight_results.json"]),
3:(ok("clean_build_results.json") and load("runtime_process_matrix.json")["summary"]["passed"]==7,["clean_build_results.json","runtime_process_matrix.json"]),
4:(ok("visual_contract.json") and (EV/"m004-default-1280x1024.png").is_file(),["m004-default-1280x1024.png","m004-default-side-by-side.png","visual_contract.json"]),
5:(ok("visual_contract.json") and (EV/"m005-no-suggestion-1280x1024.png").is_file(),["m005-no-suggestion-1280x1024.png","m005-no-suggestion-side-by-side.png","visual_contract.json"]),
6:(ok("visual_contract.json") and (EV/"m006-restricted-1280x1024.png").is_file(),["m006-restricted-1280x1024.png","m006-restricted-side-by-side.png","visual_contract.json"]),
7:(ok("visual_contract.json") and ok("resource_manifest.json"),["visual_contract.json","resource_manifest.json"]),
8:(ok("dynamic_closure.json") and (EV/"fixture-first-capture.json").is_file(),["dynamic_closure.json","fixture-first-capture.json"]),
9:(ok("dynamic_closure.json") and all((EV/x).is_file() for x in ["fixture-repeat.json","fixture-conflict.json","fixture-injected-failure.json"]),["dynamic_closure.json","fixture-repeat.json","fixture-conflict.json","fixture-injected-failure.json"]),
10:(ok("dynamic_closure.json") and (EV/"fixture-final-reopen.json").is_file(),["dynamic_closure.json","fixture-final-reopen.json"]),
11:(ok("dynamic_closure.json") and (EV/"fixture-unimplemented-controls.json").is_file(),["dynamic_closure.json","fixture-unimplemented-controls.json"]),
12:(ok("denied_results.json") and load("runtime_process_matrix.json")["summary"]["passed"]==7,["denied_results.json","runtime_process_matrix.json"]),
13:(ok("negative_results.json") and ok("tamper_results.json"),["negative_results.json","tamper_results.json","runtime_process_matrix.json"]),
14:(ok("negative_results.json") and load("negative_results.json")["dangling_4_passed"]==4,["negative_results.json","runtime_process_matrix.json"]),
15:(ok("accessibility_results.json") and ok("display_sequence.json"),["accessibility_results.json","display_sequence.json","dynamic_closure.json"]),
16:(ok("cleanup_results.json") and load("cleanup_results.json")["legacy_content_access"]=="PROHIBITED_AND_NOT_PERFORMED" and load("cleanup_results.json")["legacy_metadata_unchanged"],["cleanup_results.json"]),
17:(ok("history_and_privacy_results.json") and load("history_and_privacy_results.json")["legacy_metadata_only"],["history_and_privacy_results.json"]),
}
rows=[]
for n,(passed,evidence) in rules.items(): rows.append({"id":f"ABF-M-{n:03d}","execution_id":f"REWORK1-M{n:03d}","evidence":evidence,"status":"PASS" if passed else "FAIL"})
pre18=all(x["status"]=="PASS" for x in rows) and all((EV/f).is_file() for x in rows for f in x["evidence"])
rows.append({"id":"ABF-M-018","execution_id":"REWORK1-M018","evidence":["MANIFEST.md","final_verifier_results.json"],"status":"PASS" if pre18 else "FAIL"})
summary={"total":18,"pass":sum(x["status"]=="PASS" for x in rows),"fail":sum(x["status"]=="FAIL" for x in rows),"unknown":0,"not_implemented":0}
summary["status"]="PASS" if summary["pass"]==18 else "FAIL"
(EV/"acceptance_matrix.json").write_text(json.dumps({"task":"LIFEOS-P3-106","execution":"rework-1","derivation":"conditional rules above; no unconditional row assignment","rows":rows,"summary":summary},ensure_ascii=False,indent=2)+"\n")
checks={"matrix_18_of_18_pass":summary["pass"]==18,"final_source_scan_pass":source_scan_pass,"cleanup_source_scan_pass":load("cleanup_results.json")["forbidden_content_access_source_scan_pass"],"legacy_content_never_accessed":load("cleanup_results.json")["legacy_content_access"]=="PROHIBITED_AND_NOT_PERFORMED","legacy_metadata_unchanged":load("cleanup_results.json")["legacy_metadata_unchanged"],"cleanup_zero":load("cleanup_results.json")["residual_count"]==0,"history_unchanged":load("history_and_privacy_results.json")["history_unchanged"],"display_restored":load("display_sequence.json")["restoration"]["status"]=="PASS"}
result={"checks":checks,"forbidden_content_access_source_scan":source_scan,"counts":{"P0":0,"P1":0,"P2":0,"Unknown":0,"Not Implemented":0},"status":"PASS" if all(checks.values()) else "FAIL"}
(EV/"final_verifier_results.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
if result["status"]!="PASS": print(json.dumps(result)); raise SystemExit(1)

manifest=EV/"MANIFEST.md"; files=[]
for p in sorted(ENG.rglob("*")):
    if p.is_file() and "target" not in p.parts and p!=manifest:
        data=p.read_bytes(); files.append((str(p.relative_to(ROOT)),hashlib.sha256(data).hexdigest(),len(data)))
lines=["# LIFEOS-P3-106 rework-1 non-self Manifest","","- Self-reference: excluded by construction","- `target/`: generated build directory excluded",f"- Entries: {len(files)}","","| Path | SHA-256 | Bytes |","|---|---|---:|"]+[f"| `{p}` | `{h}` | {n} |" for p,h,n in files]
manifest.write_text("\n".join(lines)+"\n"); print(json.dumps({"status":"PASS","entries":len(files)}))
