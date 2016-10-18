def create_resource_group(resource_client, name, location):
    resource_client.resource_groups.create_or_update(name,
                                                     {
                                                         'location' : location
                                                     })

