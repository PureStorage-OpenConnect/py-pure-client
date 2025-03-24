# delete the array connection with the name 'otherarray'
client.delete_array_connections(remote_names=['otherarray'])

# delete the array connection with id '10314f42-020d-7080-8013-000ddt400090'
client.delete_array_connections(remote_ids=['10314f42-020d-7080-8013-000ddt400090'])

# Other valid fields: ids, context_names
# See section "Common Fields" for examples
