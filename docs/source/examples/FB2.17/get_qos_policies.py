# list all qos policies
res = client.get_qos_policies()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# get a specific qos policy using name
res = client.get_qos_policies(names=["myqos"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# get a specific qos policy using id
res = client.get_qos_policies(ids=["38453e5c-1c5d-459f-8d76-a2bb5d1db56a"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# filter example - enabled only
res = client.get_qos_policies(filter="enabled")
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# filter example - disabled only
res = client.get_qos_policies(filter="enabled='False'")
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# filter example - list policies with max bytes per sec less than 1G
res = client.get_qos_policies(filter="max_total_bytes_per_sec<1073741824")
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# filter example - list policies with max bytes per sec greater than or equal to 1G
res = client.get_qos_policies(filter="max_total_bytes_per_sec>='1G'")
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: continuation_token, limit, offset, sort
# See section "Common Fields" for examples
