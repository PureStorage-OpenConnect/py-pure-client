# Initiates the NLM reclamation
res = client.post_file_systems_locks_nlm_reclamations()
print(res)
if type(res) == pypureclient.responses.ValidResponse:
    print(list(res.items))