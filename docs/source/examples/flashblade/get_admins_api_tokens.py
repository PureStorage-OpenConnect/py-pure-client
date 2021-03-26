# Get api tokens with current user's exposed
res = client.get_admins_api_tokens(expose_api_token=True)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: admin_ids, admin_names, continuation_token, filter, limit, offset, sort
# See section "Common Fields" for examples
