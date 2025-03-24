# delete the object store virtual host on the array
client.delete_object_store_virtual_hosts(names=["s3.myhost.com"])

# delete by id
client.delete_object_store_virtual_hosts(ids=["10314f42-020d-7080-8013-000ddt400090"])

# Other valid fields: context_names
# See section "Common Fields" for examples
