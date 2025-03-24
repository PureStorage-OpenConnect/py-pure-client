from pypureclient.flashblade import ObjectStoreRemoteCredentials

# create a remote credentials object corresponding to user credentials on the remote
name = "remote/credentials"
access_key = "PSFBIKZFCAAAKOEJ"
secret_key = "0BEC00003+b1228C223c0FbF1ab5e4GICJGBPJPEOLJCD"
remote_credentials = ObjectStoreRemoteCredentials(access_key_id=access_key, secret_access_key=secret_key)
# post the remote credentials object on the local array
res = client.post_object_store_remote_credentials(names=[name], remote_credentials=remote_credentials)
print(res)

# Other valid fields: context_names
# See ids in section "Common Fields" for examples
