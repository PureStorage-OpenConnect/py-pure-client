res = client.post_policies_file_system_replica_links(
    policy_names=['policy_1'],
    local_file_system_names=['local_fs'],
    remote_names=['myremote'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: context_names, policy_ids, local_file_system_ids, remote_ids, member_ids
# See section "Common Fields" for examples
