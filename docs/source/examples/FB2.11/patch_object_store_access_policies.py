from pypureclient.flashblade import ObjectStoreAccessPolicy, PolicyRuleObjectAccess, PolicyRuleObjectAccessCondition

# update a policy by changing its rules, where some rules bypass our action restriction enforcement
rule = PolicyRuleObjectAccess(
    name="myupdatedrule",
    actions=["s3:ListBucket"],
    resources=["mybucket/myobject"],
    conditions=PolicyRuleObjectAccessCondition(
        source_ips=["1.2.3.4"],
        s3_prefixes=["home/"],
        s3_delimiters=["/"],
    ),
    effect="deny"
)
policy = ObjectStoreAccessPolicy(
    rules=[rule]
)
res = client.patch_object_store_access_policies(
    names=["acc1/mypolicy"], policy=policy, enforce_action_restrictions=False)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# update a different policy with the same rules, but by ID this time
res = client.patch_object_store_access_policies(
    ids=["10314f42-020d-7080-8013-000ddt400012"], policy=policy, enforce_action_restrictions=False)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
