from pathlib import Path
import argparse,json,os,shutil,subprocess,sys,threading,urllib.request
parser=argparse.ArgumentParser();parser.add_argument('--repo',type=Path,required=True);parser.add_argument('--out',type=Path,required=True);parser.add_argument('--node-modules',type=Path,required=True);args=parser.parse_args()
sys.path.insert(0,str(args.repo/'tools/specialists'))
from lab import Lab
args.out.mkdir(parents=True,exist_ok=False)
shutil.copytree(args.repo/'tools/specialists/reference/web/tests',args.out/'tests')
(args.out/'node_modules').symlink_to(args.node_modules.resolve(),target_is_directory=True)
p=args.out/'tests/parcel.spec.js';source=p.read_text();needle="  await assertOrder(page, request, journey, 1, '1 parcels — $5.00', response);"
assert source.count(needle)==1
p.write_text(source.replace(needle,needle+'\n  await page.close();'))
server=Lab('good');thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
identity=args.out/'identity.json';identity.write_text(json.dumps(server.identity()))
try:
 env=dict(os.environ,QA_IDENTITY=str(identity),PLAYWRIGHT_JSON_OUTPUT_NAME=str(args.out/'result.json'))
 command=['node',str(args.node_modules/'@playwright/test/cli.js'),'test','-c','tests','--browser=chromium','--workers=1','--retries=0','--grep=minimum quantity','--reporter=list,json','--output='+str(args.out/'browser-output')]
 result=subprocess.run(command,cwd=args.out,env=env,text=True,capture_output=True,timeout=90)
 (args.out/'console.log').write_text(result.stdout+result.stderr)
 remaining={}
 for actor in ('alice','bob'):
  request=urllib.request.Request(server.identity()['url']+'/orders',headers={'X-Lab-Actor':actor})
  with urllib.request.urlopen(request,timeout=2) as response:remaining[actor]=json.load(response)
 report=json.loads((args.out/'result.json').read_text())
 assertions={'teardown_failure_retained':result.returncode==1 and report['stats']['unexpected']==1,'page_closed_diagnostic_retained':'Target page, context or browser has been closed' in result.stdout,'owned_orders_removed':remaining=={'alice':[],'bob':[]}}
 (args.out/'probe.json').write_text(json.dumps({'kind':'real Chromium fault injection into disposable test copy; only added page.close after existing assertions','command':command,'exit':result.returncode,'orders_after':remaining,'assertions':assertions},indent=2))
 print(json.dumps(assertions));assert all(assertions.values())
finally:
 server.shutdown();server.server_close();thread.join(5)
