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
# patch a rule for the object store trust policy for a rule name
res = client.patch_object_store_roles_object_store_trust_policies_rules(role_names=['acc1/myobjrole'], names=['myrule'], rule=rule)
# patch a rule for the object store trust policy for a rule index
res = client.patch_object_store_roles_object_store_trust_policies_rules(role_names=['acc1/myobjrole'], indices=[1], rule=rule)
# patch a rule for the object store trust policy for a policy name
res = client.patch_object_store_roles_object_store_trust_policies_rules(policy_names=['acc1/myobjrole/trust-policy'], indices=[1], rule=rule)
# patch a rule for the object store trust policy for a role id
res = client.patch_object_store_roles_object_store_trust_policies_rules(role_ids=['f8b3b3b3-3b3b-3b3b-3b3b-3b3b3b3b3b3b'], indices=[1], rule=rule)

# Other valid fields: context_names
# See section "Common Fields" for examples
