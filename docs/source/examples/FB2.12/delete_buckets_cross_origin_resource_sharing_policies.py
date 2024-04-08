# delete a bucket cross-origin resource sharing policy by bucket name
client.delete_buckets_cross_origin_resource_sharing_policies(bucket_names=["bkt1"])
# delete a bucket cross-origin resource sharing policy by bucket id
client.delete_buckets_cross_origin_resource_sharing_policies(bucket_ids=["28674514-e27d-48b3-ae81-d3d2e868f647"])
# delete a bucket cross-origin resource sharing policy by name
client.delete_buckets_cross_origin_resource_sharing_policies(names=["bkt1/cors-policy"])
