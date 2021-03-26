# eradicate a destroyed file system snapshot named myfs.mysnap
client.delete_file_system_snapshots_transfer(names=["myfs.mysnap"],
                                             remote_names=["myremote"])

# Other valid fields: ids, remote_ids
# See section "Common Fields" for examples
