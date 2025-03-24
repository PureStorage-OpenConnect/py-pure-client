# download trust policy by object store role id
res = client.get_object_store_roles_object_store_trust_policies_download(role_ids=["f8b3b3b3-3b3b-3b3b-3b3b-3b3b3b3b3b3b"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# download trust policy by object store role name
res = client.get_object_store_roles_object_store_trust_policies_download(role_names=["acc1/myobjrole"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# download trust policy by trust policy name
res = client.get_object_store_roles_object_store_trust_policies_download(names=["acc1/myobjrole/trust-policy"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
