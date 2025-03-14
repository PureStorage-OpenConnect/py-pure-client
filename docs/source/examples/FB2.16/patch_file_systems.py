from pypureclient.flashblade.FB_2_16 import FileSystemPatch, NfsPatch, Http, Reference, Smb, MultiProtocol, StorageClassInfo

# update a file system object with a new provisioned size. enable hard limits.
# enable NFSv4.1, and disable NFSv3. enable SMB. disable HTTP
# adjust the default user quota to a new value
# change access control style to independent, disable safeguard acls
# set the nfs export policy to "export_policy_1"
# set the smb share policy to "share_policy_1"
# set the smb continuous availability_enabled to True
# set the group ownership to "parent-directory"
# set the storage class to "S500X-A"
# note that name field should be None
new_attr = FileSystemPatch(provisioned=1024, hard_limit_enabled=True,
                           nfs=NfsPatch(v3_enabled=False,
                                        v4_1_enabled=True,
                                        add_rules="1.1.1.1(rw,no_root_squash)",
                                        export_policy=Reference(name="export_policy_1")),
                           http=Http(enabled=False),
                           smb=Smb(enabled=True,
                                   share_policy=Reference(name="share_policy_1"),
                                   continuous_availability_enabled=True),
                           default_user_quota=4096,
                           multi_protocol=MultiProtocol(safeguard_acls=False,
                                                        access_control_style="independent"),
                           group_ownership="parent-directory",
                           storage_class=StorageClassInfo(name="S500X-A"))
# update the file system named myfs on the array
res = client.patch_file_systems(names=["myfs"], ignore_usage=True, file_system=new_attr,
                                discard_detailed_permissions=True,
                                cancel_in_progress_storage_class_transition=True)

print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# update the filesystem object to use an export_policy instead of export rules.
new_attr = FileSystemPatch(nfs=NfsPatch(export_policy=Reference(name="export_policy_1")))
res = client.patch_file_systems(names=["myfs"], file_system=new_attr)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# destroy a file system even if it has a replica link
destroy_attr = FileSystemPatch(destroyed=True,
                               nfs=NfsPatch(v4_1_enabled=False),
                               smb=Smb(enabled=False),
                               multi_protocol=MultiProtocol(access_control_style="mode-bits"))
res = client.patch_file_systems(names=["myfs"], delete_link_on_eradication=True,
                                file_system=destroy_attr)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# update the file system with id '10314f42-020d-7080-8013-000ddt400090' on the array
res = client.patch_file_systems(ids=['10314f42-020d-7080-8013-000ddt400090'],
                                ignore_usage=True, file_system=new_attr,
                                discard_non_snapshotted_data=False)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# rename a file system
new_attr = FileSystemPatch(name="new_name")
res = client.patch_file_systems(names=["old_name"], file_system=new_attr)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
