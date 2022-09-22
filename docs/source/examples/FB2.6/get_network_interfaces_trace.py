# Default behavior traces the route of UDP packets from both FMs/XFMs and one blade.
trace_dest = 'localhost'
res = client.get_network_interfaces_trace(destination=trace_dest)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Trace only from the component being specified. Use TCP and do not allow packet fragmentation.
res = client.get_network_interfaces_trace(destination=trace_dest,
                                          component_name='CH1.FB1',
                                          method='tcp',
                                          fragment_packet=False)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Trace the route to a specified port at the destination, using the specified interface (vip,
# subnet or IP) as the source. Do not resolve the destination's IP address to a hostname, and
# discover the MTU.
res = client.get_network_interfaces_trace(destination=trace_dest,
                                          port=80,
                                          source='fm1.admin0',
                                          resolve_hostname=False,
                                          discover_mtu=True)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))