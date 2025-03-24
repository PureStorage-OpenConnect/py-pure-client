from pypureclient.flashblade import (SmbSharePolicy, SmbSharePolicyRule)

# Create a share policy with a rule which allows Read (but no other) permissions for everyone.
policyname = 'share_policy_1'
policy = SmbSharePolicy()
policy.rules = [
    SmbSharePolicyRule(principal='everyone', read='allow')
]
res = client.post_smb_share_policies(names=[policyname], policy=policy)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: context_names
# See section "Common Fields" for examples
