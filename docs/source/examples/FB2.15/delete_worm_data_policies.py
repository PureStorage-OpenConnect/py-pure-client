# Delete a WORM data policy
res = client.delete_worm_data_policies(names=['worm-policy-name'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: ids
# See section "Common Fields" for examples
