# Blobコンテナの作成
resource "azurerm_storage_container" "example" {
  name                  = var.container_name
  storage_account_name  = azurerm_storage_account.example.name
  container_access_type = "private"
}

# ローカルファイルをBlobストレージにアップロード
resource "azurerm_storage_blob" "example" {
  name                   = var.blob_name
  storage_account_name   = azurerm_storage_account.example.name
  storage_container_name = azurerm_storage_container.example.name
  type                   = "Block"
  source                 = var.local_file_path
  content_md5            = filemd5(var.local_file_path)  # ファイル内容変更の検出用
}