import time,json,subprocess
from pathlib import Path
last=None
for _ in range(200):
 vals=list(map(int,Path('/proc/stat').read_text().splitlines()[0].split()[1:]));total=sum(vals);idle=vals[3]+vals[4];cpu=None if last is None else round(100*(1-(idle-last[1])/(total-last[0])),2);last=(total,idle)
 mem={x.split(':')[0]:int(x.split()[1]) for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith(('MemTotal:','MemAvailable:'))}
 print(json.dumps({'time':time.time(),'cpu_pct':cpu,'mem_total_kib':mem['MemTotal'],'mem_available_kib':mem['MemAvailable'],'loadavg':Path('/proc/loadavg').read_text().split()[:3]}),flush=True);time.sleep(10)
