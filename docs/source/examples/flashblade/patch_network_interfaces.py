from pypureclient.flashblade import NetworkInterface

# Update the existing network interface "myvip"
# Change the address to "1.2.3.201"
# Change the service type to "replication"
res = client.patch_network_interfaces(
    names=['myvip'], network_interface=NetworkInterface(address='1.2.3.201', services=['replication']))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: ids
# See section "Common Fields" for examples
