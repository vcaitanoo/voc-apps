# -*- coding: utf-8 -*-
"""ReCena V4: download direto, teste local, sem anexos ZIP do ChatGPT."""
import hashlib, json, os, shutil, subprocess, sys, time, urllib.request, uuid
from pathlib import Path
from PIL import Image, ImageOps, ImageFilter, ImageDraw

HOME=Path.home()
BASE=HOME/'Downloads'/'ComfyUI_windows_portable_nvidia_cu126'/'ComfyUI_windows_portable'
COMFY=BASE/'ComfyUI'
PY=BASE/'python_embeded'/'python.exe'
INPUT=COMFY/'input'
OUTPUT=COMFY/'output'
RUN=HOME/'Videos'/'ReCena'/'Teste_V4_GitHub'
RUN.mkdir(parents=True,exist_ok=True)
LOG=RUN/'ANDAMENTO.txt'
DREAM='DreamShaper_8_pruned.safetensors'
CANNY='control_v11p_sd15_canny_fp16.safetensors'
URL='http://127.0.0.1:8189'
POS='one authentic 1991 white-and-red McLaren Honda Formula One car on a grey Interlagos race track, same car size position direction and camera angle as input, exact fencing track and barriers, hand-drawn clean 2D cartoon comic style, near-black strong outlines, flat vibrant colors, cel shading, graphic shadows, no gradients, faithful composition'
NEG='photograph, realism, CGI, 3D render, film grain, glossy textures, blur, deformed car, extra wheels, missing wheels, changed perspective, reversed direction, different vehicle, invented objects, new flag marshal, text, watermark'
def log(message):
    s=time.strftime('[%H:%M:%S] ')+str(message)
    print(s,flush=True)
    with LOG.open('a',encoding='utf8') as f:f.write(s+'\n')
def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for buf in iter(lambda:f.read(4*1024*1024),b''): h.update(buf)
    return h.hexdigest()
def get_model(name,folder,url,expected):
    target=COMFY/'models'/folder/name
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.is_file():
        if sha(target)==expected:
            log('Ja instalado, SHA correto: '+name); return
        raise RuntimeError('Modelo existente tem SHA diferente, nao vou substituir: '+str(target))
    tmp=Path(str(target)+'.part')
    log('Baixando direto do Hugging Face: '+name)
    cmd=['curl.exe','-L','--fail','--retry','4','--retry-delay','5','-C','-','-o',str(tmp),url]
    if subprocess.call(cmd)!=0: raise RuntimeError('Download falhou; parcial mantido: '+str(tmp))
    if sha(tmp)!=expected: raise RuntimeError('SHA incorreto; parcial mantido: '+str(tmp))
    tmp.replace(target)
    log('Baixado e validado: '+name)
def get_source():
    # Usa a imagem original de Senna que o usuario ja colocou no ComfyUI.
    cands=[p for p in INPUT.glob('*.png') if 'senna' in p.name.lower()
           and 'recena_v4_' not in p.name.lower()]
    cands.sort(key=lambda p:p.stat().st_mtime,reverse=True)
    if cands: return cands[0]
    raise RuntimeError('Imagem do Senna nao encontrada em '+str(INPUT)+'; nenhum arquivo original foi alterado')
def prep():
    src=get_source()
    log('Frame original: '+str(src))
    im=ImageOps.fit(Image.open(src).convert('RGB'),(512,288),method=Image.Resampling.LANCZOS)
    for name,bounds in [('CENA',(55,18,457,244)),('CARRO',(95,32,417,213))]:
        a=im.crop(bounds).resize((512,288),Image.Resampling.LANCZOS)
        a.save(INPUT/('RECENA_V4_'+name+'.png'))
        ed=a.convert('L').filter(ImageFilter.GaussianBlur(0.6)).filter(ImageFilter.FIND_EDGES)
        ed.point(lambda x:255 if x>38 else 0).convert('RGB').save(INPUT/('RECENA_V4_'+name+'_EDGES.png'))
    im.save(RUN/'FRAME_ORIGINAL.png')
def api(path,data=None):
    req=urllib.request.Request(URL+path)
    if data is not None:
        req=urllib.request.Request(URL+path,json.dumps(data).encode('utf8'),
                                    {'Content-Type':'application/json'},method='POST')
    with urllib.request.urlopen(req,timeout=30) as r:
        return json.loads(r.read().decode('utf8'))
def new_workflow(image,denoise,control,strength,prefix):
    g={
       '1':{'class_type':'CheckpointLoaderSimple','inputs':{'ckpt_name':DREAM}},
       '2':{'class_type':'CLIPTextEncode','inputs':{'clip':['1',1],'text':POS}},
       '3':{'class_type':'CLIPTextEncode','inputs':{'clip':['1',1],'text':NEG}},
       '8':{'class_type':'LoadImage','inputs':{'image':image}},
       '9':{'class_type':'VAEEncode','inputs':{'pixels':['8',0],'vae':['1',2]}},
       '5':{'class_type':'KSampler','inputs':{'model':['1',0],'positive':['2',0],
                  'negative':['3',0],'latent_image':['9',0],'seed':482112,'steps':16,
                  'cfg':6.0,'sampler_name':'euler','scheduler':'normal','denoise':denoise}},
       '6':{'class_type':'VAEDecode','inputs':{'samples':['5',0],'vae':['1',2]}},
       '7':{'class_type':'SaveImage','inputs':{'images':['6',0],'filename_prefix':prefix}}
    }
    if control:
        g['11']={'class_type':'ControlNetLoader','inputs':{'control_net_name':CANNY}}
        g['12']={'class_type':'LoadImage','inputs':{'image':image.replace('.png','_EDGES.png')}}
        g['13']={'class_type':'ControlNetApplyAdvanced','inputs':{
            'positive':['2',0],'negative':['3',0],'control_net':['11',0],
            'image':['12',0],'strength':strength,'start_percent':0.0,'end_percent':1.0}}
        g['5']['inputs']['positive']=['13',0]
        g['5']['inputs']['negative']=['13',1]
    return g
def start_server(cpu=False):
    global URL
    port=8190 if cpu else 8189
    args=[str(PY),'-s','ComfyUI/main.py','--windows-standalone-build','--disable-assets',
          '--port',str(port)]
    args+=['--cpu','--cpu-vae'] if cpu else ['--disable-cuda-malloc','--novram','--cpu-vae']
    fp=open(RUN/('SERVIDOR_CPU.log' if cpu else 'SERVIDOR_GPU.log'),'ab',buffering=0)
    proc=subprocess.Popen(args,cwd=BASE,stdout=fp,stderr=subprocess.STDOUT)
    URL='http://127.0.0.1:'+str(port)
    for _ in range(90):
        if proc.poll() is not None: break
        try:
            api('/object_info/CheckpointLoaderSimple')
            log('Servidor local iniciado em '+URL)
            return proc,fp
        except Exception: time.sleep(2)
    fp.close()
    raise RuntimeError('Servidor local nao iniciou. Veja logs em '+str(RUN))
def do_one(name,image,dn,control,strength):
    g=new_workflow(image,dn,control,strength,name)
    (RUN/(name+'.json')).write_text(json.dumps(g,indent=2),encoding='utf8')
    r=api('/prompt',{'prompt':g,'client_id':str(uuid.uuid4())})
    pid=r.get('prompt_id')
    if not pid: raise RuntimeError('Workflow recusado pelo servidor: '+str(r)[:400])
    log('Gerando '+name)
    finish=time.monotonic()+3600
    while time.monotonic()<finish:
        time.sleep(5)
        h=api('/history/'+pid).get(pid)
        if not h: continue
        if h.get('status',{}).get('status_str')=='error':
            raise RuntimeError('Erro de geracao; veja '+str(RUN))
        imgs=h.get('outputs',{}).get('7',{}).get('images',[])
        if imgs:
            entry=imgs[0]
            path=OUTPUT/entry.get('subfolder','')/entry['filename']
            dst=RUN/(name+'.png')
            shutil.copy2(path,dst)
            log('Concluido: '+str(dst))
            return
    raise RuntimeError('Teste excedeu 60 minutos e pode ainda estar executando')
def montage():
    imgs=[p for p in RUN.glob('V4_*.png')]
    imgs.sort()
    rows=[('Original',RUN/'FRAME_ORIGINAL.png')]+[(p.stem,p) for p in imgs]
    out=Image.new('RGB',(1060,((len(rows)+1)//2)*332),(22,25,29))
    d=ImageDraw.Draw(out)
    for i,(label,p) in enumerate(rows):
        x=(i%2)*530;y=(i//2)*332
        d.text((x+12,y+10),label,fill='white')
        try:
            im=ImageOps.contain(Image.open(p).convert('RGB'),(512,288))
            out.paste(im,(x+10,y+33))
        except Exception:pass
    out.save(RUN/'COMPARACAO_RECENA_V4.jpg',quality=90)
def main():
    if not PY.exists():raise RuntimeError('ComfyUI portable nao encontrado em '+str(BASE))
    if not (COMFY/'models'/'checkpoints'/'v1-5-pruned-emaonly.safetensors').exists():
        raise RuntimeError('SD 1.5 base nao encontrado, instalacao antiga preservada')
    log('Inicio do ReCena V4 direto pelo GitHub; sem creditos.')
    prep()
    get_model(DREAM,'checkpoints',
       'https://huggingface.co/Lykon/DreamShaper/resolve/main/DreamShaper_8_pruned.safetensors',
       '879db523c30d3b9017143d56705015e15a2cb5628762c11d086fed9538abd7fd')
    get_model(CANNY,'controlnet',
       'https://huggingface.co/comfyanonymous/ControlNet-v1-1_fp16_safetensors/resolve/main/control_v11p_sd15_canny_fp16.safetensors',
       '8932b66e15aae835b3490dbf989f56c253104cee08a88bf21283762f557c9f10')
    proc=None;fp=None;cp=None;cf=None
    try:
        proc,fp=start_server(False)
        jobs=[
          ('V4_A_045','RECENA_V4_CENA.png',.45,False,0),
          ('V4_B_060','RECENA_V4_CARRO.png',.60,False,0),
          ('V4_C_CANNY_055','RECENA_V4_CENA.png',.55,True,.85),
          ('V4_D_CANNY_065','RECENA_V4_CARRO.png',.65,True,1.0)
        ]
        for name,img,dn,cn,st in jobs:
            if (RUN/(name+'.png')).exists():
                log('Teste ja existente preservado: '+name);continue
            try: do_one(name,img,dn,cn,st)
            except Exception as e:
                log('Falha de GPU: '+str(e))
                if cp is None:cp,cf=start_server(True)
                try:do_one(name,img,dn,cn,st)
                except Exception as ee:
                    log('Falha tambem na CPU: '+str(ee))
                    break
            montage()
        montage()
        log('Finalizado. Comparacao: '+str(RUN/'COMPARACAO_RECENA_V4.jpg'))
        if hasattr(os,'startfile'):os.startfile(RUN)
    finally:
        for p,f in [(proc,fp),(cp,cf)]:
            if p is not None and p.poll() is None:p.terminate()
            if f is not None:f.close()
if __name__=='__main__':
    try:main()
    except Exception as exc:
        import traceback
        log('ERRO: '+str(exc))
        (RUN/'ERRO.txt').write_text(traceback.format_exc(),encoding='utf8')
        sys.exit(1)
