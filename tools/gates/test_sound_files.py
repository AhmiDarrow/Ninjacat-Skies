"""Every shipped .ogg must be a plain Vorbis stream: Minecraft reads the first logical stream only, so an ogg that
opens with anything else (ffmpeg keeps a cover-art picture as a Theora video stream unless told -vn) never plays."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def bad_oggs():
    bad = []
    for ogg in sorted((ROOT / 'mods').glob('*/src/main/resources/assets/*/sounds/**/*.ogg')):
        head = ogg.read_bytes()[:64]
        if not head.startswith(b'OggS') or head[28:35] != b'\x01vorbis':
            bad.append(str(ogg.relative_to(ROOT)))
    return bad


class SoundFileTests(unittest.TestCase):
    def test_every_ogg_is_vorbis(self):
        self.assertEqual([], bad_oggs())


if __name__ == '__main__':
    result = unittest.main(exit=False, verbosity=1).result
    sys.exit(0 if result.wasSuccessful() else 1)
