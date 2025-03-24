# delete a SSO OIDC configuration by name
res = client.delete_sso_oidc_idps(names=['test-sso'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# delete a SSO OIDC configuration by id
res = client.delete_sso_oidc_idps(ids=['10314f42-020d-7080-8013-000ddt400012'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
