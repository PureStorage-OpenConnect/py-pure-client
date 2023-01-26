# List the Challenge Response Verification Key for the array
res = client.get_support_verification_keys()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: continuation_token, limit, offset, sort, filter
# See section "Common Fields" for examples