from pypureclient.flashblade import BucketAccessPolicyPost, BucketAccessPolicyRule, BucketAccessPolicyRulePrincipal

# create an empty access policy
res = client.post_buckets_bucket_access_policies(bucket_names=["bkt1"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# create an access policy with the public read rule
rule = BucketAccessPolicyRule(
    name="myrule",
    actions=["s3:GetObject"],
    principals=BucketAccessPolicyRulePrincipal(
        all=True
    ),
    resources=["bkt1/*"]
)
policy = BucketAccessPolicyPost(
    rules=[rule]
)

# post with bucket name
res = client.post_buckets_bucket_access_policies(bucket_names=["bkt1"], policy=policy)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# post with bucket ID
res = client.post_buckets_bucket_access_policies(bucket_ids=["28674514-e27d-48b3-ae81-d3d2e868f647"], policy=policy)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
