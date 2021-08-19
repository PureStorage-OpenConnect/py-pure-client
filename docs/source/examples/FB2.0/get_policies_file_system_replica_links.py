# list all replica link and policy connections
res = client.get_policies_file_system_replica_links()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list first five replica link and policy connections and sort by policy name
res = client.get_policies_file_system_replica_links(limit=5, sort='policy.name')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list remaining replica link and policies connections
res = client.get_policies_file_system_replica_links(
    continuation_token=res.continuation_token)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list a specific replica link and policy connection
res = client.get_policies_file_system_replica_links(
    policy_names=['policy_1'],
    local_file_system_names=['local_fs'],
    remote_names=['myremote'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: filter, local_file_system_ids, member_ids, offset, policy_ids, remote_ids,
#                     remote_file_system_ids, remote_file_system_names
# See section "Common Fields" for examples
