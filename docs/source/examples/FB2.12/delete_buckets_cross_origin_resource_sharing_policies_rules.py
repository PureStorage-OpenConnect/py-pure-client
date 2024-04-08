# delete a bucket cross-origin resource sharing policy rule by bucket name
client.delete_buckets_cross_origin_resource_sharing_policies_rules(bucket_names=["bkt1"], names=["myrule"])
# delete a bucket cross-origin resource sharing policy rule by bucket id
client.delete_buckets_cross_origin_resource_sharing_policies_rules(bucket_ids=["28674514-e27d-48b3-ae81-d3d2e868f647"], names=["myrule"])
# delete a bucket cross-origin resource sharing policy rule by policy name
client.delete_buckets_cross_origin_resource_sharing_policies_rules(policy_names=["bkt1/cors-policy"], names=["myrule"])
