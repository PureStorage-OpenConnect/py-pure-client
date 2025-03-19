# Delete an SSO SAML2 configuration by name.
res = client.delete_sso_saml2_idps(names=['test-sso'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Delete an SSO SAML2 configuration by ID.
res = client.delete_sso_saml2_idps(ids=['10314f42-020d-7080-8013-000ddt400012'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
