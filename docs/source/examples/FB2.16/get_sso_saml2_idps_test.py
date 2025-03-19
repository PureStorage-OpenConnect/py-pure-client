# Get all SSO SAML2 configurations test results
res = client.get_sso_saml2_idps_test()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Get an SSO SAML2 configuration test results by name
res = client.get_sso_saml2_idps_test(names=['test-sso'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Get an SSO SAML2 configuration test results by ID
res = client.get_sso_saml2_idps_test(ids=['10314f42-020d-7080-8013-000ddt400012'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: filter, limit, sort
# See section "Common Fields" for examples
