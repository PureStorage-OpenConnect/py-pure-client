from pypureclient.flashblade import NetworkAccessPolicyRule

policyname = 'default-network-access-policy'

# Patch client policy rule 'default-network-rules.1' in network access policy named 'default-network-rules'
res = client.patch_network_access_policies_rules(names=[policyname+'.1'],
                                                 rule=NetworkAccessPolicyRule(effect='deny'))

# Patch a policy by name with a version specifier.
# The Patch will fail if the policy version differs from specified version.
policy_version = '00000000-7b11-a468-0000-0000503669ea'
res = client.patch_network_access_policies_rules(names=[policyname+'.1'],
                                                 rule=NetworkAccessPolicyRule(interfaces=['snmp']),
                                                 versions=[policy_version])

# Insert or Move a rule default-network-rules.1 rule before 'default-network-rules.2` in policy named 'default-network-rules'
res = client.patch_network_access_policies_rules(names=[policyname+'.1'],
                                                 before_rule_name=policyname+'.2',
                                                 rule=NetworkAccessPolicyRule(interfaces=['snmp', "management-ssh"]))

# Insert or Move a rule 'default-network-rules.1` before rule id `10314f42-020d-7080-8013-000ddt400012` in policy named 'default-network-rules'
res = client.patch_network_access_policies_rules(names=[policyname+'.1'],
                                                 before_rule_id="10314f42-020d-7080-8013-000ddt400012",
                                                 rule=NetworkAccessPolicyRule(client='1.1.1.1'))

print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: ids
# See section "Common Fields" for examples