from pypureclient.flashblade import SnmpV3, SnmpAgent, SnmpV2c

# update the snmp agent using snmpv2c to use snmpv3 with v3 attributes
# there is only one snmp agent on the system
new_v3_attrs = SnmpV3(auth_protocol='SHA', auth_passphrase='my-password-1!',
                      privacy_protocol='AES', privacy_passphrase='min8chars',
                      user='service-account-1')
agent_v3_update_attrs = SnmpAgent(version='v3', v3=new_v3_attrs)
# updating the agent to use v3 instead of v2c will automatically clear out v2c
# attributes
res = client.patch_snmp_agents(snmp_agent=agent_v3_update_attrs)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# update an snmp agent using snmpv3 to use snmpv2c with v2c attributes
new_v2_attrs = SnmpV2c(community='community-for-informs-and-traps')
agent_v2c_update_attrs = SnmpAgent(version='v2c', v2c=new_v2_attrs)
# updating the agent to use v2c instead of v3 will automatically clear out v3
# attributes
res = client.patch_snmp_agents(snmp_agent=agent_v2c_update_attrs)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
