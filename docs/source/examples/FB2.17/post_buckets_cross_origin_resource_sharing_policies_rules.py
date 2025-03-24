from pypureclient.flashblade import CrossOriginResourceSharingPolicyRulePost

# create an allow all rule
rule = CrossOriginResourceSharingPolicyRulePost(
    allowed_headers=["*"],
    allowed_methods=["GET","PUT","HEAD","POST","DELETE"],
    allowed_origins=["*"]
)

# create by policy name
res = client.post_buckets_cross_origin_resource_sharing_policies_rules(policy_names=["bkt1/cors-policy"], names=["myrule"], rule=rule)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# create by bucket name
res = client.post_buckets_cross_origin_resource_sharing_policies_rules(bucket_names=["bkt1"], names=["myrule"], rule=rule)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# create by bucket id
res = client.post_buckets_cross_origin_resource_sharing_policies_rules(bucket_ids=["28674514-e27d-48b3-ae81-d3d2e868f647"], names=["myrule"], rule=rule)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: context_names
# See ids in section "Common Fields" for examples
