# test the snmp manager with the name 'my-v3-manager'
manager_name = 'my-v3-manager'
res = client.get_snmp_managers_test(names=[manager_name])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# test the snmp manager with the id '10314f42-020d-7080-8013-000ddt400090'
manager_id = '10314f42-020d-7080-8013-000ddt400090'
res = client.get_snmp_managers_test(ids=[manager_id])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: continuation_token, filter, limit, offset, sort
# See section "Common Fields" for examples
