from pypureclient.flashblade import SmbSharePolicyRule

# Patch share policy rule 'everyone' in share policy named 'share_policy_1'
res = client.patch_smb_share_policies_rules(policy_names=['share_policy_1'],
                                            names=['everyone'],
                                            rule=SmbSharePolicyRule(read='deny'))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Patch share policy rule 'everyone' in share policy with policy_id = xxxxxxxxxxxx
res = client.patch_smb_share_policies_rules(policy_ids=["10314f42-020d-7080-8013-000ddt400012"],
                                            names=['everyone'],
                                            rule=SmbSharePolicyRule(read='deny'))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: context_names, ids
# See section "Common Fields" for examples
