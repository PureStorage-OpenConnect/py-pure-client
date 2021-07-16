from pypureclient.flashblade import SyslogServerPostOrPatch

# Update the uri of the server named "main_syslog"
attr = SyslogServerPostOrPatch(uri='tcp://new_syslog_host.domain.com:541')
res = client.patch_syslog_servers(syslog_server=attr, names=["main_syslog"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: ids
# See section "Common Fields" for examples
