# post the software check
res = client.post_software_check(software_versions=["10.0.0"], software_names=["Purity//FB"])
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))
# Other valid fields: softwares
# See section "Common Fields" for examples
