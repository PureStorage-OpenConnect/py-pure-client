# List usage for all groups that have space used on usageFs
res = client.get_usage_groups(file_system_names=["usageFs"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: allow_errors, context_names, continuation_token, file_system_ids, filter, gids,
#                     group_names, limit, offset, sort
# See section "Common Fields" for examples
