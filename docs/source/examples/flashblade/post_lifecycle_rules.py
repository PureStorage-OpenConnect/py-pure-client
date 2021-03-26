from pypureclient.flashblade import LifecycleRulePost, Reference

# create a lifecycle rule 'myrule' for the bucket 'mybucket'.
attr = LifecycleRulePost(bucket=Reference(name='mybucket'),
                         rule_id='myrule',
                         keep_previous_version_for=2*24*60*60*1000,
                         prefix='myprefix')
res = client.post_lifecycle_rules(rule=attr)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
