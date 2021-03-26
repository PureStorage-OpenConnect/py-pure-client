# remove a member from a policy
client.delete_object_store_access_policies_object_store_users(
    member_names=["acc1/myobjuser"], policy_names=["pure:policy/bucket-list"])

# remove a member from a policy by id
client.delete_object_store_access_policies_object_store_users(
    member_ids=["10314f42-020d-7080-8013-000ddt400090"], policy_ids=["10314f42-020d-7080-8013-000ddt400012"])
