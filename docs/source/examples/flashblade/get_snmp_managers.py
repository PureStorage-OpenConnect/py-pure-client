# list all snmp managers
res = client.get_snmp_managers()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list the snmp manager with the name 'my-v3-manager'
manager_name = 'my-v3-manager'
res = client.get_snmp_managers(names=[manager_name])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list all snmp managers using v3 as their snmp version
version_filter_string = '(version="v3")'
res = client.get_snmp_managers(filter=version_filter_string)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# list all snmp managers sorting by host
sort_string = 'host'
res = client.get_snmp_managers(sort=sort_string)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: continuation_token, ids, limit, offset
# See section "Common Fields" for examples
