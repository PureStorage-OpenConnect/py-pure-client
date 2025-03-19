from pypureclient.flashblade.FB_2_16 import FileSystemExport, Reference

# update an existing smb export
my_updated_smb_export = FileSystemExport(export_name="new_smb_export_name",
                                         policy=Reference(name="new_smb_client_pol"),
                                         share_policy=Reference(name="new_smb_share_pol"))
res = client.patch_file_system_exports(names=["_array_server::SMB::old_smb_export_name"],
                                       file_system_export=my_updated_smb_export)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# update an existing nfs export
my_updated_nfs_export = FileSystemExport(export_name="new_nfs_export_name",
                                         policy=Reference(name="new_nfs_export_pol"))
res = client.patch_file_system_exports(ids=["cb096ae0-a2c3-acd3-8375-13a7bbd397c2"],
                                       file_system_export=my_updated_nfs_export)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
