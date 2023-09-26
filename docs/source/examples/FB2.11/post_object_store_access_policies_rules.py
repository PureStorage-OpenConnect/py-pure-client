from pypureclient.flashblade import PolicyRuleObjectAccessPost, PolicyRuleObjectAccessCondition

rule = PolicyRuleObjectAccessPost(
    actions=["s3:ListBucket"],
    resources=["*"],
    conditions=PolicyRuleObjectAccessCondition(
        source_ips=["1.2.3.4"],
        s3_prefixes=["home/"],
        s3_delimiters=["/"],
    ),
    effect="deny"
)
res = client.post_object_store_access_policies_rules(policy_names=["acc1/mypolicy"], names=["myrule"], rule=rule)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# create a rule which doesn't follow our action restrictions; also use policy ID instead of name
rule2 = PolicyRuleObjectAccessPost(
    actions=["s3:ListBucket"],
    resources=["mybucket/myobject"],
    conditions=PolicyRuleObjectAccessCondition(
        source_ips=["1.2.3.4"],
        s3_prefixes=["home/"],
        s3_delimiters=["/"],
    ),
    effect="allow"
)
res = client.post_object_store_access_policies_rules(
    policy_ids=["10314f42-020d-7080-8013-000ddt400012"], names=["myrule2"], rule=rule2, enforce_action_restrictions=False)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
