from pypureclient.flashblade import FileSystemReplicaLink, LocationReference

res = client.post_file_system_replica_links(
    local_file_system_names=["local_fs"],
    remote_file_system_names=["remote_fs"],
    remote_names=['myremote'],
    file_system_replica_link=FileSystemReplicaLink(policies=[LocationReference(name=POLICY_NAME)]))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: ids, local_file_system_ids, remote_ids
# See section "Common Fields" for examples
