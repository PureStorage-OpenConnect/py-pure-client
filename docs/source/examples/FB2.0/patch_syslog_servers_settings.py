from pypureclient.flashblade import SyslogServerSettings, Reference

# Assuming a certificate named "syslog_server_cert" has already been uploaded to the array,
# retrieve that certificate by name and configure it to be used to authenticate the
# connection with syslog servers.
cert_name = 'syslog_server_cert'
cert_res = client.get_certificates(names=[cert_name])
cert_item = list(cert_res.items)[0]
# Build a Reference using information from the certificate GET result
cert_reference = Reference(name=cert_item.name, id=cert_item.id, resource_type='certificates')
attr = SyslogServerSettings(ca_certificate=cert_reference)
res = client.patch_syslog_servers_settings(syslog_server_settings=attr)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: names, ids
# See section "Common Fields" for examples
