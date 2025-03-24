from pypureclient.flashblade import CrossOriginResourceSharingPolicyPatch, CrossOriginResourceSharingPolicyRule

# create an empty cross-origin resource sharing policy
res = client.post_buckets_cross_origin_resource_sharing_policies(bucket_names=["bkt1"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# create a cross-origin resource sharing policy with the allow all rule
rule = CrossOriginResourceSharingPolicyRule(
    name="myrule",
    allowed_headers=["*"],
    allowed_methods=["GET","PUT","HEAD","POST","DELETE"],
    allowed_origins=["*"]
)
policy = CrossOriginResourceSharingPolicyPatch(
    rules=[rule]
)

# post with bucket name
res = client.post_buckets_cross_origin_resource_sharing_policies(bucket_names=["bkt1"], policy=policy)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# post with bucket ID
res = client.post_buckets_cross_origin_resource_sharing_policies(bucket_ids=["28674514-e27d-48b3-ae81-d3d2e868f647"], policy=policy)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: context_names
# See ids in section "Common Fields" for examples
