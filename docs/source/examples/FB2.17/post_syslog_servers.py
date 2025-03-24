from pypureclient.flashblade.FB_2_17 import SyslogServerPost

# Post a syslog server using a TCP connection
attr = SyslogServerPost(uri='tcp://my_syslog_host.domain.com:541')
attr.services = ['data-audit']
res = client.post_syslog_servers(syslog_server=attr, names=["main_syslog"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Post a syslog server using a UDP connection
udp_attr = SyslogServerPost(uri='udp://my_syslog_host.domain.com:540')
attr.services = ['data-audit']
res = client.post_syslog_servers(syslog_server=udp_attr, names=["my_udp_connection"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
