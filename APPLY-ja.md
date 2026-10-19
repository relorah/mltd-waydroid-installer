# MWI 0.32 Ubuntu 26.04 / PS5 7.1.7 対応

元ソース: この環境から読み取り可能だった /home/re/Desktop/MWI_0.2.5。
元ディレクトリには書き込んでいません。--install/--reset/--reinstall は実行していません。

## 推奨: 別フォルダで使用

ZIPとMWI_0.32-SHA256SUMS.txtを同じフォルダに置き、通常ユーザーのホスト端末で実行します。
以下の最初のcdはダウンロード先に合わせてください。

```bash
cd ~/Downloads
sha256sum -c MWI_0.32-SHA256SUMS.txt
mkdir -p ~/Desktop/MWI-Ubuntu-review
unzip -n MWI_0.32.zip -d ~/Desktop/MWI-Ubuntu-review
cd ~/Desktop/MWI-Ubuntu-review/MWI_0.32
bash -n install.sh
bash -n lib/lifecycle.sh
python3 -m unittest discover -s tests -v
bash install.sh --dry-run
```

既存の展開先がある場合は別名の空フォルダを使ってください。

--dry-run はユーザーログ以外を変更しません。サービス、APT索引、モジュールを変更せず、
現在のAPT索引で依存解決を確認します。不足がなければAPT計画作成は省略されます。
ro/nodev のbinderfs警告が出た場合は、通常のPS5ホスト端末で次を確認してください。

```bash
uname -r
findmnt -t binder
ls -l /dev/binderfs
lsmod | grep -E '^(veth|bridge|binder_linux)\b'
```

binder_linux は組込みの場合lsmodに出ません。binderfsの存在で併せて確認します。
veth/bridge が未ロードで診断停止する場合は、ホストで `sudo modprobe veth` と
`sudo modprobe bridge` を実行し、再診断してください。
モジュールディレクトリがない場合も、既存の組込み機能を検査します。
ro/nodevのbinderfsはこのサンドボックスから見える制限である可能性があります。
自動remountやカーネル交換は行いません。

続いて、通常ユーザーで（sudoを先頭に付けず）:

```bash
bash install.sh --diagnose
```

これはsudo認証と /var/lib/mwi/install.lock の作成を伴います。サービスは起動しません。
診断で既存環境がないこと、binderfs・veth・bridge、Wayland、AMD render node、
同梱libnbの検査結果を確認してから、新規導入を実行できます。

```bash
bash install.sh
```

既存環境があれば --install は停止します。既存A11の修復は --repair、
全環境を退避して作り直す場合は --reset。--reinstall はデータを削除するため使わないでください。
対話確認は既存どおり残しています。新しいZIPを削除しても、実行後のWaydroid環境は戻りません。
変更後の復元はインストーラーの表示するバックアップと --restore を使用してください。

## 変更と検証

- Ubuntu 26.04を明示対応。Arch/CachyOS、dnf Fedora、rpm-ostree除外を維持。
- Ubuntuの不足パッケージだけを導入。python3-venv、lxc、dnsmasq-baseを含む。
- 全体upgradeなし。APT計画と実debのフックでカーネル・Mesa・firmware類を拒否し、削除も拒否。
- Waydroid配布元の追加や別Ubuntu版への偽装はしない。候補なしなら停止。
- /lib/modules と /usr/lib/modules、binderfs、veth、bridgeを確認。
- NAT検出でiptables/nft/legacyの各frontendを確認。alternativesは変更しない。
- Android 11イメージ、Houdini固定commit、libnbバイナリ、退避・削除ガードを維持。
- Bash構文検査成功、既存と追加の26テスト成功、パッチ適用前検査・適用・差分一致、ZIP整合性確認成功。
- 実環境のread-only診断: Ubuntu 26.04.1、uname 7.1.7、Wayland、/lib/modules/7.1.7、veth/bridge、binderfs、依存導入済み。
- binderfsはこの実行環境ではro/nodev。Android起動、GPU描画、ミリシタ、音声は未検証。
- APT不足パッケージ導入の実行とArch/Fedora実機検証は未実施。既存処理の分岐はモックテストで確認。

Waydroid公式のUbuntu導入案内: https://docs.waydro.id/usage/install-on-desktops
APT install/--simulate/--no-remove/--no-upgradeの根拠: https://manpages.ubuntu.com/manpages/noble/man8/apt-get.8.html
現行の公式Waydroid案内は26.04用配布元の自動設定を保証していないため、候補がない場合は手動で配布元対応を確認してください。

0.32追加: Ubuntu 26.04 / PS5 Linux 7.1.7対応と進捗表示。CachyOS/Arch・Fedoraの既存分岐を維持。新規フルインストールとゲーム動作は未検証です。

0.31: Ubuntuでlegacy iptables未対応の場合、Waydroidスクリプトを一意名でバックアップし、内蔵nftablesへ切替します。ホスト全体のalternativesやruleset全消去は行いません。既存Android 11は --repair で続行してください。
