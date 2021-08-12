FS_NAME = 'local_file'
# list all incoming or outgoing replica link transfers for filesystem local_file
res = client.get_file_system_replica_links_transfer(names_or_owner_names=[FS_NAME])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: continuation_token, filter, ids, limit, offset, remote_ids, remote_names, sort, total_only
# See section "Common Fields" for examples
