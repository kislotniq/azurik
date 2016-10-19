import os
from argparse import ArgumentParser
from cmazure import common
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

    def make_credentials(args):
        return AzureCredentials(
            client_id=args.client,
            secret=args.secret,
            tenant=args.tenant,
            subscription_id=args.subscription_id
        )

    def make_resource_client(args):
        return common.make_resource_client(make_credentials(args))

    list_regions_parser = subparsers.add_parser("list-regions", help="List azure regions")

    def list_regions(args):
        for region in common.regions(make_resource_client(args)):
            print("{key}".format(**region))
    list_regions_parser.set_defaults(func=list_regions)

    create_resource_group_parser = subparsers.add_parser("create-rg", help="Create resource group")
    create_resource_group_parser.add_argument(
        "rg_name",
        help="Resource group name"
    )
    create_resource_group_parser.add_argument(
        "region",
        help="Target region"
    )

    def create_resource_group(args):
        common.create_resource_group(
            make_resource_client(args),
            args.rg_name,
            args.region,
        )
    create_resource_group_parser.set_defaults(func=create_resource_group)

    create_director_parser = subparsers.add_parser("create-director", help="Create Cloud Director")
    create_director_parser.add_argument(
        "resource-group",
        help="Target resource group"
    )
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
            args.resource_group,
            args.vm_name
        )
    create_director_parser.set_defaults(func=create_director)

    create_compute_node_parser = subparsers.add_parser("launch-inst", help="Launch instance")
    create_compute_node_parser.add_argument(
        "resource-group",
        help="Target resource group"
    )
    create_compute_node_parser.add_argument(
        "vm-name",
        help="Node name"
    )
    create_compute_node_parser.add_argument(
        "--flavor",
        help="Director's flavor"
    )

    def create_compute_node(args):
        common.create_compute_node(
            make_resource_client(args),
            args.resource_group,
            args.vm_name
        )
    create_compute_node_parser.set_defaults(func=create_compute_node)

    create_volume_parser = subparsers.add_parser("create-volume", help="Create volume")
    create_volume_parser.add_argument(
        "resource-group",
        help="Target resource group"
    )
    create_volume_parser.add_argument(
        "name",
        help="Volume name"
    )

    def create_volume(args):
        common.create_volume(
            make_resource_client(args),
            args.resource_group,
            args.name
        )
    create_volume_parser.set_defaults(func=create_compute_node)

    list_resource_groups_parser = subparsers.add_parser("list-rg", help="List resource groups")

    def list_resource_groups(args):
        common.list_resource_groups(
            make_resource_client(args),
        )
    list_resource_groups_parser.set_defaults(func=list_resource_groups)

    args = parser.parse_args()
    args.func(args)
