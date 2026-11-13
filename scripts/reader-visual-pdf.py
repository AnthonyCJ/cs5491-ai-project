"""Render declared PDFs with the existing pypdfium2; no generator modification."""
import argparse, hashlib, json, os, sys, time, traceback
from pathlib import Path

p=argparse.ArgumentParser()
for key in ('task','receipt','root','request','modules','browser'): p.add_argument('--'+key,default='')
a=p.parse_args(); root=Path(a.root); out=Path(a.receipt); temp=out/'process-temp'
def save(name,data):
    with (out/name).open('x',encoding='utf8') as f: json.dump(data,f,indent=2)
def wait(name):
    end=time.monotonic()+18
    while not (out/name).exists():
        if time.monotonic()>end or (out/'stop.json').exists(): raise RuntimeError('Stopped before '+name)
        time.sleep(.02)
def audit(event,args):
    if event in ('subprocess.Popen','os.system','os.posix_spawn','os.spawn','os.exec','_winapi.CreateProcess'): raise PermissionError('PDF rendering refuses subprocess creation')
result={'status':'failed','gate_passed':False,'task':'pdf','files':[]}
try:
    if root.resolve(strict=True)!=root or temp.resolve(strict=True)!=temp or Path.cwd()!=root: raise RuntimeError('Strict paths differ')
    if not all(Path(os.environ[k]).resolve(strict=True)==temp for k in ('TEMP','TMP','TMPDIR')): raise RuntimeError('Temporary root differs')
    sys.addaudithook(audit)
    (out/'stdout.txt').write_text('',encoding='utf8');(out/'stderr.txt').write_text('',encoding='utf8')
    save('ready.json',{'pid':os.getpid(),'parent_pid':os.getppid(),'business_started':False});wait('go.json')
    import pypdfium2 as pdfium
    import importlib.metadata
    result['renderer']={'python':sys.version,'pypdfium2':importlib.metadata.version('pypdfium2'),'dpi':150}
    save('render-ready.json',{'pid':os.getpid(),'renderer':result['renderer'],'business_started':False});wait('render-go.json')
    request=(root/a.request).resolve(strict=True)
    if not request.is_relative_to(root): raise RuntimeError('Request escaped root')
    for i,rel in enumerate(json.loads(request.read_text(encoding='utf-8-sig'))['files']):
        source=root/rel
        if source.resolve(strict=True)!=source or not source.is_relative_to(root): raise RuntimeError('Source escaped/aliased')
        doc=pdfium.PdfDocument(str(source));entry={'source':rel,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'pages':[]}
        for n in range(len(doc)):
            page=doc[n];bitmap=page.render(scale=150/72);image=bitmap.to_pil();name=f'file-{i+1:02d}-page-{n+1:02d}-150dpi.png';image.save(out/name)
            entry['pages'].append({'page':n+1,'path':name,'dpi':150,'width':image.width,'height':image.height,'sha256':hashlib.sha256((out/name).read_bytes()).hexdigest(),'visual_judgment':'pending actual assistant inspection'})
            image.close();bitmap.close();page.close()
        doc.close();result['files'].append(entry)
    result.update(status='completed',gate_passed=True,temporary_cleanup_verified=not any(temp.iterdir()))
    if not result['temporary_cleanup_verified']: raise RuntimeError('Temporary directory not empty')
except BaseException:
    result.update(status='failed',gate_passed=False,error=traceback.format_exc());(out/'stderr.txt').write_text(result['error'],encoding='utf8')
finally: save('worker-result.json',result)
sys.exit(0 if result['gate_passed'] else 1)
