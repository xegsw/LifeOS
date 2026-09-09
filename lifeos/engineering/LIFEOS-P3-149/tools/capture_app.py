"""Capture only a recorded live P3-149 App's exact AX window and CG geometry."""
import sys,json,subprocess
from pathlib import Path
base=Path(__file__).resolve().parents[1];root=Path('/private/tmp/lifeos-p3-149-health-source-v1')
launch,label=sys.argv[1:];assert label.replace('-','').isalnum()
p=json.loads((base/'evidence'/('launch-'+launch+'.json')).read_text());pid=p['pid']
assert subprocess.check_output(['ps','-p',str(pid),'-o','command='],text=True).strip()==p['executable']
v=json.loads(subprocess.check_output([str(root/'native_evidence'),str(pid)],text=True));assert v['pid']==pid
w=next(w for w in v['windows'] if w['title']=='LifeOS P3-149 - Synthetic Offline');g=w['geometry'];assert any(n['role'] in ['AXWebArea','AXWebView'] for n in w['nodes'])
cg=next(w for w in v['cg'] if w['layer']==0 and all(abs(w['bounds'].get(k,0)-g[a])<2 for k,a in [('Width','width'),('Height','height'),('X','x'),('Y','y')]))
v['selected_cg']=cg;v['launch']=launch
out=base/'evidence';assert not (out/(label+'.json')).exists();(out/(label+'.json')).write_text(json.dumps(v,ensure_ascii=False,indent=2))
subprocess.run(['screencapture','-x','-o','-l',str(cg['id']),str(out/(label+'.png'))],check=True)
print(json.dumps({'pid':pid,'geometry':g,'screenshot':str(out/(label+'.png'))}))
