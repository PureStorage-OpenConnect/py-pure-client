# list all file systems
res = client.get_file_system_snapshots_transfer()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list first five filesystems and sort by provisioned in descendant order
res = client.get_file_system_snapshots_transfer(names=["myfs.mysnap"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: continuation_token, filter, ids, limit, offset, sort, total_only
# See section "Common Fields" for examples
