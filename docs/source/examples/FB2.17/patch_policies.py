from pypureclient.flashblade import PolicyPatch, PolicyRule

# Update the policy "p1", and set the "enabled" field to "False", add a rule and remove a rule
# By passing destroy_snapshots=True, we accept that snapshots created by the
# removed rule will be destroyed.
rule_to_be_removed = PolicyRule(every=1000*60*5, keep_for=1000*60*60)
rule_to_be_added = PolicyRule(every=1000*60*10, keep_for=1000*60*60)
res = client.patch_policies(
    names=["p1"],
    destroy_snapshots=True,
    policy=PolicyPatch(enabled=False,
                       remove_rules=[rule_to_be_removed],
                       add_rules=[rule_to_be_added]))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: context_names, ids
# See section "Common Fields" for examples
