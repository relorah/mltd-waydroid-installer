# MLTD Waydroid Installer (MWI)

CachyOS / Arch Linux / Fedora 環境で「アイドルマスター ミリオンライブ！ シアターデイズ（ミリシタ）」の動作環境を構築します。Waydroid（Android 11）および動作に必要なホストパッケージを確認し、システム更新と併せて導入します。

## 対応環境

- x86_64
- AMD Radeon（`amdgpu`）
- CachyOS / Arch Linux / dnf版 Fedora
- Wayland

## テスト環境

- CachyOS
- AMD Ryzen 7 9700X + Radeon RX 6600 XT
- AMD BC250

## インストール方法

```bash
chmod +x install.sh
./install.sh
```

既にWaydroidがインストール済みの場合、1: 診断、2: Houdini・libnb修復、3: 全環境退避して新規導入、4: 上書き再インストール、0: 終了 が選択可能です。

## 導入内容

新規導入はAndroid 11 GAPPS（2025-06-28版）。Houdiniは固定コミットのwaydroid_scriptから取得し、同梱libnbとNativeBridge設定を適用します。

ネットワークはDHCP・DNS・forwarding・NAT・HTTPSを確認します。UFW有効時に必要なルールが不足している場合は、Waydroid用のDHCP・DNS・転送許可を追加するか確認します。追加は任意で、既存ルールや他のUFW設定は変更しません。firewalldでは確認後、`waydroid0`のみ実行中のtrusted zoneへ追加します。既存の独自zone・nftablesルールは上書きしません。

導入後、Waydroidが起動状態となるので、Google Playからミリシタをダウンロードして下さい。

## 修復・復元

- `./install.sh --diagnose`：状態の診断
- `./install.sh --repair`：Android 11環境のHoudini・libnb修復とネットワーク確認
- `./install.sh --reset`：既存環境を退避して新規導入（`RESET_WAYDROID=1 ./install.sh`も同じ）
- `./install.sh --reinstall`：上書き再インストール。データを削除し、Android 11 GAPPS + Houdini + libnbを再導入
- `./install.sh --restore BACKUP`：修復前の設定・overlayを復元

**上書き再インストール（4 / `--reinstall`）は元データを退避せず削除します。削除対象は `/var/lib/waydroid`、現在ユーザーのWaydroidデータ（通常 `~/.local/share/waydroid`）、`/etc/waydroid-extra/images` です。削除した環境は `--restore` では戻せません。**

バックアップは`/var/lib/mwi/backups/`、ログは通常`~/.local/state/mwi/logs/`に保存します。

## 出典・謝辞

[mogareta7731氏](https://zenn.dev/mogareta7731/articles/94204fa83b239b)が配布したAndroid-x86 ISOに同梱されていたパッチ済み`test_nb`を、バイナリ・LICENSEとも無改変で使用しています。元プロジェクトは[qwerty12356-wart氏のtest_libnb](https://github.com/qwerty12356-wart/test_libnb)、BSD 2-Clauseです。MWI本体はMIT Licenseです。
両氏および[Waydroid](https://github.com/waydroid/waydroid)・[waydroid_script](https://github.com/casualsnek/waydroid_script)の作者に感謝します。\
