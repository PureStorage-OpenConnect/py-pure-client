# Create api token for admin1 for 1 hour (timeout in ms)
res = client.post_admins_api_tokens(admin_names=["admin1"], timeout=1*60*60*1000)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: admin_ids
# See section "Common Fields" for examples
