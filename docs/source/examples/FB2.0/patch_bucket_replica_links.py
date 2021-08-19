from pypureclient.flashblade import BucketReplicaLink, ObjectStoreRemoteCredentials

# Pause an existing bucket replica link
# Also change the remote credentials we're using for replication to the credentials named "remote/name"
new_attr = BucketReplicaLink(paused=True, remote_credentials=ObjectStoreRemoteCredentials(name="remote/name"))
# Update the existing replica link on the specified local bucket, to the specified remote bucket on the remote
# Use the attribute map from before to pause the link and change credentials
res = client.patch_bucket_replica_links(local_bucket_names=['localbucket'],
                                        remote_names=['remote'],
                                        remote_bucket_names=['remotebucket'],
                                        bucket_replica_link=new_attr)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Update the existing replica link on the specified local bucket, to the specified remote bucket on the remote (by ids)
# Use the attribute map from before to pause the link and change credentials
res = client.patch_bucket_replica_links(local_bucket_ids=['10314f42-020d-7080-8013-000ddt400090'],
                                        remote_ids=['10314f42-020d-7080-8013-000ddt400045'],
                                        remote_bucket_names=['remotebucket'],
                                        bucket_replica_link=new_attr)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: ids
# See section "Common Fields" for examples
