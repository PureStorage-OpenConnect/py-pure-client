from pypureclient.flashblade import KmipServer, Reference

# Create a new KMIP server named "kmip-server-1"

kmip_server_name = 'kmip-server-1'
kmip_uris = ['kmip.example.com:5696']
certificate = Reference(name='external', resource_type='certificates')

create_body = KmipServer(uris=kmip_uris, ca_certificate=certificate)
res = client.post_kmip(names=[kmip_server_name], kmip_server=create_body)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
