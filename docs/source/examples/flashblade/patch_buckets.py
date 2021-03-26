from pypureclient.flashblade import Bucket

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
# Other valid fields: ids
# See section "Common Fields" for examples
