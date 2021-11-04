from pypureclient.flashblade import ObjectStoreAccessPolicyPost, PolicyRuleObjectAccess, PolicyRuleObjectAccessCondition

# create a basic policy (no description, no rules yet)
res = client.post_object_store_access_policies(names=["acc1/mypolicy"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# create a policy with a description and some rules, where some rules bypass our action restriction enforcement
rule = PolicyRuleObjectAccess(
    name="myrule",
    actions=["s3:ListBucket"],
    resources=["mybucket/myobject"],
    conditions=PolicyRuleObjectAccessCondition(
        source_ips=["1.2.3.4"],
        s3_prefixes=["home/"],
        s3_delimiters=["/"],
    ),
)
policy = ObjectStoreAccessPolicyPost(
    description="This is my policy description.",
    rules=[rule]
)
res = client.post_object_store_access_policies(
    names=["acc1/mynewpolicy"], policy=policy, enforce_action_restrictions=False)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
