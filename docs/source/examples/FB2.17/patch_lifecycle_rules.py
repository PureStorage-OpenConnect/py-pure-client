from pypureclient.flashblade import LifecycleRule

# modify the lifecycle rule 'myrule' for the bucket 'mybucket', changing the 'keep_previous_version_for'.
attr = LifecycleRule(enabled=True,
                     keep_previous_version_for=7*24*60*60*1000,
                     prefix='mynewprefix')
res = client.patch_lifecycle_rules(names=['mybucket/myrule'], lifecycle=attr)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# modify the lifecycle rule 'myrule' again for the bucket 'mybucket' again, adding 'keep_current_version_for'.
attr = LifecycleRule(enabled=True,
                     keep_current_version_for=7*24*60*60*1000,
                     prefix='mynewprefix')
res = client.patch_lifecycle_rules(bucket_names=['mybucket'], names=['myrule'], lifecycle=attr)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# modify the lifecycle rule 'myrule' again for the bucket 'mybucket' again, deleting 'keep_current_version_for' and
# adding 'keep_current_version_until' and 'abort_incomplete_multipart_uploads_after'
attr = LifecycleRule(enabled=True,
                     keep_current_version_for=0,
                     keep_current_version_until=1639267200000,  # 2021-12-12
                     abort_incomplete_multipart_uploads_after=172800000,  # 2 day
                     prefix='mynewprefix')
res = client.patch_lifecycle_rules(bucket_ids=['10314f42-020d-7080-8013-000ddt400091'],
                                   ids=["10314f42-020d-7080-8013-000ddt400090"], lifecycle=attr, confirm_date=True)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: context_names
# See section "Common Fields" for examples
