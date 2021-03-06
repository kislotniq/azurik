import re

from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from msrestazure.azure_exceptions import CloudError
from azure.mgmt.compute import ComputeManagementClient


VM_REFERENCE = {
    'linux': {
        'publisher': 'Canonical',
        'offer': 'UbuntuServer',
        'sku': '16.04.0-LTS',
        'version': 'latest'
    },
    'windows': {
        'publisher': 'MicrosoftWindowsServerEssentials',
        'offer': 'WindowsServerEssentials',
        'sku': 'WindowsServerEssentials',
        'version': 'latest'
    }
}


def make_compute_client(credentials):
    return ComputeManagementClient(
        credentials.get_service_principal(),
        credentials.subscription_id
    )


def create_resource_group(resource_client, name, location):
    return resource_client.resource_groups.create_or_update(name,
                                                            {
                                                                'location' : location
                                                            })

def create_vm_parameters(location,
                         vm_name,
                         admin_username,
                         admin_password,
                         storage_account_name,
                         os_disk_name,
                         nic_id):
    vm_reference = VM_REFERENCE['linux']
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


def create_network(network_client,
                   resource_group_name,
                   location,
                   vnet_name,
                   subnet_name):
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
    return async_subnet_creation.result()


def networks(network_client, rg_name):
    for vnet in network_client.virtual_networks.list(rg_name):
        for subnet in network_client.subnets.list(rg_name, vnet.name):
            yield (vnet, subnet)


def create_vm(compute_client,
              resource_group_name,
              vm_name,
              tags,
              location,
              vm_parameters):
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


def remove_resource_group(resource_client, resource_group_name):
    resource_client.resource_groups.delete(resource_group_name).wait()


def make_resource_client(credentials):
    return ResourceManagementClient(
        credentials.get_service_principal(),
        credentials.subscription_id
    )


def make_network_client(credentials):
    return NetworkManagementClient(
        credentials.get_service_principal(),
        credentials.subscription_id
    )


def locations(resource_client):
    try:
        create_resource_group(resource_client, "wefewf", "wefewf")
    except CloudError as excp:
        message = str(excp)
        return (
            {"key": key} for key in
            re.search("List of available locations is '([^']+)'", message).group(1).split(",")
        )

def create_nic(network_client,
               rg_name,
               location,
               vnet_name,
               subnet_name,
               nic_name,
               ip_config_name):
    """Create a Network Interface for a VM.
    """
    vnet, subnet = next(((vnet, subnet) for vnet, subnet in networks(network_client, rg_name)
                         if vnet.name == vnet_name and subnet.name == subnet.name),
                        (None, None))
    if vnet is None or subnet is None:
        raise Exception("Could not find a subnet %s in VNet %s by location %s:",
                        subnet_name, vnet_name, location)

    # Create NIC
    async_nic_creation = network_client.network_interfaces.create_or_update(
        rg_name,
        nic_name,
        {
            'location': location,
            'ip_configurations': [{
                'name': ip_config_name,
                'subnet': {
                    'id': subnet.id
                }
            }]
        }
    )
    return async_nic_creation.result()

def create_compute_node(resource_client,
                        compute_client,
                        network_client,
                        storage_client,
                        rg_name,
                        location,
                        storage_acc_name,
                        vm_name,
                        disk_name,
                        vnet,
                        subnet):

    create_vm(
        compute_client,
        rg_name,
        vm_name,
        {
            'who-rocks': 'python',
            'where': 'on azure'
        },
        location,
        create_vm_parameters(
            location,
            vm_name,
            "matilda",
            "l8Uccc",
            storage_acc_name,
            disk_name,
            create_nic(
                network_client,
                rg_name,
                location,
                vnet,
                subnet,
                vm_name + 'nic',
                vm_name + 'ipconfig'
            ).id
        )
    )
