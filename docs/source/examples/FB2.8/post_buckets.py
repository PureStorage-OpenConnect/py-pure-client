from pypureclient.flashblade import BucketPost, Reference, ObjectLockConfigRequestBody

# Create the bucket "mybucket" under the account named "myaccount"
attr = BucketPost()
attr.account = Reference(name='myaccount')
res = client.post_buckets(names=["mybucket"], bucket=attr)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Make another bucket in "myaccount" with id '10314f42-020d-7080-8013-000ddt400090'. Provide an
# initial hard limit (i.e. enforced) quota configuration of 5G.
attr = BucketPost(account=Reference(id='10314f42-020d-7080-8013-000ddt400090'),
                  quota_limit=str(5 * 1024 * 1024),
                  hard_limit_enabled=True)
res = client.post_buckets(names=["mybucket2"], bucket=attr)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Create the bucket "mybucket3" under the account named "myaccount". Freeze locked objects
# to prevent object overwrite after object lock is enabled.
attr = BucketPost()
attr.account = Reference(name='myaccount')
attr.object_lock_config = ObjectLockConfigRequestBody(freeze_locked_objects=True)
res = client.post_buckets(names=["mybucket3"], bucket=attr)

print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Create the bucket "mybucket4" under the account named "myaccount". Freeze locked objects
# to prevent object overwrite, and enable object-lock.
attr = BucketPost()
attr.account = Reference(name='myaccount')
attr.object_lock_config = ObjectLockConfigRequestBody(
    enabled=True,
    freeze_locked_objects=True)
res = client.post_buckets(names=["mybucket4"], bucket=attr)

print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Create the bucket "mybucket5" under the account named "myaccount". Freeze locked objects
# to prevent object overwrite. By default, users will be able to use object lock for new objects
# in "mybucket5" with a retention period of 1 day, and "compliance" retention mode. Furthermore,
# the bucket will have a "ratcheted" retention lock to prevent the level of bucket protection
# from being decreased and to disable manual eradication of the bucket.
attr = BucketPost()
attr.account = Reference(name='myaccount')
attr.object_lock_config = ObjectLockConfigRequestBody(
    enabled=True,
    freeze_locked_objects=True,
    default_retention=86400000,  # 1 day in ms
    default_retention_mode="compliance")
attr.retention_lock = "ratcheted"
res = client.post_buckets(names=["mybucket5"], bucket=attr)

print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
