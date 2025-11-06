Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
  + create

Terraform will perform the following actions:

  # azurerm_storage_blob.example will be created
  + resource "azurerm_storage_blob" "example" {
      + access_tier            = (known after apply)
      + content_type           = "application/octet-stream"
      + id                     = (known after apply)
      + metadata               = (known after apply)
      + name                   = "sample.txt"
      + parallelism            = 8
      + size                   = 0
      + source                 = "./sample.txt"
      + storage_account_name   = "maikumastorageacct"
      + storage_container_name = "example-container"
      + type                   = "Block"
      + url                    = (known after apply)
    }

  # azurerm_storage_container.example will be created
  + resource "azurerm_storage_container" "example" {
      + container_access_type             = "private"
      + default_encryption_scope          = (known after apply)
      + encryption_scope_override_enabled = true
      + has_immutability_policy           = (known after apply)
      + has_legal_hold                    = (known after apply)
      + id                                = (known after apply)
      + metadata                          = (known after apply)
      + name                              = "example-container"
      + resource_manager_id               = (known after apply)
      + storage_account_name              = "maikumastorageacct"
    }

Plan: 2 to add, 0 to change, 0 to destroy.