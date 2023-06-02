from pypureclient.flashblade import SmbClientPolicy, SmbClientPolicyRule

# Disable the policy.
policy_attr = SmbClientPolicy(enabled=False)
res = client.patch_smb_client_policies(names=['client_policy_1'], policy=policy_attr)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Bulk specify a new rule for the policy.
# Note: The rules must be ordered by client type grouped by
#    IP addresses, netmasks, and asterisk (*).
bulk_rules = [
    SmbClientPolicyRule(client='*', permission='ro')
]
policy_attr = SmbClientPolicy(rules=bulk_rules)
res = client.patch_smb_client_policies(names=["client_policy_1"], policy=policy_attr)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# update the smb client policy with id '83efe671-3265-af1e-6dd2-c9ff155c2a18'
res = client.patch_smb_client_policies(ids=['83efe671-3265-af1e-6dd2-c9ff155c2a18'],
                                       policy=policy_attr)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    res_items = (list(res.items))
    print(res_items)

# Other valid fields: ids
# See section "Common Fields" for examples