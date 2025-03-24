# List usage for all users who have space used on usageFs
res = client.get_usage_users(file_system_names=["usageFs"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: allow_errors, context_names, continuation_token, file_system_ids, filter, uids,
#                     user_names, limit, offset, sort
# See section "Common Fields" for examples
