#!/usr/bin/env python3
"""GitHub-hosted autosync: run ON the GitHub runner (no local machine involved).
Pulls upstream hezhanleiok/freesub main_v2.py, applies user customizations
(- github suffix + custom source list), pushes to fork main_v2.py via
Contents API, then dispatches the fork's Actions build if idle.
Config via env: SYNC_TOKEN, FORK, UPSTREAM, SUFFIX.
"""
import json, os, base64, urllib.request

API = 'https://api.github.com'
TOK = os.environ['SYNC_TOKEN']
FK = os.environ.get('FORK', 'tthhjkk/freesub-')
UP = os.environ.get('UPSTREAM', 'hezhanleiok/freesub')
SUFFIX = os.environ.get('SUFFIX', 'github')
WF = int(os.environ.get('WORKFLOW_ID', '361298492'))
CUST_FILE = os.environ.get('CUSTOM_SOURCES', 'custom-sources.txt')

def api(method, path, auth=True, raw=False, data=None, timeout=60):
    url = API + path
    req = urllib.request.Request(url, method=method)
    req.add_header('User-Agent', 'freesub-cron')
    req.add_header('Accept', 'application/vnd.github+json')
    if auth:
        req.add_header('Authorization', f'token {TOK}')
    if data is not None:
        req.add_header('Content-Type', 'application/json')
    body = json.dumps(data).encode() if data is not None else None
    try:
        with urllib.request.urlopen(req, timeout=timeout, data=body) as r:
            out = r.read().decode()
            return out if raw else json.loads(out)
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors='replace')[:300]
        raise SystemExit(f'API {method} {path} -> HTTP {e.code}: {detail}')

def main():
    # 1) upstream file
    up = api('GET', f'/repos/{UP}/contents/scripts/main_v2.py', auth=False)
    src = base64.b64decode(up['content']).decode('utf-8')
    print(f"upstream main_v2.py sha={up['sha'][:8]} bytes={len(src)}")

    # 2) apply customization
    desired = src.replace('- xiaohe', '- ' + SUFFIX)
    urls = []
    if os.path.exists(CUST_FILE):
        for l in open(CUST_FILE, encoding='utf-8'):
            l = l.strip()
            if l and not l.startswith('#'):
                urls.append(l)
    marker = 'SOURCE_URLS = ['
    if marker in desired and urls:
        ins = ''.join(f'    "{u}",\n' for u in urls if u not in desired)
        if ins:
            desired = desired.replace(marker + '\n', marker + '\n' + ins, 1)
            print(f"injected {len(ins.splitlines())} custom source lines")

    # 3) compare & update fork
    fk = api('GET', f'/repos/{FK}/contents/scripts/main_v2.py?ref=main')
    fk_content = base64.b64decode(fk['content']).decode('utf-8')
    if desired != fk_content:
        api('PUT', f'/repos/{FK}/contents/scripts/main_v2.py', data={
            'message': f'autosync: track upstream + -{SUFFIX} customization',
            'content': base64.b64encode(desired.encode()).decode('ascii'),
            'sha': fk['sha'], 'branch': 'main'})
        print('fork main_v2.py updated via Contents API')
    else:
        print('up-to-date: fork already matches upstream+custom')

    # 4) dispatch build if idle
    runs = api('GET', f'/repos/{FK}/actions/runs?per_page=1&status=active')
    if runs.get('workflow_runs'):
        st = runs['workflow_runs'][0]['status']
        print(f'build already {st}; skip trigger')
    else:
        req = urllib.request.Request(
            f"{API}/repos/{FK}/actions/workflows/{WF}/dispatches",
            method='POST', data=b'{"ref":"main"}')
        req.add_header('User-Agent', 'freesub-cron')
        req.add_header('Authorization', f'token {TOK}')
        req.add_header('Content-Type', 'application/json')
        with urllib.request.urlopen(req, timeout=30) as r:
            print('dispatch HTTP', r.status)

main()
