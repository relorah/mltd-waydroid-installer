import importlib.util
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('apt_guard', ROOT / 'lib/apt_guard.py')
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class UbuntuTests(unittest.TestCase):
    def shell(self, body):
        return subprocess.run(['bash', '-c', 'set -Eeuo pipefail; source "$1/install.sh"; ' + body,
                               '_', str(ROOT)], capture_output=True, text=True)

    def test_detection(self):
        for ident, version, family in [('ubuntu', '26.04', 'ubuntu'), ('ubuntu', '24.04', 'unsupported'),
                                       ('arch', '', 'arch'), ('cachyos', '', 'arch'),
                                       ('fedora', '44', 'fedora'), ('debian', '13', 'unsupported')]:
            result = self.shell(f'ID={ident}; VERSION_ID={version}; detect_host; echo "$HOST_FAMILY"')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), family)

    def test_dependencies(self):
        result = self.shell('packages=(); ubuntu_packages; printf "%s\\n" "${packages[@]}"')
        self.assertEqual(result.returncode, 0, result.stderr)
        packages = result.stdout.splitlines()
        self.assertIn('python3-venv', packages)
        self.assertIn('dnsmasq-base', packages)
        self.assertFalse(any(guard.protected(p) for p in packages))

    def test_dpkg_partial_install_is_missing(self):
        result = self.shell('packages=(good partial absent); dpkg-query() { case "$3" in good) echo "install ok installed";; partial) echo "install ok unpacked";; *) return 1;; esac; }; ubuntu_missing; printf "%s\\n" "${missing[@]}"')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), ['partial', 'absent'])

    def test_plan_rejects_host_changes_and_removal(self):
        for name in ['linux-image-7.1.7', 'mesa-vulkan-drivers', 'libgl1:amd64',
                     'libdrm2', 'ps5-kernel', 'linux-firmware', 'libegl-mesa0']:
            with self.assertRaises(ValueError):
                guard.validate_plan([f'Inst {name} (1 repository)'])
        with self.assertRaises(ValueError):
            guard.validate_plan(['Remv unrelated-package [1]'])
        guard.validate_plan(['Inst waydroid (1 repository)', 'Inst python3-venv (1 repository)'])

    def test_hook_rejects_actual_protected_deb(self):
        import tempfile
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp) / 'pkg'
            (folder / 'DEBIAN').mkdir(parents=True)
            (folder / 'DEBIAN/control').write_text('Package: mesa-test\nVersion: 1\nArchitecture: all\nMaintainer: test <test@example.com>\nDescription: guard fixture\n')
            deb = Path(temp) / 'test.deb'
            subprocess.run(['dpkg-deb', '--build', str(folder), str(deb)], check=True, capture_output=True)
            result = subprocess.run(['python3', str(ROOT / 'lib/apt_guard.py')], input=str(deb)+'\n', text=True, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('mesa-test', result.stderr)

    def test_module_path_fallback(self):
        result = self.shell('uname() { echo test; }; module_directory')
        self.assertNotEqual(result.returncode, 0)

    def test_empty_waydroid_directory_is_fresh_but_partial_state_is_preserved(self):
        body = (
            'tmp=$(mktemp -d); mkdir -p "$tmp/state"; '
            'sudo() { "$@"; }; '
            'if has_existing_waydroid_state "$tmp/state" "$tmp/user" "$tmp/images"; '
            'then echo existing; else echo fresh; fi; '
            'touch "$tmp/state/waydroid.cfg"; '
            'if has_existing_waydroid_state "$tmp/state" "$tmp/user" "$tmp/images"; '
            'then echo existing; else echo fresh; fi; '
            'rm "$tmp/state/waydroid.cfg"; mkdir -p "$tmp/state/partial"; '
            'if has_existing_waydroid_state "$tmp/state" "$tmp/user" "$tmp/images"; '
            'then echo existing; else echo fresh; fi'
        )
        result = self.shell(body)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.splitlines(), ['fresh', 'existing', 'existing'])


if __name__ == '__main__':
    unittest.main()

class PackageBranchTests(unittest.TestCase):
    shell = UbuntuTests.shell
    def test_existing_package_managers_preserved(self):
        for family, expected in [('arch', ['pacman -Syu --needed']),
                                 ('fedora', ['dnf upgrade --refresh', 'dnf install'])]:
            body = '''HOST_FAMILY=FAMILY; confirm() { return 0; }; pacman() { return 1; }; rpm() { return 1; }; command() { return 1; }; sudo() { printf '%s\\n' "$*"; }; check_kernel() { :; }; prepare_ubuntu_network() { :; }; check_amd() { :; }; install_packages'''.replace('FAMILY;', family+';', 1)
            result = self.shell(body)
            self.assertEqual(result.returncode, 0, result.stderr)
            for cmd in expected:
                self.assertIn(cmd, " ".join(result.stdout.split()))
            self.assertNotIn('apt-get', result.stdout)
