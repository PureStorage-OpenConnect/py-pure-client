# Get all SSO SAML2 configurations
res = client.get_sso_saml2_idps()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Get an SSO SAML2 configuration by name
res = client.get_sso_saml2_idps(names=['test-sso'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Get an SSO SAML2 configuration by ID
res = client.get_sso_saml2_idps(ids=['10314f42-020d-7080-8013-000ddt400012'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: filter, limit, offset, sort, continuation_token
# See section "Common Fields" for examples
