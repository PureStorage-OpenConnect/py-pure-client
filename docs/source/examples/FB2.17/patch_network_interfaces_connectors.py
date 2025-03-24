from pypureclient.flashblade import HardwareConnector

# Set port count on CH1.FM1.ETH1 (can also set lane_speed)
res = client.patch_network_interfaces_connectors(names=['CH1.FM1.ETH1'],
                                       network_connector=HardwareConnector(port_count=4))
# Other valid fields: ids
# See section "Common Fields" for examples
