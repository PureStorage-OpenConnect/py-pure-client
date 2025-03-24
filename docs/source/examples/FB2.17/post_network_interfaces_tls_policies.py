# add a policy to a network interface by name
client.post_network_interfaces_tls_policies(
    member_names=["datavip1"], policy_names=["strong-tls"])

# add a policy to a network interface by id
client.post_network_interfaces_tls_policies(
    member_ids=["10314f42-020d-7080-8013-000ddt400090"], policy_ids=["10314f42-020d-7080-8013-000ddt400012"])
