from pypureclient.flashblade import UserQuota

file_system_name = "quotaFs"
# Update the quota for users with ids 123 and 124 to be 2048 bytes
res = client.patch_quotas_users(file_system_names=[file_system_name],
                                uids=[123, 124],
                                quota=UserQuota(quota=2048))
# print the updated quotas
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Update the quota for users with names user1 and user2 to be 1024 bytes
res = client.patch_quotas_users(file_system_names=[file_system_name],
                                user_names=["user1", "user2"],
                                quota=UserQuota(quota=1024))
# print the updated quotas
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: file_system_ids, names
# See section "Common Fields" for examples
