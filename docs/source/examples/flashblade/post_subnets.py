from pypureclient.flashblade import Subnet

# post the subnet object mysubnet on the array
res = client.post_subnets(names=["mysubnet"],
                          subnet=Subnet(prefix='1.2.3.0/24'))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
