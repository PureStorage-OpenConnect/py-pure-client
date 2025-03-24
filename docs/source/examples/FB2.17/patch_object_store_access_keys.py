from pypureclient.flashblade import ObjectStoreAccessKey

# Disable the object store access key named "PSABSSZRHPMEDKHMAAJPJBONPJGGDDAOFABDEXAMPLE"
res = client.patch_object_store_access_keys(
    names=['PSABSSZRHPMEDKHMAAJPJBONPJGGDDAOFABDEXAMPLE'], object_store_access_key=ObjectStoreAccessKey(enabled=False))
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: context_names
# See section "Common Fields" for examples
