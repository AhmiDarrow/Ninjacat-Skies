"""Headless play test of the Snapped Guardians on a real client.

Runs the pair defined in mods/guardians/build.gradle: `runShowcaseServer` (a flat, offline server the driver owns
through RCON) and `runShowcaseClient` (a client that joins it under Xvfb + llvmpipe, with
-Dguardians.showcase=true so client/GuardianShowcase.java takes labelled screenshots on request).

    cd mods && ./gradlew :guardians:runShowcaseServer &            # build/showcase-server (eula, rcon 25575, port 25599)
    LIBGL_ALWAYS_SOFTWARE=1 xvfb-run -a -s "-screen 0 1280x720x24" ./gradlew :guardians:runShowcaseClient &
    python3 tools/guardians_showcase.py            # every guardian, a live one, and a whole Lint Golem arena loop

Screenshots land in mods/guardians/build/showcase-client/screenshots/. What it proved for 0.7.1: the custom
renderer draws all thirteen (textures, emissive seams, facing, animation), and summon → arena → win → relic → return
works end to end on a client. Needs ~4.5 GB free (1.5 GB server + 3 GB client).
"""
import socket
import struct
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLIENT = ROOT / 'mods/guardians/build/showcase-client'
PLAYER = 'GuardianQA'
RCON = ('127.0.0.1', 25575, 'guardiansqa')
KINDS = ['beddown', 'grindmaw', 'thornmother', 'edgewalker', 'drumheart', 'cogwright', 'hivemind', 'sealbreaker', 'unwoven',
         'lintgolem', 'tangle', 'firstcut', 'overweaver']


def rcon(text):
    host, port, pw = RCON

    def read(sock, n):
        d = b''
        while len(d) < n:
            part = sock.recv(n - len(d))
            if not part:
                raise ConnectionError('rcon closed')
            d += part
        return d

    with socket.create_connection((host, port), timeout=30) as s:
        def send(kind, body):
            data = struct.pack('<ii', 42, kind) + body.encode() + b'\0\0'
            s.sendall(struct.pack('<i', len(data)) + data)

        def recv():
            size = struct.unpack('<i', read(s, 4))[0]
            d = read(s, size)
            return struct.unpack('<ii', d[:8]), d[8:-2].decode(errors='replace')

        send(3, pw)
        if recv()[0][0] < 0:
            raise RuntimeError('rcon auth failed')
        send(2, text)
        return recv()[1]


def client(cmd, timeout=30):
    done = CLIENT / 'showcase-done.txt'
    done.unlink(missing_ok=True)
    (CLIENT / 'showcase-command.txt').write_text(cmd + '\n')
    end = time.time() + timeout
    while time.time() < end:
        if done.is_file():
            r = done.read_text().splitlines()
            return r[1] if len(r) > 1 else '?'
        time.sleep(0.25)
    return 'timeout'


def say(t):
    print(time.strftime('%H:%M:%S'), t, flush=True)


def prepare():
    for c in [f'op {PLAYER}', f'gamemode creative {PLAYER}', 'time set 6000', 'gamerule doDaylightCycle false',
              'gamerule doMobSpawning false', 'forceload add -64 -64 64 64', 'kill @e[type=!player]']:
        rcon(c)
    client('hud off')


def lineup():
    say('every guardian, standing')
    for k in KINDS:
        rcon('kill @e[type=!player]'); time.sleep(0.5)
        dist = 60 if k in ('firstcut', 'overweaver') else 24
        rcon(f'tp {PLAYER} 0 -58 {dist} 180 0'); time.sleep(0.5)
        rcon(f'summon guardians:{k} 0 -60 0 {{PersistenceRequired:1b,NoAI:1b}}'); time.sleep(3.5)
        client('look 180 -8'); time.sleep(1.5)
        say(f'  {k}: {client("shot " + k)}')


def live(kind='edgewalker'):
    say(f'a live {kind}')
    rcon('kill @e[type=!player]'); time.sleep(0.5)
    rcon(f'gamemode survival {PLAYER}'); rcon(f'effect give {PLAYER} minecraft:resistance infinite 5 true')
    rcon(f'tp {PLAYER} 0 -60 18 180 0'); time.sleep(0.5)
    rcon(f'summon guardians:{kind} 0 -60 0 {{PersistenceRequired:1b}}'); time.sleep(1)
    for i in range(4):
        time.sleep(1.0); client('look 180 0'); say(f'  {client(f"shot {kind}_live_{i}")}')
    rcon('kill @e[type=!player]'); rcon(f'gamemode creative {PLAYER}')


def arena_loop():
    say('Lint Golem arena: summon → fight → win → relic → home')
    rcon(f'tp {PLAYER} 0 -60 0 0 0'); time.sleep(1)
    rcon(f'execute as {PLAYER} run guardians summon lintgolem'); time.sleep(8)
    say('  ' + rcon(f'execute as {PLAYER} run guardians status').strip())
    for yaw in (0, 90, 180, 270):
        client(f'look {yaw} 5'); time.sleep(1.2); say(f'  {client(f"shot arena_{yaw}")}')
    rcon('kill @e[type=guardians:lintgolem]'); time.sleep(14)
    say('  dimension ' + rcon(f'data get entity {PLAYER} Dimension').strip())
    say('  relic ' + rcon(f'clear {PLAYER} guardians:relic_lintwisp 0').strip())
    say('  ' + rcon(f'execute as {PLAYER} run guardians status').strip())


if __name__ == '__main__':
    if len(sys.argv) > 1:
        cmd = ' '.join(sys.argv[1:])
        print(client(cmd) if cmd.split()[0] in ('shot', 'look', 'hud', 'attack', 'fov', 'close') else rcon(cmd))
    else:
        prepare(); lineup(); live(); arena_loop()
