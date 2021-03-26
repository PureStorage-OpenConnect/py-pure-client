from pypureclient.flashblade import Dns

# update domain
res = client.patch_dns(dns=Dns(domain='new_domain'))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# update nameservers
res = client.patch_dns(dns=Dns(nameservers=['126.24.5.1', '126.24.5.2']))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# empty nameservers
res = client.patch_dns(dns=Dns(nameservers=[]))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: names, ids
# See section "Common Fields" for examples
