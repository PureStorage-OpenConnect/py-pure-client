# delete a policy rule by name
client.delete_smb_share_policies_rules(policy_names=['share_policy_1'], names=['everyone'])


# delete a policy by ID
client.delete_smb_share_policies_rules(policy_ids=['10314f42-020d-7080-8013-000ddt400012'], ids=['2a37c647-19e9-4308-b469-89d9a9753160'])
