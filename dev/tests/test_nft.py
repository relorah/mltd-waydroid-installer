import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('nft_fix', Path(__file__).resolve().parents[2] / 'lib/waydroid_nft.py')
fix = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fix)


class NftTests(unittest.TestCase):
    def test_backup_exact_and_idempotent(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'net.sh'
            original = b'#!/bin/sh\nLXC_USE_NFT="false"\nstart_nftables() { :; }\n'
            p.write_bytes(original)
            p.chmod(0o755)
            backup = fix.enable(p)
            self.assertEqual(backup.read_bytes(), original)
            self.assertIn(b'LXC_USE_NFT="true"', p.read_bytes())
            self.assertEqual(p.stat().st_mode & 0o777, 0o755)
            self.assertIsNone(fix.enable(p))

    def test_unknown_and_symlink_refused(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'net.sh'
            p.write_bytes(b'unknown')
            with self.assertRaises(ValueError): fix.enable(p)
            self.assertEqual(p.read_bytes(), b'unknown')
            link = Path(d) / 'link'
            link.symlink_to(p)
            with self.assertRaises(ValueError): fix.enable(link)
