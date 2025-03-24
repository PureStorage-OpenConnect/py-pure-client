# remove a policy from a role
client.delete_object_store_roles_object_store_access_policies(
    member_names=["acc1/myobjrole"], policy_names=["pure:policy/bucket-list"])

# remove a policy from a role by id
client.delete_object_store_roles_object_store_access_policies(
    member_ids=["10314f42-020d-7080-8013-000ddt400090"], policy_ids=["10314f42-020d-7080-8013-000ddt400012"])

# Other valid fields: context_names
# See section "Common Fields" for examples
