#!/usr/bin/env bash
# Ubuntu uses the official Waydroid APT repository and distro Python venv.
ubuntu_package_installed() {
    [[ "$(dpkg-query -W -f='${db:Status-Status}' "$1" 2>/dev/null || true)" == installed ]]
}
ubuntu_apt_candidate() {
    local value
    value="$(LC_ALL=C apt-cache policy "$1" | awk '/Candidate:/ {print $2; exit}')"
    [[ -n "$value" && "$value" != '(none)' ]]
}
prepare_ubuntu_repository() {
    sudo apt-get update
    sudo apt-get install -y ca-certificates curl software-properties-common
    sudo add-apt-repository -y universe
    sudo apt-get update
    # Preserve repositories already supplying Waydroid.
    ubuntu_apt_candidate waydroid && return 0
    local codename="${UBUNTU_CODENAME:-${VERSION_CODENAME:-}}"
    case "$codename" in
        jammy|noble|resolute) ;;
        *) die "Waydroid APT導入の対象外Ubuntuです: $codename。公式リポジトリを先に設定してください。" ;;
    esac
    local list=/etc/apt/sources.list.d/waydroid.list key=/usr/share/keyrings/waydroid.gpg
    if sudo test -e "$list" || sudo test -e "$key"; then
        die '既存のWaydroid APT設定に利用可能な候補がありません。既存ファイルを保持して中止します。公式手順に沿って設定を確認してください。'
    fi
    confirm "Waydroid公式APTリポジトリ（repo.waydro.id / $codename）を追加しますか" || die 'リポジトリ追加を中止しました。'
    # Download before modifying /etc. signed-by confines trust to this source.
    local downloaded
    downloaded="$(mktemp "$CACHE_DIR/waydroid-key.XXXXXX")"
    curl --proto '=https' --tlsv1.2 -fL --retry 3 https://repo.waydro.id/waydroid.gpg -o "$downloaded"
    [[ -s "$downloaded" ]] || die 'Waydroid署名鍵が空です。'
    sudo install -m 0644 "$downloaded" "$key"
    rm -f -- "$downloaded"
    printf 'deb [arch=amd64 signed-by=%s] https://repo.waydro.id/ %s main\n' "$key" "$codename" | sudo tee "$list" >/dev/null
    sudo apt-get update
    ubuntu_apt_candidate waydroid || die '公式リポジトリにWaydroid候補がありません。'
}
