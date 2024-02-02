import boto3
import json
from pkg_resources import resource_filename

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


if __name__ == "__main__":
    region_code = 'ap-south-1'
    instance_type = 't2.micro'
    operating_system = 'Linux'


    ec2_instance_price = get_ec2_instance_hourly_price(
        region_code=region_code, 
        instance_type=instance_type, 
        operating_system=operating_system,
    )

    print(instance_type, operating_system, region_code)
    print(ec2_instance_price)