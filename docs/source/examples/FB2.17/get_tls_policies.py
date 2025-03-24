# get all TLS Policies
res = client.get_tls_policies()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# get a TLS Policy by name
res = client.get_tls_policies(names=['test_tls_policy'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# get a TLS Policy by id
res = client.get_tls_policies(ids=['10314f42-020d-7080-8013-000ddt400013'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# evaluate and retrieve the effective ciphers for a TLS policy
res = client.get_tls_policies(names=['test_tls_policy'], effective=True)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# get the details of purity_defined "default" values in policies
res = client.get_tls_policies(purity_defined=True)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: filter, limit, offset, sort, continuation_token
# See section "Common Fields" for examples
