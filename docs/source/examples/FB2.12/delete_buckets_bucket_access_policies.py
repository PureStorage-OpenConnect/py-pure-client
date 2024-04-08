# delete a bucket access policy by bucket name
client.delete_buckets_bucket_access_policies(bucket_names=["bkt1"])
# delete a bucket access policy by bucket id
client.delete_buckets_bucket_access_policies(bucket_ids=["28674514-e27d-48b3-ae81-d3d2e868f647"])
# delete a bucket access policy by name
client.delete_buckets_bucket_access_policies(names=["bkt1/access-policy"])
