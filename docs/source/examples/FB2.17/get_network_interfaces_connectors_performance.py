# list instantaneous performance for all network connectors
res = client.get_network_interfaces_connectors_performance()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list instantaneous network connectors performance for selected ethernet connectors
res = client.get_network_interfaces_connectors_performance(names=['*ETH2*'])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# List network connectors performance by id.
res = client.get_network_interfaces_connectors_performance(ids=["10314f42-020d-7080-8013-000ddt400090"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# list historical network connectors performance for all connectors between some
# start time and end time
res = client.get_network_interfaces_connectors_performance(
    start_time=START_TIME,
    end_time=END_TIME,
    resolution=30000)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: filter, limit, offset, sort, total_only
# See section "Common Fields" for examples
