from pypureclient.flashblade import Policy, PolicyRule

# post a policy object p1 on the array
attr = Policy(enabled=True,
              rules=[
                  # Take a snapshot every 5m and keep for 1h
                  PolicyRule(every=1000*60*5, keep_for=1000*60*60)
              ])
res = client.post_policies(names=["p1"], policy=attr)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: context_names
# See section "Common Fields" for examples
