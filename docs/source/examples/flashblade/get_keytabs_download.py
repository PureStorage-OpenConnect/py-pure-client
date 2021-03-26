# download keytab file and list the file name
res = client.get_keytabs_download()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# export all keytabs on the system with a certain encryption type, and write their binary
# to a file
desired_encryption_type = 'aes256-cts-hmac-sha1-96'
filter_str = 'encryption_type="{}"'.format(desired_encryption_type)
res = client.get_keytabs(filter=filter_str)
# get the names from our results
names_to_export = []
for keytab_entry_obj in list(res.items):
    names_to_export.append(keytab_entry_obj.name)
# download file composed of the keytabs we gathered, encoded in binary
res = client.get_keytabs_download(keytab_names=names_to_export)
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# Other valid fields: keytab_ids
# See section "Common Fields" for examples
