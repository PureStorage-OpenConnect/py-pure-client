# list all file systems
res = client.get_file_system_snapshots_transfer()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list snapshot transfers for snapshots with name myfs.mysnap
res = client.get_file_system_snapshots_transfer(names_or_owner_names=["myfs.mysnap"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: continuation_token, filter, ids, limit, offset, sort, total_only
# See section "Common Fields" for examples
