#!/usr/bin/env python3
"""Safely change only the recognized Waydroid native nft selector."""
import os
from pathlib import Path
import stat
import tempfile

SCRIPT = Path('/usr/lib/waydroid/data/scripts/waydroid-net.sh')


def enable(path=SCRIPT):
    path = Path(path)
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise ValueError('Waydroidスクリプトは通常ファイルである必要があります。')
    original = path.read_bytes()
    lines = original.splitlines(keepends=True)
    selectors = [i for i, line in enumerate(lines) if line.startswith(b'LXC_USE_NFT=')]
    if len(selectors) != 1:
        raise ValueError('未知のWaydroidスクリプト構造です。変更しません。')
    index = selectors[0]
    if lines[index].rstrip(b'\n') == b'LXC_USE_NFT="true"':
        return None
    if lines[index].rstrip(b'\n') != b'LXC_USE_NFT="false"' or b'start_nftables()' not in original:
        raise ValueError('内蔵nftables方式を確認できません。変更しません。')
    fd, backup = tempfile.mkstemp(prefix=path.name + '.mwi-backup-', dir=path.parent)
    with os.fdopen(fd, 'wb') as out:
        out.write(original)
        out.flush()
        os.fsync(out.fileno())
    os.chmod(backup, stat.S_IMODE(info.st_mode))
    lines[index] = b'LXC_USE_NFT="true"\n'
    fd, temporary = tempfile.mkstemp(prefix='.mwi-net-', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as out:
            out.write(b''.join(lines))
            os.fchmod(out.fileno(), stat.S_IMODE(info.st_mode))
            os.fchown(out.fileno(), info.st_uid, info.st_gid)
            out.flush()
            os.fsync(out.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    print(f'Waydroid nftables有効化。元スクリプト: {backup}')
    return Path(backup)


if __name__ == '__main__':
    enable()
