from pypureclient.flashblade import Target

# Change the name of an existing target to "remote2"
# Change the address of an existing target to "1.1.1.1"
new_attr = Target(name='remote2',
                  address='1.1.1.1')
# Update the existing target that's named 'remote1' with our new attributes
res = client.patch_targets(names=['remote1'], target=new_attr)
print(res)

# Update the existing target that has the id '10314f42-020d-7080-8013-000ddt400090' with our new attributes
res = client.patch_targets(ids=['10314f42-020d-7080-8013-000ddt400090'], target=new_attr)
print(res)
