from pypureclient.flashblade import BucketPost, Reference

# post the bucket object mybucket on the array
attr = BucketPost()
attr.account = Reference(name='myaccount')
res = client.post_buckets(names=["mybucket"], bucket=attr)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# make another bucket in the account with id '10314f42-020d-7080-8013-000ddt400090'
id_attr = BucketPost()
id_attr.account = Reference(id='10314f42-020d-7080-8013-000ddt400090')
res = client.post_buckets(names=["mybucket"], bucket=id_attr)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
