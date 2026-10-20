# Mirishita Waydroid Installer (MWI) 0.32

CachyOS / Arch Linux / Fedora / Ubuntu 26.04 + Waydroid Android 11環境で「アイドルマスター ミリオンライブ！ シアターデイズ（ミリシタ）」の動作環境を構築します。

## 対応環境

- x86_64、AMD Radeon（`amdgpu`）
- CachyOS / Arch Linux
- dnf版Fedora（KDE Plasmaを含む、実機未検証。Kinoiteなどrpm-ostree版は対象外）
- Ubuntu 26.04 / PS5 Linux Kernel 7.1.7
- Wayland

## テスト環境

- AMD Ryzen 7 9700X + Radeon RX 6600 XT
- AMD BC250
- SONY PS5 FW13.60

CachyOSおよびUbuntuにて動作確認済み。Fedoraは実機未確認です。

## 使い方

```bash
cd MWI_v0.32
chmod +x install.sh
./install.sh
```

既存Waydroidがあれば、1: 診断、2: Houdini・libnb修復、3: 全環境退避して新規導入、4: 上書き再インストール（データも初期化）、0: 終了を選べます。

## 導入内容

新規導入はAndroid 11 GAPPS（2025-06-28版）。Houdiniは固定コミットのwaydroid_scriptから取得し、同梱libnbとNativeBridge設定を適用します。

ネットワーク接続を確認し、必要に応じてWaydroidを再起動します。UFW・firewalldの例外追加は事前確認し、Waydroidに必要な範囲だけを対象とします。既存設定の上書きやルールの重複追加は行いません。UFWへの追加は永続、firewalldへの追加は再起動まで有効です。

## 修復・復元

- `./install.sh --diagnose`：診断
- `./install.sh --repair`：Android 11環境のHoudini・libnb修復とネットワーク確認
- `./install.sh --reset`：既存環境を退避して新規導入（`RESET_WAYDROID=1 ./install.sh`も同じ）
- `./install.sh --reinstall`：上書き再インストール。既存Waydroid・現在ユーザーのゲーム／ログインデータ・指定イメージを削除し、Android 11 GAPPS + Houdini + libnbを再導入
- `./install.sh --restore BACKUP`：修復前の設定・overlayを復元

**上書き再インストール（4 / `--reinstall`）は退避せず削除します。** 削除対象は `/var/lib/waydroid`、現在ユーザーのWaydroidデータ（通常 `~/.local/share/waydroid`）、`/etc/waydroid-extra/images` です。削除前に `[y/N]` で確認し、両イメージのダウンロード・ZIP検査に成功してから停止・削除します。**削除した環境は `--restore` では戻せません。**
バックアップは`/var/lib/mwi/backups/`、ログは通常`~/.local/state/mwi/logs/`に保存します。

## 出典・謝辞

[mogareta7731氏](https://zenn.dev/mogareta7731/articles/94204fa83b239b)が配布したAndroid-x86 ISOに同梱されていたパッチ済み`test_nb`を、バイナリ・LICENSEとも無改変で使用しています。元プロジェクトは[qwerty12356-wart氏のtest_libnb](https://github.com/qwerty12356-wart/test_libnb)、BSD 2-Clauseです。MWI本体はMIT Licenseです。
両氏および[Waydroid](https://github.com/waydroid/waydroid)・[waydroid_script](https://github.com/casualsnek/waydroid_script)の作者に心より感謝します。
