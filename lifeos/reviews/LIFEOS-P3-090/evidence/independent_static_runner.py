#!/usr/bin/env python3
"""Independent, task-local static review for LIFEOS-P3-090.

This runner intentionally reads the copied UI bundle directly and does not
import, call, or reproduce P3-089's runner/tests.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/private/tmp/lifeos-p3-090-review-app')
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).with_name('independent_static_results.json')
EXPECTED = {
    'default-recovery.html': 'c8e6e130bdb26962f6663afc56529fecf2c3501f643633655837daa433ee16b4',
    'no-reliable-suggestion.html': 'c38a3d8fe35bb00d5d13ca1fa1967daa813c1b8af083e75de3fb9cb593d0520d',
    'restricted-offline.html': '0965726629e105087b94680476f18e5a35f361f046be23ccbc468850ac84085f',
    'styles.css': '052600b12672a7d9bf255c130edbb4eb5d6d3d3bfee3a64be403e24e74dfe94a',
    'app.js': '88dc10ffa945d12baf42b771e4c6fddef791a5f1305e9f1d349161977684fe1a',
}
HISTORY = {
    'P3-079 integrated_runtime.py': ('lifeos/engineering/LIFEOS-P3-079/src/integrated_runtime.py', '19d337a560cfa3e6098571b29a71fc121e059db1c0914e3e3f58f3f740905788'),
    'P3-087 app.js': ('lifeos/engineering/LIFEOS-P3-087/app.js', 'fa50eb0e7bfa177a3ba2c6e97ec1185370506e84cc2f1d01434ac9d5ea090d0c'),
    'P3-088 manifest': ('lifeos/reviews/LIFEOS-P3-088/evidence/MANIFEST.md', 'b8712cd7602850dcce359c338f8c801e0fb70200a0ae83d361e46a3edc6bcec6'),
}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
tests=[]
def check(case, ok, detail): tests.append({'id':case,'pass':bool(ok),'detail':detail})
bundle={name:(ROOT/name).read_text() for name in EXPECTED}
for name,want in EXPECTED.items(): check('HASH-'+name, sha(ROOT/name)==want, 'task-local source hash matches reviewed P3-089 manifest')
for label,(path,want) in HISTORY.items(): check('HIST-'+label, sha(path)==want, 'specified readonly historical hash remains unchanged')
pages=[bundle[x] for x in ('default-recovery.html','no-reliable-suggestion.html','restricted-offline.html')]
check('UI-01', all('合成生命周期演示' in p and 'AI 未启用' in p for p in pages), 'all pages identify synthetic UI and disabled AI')
check('UI-02', all('skip-link' in p and 'page-nav' in p for p in pages), 'all pages retain skip link and three-page navigation')
check('UI-03', '已拒绝空输入' in bundle['app.js'] and '重复确认：幂等回执' in bundle['app.js'], 'capture is explicit and repeat-aware')
check('UI-04', '权限未获明确 grant' in bundle['app.js'] and "permission: '默认拒绝'" in bundle['app.js'], 'restore is default-deny')
check('UI-05', "value.trim() !== 'CONFIRM'" in bundle['app.js'] and '重复 CONFIRM：幂等回执' in bundle['app.js'], 'restore requires exact confirmation and is idempotent')
check('UI-06', 'fail-closed' in bundle['app.js'] and '回执已清理' in bundle['app.js'], 'revoke clears preview and receipt')
check('UI-07', '模拟失败：未显示成功' in bundle['app.js'] and '未保存、未授权、未恢复任何真实内容' in bundle['app.js'], 'failure clears partial UI and discloses no real action')
all_text='\n'.join(bundle.values()).lower()
for forbidden in ('http://','https://','fetch(','xmlhttprequest','localstorage','sessionstorage','indexeddb','navigator.sendbeacon','websocket','showopenfilepicker','sqlite','tauri','invoke(','export '):
    check('CLOSED-'+forbidden, forbidden not in all_text, 'forbidden runtime or external capability absent from UI source')
check('BOUNDARY-01', 'P3-079' not in all_text and '.py' not in all_text, 'no P3-079 Python/SQLite runtime wiring appears in UI source')
result={'task':'LIFEOS-P3-090','runner':'independent_static_runner.py','bundle':str(ROOT),'pass':sum(x['pass'] for x in tests),'fail':sum(not x['pass'] for x in tests),'results':tests,'counts':{'P0':0,'P1':0,'P2':0,'Unknown':0,'NotImplemented':0}}
OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(f"{result['pass']} PASS / {result['fail']} FAIL")
sys.exit(1 if result['fail'] else 0)
