from pypureclient.flashblade import ArrayConnection

# Update the management and replication addresses of an array connection
new_attr = ArrayConnection(management_address="10.202.101.70",
                           replication_addresses=["10.202.101.71", "10.202.101.72"])
# update the array connection named otherarray
res = client.patch_array_connections(remote_names=["otherarray"], array_connection=new_attr)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# update the array connection with id '10314f42-020d-7080-8013-000ddt400090'
res = client.patch_array_connections(ids=['10314f42-020d-7080-8013-000ddt400090'],
                                     array_connection=new_attr)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: remote_ids
# See section "Common Fields" for examples
