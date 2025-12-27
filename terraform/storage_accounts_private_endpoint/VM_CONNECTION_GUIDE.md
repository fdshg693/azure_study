# プライベートエンドポイント VM テスト接続ガイド

このガイドは、Terraform で作成した Storage Account のプライベートエンドポイント経由でのアクセスをテストするための完全な手順です。

---

## 📋 目次

1. [前提条件](#前提条件)
2. [Terraform デプロイ手順](#terraform-デプロイ手順)
3. [VM 接続方法](#vm-接続方法)
4. [Storage Account アクセステスト](#storage-account-アクセステスト)
5. [トラブルシューティング](#トラブルシューティング)

---

## 前提条件

### 必要な環境
- Azure CLI がインストール済み
- Terraform がインストール済み （v1.0 以上推奨）
- SSH クライアント（Windows 10以降は標準搭載）
- Azure アカウント（有効なサブスクリプション）

### 認証設定
```bash
# Azure CLI でログイン
az login

# サブスクリプションを確認
az account show

# 異なるサブスクリプションを使用する場合
az account set --subscription "<subscription-id>"
```

---

## Terraform デプロイ手順

### ステップ 1: ディレクトリに移動
```bash
cd terraform/storage_accounts_private_endpoint
```

### ステップ 2: Terraform 初期化
```bash
# Terraform の初期化（Azureプロバイダーをダウンロード）
terraform init
```

**出力例:**
```
Initializing the backend...
Initializing provider plugins...
- Reusing previous version of hashicorp/azurerm from the lock file
- Using previously-installed hashicorp/azurerm v3.x.x
...
Terraform has been successfully configured!
```

### ステップ 3: デプロイプランを確認
```bash
# リソース作成計画を表示
terraform plan -var-file="terraform.dev.tfvars"
```

**確認ポイント:**
- 作成されるリソース数
- リソースグループ、VNet、VM、Storage Account などが含まれているか
- 削除対象のリソースがないか

### ステップ 4: Terraform を適用
```bash
# リソースを作成（確認プロンプトに "yes" で応答）
terraform apply -var-file="terraform.dev.tfvars"
```

**デプロイ時間:**
- 通常: 5～10分
- VM イメージダウンロード: 2～3分
- Private DNS Zone 設定: 1～2分

### ステップ 5: 出力値を確認
```bash
# すべての出力を表示
terraform output

# または、個別に確認
terraform output -raw vm_public_ip
terraform output -raw ssh_command
```

**重要な出力値:**
- `vm_public_ip`: VM の公開 IP アドレス
- `vm_private_ip`: VM のプライベート IP アドレス
- `storage_account_name`: Storage Account 名
- `ssh_command`: SSH 接続コマンド

---

## VM 接続方法

### 方法 1: SSH コマンド（推奨）

#### 基本的な接続コマンド
```bash
# 出力から SSH コマンドを取得（自動）
ssh $(terraform output -raw ssh_command)
```

#### または、手動で構築
```bash
# 変数を取得
SSH_KEY="azureuser"
PUBLIC_IP=$(terraform output -raw vm_public_ip)

# SSH で接続（パスワード認証）
ssh ${SSH_KEY}@${PUBLIC_IP}
```

**接続時のプロンプト:**
```
The authenticity of host '...' can't be established.
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```
→ `yes` と入力して確認

#### パスワード入力
```
azureuser@...'s password:
```
→ terraform.dev.tfvars で設定したパスワードを入力: `P@ssw0rd2024Dev!`

### 方法 2: Azure Portal を使用

1. Azure Portal にログイン
2. 「Virtual Machines」を検索
3. `vm-test-private-endpoint` を選択
4. 「接続」→「SSH」タブをクリック
5. 「接続文字列をコピー」ボタンをクリック
6. Cloud Shell または ローカルターミナルで実行

### 方法 3: Azure Bastion を使用（推奨：本番環境）

```bash
# Bastion ホストを作成（オプション：セキュリティ向上）
# ※ この構成には含まれていないため、別途設定が必要
```

---

## Storage Account アクセステスト

### テスト 1: DNS 解決のテスト（プライベートエンドポイント確認）

#### VM 上で実行
```bash
# VM に SSH 接続後

# Storage Account の DNS 解決テスト
nslookup storagedevendpoint001.blob.core.windows.net

# 期待される出力:
# Name:    storagedevendpoint001.blob.core.windows.net
# Address: 10.0.x.x  (プライベートエンドポイントのプライベート IP)
```

#### ローカルマシンから実行（Windows PowerShell）
```powershell
# Storage Account へのアクセスが拒否される（パブリックアクセス制限）
nslookup storagedevendpoint001.blob.core.windows.net
# → パブリック IP アドレスに解決される
# → 接続試行時は拒否される
```

### テスト 2: Curl でのアクセステスト

#### VM 上で実行
```bash
# VM に SSH 接続後

# Storage Account へのアクセステスト
curl -I https://storagedevendpoint001.blob.core.windows.net/

# 期待される出力（200 OK が返される）:
# HTTP/1.1 200 OK
# Content-Length: 0
# Server: Windows-Azure-Blob/1.0 Microsoft-HTTPAPI/2.0
```

### テスト 3: Azure CLI を使用したアクセステスト

#### VM 上で実行
```bash
# VM に SSH 接続後

# Azure CLI でログイン（スキップ可能：マネージド ID 設定時）
# az login

# Storage Account 情報を変数に設定
STORAGE_ACCOUNT="storagedevendpoint001"
CONTAINER_NAME="dev-data-container"

# Blob リストを確認
az storage blob list \
  --account-name ${STORAGE_ACCOUNT} \
  --container-name ${CONTAINER_NAME} \
  --auth-mode login \
  --output table

# 期待される出力:
# Name              Blob Type    Length
# ----------------  -----------  --------
# dev-data-file.txt  BlockBlob    XXX
```

### テスト 4: テストファイルの作成とアップロード

#### VM 上で実行
```bash
# VM に SSH 接続後

# テスト用ファイルを作成
echo "Test file from VM at $(date)" > /tmp/test-upload.txt

# ファイルをアップロード
az storage blob upload \
  --account-name storagedevendpoint001 \
  --container-name dev-data-container \
  --name "vm-uploaded-$(date +%s).txt" \
  --file /tmp/test-upload.txt \
  --auth-mode login

# アップロード確認
az storage blob list \
  --account-name storagedevendpoint001 \
  --container-name dev-data-container \
  --auth-mode login \
  --output table
```

### テスト 5: 提供されているテストスクリプトを実行

#### VM 上で実行
```bash
# VM に SSH 接続後

# カスタムデータで自動作成されたスクリプトを実行
/home/azureuser/test_storage.sh

# 出力例:
# Testing DNS resolution for Storage Account...
# Server:  127.0.0.53
# Address: 127.0.0.53#53
# 
# Non-authoritative answer:
# Name:    storagedevendpoint001.blob.core.windows.net
# Address: 10.0.1.x
```

---

## 詳細な接続例

### 完全な SSH セッション例

```bash
# 1. Terraform 出力から接続情報を取得
PUBLIC_IP=$(terraform output -raw vm_public_ip)
echo "接続先: $PUBLIC_IP"

# 2. SSH で接続
ssh azureuser@$PUBLIC_IP

# 3. VM 上で実行（パスワード入力後）

# 4. DNS テスト
nslookup storagedevendpoint001.blob.core.windows.net

# 5. Curl テスト
curl -I https://storagedevendpoint001.blob.core.windows.net/

# 6. Azure CLI テスト
az storage blob list \
  --account-name storagedevendpoint001 \
  --container-name dev-data-container \
  --auth-mode login \
  --output table

# 7. SSH セッションを終了
exit
```

### ワンライナーコマンド

```bash
# SSH で接続して、すぐにテストを実行
ssh azureuser@$(terraform output -raw vm_public_ip) << 'EOF'
  echo "=== DNS Resolution Test ==="
  nslookup storagedevendpoint001.blob.core.windows.net
  
  echo ""
  echo "=== Connectivity Test ==="
  curl -I https://storagedevendpoint001.blob.core.windows.net/
  
  echo ""
  echo "=== Blob List Test ==="
  az storage blob list \
    --account-name storagedevendpoint001 \
    --container-name dev-data-container \
    --auth-mode login \
    --output table
EOF
```

---

## トラブルシューティング

### 問題 1: SSH 接続タイムアウト

**症状:**
```
ssh: connect to host XXX.XXX.XXX.XXX port 22: Connection timed out
```

**原因と解決:**

1. **VM がまだ起動していない**
   ```bash
   # VM のステータスを確認
   az vm get-instance-view \
     --resource-group rg-storage-private-endpoint-dev \
     --name vm-test-private-endpoint \
     --query instanceView.statuses
   ```

2. **Network Security Group (NSG) ルール確認**
   ```bash
   # NSG ルールを確認
   az network nsg rule list \
     --resource-group rg-storage-private-endpoint-dev \
     --nsg-name nsg-vm
   ```

3. **SSH ポートが開いているか確認**
   ```bash
   # ローカルマシンから確認
   telnet $(terraform output -raw vm_public_ip) 22
   ```

### 問題 2: パスワード認証が失敗する

**症状:**
```
Permission denied (publickey,password).
```

**原因と解決:**

1. **パスワードが正確に入力されていない**
   - terraform.dev.tfvars で設定: `P@ssw0rd2024Dev!`
   - 大文字小文字を区別して入力

2. **パスワード認証が無効化されている**
   - vm.tf で `disable_password_authentication = false` を確認

### 問題 3: DNS 解決が失敗する

**症状:**
```
nslookup: can't resolve 'storagedevendpoint001.blob.core.windows.net': No address associated with hostname
```

**原因と解決:**

1. **Private DNS Zone がリンクされていない**
   ```bash
   # リンク状況を確認
   az network private-dns link vnet list \
     --resource-group rg-storage-private-endpoint-dev \
     --zone-name privatelink.blob.core.windows.net
   ```

2. **VNet の DNS 設定を確認**
   ```bash
   # VNet の DNS サーバーを確認
   az network vnet show \
     --resource-group rg-storage-private-endpoint-dev \
     --name vnet-storage-pe \
     --query dhcpOptions.dnsServers
   ```

### 問題 4: Storage Account へのアクセスが拒否される

**症状:**
```
curl: (52) Empty reply from server
HTTP/1.1 403 Forbidden
```

**原因と解決:**

1. **パブリックアクセスが制限されている（設計通り）**
   ```bash
   # Storage Account のネットワーク設定を確認
   az storage account show \
     --resource-group rg-storage-private-endpoint-dev \
     --name storagedevendpoint001 \
     --query networkRuleSet
   ```

2. **プライベートエンドポイント経由でアクセスしているか確認**
   - VM 内から実行してください（VNet 内から）

### 問題 5: Azure CLI がインストールされていない

**症状:**
```
bash: az: command not found
```

**解決:**

VM 上で Azure CLI をインストール
```bash
# 方法 1: カスタムデータで自動インストール（初回デプロイ時）
# vm.tf に含まれているため、既にインストール済みのはず

# 方法 2: 手動インストール
curl -sL https://aka.ms/InstallAzureCLIDeb | bash

# インストール確認
az --version
```

### 問題 6: Terraform が状態ファイルをロック

**症状:**
```
Error acquiring the state lock
```

**解決:**

```bash
# ロックを強制解除（注意：他のプロセスが実行中でないことを確認）
terraform force-unlock <LOCK_ID>

# または、状態ファイルをリセット
rm -rf .terraform.lock.hcl
rm -rf terraform.tfstate*

# 再初期化
terraform init
```

---

## リソースのクリーンアップ

### 全リソースを削除

```bash
# デプロイを削除（確認プロンプトに "yes" で応答）
terraform destroy -var-file="terraform.dev.tfvars"

# リソースが削除されたか確認（数分後）
az group show \
  --resource-group rg-storage-private-endpoint-dev \
  2>&1 | grep "not found" && echo "削除完了" || echo "まだ存在"
```

### 部分削除（特定のリソースのみ削除）

```bash
# VM だけを削除
terraform destroy -target=azurerm_linux_virtual_machine.test \
  -var-file="terraform.dev.tfvars"

# Storage Account を除外して削除
terraform destroy -target=azurerm_storage_account.main \
  -var-file="terraform.dev.tfvars"
```

---

## セキュリティ推奨事項

### 1. SSH 公開鍵認証の使用

```bash
# SSH キーペアを生成（初回のみ）
ssh-keygen -t rsa -b 4096 -f ~/.ssh/azure_vm_key

# vm.tf を編集してパスワード認証を無効化
# disable_password_authentication = true
# 
# admin_ssh_key {
#   username   = var.admin_username
#   public_key = file("~/.ssh/azure_vm_key.pub")
# }
```

### 2. NSG ルールで SSH アクセスを制限

```bash
# 特定の IP アドレスからのアクセスのみ許可
az network nsg rule update \
  --resource-group rg-storage-private-endpoint-dev \
  --nsg-name nsg-vm \
  --name AllowSSH \
  --source-address-prefixes "YOUR_IP/32" \
  --access Allow \
  --priority 100
```

### 3. Storage Account アクセスキーの保護

```bash
# アクセスキーを表示（最小限に）
terraform output -raw storage_account_primary_access_key

# または、マネージド ID を使用
# az login で認証後、キーなしでアクセス可能
```

---

## パフォーマンステスト

### ネットワークレイテンシー測定

```bash
# VM 上で実行
ping -c 4 storagedevendpoint001.blob.core.windows.net

# 出力例:
# PING storagedevendpoint001.blob.core.windows.net (10.0.1.x) 56(84) bytes of data.
# 64 bytes from 10.0.1.x: icmp_seq=1 time=0.5 ms
```

### スループットテスト

```bash
# VM 上でテストファイルを作成してアップロード
dd if=/dev/zero bs=1M count=10 of=/tmp/test-10mb.bin

time az storage blob upload \
  --account-name storagedevendpoint001 \
  --container-name dev-data-container \
  --name "perf-test-10mb.bin" \
  --file /tmp/test-10mb.bin \
  --auth-mode login
```

---

## よく使うコマンド集

```bash
# VM の状態確認
terraform output -raw vm_public_ip

# SSH コマンド（ワンライナー）
ssh azureuser@$(terraform output -raw vm_public_ip)

# Storage Account 情報表示
terraform output | grep -i storage

# リソースグループ内のすべてのリソース確認
az resource list \
  --resource-group rg-storage-private-endpoint-dev \
  --output table

# VM のログを確認
az vm diagnostics get-default-config \
  --resource-group rg-storage-private-endpoint-dev \
  --name vm-test-private-endpoint

# 全リソース削除
terraform destroy -var-file="terraform.dev.tfvars"
```

---

## 参考資料

- [Azure Storage Private Endpoint Documentation](https://docs.microsoft.com/en-us/azure/storage/common/storage-private-endpoints)
- [Azure Private DNS Documentation](https://docs.microsoft.com/en-us/azure/dns/private-dns-overview)
- [Azure Virtual Machine SSH Connection](https://docs.microsoft.com/en-us/azure/virtual-machines/linux/mac-create-ssh-keys)
- [Azure CLI Storage Commands](https://docs.microsoft.com/en-us/cli/azure/storage)
- [Terraform Azure Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)

---

**最終更新**: 2025年12月27日
**バージョン**: 1.0
