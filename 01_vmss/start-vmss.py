"""
Azure Automation documentation : https://aka.ms/azure-automation-python-documentation
Azure Python SDK documentation : https://aka.ms/azure-python-sdk
"""

import automationassets
import sys
from msrestazure.azure_cloud import AZURE_PUBLIC_CLOUD
from azure.mgmt.compute import ComputeManagementClient

# Function Def
def get_automation_runas_credential(runas_connection, resource_url, authority_url ):
    """ Returns credentials to authenticate against Azure resoruce manager """
    from OpenSSL import crypto
    from msrestazure import azure_active_directory
    import adal

    # Get the Azure Automation RunAs service principal certificate
    cert = automationassets.get_automation_certificate("AzureRunAsCertificate")
    pks12_cert = crypto.load_pkcs12(cert)
    pem_pkey = crypto.dump_privatekey(crypto.FILETYPE_PEM, pks12_cert.get_privatekey())

    # Get run as connection information for the Azure Automation service principal
    application_id = runas_connection["ApplicationId"]
    thumbprint = runas_connection["CertificateThumbprint"]
    tenant_id = runas_connection["TenantId"]

    # Authenticate with service principal certificate
    authority_full_url = (authority_url + '/' + tenant_id)
    context = adal.AuthenticationContext(authority_full_url)
    return azure_active_directory.AdalAuthentication(
        lambda: context.acquire_token_with_client_certificate(
            resource_url,
            application_id,
            pem_pkey,
            thumbprint)
    )

def start_vmss(compute_client, resource_group, vmss_name):
    print('\n' + vmss_name)
    async_vmss_start = compute_client.virtual_machine_scale_sets.start(resource_group, vmss_name)
    async_vmss_start.wait()

# Authenticate to Azure using the Azure Automation RunAs service principal
runas_connection = automationassets.get_automation_connection("AzureRunAsConnection")
resource_url = AZURE_PUBLIC_CLOUD.endpoints.active_directory_resource_id
authority_url = AZURE_PUBLIC_CLOUD.endpoints.active_directory
resourceManager_url = AZURE_PUBLIC_CLOUD.endpoints.resource_manager
azure_credential = get_automation_runas_credential(runas_connection, resource_url, authority_url)

# Compute client
compute_client = ComputeManagementClient(azure_credential, str(runas_connection["SubscriptionId"]))

# Constructing the VMSS resource group name from the cluster's RG/cluster/location names.
cluster_rg_name = str(sys.argv[0])
cluster_name = str(sys.argv[1])
cluster_location = str(sys.argv[2])
mc_rg_name = 'MC_' + cluster_rg_name + '_' + cluster_name + '_' + cluster_location

# Get VMSS list
vmss_list = compute_client.virtual_machine_scale_sets.list(mc_rg_name)

# Start VMSS
for vmss in vmss_list
	start_vmss(compute_client, mc_rg_name, vmss)
