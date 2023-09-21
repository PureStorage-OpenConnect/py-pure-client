from pypureclient.flashblade import SmbClientPolicyRule

policyname = 'client_policy_1'

# Create a new client policy rule in the client policy named 'client_policy_1'
# with specified client, permission, and encryption
res = client.post_smb_client_policies_rules(policy_names=[policyname],
                                            rule=SmbClientPolicyRule(client='*', permission='ro', encryption='required'))

# Insert or Move a policy by name with a version specifier.
# The Post will fail if the policy version differs from specified version.
policy_version = '00000000-7b11-a468-0000-0000503669ea'
res = client.post_smb_client_policies_rules(policy_names=[policyname],
                                            rule=SmbClientPolicyRule(client='*', permission='ro', encryption='required'),
                                            versions=[policy_version])

# Insert or Move a rule client_policy_1.1 rule before 'client_policy_1.2` in client policy named 'client_policy_1'
res = client.post_smb_client_policies_rules(before_rule_name=[policyname+'.2'],
                                            policy_names=[policyname],
                                            rule=SmbClientPolicyRule(client='*', permission='ro', encryption='required'))

# Insert or Move a rule 'client_policy_1.1` before rule id `10314f42-020d-7080-8013-000ddt400012` in client policy named 'client_policy_1'
res = client.post_smb_client_policies_rules(before_rule_id=["10314f42-020d-7080-8013-000ddt400012"],
                                            policy_names=[policyname],
                                            rule=SmbClientPolicyRule(client='*', permission='ro', encryption='required'))

print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: policy_ids
# See section "Common Fields" for examples