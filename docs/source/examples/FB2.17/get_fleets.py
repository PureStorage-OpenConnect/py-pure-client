res = client.get_fleets()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: continuation_token, filter, ids, limit, names, offset, sort, total_only
# See section "Common Fields" for examples