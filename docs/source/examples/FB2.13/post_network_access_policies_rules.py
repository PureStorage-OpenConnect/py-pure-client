from pypureclient.flashblade import NetworkAccessPolicyRule

policyname = 'default-network-access-policy'

# Create a new client policy rule in the policy named 'default-network-rules'
res = client.post_network_access_policies_rules(policy_names=[policyname],
                                                rule=NetworkAccessPolicyRule(client='192.168.1.0/24', interfaces=['snmp']))

# Insert or Move a policy by name with a version specifier.
# The Post will fail if the policy version differs from specified version.
policy_version = '00000000-7b11-a468-0000-0000503669ea'
res = client.post_network_access_policies_rules(policy_names=[policyname],
                                                rule=NetworkAccessPolicyRule(client='*', interfaces=['management-ssh']),
                                                versions=[policy_version])

# Insert or Move a rule default-network-rules.1 rule before 'default-network-rules.2` in policy named 'default-network-rules'
res = client.post_network_access_policies_rules(before_rule_name=policyname+'.2',
                                                policy_names=[policyname],
                                                rule=NetworkAccessPolicyRule(client='*', interfaces=['management-ssh']))

# Insert or Move a rule 'default-network-rules.1` before rule id `10314f42-020d-7080-8013-000ddt400012` in policy named 'default-network-rules'
res = client.post_network_access_policies_rules(before_rule_id="10314f42-020d-7080-8013-000ddt400012",
                                                policy_names=[policyname],
                                                rule=NetworkAccessPolicyRule(client='*', interfaces=['management-ssh']))

print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: policy_ids
# See section "Common Fields" for examples