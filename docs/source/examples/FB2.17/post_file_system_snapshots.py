from pypureclient.flashblade import FileSystemSnapshotPost

# create a snapshot for the file system named myfs
res = client.post_file_system_snapshots(source_names=["myfs"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# create a snapshot with suffix mysnap for the file system named myfs
res = client.post_file_system_snapshots(source_names=["myfs"],
                                        file_system_snapshot=FileSystemSnapshotPost("mysnap"))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# create a snapshot with suffix mysnap for the file system named myfs
res = client.post_file_system_snapshots(source_names=["myfs"],
                                        send=True,
                                        targets=["myremote"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: context_names, source_ids
# See section "Common Fields" for examples
