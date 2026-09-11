"""Fail-closed distribution rules shared by exports and archive verification."""
import hashlib
import re

# CurseForge rejected 0.7.0-alpha (file 8843687) because our own companion jars rode in overrides/mods. Nothing is
# bundled any more: every jar in pack/mods, ours included, is a CurseForge file referenced from pack/modlist-resolved.json.
#   Ninjacat Skies Core (project 1689718) - the five companion mods nested in one jar (tools/build_core_jar.py)
#   Tribal Power        (project 1684851)
CORE_PROJECT = 1689718
TRIBAL_PROJECT = 1684851
CANONICAL_PROJECT = {'ninjacatskies-core-': CORE_PROJECT, 'tribalpower-': TRIBAL_PROJECT}
# The companions only ever ship inside the Core jar; a loose copy in pack/mods would load twice.
LOOSE_COMPANION = re.compile(r"(?:ninjacatskies|ninjacatlib|clowderhall|voidloom|guardians)-[0-9][A-Za-z0-9.+_-]*\.jar")


def is_owned_jar(name):
    """Jars allowed inside an exported archive. None: CurseForge only accepts manifest references."""
    return False


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
        if LOOSE_COMPANION.fullmatch(jar.name):
            raise ValueError(f'Loose companion jar in pack/mods: {jar.name}; run tools/build_core_jar.py '
                             '(the companions ship inside Ninjacat Skies Core)')
        row = by_file.get(jar.name, {})
        pid, fid = row.get('projectId'), row.get('fileId')
        if type(pid) is not int or type(fid) is not int or pid <= 0 or fid <= 0:
            raise ValueError(f'Unresolved CurseForge dependency: {jar.name}; refusing to bundle jars')
        if pid in projects:
            raise ValueError(f'Duplicate CurseForge project: {pid}')
        for prefix, canonical in CANONICAL_PROJECT.items():
            if jar.name.startswith(prefix) and pid != canonical:
                raise ValueError(f'{jar.name} must use CurseForge project {canonical}')
        sha1 = hashlib.sha1(jar.read_bytes()).hexdigest()
        if row.get('sha1') != sha1:
            raise ValueError(f'Unverified or changed dependency jar: {jar.name}; resolve its official CF file first')
        projects.add(pid)
        entries.append({'projectID': pid, 'fileID': fid, 'required': True})
    return entries
