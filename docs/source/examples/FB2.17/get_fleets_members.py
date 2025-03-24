# list fleet members
res = client.get_fleets_members()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: fleets, members, continuation_token, filter, fleet_ids, fleet_names, limit, member_ids, member_names, offset, sort, total_only
# See section "Common Fields" for examples