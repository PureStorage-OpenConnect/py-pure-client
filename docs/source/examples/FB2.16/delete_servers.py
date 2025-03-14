# Delete servers
# Please note: cascade_delete parameter is required
res = client.delete_servers(names=['myserver'], cascade_delete='directory-services')

# Other valid fields: ids, references
# See section "Common Fields" for examples
