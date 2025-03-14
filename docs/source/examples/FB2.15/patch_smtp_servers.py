from pypureclient.flashblade import SmtpServer

# Update the SMTP server settings to use the specified relay host, sender domain and encryption mode
smtp_settings = SmtpServer(relay_host="test-host.com", sender_domain="purestorage.com", encryption_mode="starttls")
res = client.patch_smtp_servers(smtp=smtp_settings)

# print the updated SMTP server settings
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

