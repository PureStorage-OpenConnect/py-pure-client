from pypureclient.flashblade import RapidDataLocking, Reference

# Enable Rapid Data Locking

kmip_server_name = 'kmip-server-1'
kmip_server_ref = Reference(name=kmip_server_name, resource_type="kmip")

create_body = RapidDataLocking(enabled=True, kmip_server=kmip_server_ref)
res = client.patch_rapid_data_locking(rapid_data_locking=create_body)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
