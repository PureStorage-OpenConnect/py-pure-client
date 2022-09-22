# Default behavior will send a single ping from both FMs/XFMs and one blade.
ping_dest = 'localhost'
res = client.get_network_interfaces_ping(destination=ping_dest)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Send 5 pings from the component being specified. Also include the full
# user-to-user latency.
res = client.get_network_interfaces_ping(destination=ping_dest,
                                         count=5,
                                         component_name='CH1.FB1',
                                         print_latency=True)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Send pings using 120-byte packets, and using the specified interface (subnet, vip, or IP)
# as the source. Do not resolve the destination's IP address to a hostname
res = client.get_network_interfaces_ping(destination=ping_dest,
                                         packet_size=120,
                                         source='fm1.admin0',
                                         resolve_hostname=False)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))