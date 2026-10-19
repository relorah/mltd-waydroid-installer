# Mirishita Waydroid Installer (MWI) 0.32

CachyOS / Arch Linux / Fedora / Ubuntu 26.04 + Waydroid Android 11環境で「アイドルマスター ミリオンライブ！ シアターデイズ（ミリシタ）」の動作環境を構築します。必要なホストパッケージだけを確認・導入します。Ubuntuでは全体更新やPS5向けカーネル・Mesaの置換を行いません。

## 対応環境

- x86_64、AMD Radeon（`amdgpu`）
- CachyOS / Arch Linux
- dnf版Fedora（KDE Plasmaを含む、実機未検証。Kinoiteなどrpm-ostree版は対象外）
- Ubuntu 26.04 / PS5 Linux 7.1.7（診断とパッケージ安全性を確認。フルインストール未検証）
- Wayland

## テスト環境

- AMD Ryzen 7 9700X + Radeon RX 6600 XT
- AMD BC250

CachyOSでの実行実績があります。Ubuntu 26.04は実機でread-only診断を確認しましたが、この版によるフルインストールとゲーム起動は未検証です。Fedora対応と今回のネットワーク修正も実機未確認です。

## 使い方

x86_64・AMD GPU・Wayland・binderfs対応カーネル・sudo権限が必要です。
配布ZIP `MWI_v0.32.zip` を展開し、`MWI_v0.32/` 内で通常ユーザーとして実行します（ディレクトリ名は `MWI_v[ver]` 形式）。

```bash
cd MWI_v0.32
chmod +x install.sh
./install.sh
```

既存Waydroidがあれば、1: 診断、2: Houdini・libnb修復、3: 全環境退避して新規導入、4: 上書き再インストール（データも初期化）、0: 終了を選べます。
変更前の確認はすべて `[y/N]` 表示です。続行する場合は `y` または `Y` を入力してください。空入力やそれ以外の入力では拒否します（必須操作は中止、任意のUFW例外は追加せず続行）。

## 配布ZIPの生成

リポジトリ内で `python3 tools/build_zip.py` を実行すると、READMEの版番号に合わせた `dist/MWI_v0.32.zip` を生成します。ZIP内のトップディレクトリは `MWI_v0.32/` です。GitHubの自動生成ソースZIPはこの配布ZIPとは異なります。

## 導入内容

新規導入はAndroid 11 GAPPS（2025-06-28版）。Houdiniは固定コミットのwaydroid_scriptから取得し、同梱libnbとNativeBridge設定を適用します。

ネットワークはDHCP・route・DNS・forwarding・NAT・HTTPSを確認し、必要に応じて再起動を行います。UFW例外は任意で、インストール・修復時にUFWがactiveかつ必要ルールが不足している場合のみ `Waydroid用のUFW例外を追加しますか [y/N]` と確認します。`y` / `Y` の場合のみ不足するDHCP UDP/67・DNS UDP/TCP 53・転送許可を追加し、`n` / Enterなら変更せず続行します。同じ実行中の再確認や既存ルールの重複追加は行わず、他のUFW設定は変更しません。拒否後にネットワーク検証が失敗した場合は、DHCP/DNSがUFWに遮断されている可能性と確認箇所を表示します。firewalldでは確認後に`waydroid0`のみ実行中のtrusted zoneへ追加します（Androidからホストへの通信も許可、firewalld再起動で解除）。既存の独自zone・nftablesルールは上書きしません。

**背景化時はAndroid sessionが停止します。** 追加したUFWルールは復元対象外です。

## 修復・復元

- `./install.sh --diagnose`：診断
- `./install.sh --repair`：Android 11環境のHoudini・libnb修復とネットワーク確認
- `./install.sh --reset`：既存環境を退避して新規導入（`RESET_WAYDROID=1 ./install.sh`も同じ）
- `./install.sh --reinstall`：上書き再インストール。既存Waydroid・現在ユーザーのゲーム／ログインデータ・指定イメージを削除し、Android 11 GAPPS + Houdini + libnbを再導入
- `./install.sh --restore BACKUP`：修復前の設定・overlayを復元

**上書き再インストール（4 / `--reinstall`）は退避せず削除します。削除対象は `/var/lib/waydroid`、現在ユーザーのWaydroidデータ（通常 `~/.local/share/waydroid`）、`/etc/waydroid-extra/images` です。削除前に `[y/N]` で確認し、両イメージのダウンロード・ZIP検査に成功してから停止・削除します。削除した環境は `--restore` では戻せません。**

reset後はゲーム・ログイン状態を引き継ぎません。resetの退避は`--restore`の対象外です。
バックアップは`/var/lib/mwi/backups/`、ログは通常`~/.local/state/mwi/logs/`に保存します。

## 出典・謝辞

[mogareta7731氏](https://zenn.dev/mogareta7731/articles/94204fa83b239b)が配布したAndroid-x86 ISOに同梱されていたパッチ済み`test_nb`を、バイナリ・LICENSEとも無改変で使用しています。元プロジェクトは[qwerty12356-wart氏のtest_libnb](https://github.com/qwerty12356-wart/test_libnb)、BSD 2-Clauseです。MWI本体はMIT Licenseです。
両氏および[Waydroid](https://github.com/waydroid/waydroid)・[waydroid_script](https://github.com/casualsnek/waydroid_script)の作者に心より感謝します。

## 0.2.5: UFW DHCP修復

UFWがactiveの場合、起動・修復・ネットワーク再起動の前に、waydroid0のDHCP UDP/67（IPv4 broadcastと未取得クライアントを含む）、192.168.240.0/24から192.168.240.1へのDNS UDP/TCP 53、同subnetから検出したIPv4 uplinkへのroute forwardingを許可します。inactive・未導入のUFWは変更しません。uplinkを検出できない場合はルール追加前に停止します。

UFWのinsertで同等ルールの重複と既存コメントの書き換えを防ぎます。限定ルールを先頭に配置するため、既存の包括的denyよりWaydroid例外が優先されます。既存ルールの削除、default policyの変更、reset、enable、reloadは行いません。追加ルールは永続化され、従来どおりrestore対象外です。uplink変更時には新uplink向けルールを追加し、旧ルールは削除しません。

DHCP待機失敗時も修復前に即終了せず、再起動後の診断を保存して判定します。最終的にAndroid IPv4に対応するlease、IPv4、全routing table・policy ruleの診断、gateway疎通、NAT、forwarding、DNS、HTTPSを再検証します。ログはnetwork-dhcp-leases.txt、network-ufw-before.txt、network-ufw-apply.txtおよび既存network-*に保存します。

MWI 01の実機結果（DHCP/IPv4/gateway/外部IP/DNS成功、main tableにdefaultなし）を反映し、Android netdのpolicy routingを尊重します。main tableのdefault必須判定と手動route追加を廃止し、DNS・HTTPSの実際の通信を最終判定に使います。gateway/外部IPのpingは診断用途で、ICMPが拒否されてもHTTPS成功を妨げません。全tableとip ruleを保存し、ネットワーク検証コマンドはstdinからWaydroid shellへ渡します。


### Ubuntu 26.04 / PS5 Linux 7.1.7 対応

Ubuntu は ID=ubuntu / VERSION_ID=26.04 のみ変更操作に対応します。
PS5のカーネル、Mesa、firmwareは既存のものを使用します。
不足依存のみ apt-get install --no-upgrade --no-remove --no-install-recommends
で導入し、APT計画と実際のdebを検査して保護対象の変更を拒否します。
APT索引の更新以外に全体upgrade、autoremove、配布元追加は行いません。
Waydroid候補がない場合は停止します。別Ubuntu版の配布元を自動流用しません。
python3-venv、lxc、dnsmasq-base を明示的に確認します。
AppArmor、UFW、Secure Boot、iptables alternativesを無効化・切替しません。
Ubuntuでlegacy方式が利用できない場合は、Waydroid固有スクリプトをバックアップ後、内蔵nftables方式へ切り替えます。
Ubuntu固有のLXC/AppArmor拒否はjournalを確認してください。

最初に通常ユーザーのWayland端末で `bash install.sh --dry-run` を実行してください。
このモードはsudo・サービス操作・モジュール読み込みを行わず、ユーザーの
状態ディレクトリに診断ログのみ作ります。APT情報は現在の索引に基づきます。
`--diagnose` は既存どおりsudo認証・システムロック作成を伴います。
カーネル番号だけで互換性を判定せず、binderfs、veth、bridgeを確認します。
/lib/modules と /usr/lib/modules の両方を探し、組込み機能も許容します。
Android 11イメージ、固定Houdini commit、同梱libnbは変更していません。
実機のAndroid起動・GPU描画・ミリシタ動作は別途検証が必要です。


## 0.32: Ubuntu 26.04 / PS5 Linux 7.1.7対応と進捗表示

system/vendor展開は実際の展開バイト数による進捗バーを表示します。
CRC検証と配置を完了してから100%を表示します。Waydroid初期化は経過時間、
Android起動は経過時間と待機上限を表示します。全体の架空の進捗率は表示しません。
進捗は次回実行から反映されます。実行中の旧版には適用されません。


## 0.31: PS5のネットワーク起動修正

Ubuntuでlegacy iptablesのfilter/nat/mangleを確認し、未対応の場合は
Waydroid内蔵nftablesへ変更してからAndroid初期化を行います。
カーネル交換、iptables alternativesの変更、ホストのruleset全消去はしません。
変更前スクリプトは .mwi-backup- で始まる一意名で保存します。
Waydroidのパッケージ更新で設定が戻った場合も次回のMWI実行時に確認します。
今回のPS5では手動nftables切替後にAndroid起動成功を確認済みですが、
この版による全導入とゲーム実行は未検証です。
既にAndroid 11を初期化済みの場合は --repair を使用し、再削除は不要です。


MWI 0.32ではUbuntu 26.04 / PS5 Linux 7.1.7対応、APT安全ガード、進捗表示をまとめました。Ubuntuのread-only診断と既存テストは確認済みですが、このリリースによる新規フルインストール、Android起動、ゲーム動作は未検証です。CachyOS/ArchとFedoraの既存分岐を維持しています。
