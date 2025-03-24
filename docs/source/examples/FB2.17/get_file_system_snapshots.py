# list all file system snapshots
res = client.get_file_system_snapshots()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list all destroyed file system snapshots
res = client.get_file_system_snapshots(destroyed=True)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list all file system snapshots with owning filesystem 'myfs'
res = client.get_file_system_snapshots(names_or_owner_names='myfs')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list with page size 5, and sort by source file system name
res = client.get_file_system_snapshots(limit=5, sort="source.name")
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list all remaining file system snapshots
res = client.get_file_system_snapshots(continuation_token=res.continuation_token)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list with filter
res = client.get_file_system_snapshots(filter='source.name=\'myfs*\' and contains(suffix, \'1\')')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: allow_errors, context_names, ids, offset, owner_ids, total_only
# See section "Common Fields" for examples
