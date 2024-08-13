import boto3
import pandas as pd
from datetime import datetime

# List of AWS profiles
aws_profiles = ['default', '181495356657-read', '475568831057-read', '840218642752-read', '244857349068-read', '005146673688-OrganizationAccountAccessRole', '373135327220-OrganizationAccountAccessRole', '270494154421-OrganizationAccountAccessRole']

# Initialize an empty DataFrame
df_all = pd.DataFrame()

for profile in aws_profiles:
    print(f"Checking profile: {profile}")
    boto3.setup_default_session(profile_name=profile)
    
    s3_client = boto3.client('s3')
    
    # Get the list of S3 buckets
    response = s3_client.list_buckets()
    
    rows = []
    
    for bucket in response['Buckets']:
        bucket_name = bucket['Name']
        
        # Get the bucket location
        bucket_location = s3_client.get_bucket_location(Bucket=bucket_name)
        region = bucket_location.get('LocationConstraint', 'us-east-1')
        
        row = {
            'Account': profile,
            'BucketName': bucket_name,
            'CreationDate': bucket['CreationDate'].strftime('%Y-%m-%d %H:%M:%S'),
            'Region': region
        }
        
        rows.append(row)
    
    # Create a DataFrame and append it to the main DataFrame
    df = pd.DataFrame(rows)
    df_all = df_all._append(df, ignore_index=True)

# Get the current date
now = datetime.now()

# Format the date as a string
date_str = now.strftime('%Y-%m-%d')

# Create the filename
filename = f"S3_inventory_list_{date_str}.xlsx"

# Write the DataFrame to an Excel file
df_all.to_excel(filename, index=False)
