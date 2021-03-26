from pypureclient.flashblade import ObjectStoreRemoteCredentials

# Change the name of an existing set of remote credentials to "remote/credentials2"
# Change the access key id of an existing set of remote credentials
# Change the secret access key of an existing set of remote credentials
new_attr = ObjectStoreRemoteCredentials(name='remote/credentials2',
                                        access_key_id='PSFBIKZFCAAAKOEJ',
                                        secret_access_key='0BEC00003+b1228C223c0FbF1ab5e4GICJGBPJPEOLJCD')
# update the the remote credentials with the name 'remote/credentials1' with our new attributes
res = client.patch_object_store_remote_credentials(names=['remote/credentials1'],
                                                   remote_credentials=new_attr)
print(res)
# update the the remote credentials with the id '10314f42-020d-7080-8013-000ddt400090' with our new attributes
res = client.patch_object_store_remote_credentials(ids=['10314f42-020d-7080-8013-000ddt400090'],
                                                   remote_credentials=new_attr)
print(res)
