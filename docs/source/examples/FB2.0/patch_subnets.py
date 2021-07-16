from pypureclient.flashblade import Subnet

# update a subnet's gateway by name
res = client.patch_subnets(
    names=['mysubnet'], subnet=Subnet(gateway='1.2.3.1'))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: ids
# See section "Common Fields" for examples
