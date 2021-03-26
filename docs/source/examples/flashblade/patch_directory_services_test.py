from pypureclient.flashblade import DirectoryService, Reference

# test the existing nfs directory service configuration, but using a different certificate
# and bind user
test_bind_user = 'CN=differentUser,CN=Users,DC=example,DC=com'
test_certificate_name = 'nfs-server-certificate'
cert_reference = Reference(name=test_certificate_name)
test_ds_config = DirectoryService(bind_user=test_bind_user, ca_certificate=cert_reference)
res = client.patch_directory_services_test(names=['nfs'],
                                           directory_service=test_ds_config)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: ids, filter, sort
# See section "Common Fields" for examples
