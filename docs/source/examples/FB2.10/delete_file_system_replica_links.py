# delete replica link defined by local file system 'local_fs', remote array 'my_remote' and
# optionally remote file system 'remote_fs'
res = client.delete_file_system_replica_links(local_file_system_names=['local_fs'],
                                              remote_file_system_names=['remote_fs'],
                                              remote_names=['my_remote'],
                                              cancel_in_progress_transfers=True)

print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# delete replica link defined by id
res = client.delete_file_system_replica_links(ids=['10314f42-020d-7080-8013-000ddt400092'],
                                              cancel_in_progress_transfers=True)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: local_file_system_ids, remote_ids, remote_file_system_ids
# See section "Common Fields" for examples
