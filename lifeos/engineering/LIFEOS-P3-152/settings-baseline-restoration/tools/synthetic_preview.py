from pathlib import Path
import http.server,json,subprocess,threading
D=Path(__file__).resolve().parents[1];UI=D/'candidate/ui'
child=subprocess.Popen(['/private/tmp/lifeos-p3-152-health-conversation-v1/real-target/debug/synthetic-driver'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True)
lock=threading.Lock();counter=0

def invoke(command,request):
 global counter
 with lock:
  counter+=1;child.stdin.write(json.dumps({'id':counter,'command':command,'request':request})+'\n');child.stdin.flush();result=json.loads(child.stdout.readline());assert result['id']==counter;return result
assert invoke('get_context_recovery',{'version':4,'operation':'conversation_snapshot','payload':{}})['result']['mode']=='synthetic'
shim=b'''<script>window.__TAURI__={core:{invoke:async(command,bytes)=>{const request=JSON.parse(new TextDecoder().decode(bytes));const r=await(await fetch('/ipc',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({command,request})})).json();if(!r.ok)throw r.error;return r.result;}}};</script>'''
class Handler(http.server.BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_GET(self):
  name='index.html' if self.path=='/' else self.path.removeprefix('/')
  if '/' in name or name not in {p.name for p in UI.iterdir() if p.is_file()}:self.send_error(404);return
  content=(UI/name).read_bytes()
  if name=='index.html':content=content.replace(b'<script type="module"',shim+b'<script type="module"')
  self.send_response(200);self.send_header('Content-Type','text/html' if name.endswith('.html') else 'text/javascript' if name.endswith('.js') else 'text/css');self.end_headers();self.wfile.write(content)
 def do_POST(self):
  if self.path!='/ipc' or self.headers.get('Origin') not in (None,'http://127.0.0.1:18752'):self.send_error(403);return
  size=int(self.headers.get('Content-Length',0))
  if not 0<size<20000:self.send_error(400);return
  v=json.loads(self.rfile.read(size));result=invoke(v['command'],v['request']);self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(json.dumps(result).encode())
print(json.dumps({'mode':'synthetic','driver_pid':child.pid,'url':'http://127.0.0.1:18752'}),flush=True)
try:http.server.HTTPServer(('127.0.0.1',18752),Handler).serve_forever()
finally:child.terminate();child.wait(timeout=5)
