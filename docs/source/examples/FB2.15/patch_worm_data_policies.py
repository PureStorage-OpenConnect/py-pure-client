from pypureclient.flashblade.FB_2_15 import WormDataPolicy

# update a WORM data policy
policy_body = WormDataPolicy(
    enabled=True, retention_lock='unlocked', mode='compliance',
    min_retention=1000, max_retention=10000, default_retention=5000)

res = client.patch_worm_data_policies(names=['worm-policy-name'],
                                      policy=policy_body)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    res_items = (list(res.items))
    print(res_items)

# Other valid fields: ids
# See section "Common Fields" for examples
