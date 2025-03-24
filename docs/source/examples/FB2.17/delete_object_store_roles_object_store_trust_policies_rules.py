# remove a rule by role name and rule name
client.delete_object_store_roles_object_store_trust_policies_rules(role_names=["acc1/myobjrole"], names=["myrule"])
# remove a rule by role name and rule index
client.delete_object_store_roles_object_store_trust_policies_rules(role_names=["acc1/myobjrole"], indices=[1])
# remove a rule by role id and rule name
client.delete_object_store_roles_object_store_trust_policies_rules(role_ids=["f8b3b3b3-3b3b-3b3b-3b3b-3b3b3b3b3b3b"], names=["myrule"])
# remove a rule by role id and rule index
client.delete_object_store_roles_object_store_trust_policies_rules(role_ids=["f8b3b3b3-3b3b-3b3b-3b3b-3b3b3b3b3b3b"], indices=[1])
# remove a rule by policy name and rule name
client.delete_object_store_roles_object_store_trust_policies_rules(policy_names=["acc1/myobjrole/trust-policy"], names=["myrule"])
# remove a rule by policy name and rule index
client.delete_object_store_roles_object_store_trust_policies_rules(policy_names=["acc1/myobjrole/trust-policy"], indices=[1])

# Other valid fields: context_names
# See section "Common Fields" for examples
