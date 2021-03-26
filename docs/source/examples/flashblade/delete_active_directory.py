# Delete active directory account
client.delete_active_directory(names=["test-config"])

# Do a local-only delete of an active directory account
client.delete_active_directory(names=["test-config"], local_only=True)

# Other valid fields: ids
# See section "Common Fields" for examples
