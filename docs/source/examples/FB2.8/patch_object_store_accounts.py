from pypureclient.flashblade import BucketDefaults, ObjectStoreAccountPatch

# Update the quota settings for the account named "my-obj-store-account". Enable a
# hard limit (i.e. enforced) quota of 100G.
res = client.patch_object_store_accounts(names=["my-obj-store-account"],
                                         object_store_account=ObjectStoreAccountPatch(quota_limit=str(100*1024*1024*1024),
                                                                                      hard_limit_enabled=True))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Reduce the hard limit quota for "my-obj-store-account" to 80G while ignoring its current usage (i.e.
# the operation should not fail due to the account's size currently being greater than 80G)
res = client.patch_object_store_accounts(names=["my-obj-store-account"],
                                         object_store_account=ObjectStoreAccountPatch(quota_limit=str(80*1024*1024*1024)),
                                         ignore_usage=True)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Update the BucketDefaults for "my-obj-store-account". Enable a soft (i.e. alerted but unenforced)
# quota limit of 10G for each new bucket for which an overriding quota configuration is not provided.
bucket_default_attr = BucketDefaults(quota_limit=str(10*1024*1024*1024),
                                     hard_limit_enabled=False)
res = client.patch_object_store_accounts(names=["my-obj-store-account"],
                                         object_store_account=ObjectStoreAccountPatch(bucket_defaults=bucket_default_attr))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Clear the quota limit for "my-obj-store-account"
res = client.patch_object_store_accounts(names=["my-obj-store-account"],
                                         object_store_account=ObjectStoreAccountPatch(quota_limit=''))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: ids
# See section "Common Fields" for examples
