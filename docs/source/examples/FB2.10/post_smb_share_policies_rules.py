from pypureclient.flashblade import SmbSharePolicyRule

policyname = 'share_policy_1'

# Create a new share policy rule in the share policy named 'share_policy_1'
res = client.post_smb_share_policies_rules(rule=SmbSharePolicyRule(principal='everyone',
                                                                   read='allow'),
                                           policy_names=[policyname])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: policy_ids
# See section "Common Fields" for examples
