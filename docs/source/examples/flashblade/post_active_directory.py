from pypureclient.flashblade import ActiveDirectoryPost

# Create new Active Directory account with specified LDAP and kerberos servers, computer name
# and specified encryption types, fqdns, and join_ou.
# Can alternatively supply service_principal_names instead of fqdns.
ad_config = ActiveDirectoryPost(computer_name="FLASHBLADE01",
                                directory_servers=["ldap.my-corporation.com"],
                                kerberos_servers=["kdc.my-corporation.com"],
                                domain="my-corporation.com",
                                encryption_types=["aes128-cts-hmac-sha1-96"],
                                fqdns=["vip1.my-array.my-corporation.com"],
                                join_ou="CN=FakeOU",
                                user="Administrator",
                                password="Password")

res = client.post_active_directory(names=["test-config"], active_directory=ad_config)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Join AD domain using an existing computer account
existing_ad_config = ActiveDirectoryPost(computer_name="FLASHBLADE01",
                                         domain="my-corporation.com",
                                         user="Administrator",
                                         password="Password")
res = client.post_active_directory(names=["test-config"], active_directory=existing_ad_config,
                                   join_existing_account=True)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
