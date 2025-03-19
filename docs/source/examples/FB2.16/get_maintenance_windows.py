# List Maintenance Windows
res = client.get_maintenance_windows()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: continuation_token, filter, ids, limit, names, offset, sort, references
# See section "Common Fields" for examples
