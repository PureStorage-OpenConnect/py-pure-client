# list all bucket cross-origin resource sharing policy rules by bucket id
res = client.get_buckets_cross_origin_resource_sharing_policies_rules(bucket_ids=["28674514-e27d-48b3-ae81-d3d2e868f647"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list all bucket cross-origin resource sharing policy rules by bucket name
res = client.get_buckets_cross_origin_resource_sharing_policies_rules(bucket_names=["bkt1"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list all bucket cross-origin resource sharing policy rules by policy name
res = client.get_buckets_cross_origin_resource_sharing_policies_rules(policy_names=["bkt1/cors-policy"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list specific bucket cross-origin resource sharing policy rule
res = client.get_buckets_cross_origin_resource_sharing_policies_rules(policy_names=["bkt1/cors-policy"], names=["myrule"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: continuation_token, filter, limit, offset, sort
# See section "Common Fields" for examples