import boto3
import pandas as pd
import json
from pkg_resources import resource_filename

# List of AWS profiles
aws_profiles = ['default', '181495356657-read', '475568831057-read', '840218642752-read', '244857349068-read']

# Initialize an empty DataFrame
df_all = pd.DataFrame()





def get_region_name(region_code):

    endpoint_file = resource_filename('botocore', 'data/endpoints.json')

    with open(endpoint_file, 'r') as f:
        endpoint_data = json.load(f)

    region_name = endpoint_data['partitions'][0]['regions'][region_code]['description']

    region_name = region_name.replace('Europe', 'EU')

    return region_name


def get_ec2_instance_hourly_price(region_code, 
                                  instance_type, 
                                  operating_system, 
                                  preinstalled_software='NA', 
                                  tenancy='Shared', 
                                  is_byol=False):
                                       
    region_name = get_region_name(region_code)

    if is_byol:
        license_model = 'Bring your own license'
    else:
        license_model = 'No License required'

    if tenancy == 'Host':
        capacity_status = 'AllocatedHost'
    else:
        capacity_status = 'Used'
    
    filters = [
        {'Type': 'TERM_MATCH', 'Field': 'termType', 'Value': 'OnDemand'},
        {'Type': 'TERM_MATCH', 'Field': 'capacitystatus', 'Value': capacity_status},
        {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': region_name},
        {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': instance_type},
        {'Type': 'TERM_MATCH', 'Field': 'tenancy', 'Value': tenancy},
        {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': operating_system},
        {'Type': 'TERM_MATCH', 'Field': 'preInstalledSw', 'Value': preinstalled_software},
        {'Type': 'TERM_MATCH', 'Field': 'licenseModel', 'Value': license_model},
    ]

    pricing_client = boto3.client('pricing', region_name='us-east-1')
    
    response = pricing_client.get_products(ServiceCode='AmazonEC2', Filters=filters)

    for price in response['PriceList']:
        price = json.loads(price)

        for on_demand in price['terms']['OnDemand'].values():
            for price_dimensions in on_demand['priceDimensions'].values():
                price_value = price_dimensions['pricePerUnit']['USD']
            
        return float(price_value)
    return None






for profile in aws_profiles:
    # Initialize the session
    session = boto3.Session(profile_name=profile, region_name='ap-east-1')

    # Initialize the EC2 and STS clients
    ec2 = session.client('ec2')
    sts = session.client('sts')

    # Get the account ID
    account_id = sts.get_caller_identity()["Account"]

    # Retrieve the instances and their tags
    instances = ec2.describe_instances()

    # Create a list of unique tag keys across all instances
    tag_keys = set()
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            if 'Tags' in instance:
                for tag in instance['Tags']:
                    tag_keys.add(tag['Key'])

    # Initialize an empty list to store the rows
    rows = []

    # Create data rows
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:

            # Assume the operating system is Linux for this example
            operating_system = 'Linux'
            
            # Get the instance type and region
            instance_type = instance['InstanceType']
            region_code = session.region_name

            # Get the instance price
            ec2_instance_price = get_ec2_instance_hourly_price(
                region_code=region_code, 
                instance_type=instance_type, 
                operating_system=operating_system,
            )

            row = {
                'Account': account_id,
                'InstanceId': instance['InstanceId'],
                'InstanceType': instance['InstanceType'],
                'State': instance['State']['Name'],
                'Zone': instance['Placement']['AvailabilityZone'],
                'PrivateIpAddress': instance['PrivateIpAddress'],
                'PrivateDnsName': instance['PrivateDnsName'],
                'PublicDnsName': instance['PublicDnsName'],
                'LaunchTime': instance['LaunchTime'].strftime('%Y-%m-%d %H:%M:%S'),
                'Estimated_Hourly_Cost': ec2_instance_price,
                'Estimated_montly_cost': ec2_instance_price * 24 * 30
            }
            

            if 'Tags' in instance:
                for tag in instance['Tags']:
                    row[tag['Key']] = tag['Value']

            rows.append(row)

    # Create a DataFrame and append it to the main DataFrame
    df = pd.DataFrame(rows)
    df_all = df_all._append(df, ignore_index=True)

# Write the DataFrame to an Excel file
df_all.to_excel('ec2_inventory_list3.xlsx', index=False)