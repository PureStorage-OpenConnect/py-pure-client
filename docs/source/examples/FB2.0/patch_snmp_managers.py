from pypureclient.flashblade import SnmpV3, SnmpManager, SnmpV2c

# update an snmp trap manager using snmpv2c with the name 'my-manager' to use snmpv3
# with v3 attributes
new_v3_attrs = SnmpV3(auth_protocol='SHA', auth_passphrase='my-password-1!',
                      privacy_protocol='AES', privacy_passphrase='min8chars',
                      user='service-account-1')
manager_v3_update_attrs = SnmpManager(version='v3', v3=new_v3_attrs)
existing_manager_name = 'my-v3-manager'
# updating the manager to use v3 instead of v2c will automatically clear out v2c
# attributes
res = client.patch_snmp_managers(names=[existing_manager_name],
                                 snmp_manager=manager_v3_update_attrs)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# update an snmp trap manager using snmpv3 with the name 'my-manager-2' to use snmpv2c
# with v2c attributes
new_v2_attrs = SnmpV2c(community='community-for-informs-and-traps')
manager_v2c_update_attrs = SnmpManager(version='v2c', v2c=new_v2_attrs)
existing_manager_name = 'my-v2c-manager'
# updating the manager to use v2c instead of v3 will automatically clear out v3
# attributes
res = client.patch_snmp_managers(names=[existing_manager_name],
                                 snmp_manager=manager_v2c_update_attrs)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: ids
# See section "Common Fields" for examples
