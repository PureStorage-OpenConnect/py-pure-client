from pypureclient.flashblade import FileSystemPost, Nfs, Smb, Reference, MultiProtocolPost, FileSystemEradicationConfig

# create a local file system object with given name, provisioned size, default quotas,
# NFSv4.1 enabled, nfs export policy "export_policy_1", smb enabled, and smb share
# policy "share_policy_1"
default_user_space_quota = 1024000
default_group_space_quota = 1024000000
export_policy = Reference(name="export_policy_1")
share_policy = Reference(name="share_policy_1")
myfs = FileSystemPost(provisioned=5000, hard_limit_enabled=True,
                      nfs=Nfs(v4_1_enabled=True, export_policy=export_policy),
                      smb=Smb(enabled=True, share_policy=share_policy),
                      default_user_quota=default_user_space_quota,
                      default_group_quota=default_group_space_quota,
                      multi_protocol=MultiProtocolPost(access_control_style="nfs"))
# post the file system object myfs on the array with the specific default user and group
# quotas
res = client.post_file_systems(names=["myfs"], file_system=myfs)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# copy snapshot 'myfs.mysnap' to file system 'myfs'
myfs = FileSystemPost(source=Reference(name='myfs.mysnap'))
# post the file system object myfs on the array
res = client.post_file_systems(names=["myfs"], overwrite=True,
                               discard_non_snapshotted_data=True, file_system=myfs)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# create WORM file system
era_conf = FileSystemEradicationConfig(eradication_mode='retention-based')
myfs = FileSystemPost(eradication_config=era_conf)
res = client.post_file_systems(names=["myfs"], policy_names=['worm-policy'], file_system=myfs)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

res = client.post_file_systems(names=["myfs"], policy_ids=['10314f42-020d-7080-8013-000ddt400014'], file_system=myfs)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
