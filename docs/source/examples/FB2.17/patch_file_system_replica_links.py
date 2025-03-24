
res = client.patch_file_system_replica_links(
    local_file_system_names=['local_fs'],
    remote_names=['myremote'],
    replicate_now=True)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))


res = client.patch_file_system_replica_links(
    local_file_system_ids=['10314f42-020d-7080-8013-000ddt400090'],
    remote_ids=['10314f42-020d-7080-8013-000ddt400091'],
    replicate_now=True)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

res = client.patch_file_system_replica_links(
    ids=['10314f42-020d-7080-8013-000ddt400092'],
    replicate_now=True)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: context_names
# See section "Common Fields" for examples
