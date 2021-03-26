from pypureclient.flashblade import UserQuota

file_system_name = "quotaFs"

# Add a quota of 1024 for the file system to apply to the users with ids 123 and 124
res = client.post_quotas_users(file_system_names=[file_system_name], uids=[123, 124],
                               quota=UserQuota(quota=1024))
# print the created quotas
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Add a quota of 2048 for the file system to apply to the users with names user1 and user2
res = client.post_quotas_users(file_system_names=[file_system_name],
                               user_names=["user1", "user2"],
                               quota=UserQuota(quota=2048))
# print the created quotas
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: file_system_ids
# See section "Common Fields" for examples
