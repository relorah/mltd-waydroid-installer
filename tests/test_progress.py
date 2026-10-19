import contextlib
import importlib.util
import io
from pathlib import Path
import subprocess
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('state_progress', ROOT / 'lib/state.py')
state = importlib.util.module_from_spec(spec)
spec.loader.exec_module(state)


class ProgressTests(unittest.TestCase):
    def test_extraction_bytes_and_completion(self):
        with tempfile.TemporaryDirectory() as folder:
            state.IMAGE = Path(folder)
            archive = Path(folder) / 'test.zip'
            payload = b'android fixture' * 100000
            with zipfile.ZipFile(archive, 'w') as z:
                z.writestr('system.img', payload)
            output = io.StringIO()
            with contextlib.redirect_stderr(output):
                state.extract_image(archive, Path(folder) / 'system.img')
            self.assertEqual((Path(folder) / 'system.img').read_bytes(), payload)
            self.assertIn('[####################] 100% 配置完了', output.getvalue())

    def test_activity_preserves_failure(self):
        result = subprocess.run(['bash', '-c', 'source "$1/install.sh"; run_with_activity fixture bash -c "exit 7"', '_', str(ROOT)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 7)
        self.assertNotIn('fixture: 完了', result.stdout)
