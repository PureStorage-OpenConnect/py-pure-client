# list the array's SNMP agent MIB
res = client.get_snmp_agents_mib()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
