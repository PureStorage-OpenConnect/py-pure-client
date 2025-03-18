from pypureclient.flashblade import Server, Reference

# update dns configuration of server with name 'myserver'
dns_list = [Reference(name="mydns")]
res = client.patch_servers(names=["myserver"], server=Server(dns=dns_list))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: ids, references
# See section "Common Fields" for examples
