# delete a bucket access policy rule by bucket name
client.delete_buckets_bucket_access_policies_rules(bucket_names=["bkt1"], names=["myrule"])
# delete a bucket access policy rule by bucket id
client.delete_buckets_bucket_access_policies_rules(bucket_ids=["28674514-e27d-48b3-ae81-d3d2e868f647"], names=["myrule"])
# delete a bucket access policy rule by policy name
client.delete_buckets_bucket_access_policies_rules(policy_names=["bkt1/access-policy"], names=["myrule"])

# Other valid fields: context_names
# See section "Common Fields" for examples
