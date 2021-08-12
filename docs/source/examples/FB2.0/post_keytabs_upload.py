# read the binary data from your keytab file
with open('/etc/krb5.keytab', 'rb') as binary_keytab_file:
    my_binary_keytab_data = binary_keytab_file.read()
# upload the binary data. we use a tuple of (filename, file contents) as the keytab file to
# upload in order to be generically compatible across different python versions
res = client.post_keytabs_upload(name_prefixes='binary-uploaded-krb5',
                                 keytab_file=('krb5.keytab', my_binary_keytab_data))
# our result is the contents of the file we just uploaded
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))

# we can also upload a base64 encoded keytab file, in case we were sent a keytab
# through some medium where binary wasn't feasible (e.g. copied into a bash terminal,
# sent as text over an internal corporate messaging system)
with open('/etc/krb5.txt', 'r') as base64_keytab_file:
    my_base64_keytab_data = base64_keytab_file.read()

res = client.post_keytabs_upload(name_prefixes='base64-uploaded-krb5',
                                 keytab_file=('krb5.txt', my_base64_keytab_data))
# our result is the contents of the file we just uploaded
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
