#!/usr/bin/env python3
"""Resolve exact local jars to CF manifest entries; never choose a different version.

Uses CurseForge fingerprint matching, then confirms SHA-1 before writing metadata.
Requires CF_API_KEY in the existing ignored secrets file. No jars are uploaded.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import urllib.request
from upload_curseforge import load_secrets

ROOT = Path(__file__).resolve().parents[1]


def fingerprint(data):
    data = data.translate(None, b"\x09\x0a\x0d\x20")
    m = 0x5bd1e995
    h = 1 ^ len(data)
    end = len(data) // 4 * 4
    for (k,) in struct.iter_unpack('<I', data[:end]):
        k = (k * m) & 0xffffffff
        k ^= k >> 24
        k = (k * m) & 0xffffffff
        h = ((h * m) ^ k) & 0xffffffff
    tail = data[end:]
    if tail:
        h ^= int.from_bytes(tail, 'little')
        h = (h * m) & 0xffffffff
    h ^= h >> 13
    h = (h * m) & 0xffffffff
    return (h ^ (h >> 15)) & 0xffffffff


def api(path, body=None):
    headers = {'x-api-key': load_secrets()['CF_API_KEY'], 'Accept': 'application/json'}
    if body is not None:
        headers['Content-Type'] = 'application/json'
    req = urllib.request.Request('https://api.curseforge.com/v1' + path,
        data=json.dumps(body).encode() if body is not None else None, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.load(response)['data']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    args = ap.parse_args()
    path = ROOT / 'pack/modlist-resolved.json'
    rows = json.loads(path.read_text(encoding='utf-8'))
    indexed = {r['filename']: r for r in rows}
    jars = [p for p in sorted((ROOT / 'pack/mods').glob('*.jar'))
            if not indexed.get(p.name, {}).get('fileId')]
    local = {}
    for p in jars:
        data = p.read_bytes()
        local[p.name] = {'fingerprint': fingerprint(data), 'sha1': hashlib.sha1(data).hexdigest()}
    result = api('/fingerprints/432', {'fingerprints': [r['fingerprint'] for r in local.values()]})
    matches = result['exactMatches']
    projects = api('/mods', {'modIds': sorted({m['file']['modId'] for m in matches})}) if matches else []
    projects = {p['id']: p for p in projects}
    report = []
    for name, value in local.items():
        candidates = [m['file'] for m in matches if m['file']['fileFingerprint'] == value['fingerprint']
                      and any(h['algo'] == 1 and h['value'].lower().zfill(40) == value['sha1'] for h in m['file']['hashes'])
                      and m['file'].get('isAvailable')]
        if len(candidates) != 1:
            print('UNRESOLVED:', name, 'verified matches:', len(candidates))
            report.append({'filename': name, **value, 'resolved': False})
            continue
        f = candidates[0]; project = projects[f['modId']]
        row = indexed.get(name)
        if row is None:
            row = {'key': project['name']}; rows.append(row)
        row.update(name=project['name'], slug=project['slug'], projectId=f['modId'], fileId=f['id'],
                   filename=name, releaseType=f['releaseType'], sha1=value['sha1'])
        report.append({'filename': name, **value, 'resolved': True, 'projectId': f['modId'], 'fileId': f['id']})
        print('VERIFIED:', name, '->', f['modId'], f['id'])
    out = ROOT / 'build/curseforge-resolution.json'; out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    if args.write:
        path.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('Resolved', sum(r['resolved'] for r in report), 'of', len(report), 'previously bundled jars.')

if __name__ == '__main__':
    main()
