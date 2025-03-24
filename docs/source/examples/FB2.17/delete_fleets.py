# delete fleet by name
res = client.delete_fleets(names=['my-fleet'])
print(res)

# delete fleet by id
res = client.delete_fleets(ids=['635c0a0c-37ad-4f91-bad7-5224c284c2ad'])
print(res)

