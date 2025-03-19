# Get all software check
res = client.get_software_check()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# get by names
res = client.get_software_check(names=['1'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# get by ids
res = client.get_software_check(ids=['4ed534f8-e47e-cd29-25f0-841811266ba3'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# get by software_versions
res = client.get_software_check(software_versions='5.0.0')
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# get by software_names
res = client.get_software_check(software_names="Purity//FB")
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: softwares, filter, limit, offset, sort, total_item_count
# See section "Common Fields" for examples

