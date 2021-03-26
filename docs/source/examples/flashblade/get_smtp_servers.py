res = client.get_smtp_servers() # The SMTP properties are related to alert routing
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Valid fields: continuation_token, filter, ids, limit, names, offset, sort
# See section "Common Fields" for examples
