from pypureclient.flashblade import NetworkAccessPolicy, NetworkAccessPolicyRule

# Rename the policy.
policy_attr = NetworkAccessPolicy(name='new-default-rules')
res = client.patch_network_access_policies(names=['default-network-access-policy'], policy=policy_attr)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Bulk specify a set of new rules for the policy.
# Note: The rules must be ordered by client type grouped by
#    IP addresses, netmasks, and asterisk (*).
bulk_rules = [
    NetworkAccessPolicyRule(client='1.2.3.4', effect='deny', interfaces=['snmp', 'management-ssh']),
    NetworkAccessPolicyRule(client='*', interfaces=['snmp', 'management-ssh', 'management-web-ui'])
]
policy_attr = NetworkAccessPolicy(rules=bulk_rules)
res = client.patch_network_access_policies(names=['default-network-access-policy'], policy=policy_attr)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# update the network access policy with id '83efe671-3265-af1e-6dd2-c9ff155c2a18'
res = client.patch_network_access_policies(ids=['83efe671-3265-af1e-6dd2-c9ff155c2a18'],
                                           policy=policy_attr)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    res_items = (list(res.items))
    print(res_items)

# Other valid fields: ids, versions
# See section "Common Fields" for examples