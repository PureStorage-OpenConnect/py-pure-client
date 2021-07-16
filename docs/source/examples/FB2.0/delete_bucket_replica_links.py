# delete the replica link on the local bucket with the name 'my-connected-array'
client.delete_bucket_replica_links(local_bucket_names=['localbucket'],
                                   remote_bucket_names=['remotebucket'],
                                   remote_names=['my-connected-array'])

# delete the replica link on the local bucket with id '10314f42-020d-7080-8013-000ddt400090'
client.delete_bucket_replica_links(local_bucket_ids=['10314f42-020d-7080-8013-000ddt400090'],
                                   remote_bucket_names=['remotebucket'],
                                   remote_ids=['10314f42-020d-7080-8013-000ddt400012'])

# Other valid fields: ids
# See section "Common Fields" for examples
