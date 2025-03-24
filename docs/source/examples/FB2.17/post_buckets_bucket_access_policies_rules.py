from pypureclient.flashblade import BucketAccessPolicyRulePost, BucketAccessPolicyRulePrincipal

# create a public read rule
rule = BucketAccessPolicyRulePost(
    actions=["s3:GetObject"],
    principals=BucketAccessPolicyRulePrincipal(
        all=True
    ),
    resources=["bkt1/*"]
)

# create by policy name
res = client.post_buckets_bucket_access_policies_rules(policy_names=["bkt1/access-policy"], names=["myrule"], rule=rule)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# create by bucket name
res = client.post_buckets_bucket_access_policies_rules(bucket_names=["bkt1"], names=["myrule"], rule=rule)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# create by bucket id
res = client.post_buckets_bucket_access_policies_rules(bucket_ids=["28674514-e27d-48b3-ae81-d3d2e868f647"], names=["myrule"], rule=rule)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: context_names
# See ids in section "Common Fields" for examples
