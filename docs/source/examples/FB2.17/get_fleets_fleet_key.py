res = client.get_fleets_fleet_key()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: continuation_token, filter, limit, offset, sort, total_only
# See section "Common Fields" for examples
