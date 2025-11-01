Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
-/+ destroy and then create replacement

Terraform will perform the following actions:

  # azurerm_storage_blob.example must be replaced
-/+ resource "azurerm_storage_blob" "example" {
      ~ access_tier            = "Hot" -> (known after apply)
      + content_md5            = "64455ae45bd2ba523591067274b27d43" # forces replacement
      ~ id                     = "https://maikumastorageacct.blob.core.windows.net/example-container/sample.txt" -> (known after apply)
      ~ metadata               = {} -> (known after apply)
        name                   = "sample.txt"
      ~ url                    = "https://maikumastorageacct.blob.core.windows.net/example-container/sample.txt" -> (known after apply)
        # (9 unchanged attributes hidden)
    }

Plan: 1 to add, 0 to change, 1 to destroy.