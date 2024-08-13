import boto3
import pandas as pd
from datetime import datetime
from botocore.exceptions import ClientError, NoCredentialsError

# List of AWS profiles
aws_profiles = ['default', '181495356657-read', '475568831057-read', '840218642752-read', '244857349068-read', '005146673688-OrganizationAccountAccessRole', '373135327220-OrganizationAccountAccessRole', '270494154421-OrganizationAccountAccessRole']

# List of AWS regions to use
aws_regions = ['ap-east-1', 'us-east-1']

# Initialize an empty DataFrame
df_all = pd.DataFrame()

for profile in aws_profiles:
    print(f"Checking profile: {profile}")
    session = boto3.Session(profile_name=profile)
    
    for region in aws_regions:
        print(f"Checking region: {region} for profile: {profile}")
        try:
            efs_client = session.client('efs', region_name=region)
            
            try:
                # Get the list of EFS file systems
                response = efs_client.describe_file_systems()
                
                rows = []
                
                for file_system in response['FileSystems']:
                    row = {
                        'Account': profile,
                        'FileSystemId': file_system['FileSystemId'],
                        'CreationTime': file_system['CreationTime'].strftime('%Y-%m-%d %H:%M:%S'),
                        'Region': region,
                        'LifeCycleState': file_system['LifeCycleState'],
                        'NumberOfMountTargets': file_system['NumberOfMountTargets'],
                        'SizeInBytes': file_system['SizeInBytes']['Value']
                    }
                    
                    rows.append(row)
                
                # Create a DataFrame and append it to the main DataFrame
                df = pd.DataFrame(rows)
                df_all = pd.concat([df_all, df], ignore_index=True)
            
            except ClientError as e:
                print(f"Error describing file systems in region {region}: {e}")
        
        except (ClientError, NoCredentialsError) as e:
            print(f"Failed to create EFS client for region {region} and profile {profile}: {e}")

# Get the current date
now = datetime.now()

# Format the date as a string
date_str = now.strftime('%Y-%m-%d')

# Create the filename
filename = f"EFS_inventory_list_{date_str}.xlsx"

# Write the DataFrame to an Excel file
df_all.to_excel(filename, index=False)
