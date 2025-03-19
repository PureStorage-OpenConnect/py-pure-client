from pypureclient.flashblade import FileSystemExportPost, Reference

# example 1
# create smb and nfs exports for an existing file system 'my_fs' on the server 'my_server'
my_exports = FileSystemExportPost(export_name="my_export",
                                  server=Reference(name="my_server"),
                                  share_policy=Reference(name="smb_share_policy_1"))
res = client.post_file_system_exports(member_names=["my_fs"],
                                      policy_names=["nfs_export_policy_1", "smb_client_policy_1"],
                                      file_system_export=my_exports)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# example 2
# create only nfs export for an existing file system 'my_fs' on the server 'my_server'
my_nfs_export = FileSystemExportPost(export_name="my_nfs_export",
                                     server=Reference(name="my_server"))
res = client.post_file_system_exports(member_names=["my_fs"],
                                      policy_names=["nfs_export_policy_1"],
                                      file_system_export=my_nfs_export)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# example 3
# create only smb export for an existing file system 'my_fs' on the server 'my_server'
my_smb_export = FileSystemExportPost(export_name="my_export",
                                     server=Reference(name="my_server"),
                                     share_policy=Reference(name="smb_share_policy_1"))
res = client.post_file_system_exports(member_ids=["bfba6e16-963b-d0b4-f597-9f98916f370c"],
                                      policy_ids=["cb096ae0-a2c3-acd3-8375-13a7bbd397c2"],
                                      file_system_export=my_smb_export)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
