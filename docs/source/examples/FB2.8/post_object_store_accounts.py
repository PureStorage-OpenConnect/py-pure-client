from pypureclient.flashblade import BucketDefaults, ObjectStoreAccountPost

# Post the object store account object "myobjaccount" on the array. Provide an initial quota
# configuration that uses a hard (i.e. enforced) quota limit of 1T for the account, and a default
# soft quota limit of 50G for buckets that will be created in the account.
bucket_default_attr = BucketDefaults(quota_limit=str(50*1024*1024*1024),
                                     hard_limit_enabled=False)
res = client.post_object_store_accounts(names=["myobjaccount"],
                                        object_store_account=ObjectStoreAccountPost(quota_limit=str(1024*1024*1024*1024),
                                                                                    hard_limit_enabled=True,
                                                                                    bucket_defaults=bucket_default_attr))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
