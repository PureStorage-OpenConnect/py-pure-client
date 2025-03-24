# list TLS policies for network interfaces
res = client.get_network_interfaces_tls_policies()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list TLS policies for specific network interface
res = client.get_network_interfaces_tls_policies(member_names=["datavip1"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list TLS policies for specific network interface by id
res = client.get_network_interfaces_tls_policies(member_ids=["10314f42-020d-7080-8013-000ddt400090"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list only network interfaces belonging to a specific policy by name
res = client.get_network_interfaces_tls_policies(policy_names=["strong-tls-policy"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list only network interfaces with a specific policy by id
res = client.get_network_interfaces_tls_policies(policy_ids=["10314f42-020d-7080-8013-000ddt400012"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: continuation_token, filter, limit, offset, sort
# See section "Common Fields" for examples
