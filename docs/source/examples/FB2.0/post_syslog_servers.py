from pypureclient.flashblade import SyslogServerPostOrPatch

# Post a syslog server using a TCP connection
attr = SyslogServerPostOrPatch(uri='tcp://my_syslog_host.domain.com:541')
res = client.post_syslog_servers(syslog_server=attr, names=["main_syslog"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Post a syslog server using a UDP connection
udp_attr = SyslogServerPostOrPatch(uri='udp://my_syslog_host.domain.com:540')
res = client.post_syslog_servers(syslog_server=udp_attr, names=["my_udp_connection"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
