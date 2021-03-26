from pypureclient.flashblade import FileSystemSnapshot

# Destroy an existing snapshot
new_attr = FileSystemSnapshot(destroyed=True)
# Update the file system snapshot myfs.mysnap with our new attributes, in this case destroying it
res = client.patch_file_system_snapshots(names=["myfs.mysnap"], file_system_snapshot=new_attr)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# destroying the latest replicated snapshot should specify "latest_replica=True"
res = client.patch_file_system_snapshots(names=["myfs.mysnap"],
                                         latest_replica=True,
                                         file_system_snapshot=new_attr)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: ids
# See section "Common Fields" for examples
