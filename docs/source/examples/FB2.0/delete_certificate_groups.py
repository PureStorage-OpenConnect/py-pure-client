# delete our group for active directory certificates
group_for_active_directory_certs = 'all-ad-certs'
client.delete_certificate_groups(names=[group_for_active_directory_certs])

# Other valid fields: ids
# See section "Common Fields" for examples
