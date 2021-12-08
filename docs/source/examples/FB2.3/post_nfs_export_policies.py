from pypureclient.flashblade import (NfsExportPolicy, NfsExportPolicyRuleInPolicy)

# Create an export policy with 2 rules. The first for client 10.20.30.40 with readwrite permissions
# and root-squash.  The second with read-only permissions for all other clients.
policyname = "export_policy_1"
policy = NfsExportPolicy()
policy.rules = [
    NfsExportPolicyRuleInPolicy(client='10.20.30.40', permission='rw', access='root-squash'),
    NfsExportPolicyRuleInPolicy(client='*', permission='ro')
]
res = client.post_nfs_export_policies(names=[policyname], policy=policy)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
