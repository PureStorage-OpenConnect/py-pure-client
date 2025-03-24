# list remote arrays
res = client.get_remote_arrays(current_fleet_only=True)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: continuation_token, filter, ids, limit, names, offset, sort, total_only
# See section "Common Fields" for examples
