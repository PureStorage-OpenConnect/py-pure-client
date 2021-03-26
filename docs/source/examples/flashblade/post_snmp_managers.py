from pypureclient.flashblade import SnmpV3, SnmpManagerPost, SnmpV2c

snmp_host = 'snmphost1.example.gov'
# create an snmp trap manager using snmpv3 with the name 'my-v3-manager' and appropriate
# v3 attributes
v3_attrs = SnmpV3(auth_protocol='SHA', auth_passphrase='my-password-1!',
                  privacy_protocol='AES', privacy_passphrase='min8chars',
                  user='service-account-1')
new_v3_manager = SnmpManagerPost(host=snmp_host, notification='trap',
                                 version='v3', v3=v3_attrs)
v3_manager_name = 'my-v3-manager'
res = client.post_snmp_managers(names=[v3_manager_name],
                                snmp_manager=new_v3_manager)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# create an snmp inform manager using snmpv2c with the name 'my-v2c-manager' and appropriate
# v2c attributes
v2_attrs = SnmpV2c(community='some-community-for-informs')
new_v2c_manager = SnmpManagerPost(host=snmp_host, notification='inform',
                                  version='v2c', v2c=v2_attrs)
v2c_manager_name = 'my-v2c-manager'
res = client.post_snmp_managers(names=[v2c_manager_name],
                                snmp_manager=new_v2c_manager)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
