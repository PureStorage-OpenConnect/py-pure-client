from pypureclient.flashblade import Bucket, ObjectLockConfigRequestBody, PublicAccessConfig, BucketEradicationConfig

# Destroy the bucket named "mybucket", and also suspend versioning
res = client.patch_buckets(names=["mybucket"],
                           bucket=Bucket(destroyed=True, versioning="suspended"))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Recover the bucket "mybucket", and also enable versioning
res = client.patch_buckets(names=["mybucket"],
                           bucket=Bucket(destroyed=False, versioning="enabled"))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Update the quota settings for "mybucket". Enable a hard limit (i.e. enforced)
# quota of 10G for this bucket.
res = client.patch_buckets(names=["mybucket"],
                           bucket=Bucket(quota_limit=str(10*1024*1024*1024),
                                         hard_limit_enabled=True))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Reduce the hard limit quota for "mybucket" to 1G while ignoring its current usage (i.e.
# the operation should not fail due to the bucket's size currently being greater than 1G)
res = client.patch_buckets(names=["mybucket"],
                           bucket=Bucket(quota_limit=str(1*1024*1024*1024)),
                           ignore_usage=True)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Clear the quota limit for "mybucket"
res = client.patch_buckets(names=["mybucket"],
                           bucket=Bucket(quota_limit='',))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Enable object lock for "mybucket"
res = client.patch_buckets(names=["mybucket"],
                           bucket=Bucket(object_lock_config=ObjectLockConfigRequestBody(enabled=True)))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Change default retention to 1 day and default retention mode to "compliance" for "mybucket".
res = client.patch_buckets(names=["mybucket"],
                           bucket=Bucket(object_lock_config=ObjectLockConfigRequestBody(
                               default_retention=86400000,  # 1 day in ms
                               default_retention_mode="compliance")))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Change retention lock to "ratcheted" to prevent the level of locked objects protection
# from being decreased and to disable manual eradication of the bucket for "mybucket".
res = client.patch_buckets(names=["mybucket"],
                           bucket=Bucket(retention_lock="ratcheted"))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Freeze locked objects to prevent object overwrite after object lock is enabled for "mybucket".
res = client.patch_buckets(names=["mybucket2"],
                           bucket=Bucket(object_lock_config=ObjectLockConfigRequestBody(freeze_locked_objects=True)))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Disable block new public policies for "mybucket".
res = client.patch_buckets(names=["mybucket"],
                           bucket=Bucket(public_access_config=PublicAccessConfig(block_new_public_policies=False)))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Disable block public access for "mybucket".
res = client.patch_buckets(names=["mybucket"],
                           bucket=Bucket(public_access_config=PublicAccessConfig(block_public_access=False)))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Block new public policies and public access for "mybucket".
res = client.patch_buckets(names=["mybucket"],
                           bucket=Bucket(public_access_config=PublicAccessConfig(
                           block_new_public_policies=True,
                           block_public_access=True)))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Change eradication mode to "retention-based" to prevent eradication of the bucket 
# as long as there areany objects are protected with object lock of the bucket for "mybucket".
res = client.patch_buckets(names=["mybucket"],
                           bucket=Bucket(
                           eradication_config=
                           BucketEradicationConfig(eradication_mode="retention-based")))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: ids
# See section "Common Fields" for examples
