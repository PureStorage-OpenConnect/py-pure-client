from pypureclient.flashblade import LifecycleRule

# modify the lifecycle rule 'myrule' for the bucket 'mybucket'.
attr = LifecycleRule(enabled=True,
                     keep_previous_version_for=7*24*60*60*1000,
                     prefix='mynewprefix')
res = client.patch_lifecycle_rules(names=['mybucket/myrule'], lifecycle=attr)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: bucket_ids, bucket_names, ids
# See section "Common Fields" for examples
