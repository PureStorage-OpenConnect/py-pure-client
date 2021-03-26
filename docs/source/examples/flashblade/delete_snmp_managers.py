# delete the snmp manager with the name 'my-v3-manager'
manager_name = 'my-v3-manager'
client.delete_snmp_managers(names=[manager_name])

# list all snmp managers using v2c as their snmp version and then delete them, thus cleaning
# up managers on older versions
version_filter_string = '(version="v2c")'
res = client.get_snmp_managers(filter=version_filter_string)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    items = list(res.items)
    print(items)
    for snmp_manager in items:
        name_to_delete = snmp_manager.name
        client.delete_snmp_managers(names=[name_to_delete])

# Other valid fields: ids
# See section "Common Fields" for examples
