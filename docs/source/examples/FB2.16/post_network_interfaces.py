from pypureclient.flashblade import NetworkInterface

# create vip named myvip on the array
res = client.post_network_interfaces(
    names=["myvip"],
    network_interface=NetworkInterface(address='1.2.3.101',
                                       services=["data"],
                                       type="vip"))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# create a replication vip named replvip on the array
res = client.post_network_interfaces(
    names=["replvip"],
    network_interface=NetworkInterface(address='1.2.3.101',
                                       services=["replication"],
                                       type="vip"))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# create vip inside 'my_server' server object
res = client.post_network_interfaces(
    names=["replvip"],
    network_interface=NetworkInterface(address='1.2.3.101',
                                       services=["replication"],
                                       type="vip",
                                       server={"name": "my_server"}))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
