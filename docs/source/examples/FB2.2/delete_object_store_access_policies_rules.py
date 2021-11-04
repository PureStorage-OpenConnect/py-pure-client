# delete a rule by policy name
client.delete_object_store_access_policies_rules(policy_names=["acc1/mypolicy"], names=["myrule"])

# delete by policy ID
client.delete_object_store_access_policies_rules(
    policy_ids=["10314f42-020d-7080-8013-000ddt400012"], names=["myrule"])
