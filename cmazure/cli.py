import os
from argparse import ArgumentParser
from cmazure import common
from cmazure.storage import account as storageaccount
from cmazure.storage import common as storagecommon
from cmazure.storage.client import StorageClient
from cmazure.credentials import AzureCredentials


def main():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(help="SUBPARSERS_HELP")
    parser.add_argument("--client",
                        help="Azure client ID. Default: env AZURE_CLIENT_ID",
                        default=os.environ.get("AZURE_CLIENT_ID"))
    parser.add_argument("--secret",
                        help="Azure client secret. Default: env AZURE_CLIENT_SECRET",
                        default=os.environ.get("AZURE_CLIENT_SECRET"))
    parser.add_argument("--tenant",
                        help="Azure tenant ID. Default: env AZURE_TENANT_ID",
                        default=os.environ.get("AZURE_TENANT_ID"))
    parser.add_argument("--subscription-id",
                        help="Azure subscription ID. Default: env AZURE_SUBSCRIPTION_ID",
                        default=os.environ.get("AZURE_SUBSCRIPTION_ID"))
    parser.add_argument("-g", "--rg-name",
                        help="Resource group name")
    parser.add_argument("-r", "--region",
                        help="Target region",
                        default="westus")

    def make_credentials(args):
        return AzureCredentials(
            client_id=args.client,
            secret=args.secret,
            tenant=args.tenant,
            subscription_id=args.subscription_id
        )

    def make_resource_client(args):
        return common.make_resource_client(make_credentials(args))

    def make_network_client(args):
        return common.make_network_client(make_credentials(args))

    list_regions_parser = subparsers.add_parser("list-regions", help="List azure regions")

    def list_regions(args):
        for region in common.regions(make_resource_client(args)):
            print("{key}".format(**region))
    list_regions_parser.set_defaults(func=list_regions)

    create_resource_group_parser = subparsers.add_parser("create-rg", help="Create resource group")

    def create_resource_group(args):
        return common.create_resource_group(
            make_resource_client(args),
            args.rg_name,
            args.region,
        )
    create_resource_group_parser.set_defaults(func=create_resource_group)

    create_director_parser = subparsers.add_parser("create-director", help="Create Cloud Director")
    create_director_parser.add_argument(
        "vm-name",
        help="Director name"
    )
    create_director_parser.add_argument(
        "--flavor",
        help="Director's flavor"
    )

    def create_director(args):
        common.create_director(
            make_resource_client(args),
            args.rg_name,
            args.vm_name
        )
    create_director_parser.set_defaults(func=create_director)

    create_vm_parser = subparsers.add_parser("create-vm", help="Create VM")
    create_vm_parser.add_argument(
        "location",
        help="Node location"
    )
    create_vm_parser.add_argument(
        "resource_group",
        help="Target resource group"
    )
    create_vm_parser.add_argument(
        "vm_name",
        help="Node name"
    )
    create_vm_parser.add_argument(
        "disk_name",
        help="Disk name"
    )
    create_vm_parser.add_argument(
        "nic_id",
        help="NIC id"
    )
    create_vm_parser.add_argument(
        "storage_acc",
        help="Storage account name"
    )


    def make_compute_client(args):
        return common.make_compute_client(make_credentials(args))

    def create_compute_node(args):
        common.create_vm(
            make_compute_client(args),
            args.rg_name,
            args.vm_name,
            {
                'who-rocks': 'python',
                'where': 'on azure'
            },
            args.location,
            common.create_vm_parameters(args.location,
                                        args.vm_name,
                                        "matilda",
                                        "l8Uccc",
                                        args.disk_name,
                                        args.nic_id,
                                        args.storage_acc)
        )
    create_vm_parser.set_defaults(func=create_compute_node)

    create_volume_parser = subparsers.add_parser("create-volume", help="Create volume")
    create_volume_parser.add_argument(
        "name",
        help="Volume name"
    )

    create_storage_account_parser = subparsers.add_parser(
        "create-storage-account", help="Create Storage Account")
    create_storage_account_parser.add_argument("name", help="Account name")

    def create_storage_account(args):
        return storageaccount.create_account(storagecommon.make_storage_client(make_credentials(args)),
                                             args.rg_name,
                                             args.name,
                                             args.region)

    create_storage_account_parser.set_defaults(func=create_storage_account)

    def create_volume(args):
        common.create_volume(
            make_resource_client(args),
            args.rg_name,
            args.name
        )
    create_volume_parser.set_defaults(func=create_compute_node)

    list_resource_groups_parser = subparsers.add_parser("list-rg", help="List resource groups")

    def list_resource_groups(args):
        common.list_resource_groups(
            make_resource_client(args),
        )
    list_resource_groups_parser.set_defaults(func=list_resource_groups)

    create_resource_group_parser.set_defaults(func=create_resource_group)

    create_nic_parser = subparsers.add_parser("create-nic", help="Create NIC")
    create_nic_parser.add_argument(
        "region",
        help="Region"
    )
    create_nic_parser.add_argument(
        "nic_name",
        help="NIC name"
    )
    create_nic_parser.add_argument(
        "--vnet-name",
        help="VNet name. Default nicnamevnet"
    )
    create_nic_parser.add_argument(
        "--subnet-name",
        help="Subnet name. Default nicnamesubnet"
    )
    create_nic_parser.add_argument(
        "--ipconfig-name",
        help="IP Config name. Default nicnameipconfig"
    )

    def create_nic(args):
        common.create_nic(
            network_client=make_network_client(args),
            location=args.region,
            resource_group_name=args.rg_name,
            nic_name=args.nic_name,
            vnet_name=args.vnet_name or args.nic_name + "vnet",
            subnet_name=args.subnet_name or args.nic_name + "subnet",
            ip_config_name=args.ipconfig_name or args.nic_name + "ipconfig"
        )
    create_nic_parser.set_defaults(func=create_nic)

    def upload(args):
       storage_client = storagecommon.make_storage_client(make_credentials(args))
       account = storageaccount.get_account(storage_client, args.rg_name, args.account_name)
       return StorageClient(account).mkdir("/home/oleksandr")

    upload_parser = subparsers.add_parser(
        "upload", help="Upload file to storage account")
    upload_parser.add_argument("account_name", help="Storage account name",
                               default=os.environ.get("AZURE_STORAGE_ACCOUNT"))
    upload_parser.add_argument("file", help="File to upload")
    upload_parser.set_defaults(func=upload)

    args = parser.parse_args()
    args.func(args)
