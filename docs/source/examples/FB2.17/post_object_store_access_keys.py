from pypureclient.flashblade import ObjectStoreAccessKeyPost

# generate access key and secret key for object store user
# note: you need to handle the secret key since you can't retrieve it from the array after create
res = client.post_object_store_access_keys(
    object_store_access_key=ObjectStoreAccessKeyPost(user={'name': 'acc1/myobjuser'}))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# make another access key for the user with id '100abf42-0000-4000-8023-000det400090'
res = client.post_object_store_access_keys(
    object_store_access_key=ObjectStoreAccessKeyPost(user={'id': '100abf42-0000-4000-8023-000det400090'}))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# import credentials from another FlashBlade
res = client.post_object_store_access_keys(
    names=['PSABSSZRHPMEDKHMAAJPJBONPJGGDDAOFABDGLBJLHO'],
    object_store_access_key=ObjectStoreAccessKeyPost(
        user={'name': 'acc1/myobjuser'}, secret_access_key='BAG61F63105e0d3669/e066+5C5DFBE2c127d395LBGG'
    )
)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: context_names
# See ids in section "Common Fields" for examples
