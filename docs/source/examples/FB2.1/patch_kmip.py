from pypureclient.flashblade import KmipServer

# Update a KMIP server configuration with a new set of URIs

kmip_server_name = 'kmip-server-1'
kmip_uris = ['kmip1.example.com:5696', 'kmip2.example.com:5696']
create_body = KmipServer(uris=kmip_uris)

res = client.patch_kmip(names=[kmip_server_name], kmip_server=create_body)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: ids
# See section "Common Fields" for examples
