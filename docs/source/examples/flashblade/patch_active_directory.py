from pypureclient.flashblade import ActiveDirectoryPatch

# Change existing Active Directory account LDAP and kerberos servers, encryption types, and
# service principal names.
# Can alternatively supply fqdns instead of service_principal_names
ad_config = ActiveDirectoryPatch(directory_servers=["ldap.my-corporation.com"],
                                 kerberos_servers=["kdc.my-corporation.com"],
                                 encryption_types=["aes256-cts-hmac-sha1-96"],
                                 service_principal_names=["nfs/vip2.my-array.my-corporation.com"])
res = client.patch_active_directory(names=["test-config"], active_directory=ad_config)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Move existing Active Directory account to a different Join OU
ad_config = ActiveDirectoryPatch(join_ou="OU=FakeOU")
res = client.patch_active_directory(names=["test-config"], active_directory=ad_config)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: ids
# See section "Common Fields" for examples
