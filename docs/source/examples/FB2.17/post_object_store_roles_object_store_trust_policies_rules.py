from pypureclient.flashblade.FB_2_17 import TrustPolicyRule, TrustPolicyRuleCondition, Reference

rule = TrustPolicyRule(
    effect='allow',
    actions=['sts:AssumeRoleWithSAML'],
    principals=[Reference(name='SAMLProvider')],
    conditions=[
        TrustPolicyRuleCondition(
            key='saml:aud',
            operator='StringEquals',
            values=['https://signin.flashblade.purestorage.com/']
        )
    ]
)
# Create a new rule for the object store trust policy for a role name
res = client.post_object_store_roles_object_store_trust_policies_rules(role_names=['acc1/myobjrole'], names=['myrule'], rule=rule)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    res_items = (list(res.items))
    print(res_items)
# Create a new rule for the object store trust policy for a role ID
res = client.post_object_store_roles_object_store_trust_policies_rules(role_ids=['10314f42-020d-7080-8013-000ddt400012'], names=['myrule'], rule=rule)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    res_items = (list(res.items))
    print(res_items)
# Create a new rule for the object store trust policy for a trust policy name
res = client.post_object_store_roles_object_store_trust_policies_rules(policy_names=['acc1/myobjrole/trust-policy'], names=['myrule'], rule=rule)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    res_items = (list(res.items))
    print(res_items)

# Other valid fields: context_names
# See ids in section "Common Fields" for examples
