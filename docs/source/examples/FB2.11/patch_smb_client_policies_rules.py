from pypureclient.flashblade import SmbClientPolicyRule

policyname = 'client_policy_1'

# Patch client policy rule 'client_policy_1.1' in client policy named 'client_policy_1'
res = client.patch_smb_client_policies_rules(names=[policyname+'.1'],
                                             rule=SmbClientPolicyRule(permission='ro', encryption='required'))

print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Patch a policy by name with a version specifier.
# The Patch will fail if the policy version differs from specified version.
policy_version = '00000000-7b11-a468-0000-0000503669ea'
res = client.patch_smb_client_policies_rules(names=[policyname+'.1'],
                                             rule=SmbClientPolicyRule(permission='ro', encryption='required'),
                                             versions=[policy_version])

print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Insert or Move a rule client_policy_1.1 rule before 'client_policy_1.2` in client policy named 'client_policy_1'
res = client.patch_smb_client_policies_rules(names=[policyname+'.1'],
                                             before_rule_name=[policyname+'.2'],
                                             rule=SmbClientPolicyRule(permission='ro', encryption='required'))

print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Insert or Move a rule 'client_policy_1.1` before rule id `10314f42-020d-7080-8013-000ddt400012` in client policy named 'client_policy_1'
res = client.patch_smb_client_policies_rules(names=[policyname+'.1'],
                                             before_rule_id=["10314f42-020d-7080-8013-000ddt400012"],
                                             rule=SmbClientPolicyRule(permission='ro', encryption='required'))

print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: ids
# See section "Common Fields" for examples