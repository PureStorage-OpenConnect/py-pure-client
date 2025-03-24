# Delete the lifecycle rule named 'myrule' from bucket 'mybucket'
client.delete_lifecycle_rules(names=['mybucket/myrule'])

# Delete the lifecycle rule with id '10314f42-020d-7080-8013-000ddt400090'
client.delete_lifecycle_rules(ids=['10314f42-020d-7080-8013-000ddt400090'])

# Delete all the lifecycle rules from bucket 'mybucket'
client.delete_lifecycle_rules(bucket_names=['mybucket'])

# Delete all the lifecycle rules from bucket with id '100abf42-0000-4000-8023-000det400090'
client.delete_lifecycle_rules(bucket_ids=['100abf42-0000-4000-8023-000det400090'])

# Other valid fields: context_names
# See section "Common Fields" for examples
