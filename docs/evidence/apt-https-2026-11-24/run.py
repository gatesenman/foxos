import os,json,hashlib,importlib.util,subprocess,shlex,datetime
from pathlib import Path
r=Path('/opt/foxos-artifacts/controller-validation-09b6dde/apt-diagnostic');work=r/'vm';os.environ['FOXOS_E2E_WORK']=str(work);os.environ['FOXOS_E2E_ACCEL']='tcg'
s=importlib.util.spec_from_file_location('e','/workspace/everyos-publish/scripts/os/e2e/iso_e2e.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
iso=Path('/opt/foxos-artifacts/candidate-86c7c2e/FoxOS-0.3.4-candidate-86c7c2e-amd64.iso');assert hashlib.file_digest(iso.open('rb'),'sha256').hexdigest()=='8f7658ba6019b40b2b39ecd9d2e096b323512abd491e92a18f3cce3724530bee'
rows=[]
def probe(name,command,timeout=50):
    p=m.ssh(command,timeout=timeout)
    text=p.stdout+p.stderr
    text='\n'.join(line for line in text.splitlines() if not line.lower().startswith('set-cookie:'))
    (r/(name+'.log')).write_text(text+'\n')
    rows.append({'case':name,'returncode':p.returncode,'command':command})
    (r/'progress.json').write_text(json.dumps(rows,indent=2)+'\n')
    print(m.now(),name,'returncode',p.returncode,flush=True)
    return p
m.boot(str(iso),False,4096,4)
try:
    m.wait_ssh(360)
    probe('configuration',"python3 - <<'P'\nimport os,json,subprocess\nfrom pathlib import Path\nnames=['http_proxy','https_proxy','HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','all_proxy']\na=subprocess.check_output(['apt-config','dump'],text=True)\nprint(json.dumps({'proxy_env_present':{n:bool(os.environ.get(n)) for n in names},'proxy_directive_names':[x.split()[0] for x in a.splitlines() if 'Proxy' in x],'ssl_verify_directives':[x for x in a.splitlines() if 'Verify-Peer' in x or 'Verify-Host' in x],'ca_pem_files':len(list(Path('/etc/ssl/certs').glob('*.pem')))},indent=2))\nP\ncat /etc/apt/sources.list; curl --version; apt-get --version; ldd /usr/lib/apt/methods/https; getent ahostsv4 archive.ubuntu.com")
    url='https://archive.ubuntu.com/ubuntu/dists/noble/InRelease'
    probe('curl-default-get',f"curl --fail --connect-timeout 10 --max-time 25 -sS -w 'http=%{{http_code}} verify=%{{ssl_verify_result}} remote=%{{remote_ip}} bytes=%{{size_download}}\\n' -o /tmp/noble-curl {url}; rc=$?; test $rc = 0 && sha256sum /tmp/noble-curl; exit $rc")
    probe('curl-http11-get',f"curl --http1.1 --fail --connect-timeout 10 --max-time 25 -sS -w 'http=%{{http_code}} verify=%{{ssl_verify_result}} remote=%{{remote_ip}} bytes=%{{size_download}}\\n' -o /tmp/noble-curl11 {url}; rc=$?; test $rc = 0 && sha256sum /tmp/noble-curl11; exit $rc")
    probe('ubuntu-signature',"gpgv --keyring /usr/share/keyrings/ubuntu-archive-keyring.gpg /tmp/noble-curl; rc=$?; test $rc = 0 && cmp /tmp/noble-curl /tmp/noble-curl11; exit $rc")
    probe('apt-default-get',f"/usr/lib/apt/apt-helper -o Acquire::Retries=0 -o Acquire::https::Timeout=15 download-file {url} /tmp/noble-apt")
    config='Dir::Etc::parts "-";\nDir::Etc::main "-";\nAcquire::Retries "0";\nAcquire::https::Timeout "15";\n'
    probe('apt-clean-config-get',"printf %s "+shlex.quote(config)+" > /tmp/foxos-apt-isolated.conf; env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u all_proxy APT_CONFIG=/tmp/foxos-apt-isolated.conf /usr/lib/apt/apt-helper download-file "+url+" /tmp/noble-apt-clean")
finally:
    shutdown=m.poweroff();(r/'shutdown.json').write_text(json.dumps(shutdown,indent=2)+'\n')
(r/'complete.json').write_text(json.dumps({'at':m.now(),'probes':rows,'production_sources_changed':False,'tls_or_signature_bypass':False},indent=2)+'\n')
