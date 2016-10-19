import os
import sys
from argparse import ArgumentParser
from cmazure import common
from cmazure.storage import account as storageaccount
from cmazure.storage import common as storagecommon
from cmazure.storage.client import StorageClient
from cmazure.credentials import AzureCredentials

import logging

root = logging.getLogger()
root.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)


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


def do_magic(args):
    def input_prefix(text, default):
        default = "%s%s" % (args.prefix, default)
        return input("%s [%s]: " % (text, default)) or default
    resource_client = make_resource_client(args)
    network_client = make_network_client(args)
    rg_name = args.rg_name or input_prefix("Resource group name: ", "rg")
    location = args.location or input("Location: ")
    common.create_resource_group(resource_client,
                                 rg_name,
                                 location)
    completed = False
    try:
        subnet_name = input_prefix("Subnet name", "subnet")
        vnet_name = input_prefix("VNet name", "vnet")
        sa_name = input_prefix("Storage account name", "sa")
        vm1_name = input_prefix("VM1 name", "vm1")
        vm2_name = input_prefix("VM2 name", "vm2")
        logging.info("Creating VNet %s and subnet %s...", vnet_name, subnet_name)
        common.create_network(network_client,
                              rg_name,
                              location,
                              vnet_name,
                              subnet_name)
        logging.info("Creating storage account  %s...", sa_name)
        storageaccount.create_account(
            storagecommon.make_storage_client(make_credentials(args)),
            rg_name,
            sa_name,
            location)
        logging.info("Creating vm1 %s...", vm1_name)
        completed = True
    finally:
        if not completed:
            common.remove_resource_group(resource_client, rg_name)


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
    parser.add_argument("-l", "--location",
                        help="Target location",
                        default="westus")

    list_locations_parser = subparsers.add_parser("list-locations", help="List azure locations")

    def list_locations(args):
        for location in common.locations(make_resource_client(args)):
            print("{key}".format(**location))
    list_locations_parser.set_defaults(func=list_locations)

    create_resource_group_parser = subparsers.add_parser("create-rg", help="Create resource group")

    def create_resource_group(args):
        return common.create_resource_group(
            make_resource_client(args),
            args.rg_name,
            args.location,
        )
    create_resource_group_parser.set_defaults(func=create_resource_group)

    remove_resource_group_parser = subparsers.add_parser("remove-rg", help="Remove resource group")

    def remove_resource_group(args):
        return common.remove_resource_group(
            make_resource_client(args),
            args.rg_name,
        )
    remove_resource_group_parser.set_defaults(func=remove_resource_group)

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
        "vm_name",
        help="Node name"
    )
    create_vm_parser.add_argument(
        "storage_acc",
        help="Storage account name"
    )
    create_vm_parser.add_argument(
        "disk_name",
        help="Disk name"
    )
    create_vm_parser.add_argument(
        "vnet",
        help="vnet name"
    )
    create_vm_parser.add_argument(
        "subnet",
        help="subnet name"
    )


    def make_compute_client(args):
        return common.make_compute_client(make_credentials(args))

    def create_compute_node(args):
        resource_client = make_resource_client(args)
        compute_client = make_compute_client(args)
        network_client = make_network_client(args)
        storage_client = storagecommon.make_storage_client(make_credentials(args))

        common.create_compute_node(resource_client,
                                   compute_client,
                                   network_client,
                                   storage_client,
                                   args.rg_name,
                                   args.location,
                                   args.storage_acc,
                                   args.vm_name,
                                   args.disk_name,
                                   args.vnet,
                                   args.subnet)

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
                                             args.location)

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

    do_magic_parser = subparsers.add_parser("do-magic", help="ABRA KADABRA")
    do_magic_parser.add_argument(
        "prefix",
        help="Name prefix"
    )
    do_magic_parser.set_defaults(func=do_magic)

    create_resource_group_parser.set_defaults(func=create_resource_group)

    create_net_parser = subparsers.add_parser("create-net", help="Create subnet and VNet")
    create_net_parser.add_argument(
        "prefix",
        help="Name prefix"
    )
    create_net_parser.add_argument(
        "--vnet-name",
        help="VNet name. Default prefixvnet"
    )
    create_net_parser.add_argument(
        "--subnet-name",
        help="Subnet name. Default prefixsubnet"
    )

    def create_net(args):
        common.create_network(
            network_client=make_network_client(args),
            location=args.location,
            resource_group_name=args.rg_name,
            vnet_name=args.vnet_name or args.prefix + "vnet",
            subnet_name=args.subnet_name or args.prefix + "subnet",
        )
    create_net_parser.set_defaults(func=create_net)

    list_net_parser = subparsers.add_parser("list-net", help="List networks")

    def list_net(args):
        for vnet, subnet in common.networks(make_network_client(args), args.rg_name):
            print("{0.name}\t{1.name}".format(vnet, subnet))
    list_net_parser.set_defaults(func=list_net)

    def upload(args):
       account = storagecommon.make_cloud_storage_account(args.account_name,
                                                          args.account_key,
                                                          args.sas_token)
       return StorageClient(account).upload(args.share_name, args.file)

    upload_parser = subparsers.add_parser(
        "upload", help="Upload file to storage account")
    upload_parser.add_argument("-a", "--account-name", help="Storage account name",
                               default=os.environ.get("AZURE_STORAGE_ACCOUNT_NAME"))
    upload_parser.add_argument("-k", "--account-key", help="Storage account key",
                               default=os.environ.get("AZURE_STORAGE_ACCOUNT_KEY"))
    upload_parser.add_argument("-t", "--sas-token", help="SAS token",
                               default=os.environ.get("AZURE_STORAGE_SAS_TOKEN"))
    upload_parser.add_argument("-s", "--share-name", help="Share name")
    upload_parser.add_argument("file", help="File to upload")
    upload_parser.set_defaults(func=upload)

    def download(args):
       account = storagecommon.make_cloud_storage_account(args.account_name,
                                                          args.account_key,
                                                          args.sas_token)
       return StorageClient(account).download(args.share_name, args.file)

    download_parser = subparsers.add_parser(
        "download", help="download file to storage account")
    download_parser.add_argument("-a", "--account-name", help="Storage account name",
                                 default=os.environ.get("AZURE_STORAGE_ACCOUNT_NAME"))
    download_parser.add_argument("-k", "--account-key", help="Storage account key",
                                 default=os.environ.get("AZURE_STORAGE_ACCOUNT_KEY"))
    download_parser.add_argument("-t", "--sas-token", help="SAS token",
                                 default=os.environ.get("AZURE_STORAGE_SAS_TOKEN"))
    download_parser.add_argument("-s", "--share-name", help="Share name")
    download_parser.add_argument("file", help="File to download")
    download_parser.set_defaults(func=download)

    args = parser.parse_args()
    args.func(args)

    # try:
    #     args.func(args)
    # except AttributeError:
    #     parser.print_help()
