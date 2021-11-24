# list global admin settings
res = client.get_admins_settings()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: continuation_token, filter, limit, offset, sort
# See section "Common Fields" for examples
