from pypureclient.flashblade import BucketReplicaLinkPost

# create a replica link from a specified local bucket, to a specified remote bucket
# on the remote corresponding to the remote credentials
local_bucket_names = ["localbucket"]
remote_bucket_names = ["remotebucket"]
remote_credentials_names = ["remote/credentials"]
my_replica_link = BucketReplicaLinkPost(paused=False)
# post the bucket replica link object on the local array
res = client.post_bucket_replica_links(local_bucket_names=local_bucket_names,
                                       remote_bucket_names=remote_bucket_names,
                                       remote_credentials_names=remote_credentials_names,
                                       bucket_replica_link=my_replica_link)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: local_bucket_ids, remote_credentials_ids
# See ids in section "Common Fields" for examples
