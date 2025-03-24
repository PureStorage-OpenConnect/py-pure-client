# delete a TLS policy by name
tls_policy_name = 'example_policy'
res = client.delete_tls_policies(names=[tls_policy_name])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# delete a TLS policy by id
tls_policy_id = '10314f42-020d-7080-8013-000ddt400013'
res = client.delete_tls_policies(ids=[tls_policy_id])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
