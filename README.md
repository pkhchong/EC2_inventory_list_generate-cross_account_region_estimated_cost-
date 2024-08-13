# EC2_inventory_list_generate
setup aws credential with different profile
```
vi .aws/credential
```
if you have to assume different account role. your aws credential would be simliar with this
```
[181xxxxxxxxx7-read]
role_arn = arn:aws:iam::181xxxxxxxxxx:role/ReadOnlyFull
source_profile = default

[4755xxxxxxxxx7-read]
role_arn = arn:aws:iam::4755xxxxxxxxxxx:role/ReadOnlyFull
source_profile = default

[84xxxxxxxxxxx-read]
role_arn = arn:aws:iam::840xxxxxxxxxx:role/ReadOnlyFull
source_profile = default

[2448xxxxxxxxxx-read]
role_arn = arn:aws:iam::2448xxxxxx:role/ReadOnlyFull
source_profile = default

[default]
aws_access_key_id = AKIAWxxxxxxxxxxxxxxxx
aws_secret_access_key = MBXxxxxxxxxxxxxxxxxxxxxxxxxxxx

```

after that you may also update list of AWS profiles in generate_EC2_inventory_list_with_prices.py
```
aws_profiles = ['default', '18149xxxxxxxxxx-read', '4755xxxxxxxxxxxxxx-read', '8402xxxxxxxxxxxxx-read', '2448xxxxxxxxxxxxx-read']
```


install depandancy for python
```
pip install pandas
pip install openpyxl
pip install boto3
```

run the EC2 inventory list generate, it took around 3mins for generate the list(since it have to get the price list for each instance)
```
python3 generate_EC2_inventory_list_with_prices.py
```
