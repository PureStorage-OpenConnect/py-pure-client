from pypureclient.flashblade import LinkAggregationGroup

# create lag named "mylag" with ports 'CH1.FM1.ETH4' and 'CH1.FM2.ETH4'
res = client.post_link_aggregation_groups(
    names=["mylag"],
    link_aggregation_group=LinkAggregationGroup(ports=[{'name': 'CH1.FM1.ETH4'},
                                                       {'name': 'CH1.FM2.ETH4'}]))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
