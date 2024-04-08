# delete a policy rule by name
client.delete_network_access_policies_rules(names=['default-network-access-policy.1'])

# delete a policy by name with a version specifier.
# The delete will fail if the policy version differs from specified version.
policy_version = '00000000-7b11-a468-0000-0000503669ea'
client.delete_network_access_policies_rules(names=['default-network-access-policy.1'], versions=[policy_version])

# delete a policy by ID
client.delete_network_access_policies_rules(ids=['2a37c647-19e9-4308-b469-89d9a9753160'])