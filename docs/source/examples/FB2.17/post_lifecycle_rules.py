from pypureclient.flashblade import LifecycleRulePost, Reference

# create a lifecycle rule 'myrule' for the bucket 'mybucket' with 'keep_previous_version_for'
attr = LifecycleRulePost(bucket=Reference(name='mybucket'),
                         rule_id='myrule',
                         keep_previous_version_for=2*24*60*60*1000,
                         prefix='myprefix')
res = client.post_lifecycle_rules(rule=attr)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# create a lifecycle rule 'myrule1' for the bucket 'mybucket' with 'keep_current_version_for'
attr = LifecycleRulePost(bucket=Reference(name='mybucket'),
                         rule_id='myrule1',
                         keep_current_version_for=2*24*60*60*1000,
                         prefix='myprefix')
res = client.post_lifecycle_rules(rule=attr)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# create a lifecycle rule 'myrule2' for the bucket 'mybucket' with
# 'keep_current_version_until' and 'abort_incomplete_multipart_uploads_after'
attr = LifecycleRulePost(bucket=Reference(name='mybucket'),
                         rule_id='myrule2',
                         keep_current_version_until=1639267200000,  # 2021-12-12
                         abort_incomplete_multipart_uploads_after=172800000,  # 2 day
                         prefix='myprefix')
res = client.post_lifecycle_rules(rule=attr, confirm_date=True)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: context_names
# See ids in section "Common Fields" for examples
