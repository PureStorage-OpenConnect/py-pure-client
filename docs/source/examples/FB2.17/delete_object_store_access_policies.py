# delete a policy by name
client.delete_object_store_access_policies(names=["acc1/mypolicy"])

# delete a policy by ID
client.delete_object_store_access_policies(ids=["10314f42-020d-7080-8013-000ddt400012"])

# Other valid fields: context_names
# See section "Common Fields" for examples
