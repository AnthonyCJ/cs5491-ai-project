// Offline visual evidence producer. No installation, server, or network fetching.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {createRequire} = require('node:module');
const {pathToFileURL} = require('node:url');
const opts = Object.fromEntries(process.argv.slice(2).reduce((a,v,i,all)=>i%2?a:[...a,[v.replace(/^--/,''),all[i+1]]],[]));
const root=path.resolve(opts.root), out=path.resolve(opts.receipt), temp=path.join(out,'process-temp');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const save=(name,value)=>fs.writeFileSync(path.join(out,name),JSON.stringify(value,null,2)+'\n',{flag:'wx'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
const within=p=>p===root||p.startsWith(root+path.sep);
const source=rel=>{const p=path.resolve(root,rel);if(!within(p)||fs.realpathSync(p)!==p)throw Error('Input escaped or aliased: '+rel);return p;};
let browser, context, page, sharp, modules, result={status:'failed',gate_passed:false,task:opts.task,files:[]};
async function wait(name){const end=Date.now()+18000;while(!fs.existsSync(path.join(out,name))){if(Date.now()>end||fs.existsSync(path.join(out,'stop.json')))throw Error('Control stopped at '+name);await sleep(20);}}
async function tiles(buffer,prefix){
  const m=await sharp(buffer).metadata();const rows=[];const w=1600,h=1200,overlap=80;
  for(let y=0;y<m.height;y+=h-overlap)for(let x=0;x<m.width;x+=w-overlap){
    const rect={left:x,top:y,width:Math.min(w,m.width-x),height:Math.min(h,m.height-y)};
    const name=prefix+'-'+String(rows.length+1).padStart(3,'0')+'.png';
    const data=await sharp(buffer).extract(rect).png().toBuffer();fs.writeFileSync(path.join(out,name),data,{flag:'wx'});
    rows.push({path:name,sha256:sha(data),...rect});
  }
  return {width:m.width,height:m.height,tiles:rows};
}
function localLinks(tokens, file){
  const links=[]; const walk=ts=>{for(const t of ts||[]){if(t.type==='link'||t.type==='image')links.push({href:t.href,type:t.type});if(t.tokens)walk(t.tokens);if(t.items)for(const it of t.items)walk(it.tokens);if(t.header)for(const c of t.header)walk(c.tokens);if(t.rows)for(const r of t.rows)for(const c of r)walk(c.tokens);}};walk(tokens);
  return links.map(l=>{if(/^[a-z]+:|^\/\//i.test(l.href))return {...l,kind:'external',checked:'not fetched; no remote access needed for local route'};
    const [part,anchor]=l.href.split('#');const target=path.resolve(path.dirname(source(file)),decodeURIComponent(part||path.basename(file)));
    if(!within(target))return {...l,kind:'outside package',exists:false};
    return {...l,kind:'local',target:path.relative(root,target).replace(/\\/g,'/'),anchor:anchor?decodeURIComponent(anchor):null,exists:fs.existsSync(target)};});
}
async function htmlFor(file){
  const text=fs.readFileSync(source(file),'utf8');const {marked}=modules;
  let body=await marked.parse(text,{gfm:true,breaks:false});
  const counts=new Map();body=body.replace(/<h([1-6])>([\s\S]*?)<\/h\1>/g,(_,level,inner)=>{
    const raw=inner.replace(/<[^>]*>/g,'').replace(/&amp;/g,'&').toLowerCase().replace(/[^\p{L}\p{N}_\-\s]/gu,'').replace(/\s/g,'-');const n=counts.get(raw)||0;counts.set(raw,n+1);return `<h${level} id="${raw}${n?'-'+n:''}">${inner}</h${level}>`;
  });
  // Embed package images; remote resources are never loaded.
  body=body.replace(/<img\b[^>]*src="([^"]+)"[^>]*>/g,(tag,href)=>{if(/^[a-z]+:|^\/\//i.test(href))return '<p>[External image not fetched]</p>';const p=path.resolve(path.dirname(source(file)),decodeURIComponent(href));if(!within(p)||!fs.existsSync(p))throw Error('Missing package image: '+href);const mime=path.extname(p).toLowerCase()==='.svg'?'image/svg+xml':'image/png';return tag.replace(href,'data:'+mime+';base64,'+fs.readFileSync(p).toString('base64'));});
  return {text,links:localLinks(marked.lexer(text),file),html:'<!doctype html><html lang="en"><meta charset="utf-8"><style>html{background:#fff;color:#17212b;font:18px/1.5 Arial,sans-serif}body{max-width:1120px;margin:24px auto;padding:24px}h1,h2,h3{line-height:1.2}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f3f5f7;padding:14px;font:14px/1.45 Consolas,monospace}code{overflow-wrap:anywhere}table{border-collapse:collapse;width:100%;font-size:16px}th,td{border:1px solid #c5cdd5;padding:8px;vertical-align:top;overflow-wrap:anywhere}img{max-width:100%;height:auto}a{color:#075db5;overflow-wrap:anywhere}blockquote{border-left:4px solid #aab7c4;margin-left:0;padding-left:18px}</style><body>'+body+'</body></html>'};
}
async function main(){
  if(fs.realpathSync(root)!==root||fs.realpathSync(temp)!==temp||process.cwd()!==root)throw Error('Strict working/temp path mismatch');
  if(!['TEMP','TMP','TMPDIR'].every(k=>path.resolve(process.env[k]||'')===temp))throw Error('Unexpected temporary directory');
  fs.writeFileSync(path.join(out,'stdout.txt'),'');fs.writeFileSync(path.join(out,'stderr.txt'),'');
  save('ready.json',{pid:process.pid,parent_pid:process.ppid,business_started:false});await wait('go.json');
  const req=JSON.parse(fs.readFileSync(source(opts.request),'utf8').replace(/^\uFEFF/,''));
  const requireAt=createRequire(path.join(opts.modules,'sharp','package.json'));sharp=requireAt(path.join(opts.modules,'sharp'));
  result.renderer={node:process.version,sharp:sharp.versions};
  if(opts.task==='markdown'){
    const marked=await import(pathToFileURL(path.join(opts.modules,'marked','lib','marked.esm.js')).href);
    const pw=requireAt(path.join(opts.modules,'playwright'));modules={marked:marked.marked};
    browser=await pw.chromium.launch({executablePath:opts.browser,headless:true,chromiumSandbox:true,downloadsPath:path.join(temp,'downloads'),artifactsDir:path.join(temp,'artifacts'),env:{...process.env}});
    context=await browser.newContext({viewport:{width:1280,height:1000},deviceScaleFactor:1});await context.route('**/*',r=>r.abort());page=await context.newPage();
    result.renderer.playwright=requireAt(path.join(opts.modules,'playwright','package.json')).version;result.renderer.marked=requireAt(path.join(opts.modules,'marked','package.json')).version;result.renderer.browser=await browser.version();
  }
  save('render-ready.json',{pid:process.pid,renderer:result.renderer,browser_started:!!browser,business_started:false});await wait('render-go.json');
  for(let i=0;i<req.files.length;i++){
    const rel=req.files[i],buf=fs.readFileSync(source(rel)),entry={source:rel,sha256:sha(buf),task:opts.task};
    if(opts.task==='svg'||opts.task==='png'){
      const isSvg=path.extname(rel).toLowerCase()==='.svg';if(opts.task==='svg'&&!isSvg)throw Error('SVG requires its SVG source');
      const png=await sharp(buf,isSvg?{density:120,limitInputPixels:400000000}:{limitInputPixels:400000000}).png().toBuffer();
      const name='file-'+String(i+1).padStart(2,'0');fs.writeFileSync(path.join(out,name+'.png'),png,{flag:'wx'});entry.full_render={path:name+'.png',sha256:sha(png),density:isSvg?120:'source pixels'};Object.assign(entry,await tiles(png,name));
    }else if(opts.task==='markdown'){
      const doc=await htmlFor(rel);await page.setContent(doc.html,{waitUntil:'load',timeout:10000});await page.evaluate(()=>document.fonts.ready);
      const overflow=await page.evaluate(()=>({scroll:document.documentElement.scrollWidth,client:document.documentElement.clientWidth,height:document.documentElement.scrollHeight}));if(overflow.scroll>overflow.client+1)throw Error('Horizontal clipping: '+rel);
      const anchors=await page.locator('[id]').evaluateAll(es=>es.map(e=>e.id));entry.navigation=[];
      for(const l of doc.links){if(l.kind==='local'){
        if(!l.exists)throw Error('Missing navigation target: '+l.href+' in '+rel);
        if(l.anchor){const target=path.extname(l.target).toLowerCase()==='.md'?await htmlFor(l.target):null;if(target){const html=target.html;if(!html.includes('id="'+l.anchor+'"')&&!html.includes("id='"+l.anchor+"'"))throw Error('Missing anchor '+l.href);}}
        entry.navigation.push({...l,verified:true});
      }else entry.navigation.push(l);}
      // Exercise same-page anchor navigation on the rendered DOM without file:// or a server.
      const nav=await page.evaluate(()=>{const a=document.querySelector('a[href^="#"]');if(!a)return {available:false};a.click();return {available:true,hash:location.hash,target_exists:!!document.getElementById(decodeURIComponent(location.hash.slice(1)))};});
      if(nav.available&&!nav.target_exists)throw Error('Rendered anchor navigation failed');entry.actual_anchor_navigation=nav;entry.anchors=anchors;
      await page.evaluate(()=>scrollTo(0,0));const png=await page.screenshot({fullPage:true,timeout:10000});const name='file-'+String(i+1).padStart(2,'0');fs.writeFileSync(path.join(out,name+'.html'),doc.html,{flag:'wx'});fs.writeFileSync(path.join(out,name+'.png'),png,{flag:'wx'});entry.full_render={path:name+'.png',sha256:sha(png),viewport:{width:1280,height:1000}};Object.assign(entry,await tiles(png,name));
    }else throw Error('Unsupported visual task');
    entry.visual_judgment='pending actual assistant inspection';result.files.push(entry);
  }
  result.status='completed';result.gate_passed=true;
}
(async()=>{try{await main();}catch(e){result.error=String(e.stack||e);try{fs.appendFileSync(path.join(out,'stderr.txt'),result.error+'\n');}catch{}}finally{
  try{if(context)await context.close();if(browser)await browser.close();if(fs.realpathSync(temp)!==temp||!temp.startsWith(out+path.sep)||!out.startsWith(path.join(root,'results')+path.sep))throw Error('Unsafe cleanup target');for(const name of fs.readdirSync(temp))fs.rmSync(path.join(temp,name),{recursive:true,force:false,maxRetries:0});result.temporary_cleanup_verified=fs.readdirSync(temp).length===0;}catch(e){result.status='failed';result.gate_passed=false;result.cleanup_error=String(e);}
  result.ended_at=new Date().toISOString();save('worker-result.json',result);process.exitCode=result.gate_passed?0:1;
}})();
