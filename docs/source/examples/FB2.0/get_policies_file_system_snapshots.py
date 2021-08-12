# list all policies
res = client.get_policies_file_system_snapshots()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# assume we have a policy named "p1", and a file system snapshot named "myfs.1"
res = client.get_policies_file_system_snapshots(policy_names=["p1"],
                                                member_names=["myfs.1"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# assume we have a policy with id "10314f42-020d-7080-8013-000ddt400090",
# and a file system snapshot with name "myfs.2"
res = client.get_policies_file_system_snapshots(policy_ids=["10314f42-020d-7080-8013-000ddt400090"],
                                                member_names=["myfs.2"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list and sort by name in descendant order
res = client.get_policies_file_system_snapshots(limit=5, sort="policy.name-")
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list with page size 5
res = client.get_policies_file_system_snapshots(limit=5)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: continuation_token, filter, member_ids, offset
# See section "Common Fields" for examples
