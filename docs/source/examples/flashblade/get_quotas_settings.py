# check the contact info being sent to end users and groups regarding their quotas, and
# check if direct notifications to them are enabled
res = client.get_quotas_settings()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: ids, names
# See section "Common Fields" for examples
