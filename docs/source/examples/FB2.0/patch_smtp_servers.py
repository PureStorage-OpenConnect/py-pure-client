from pypureclient.flashblade import SmtpServer

smtp_settings = SmtpServer(relay_host="test-host.com", sender_domain="purestorage.com")
res = client.patch_smtp_servers(smtp=smtp_settings)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
