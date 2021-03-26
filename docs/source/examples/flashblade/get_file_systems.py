# list all file systems
res = client.get_file_systems()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list all destroyed file systems
res = client.get_file_systems(destroyed=True)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list first five filesystems using default sort
res = client.get_file_systems(limit=5)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list first five filesystems and sort by provisioned in descendant order
res = client.get_file_systems(limit=5, sort="provisioned-")
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list all remaining file systems
res = client.get_file_systems(continuation_token=res.continuation_token)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list with filter to see only file systems with at least one type of nfs enabled
res = client.get_file_systems(filter='nfs.v3_enabled or nfs.v4_1_enabled')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: ids, names, offset, sort, total_only
# See section "Common Fields" for examples
