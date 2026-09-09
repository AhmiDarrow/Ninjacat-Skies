"""Fail-closed distribution rules shared by exports and archive verification."""
import hashlib
import re

# These are original companion mods maintained in this repository, not CF-hosted dependencies.
OWN_JAR = re.compile(r"(?:ninjacatskies|ninjacatlib|clowderhall|voidloom|guardians)-[0-9][A-Za-z0-9.+_-]*\.jar")


def is_owned_jar(name):
    return OWN_JAR.fullmatch(name) is not None


def manifest_entries(jars, resolved):
    by_file = {}
    for row in resolved:
        name = row.get('filename')
        if not name or name in by_file:
            raise ValueError(f'Missing or duplicate dependency filename: {name}')
        by_file[name] = row
    entries = []
    projects = set()
    for jar in jars:
        if is_owned_jar(jar.name):
            continue
        row = by_file.get(jar.name, {})
        pid, fid = row.get('projectId'), row.get('fileId')
        if type(pid) is not int or type(fid) is not int or pid <= 0 or fid <= 0:
            raise ValueError(f'Unresolved CurseForge dependency: {jar.name}; refusing to bundle third-party jars')
        if pid in projects:
            raise ValueError(f'Duplicate CurseForge project: {pid}')
        if jar.name.startswith('tribalpower-') and pid != 1684851:
            raise ValueError('Tribal Power must use CurseForge project 1684851')
        sha1 = hashlib.sha1(jar.read_bytes()).hexdigest()
        if row.get('sha1') != sha1:
            raise ValueError(f'Unverified or changed dependency jar: {jar.name}; resolve its official CF file first')
        projects.add(pid)
        entries.append({'projectID': pid, 'fileID': fid, 'required': True})
    return entries
