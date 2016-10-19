def create_resource_group(resource_client, name, location):
    result = resource_client.resource_groups.create_or_update(name,
                                                              {
                                                                  'location' : location
                                                              })
    return result.wait()

def create_vm_parameters(location,
                         vm_name,
                         admin_username,
                         admin_password,
                         os_disk_name,
                         nic_id,
                         vm_reference,
                         storage_account_name):
    """Create the VM parameters structure.
    """
    return {
        'location': location,
        'os_profile': {
            'computer_name': vm_name,
            'admin_username': admin_username,
            'admin_password': admin_password,
        },
        'hardware_profile': {
            'vm_size': 'Standard_DS1'
        },
        'storage_profile': {
            'image_reference': {
                'publisher': vm_reference['publisher'],
                'offer': vm_reference['offer'],
                'sku': vm_reference['sku'],
                'version': vm_reference['version']
            },
            'os_disk': {
                'name': os_disk_name,
                'caching': 'None',
                'create_option': 'fromImage',
                'vhd': {
                    'uri': 'https://{}.blob.core.windows.net/vhds/{}.vhd'.format(
                        storage_account_name, vm_name)
                }
            },
        },
        'network_profile': {
            'network_interfaces': [{
                'id': nic_id,
            }]
        },
    }

def create_nic(resource_group_name,
               vnet_name,
               subnet_name,
               network_client,
               nic_name,
               location,
               ip_config_name):
    """Create a Network Interface for a VM.
    """
    # Create VNet
    async_vnet_creation = network_client.virtual_networks.create_or_update(
        resource_group_name,
        vnet_name,
        {
            'location': location,
            'address_space': {
                'address_prefixes': ['10.0.0.0/16']
            }
        }
    )
    async_vnet_creation.wait()

    # Create Subnet
    async_subnet_creation = network_client.subnets.create_or_update(
        resource_group_name,
        vnet_name,
        subnet_name,
        {'address_prefix': '10.0.0.0/24'}
    )
    subnet_info = async_subnet_creation.result()

    # Create NIC
    async_nic_creation = network_client.network_interfaces.create_or_update(
        resource_group_name,
        nic_name,
        {
            'location': location,
            'ip_configurations': [{
                'name': ip_config_name,
                'subnet': {
                    'id': subnet_info.id
                }
            }]
        }
    )
    return async_nic_creation.result()

def create_vm(compute_client,
              resource_group_name,
              vm_name,
              vm_parameters,
              tags,
              location):
    result = compute_client.virtual_machines.create_or_update(resource_group_name,
                                                              vm_name,
                                                              vm_parameters)

    result.wait()

    # tag a vm
    vm_tag = compute_client.virtual_machines.create_or_update(resource_group_name,
                                                              vm_name,
                                                              {
                                                                  'location': location,
                                                                  'tags': tags
                                                              })

    vm_tag.wait()
