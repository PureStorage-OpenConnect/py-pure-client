# Assume you have a file system named quotaFs
file_system_name = "quotaFs"

# Delete the quotas of users on the file system with ids 123 and 124
client.delete_quotas_users(file_system_names=[file_system_name], uids=[123, 124])

# Delete the quotas of users on the file system with names user1 and user2
client.delete_quotas_users(file_system_names=[file_system_name],
                           user_names=["user1", "user2"])

# Other valid fields: file_system_ids, names
# See section "Common Fields" for examples
