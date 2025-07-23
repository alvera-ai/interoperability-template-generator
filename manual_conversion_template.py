# Manual Conversion Template for Users API to Database
# This template converts JSONPlaceholder users API response to database format

# Initialize output data
output_data = {}

# Direct field mappings
if 'id' in input_data:
    output_data['user_id'] = int(input_data['id'])

if 'name' in input_data:
    output_data['full_name'] = str(input_data['name'])

if 'username' in input_data:
    output_data['username'] = str(input_data['username'])

if 'email' in input_data:
    output_data['email'] = str(input_data['email'])

if 'phone' in input_data:
    output_data['phone'] = str(input_data['phone'])

if 'website' in input_data:
    output_data['website'] = str(input_data['website'])

# Address fields (nested object)
if 'address' in input_data and isinstance(input_data['address'], dict):
    address = input_data['address']
    
    if 'street' in address:
        output_data['street'] = str(address['street'])
    
    if 'suite' in address:
        output_data['suite'] = str(address['suite'])
    
    if 'city' in address:
        output_data['city'] = str(address['city'])
    
    if 'zipcode' in address:
        output_data['zipcode'] = str(address['zipcode'])
    
    # Geo coordinates (nested within address)
    if 'geo' in address and isinstance(address['geo'], dict):
        geo = address['geo']
        
        if 'lat' in geo:
            try:
                output_data['latitude'] = float(geo['lat'])
            except (ValueError, TypeError):
                output_data['latitude'] = None
        
        if 'lng' in geo:
            try:
                output_data['longitude'] = float(geo['lng'])
            except (ValueError, TypeError):
                output_data['longitude'] = None

# Company fields (nested object)
if 'company' in input_data and isinstance(input_data['company'], dict):
    company = input_data['company']
    
    if 'name' in company:
        output_data['company_name'] = str(company['name'])
    
    if 'catchPhrase' in company:
        output_data['company_catchphrase'] = str(company['catchPhrase'])
    
    if 'bs' in company:
        output_data['company_bs'] = str(company['bs'])

# Ensure we have required fields with defaults if missing
if 'user_id' not in output_data:
    output_data['user_id'] = 0

if 'full_name' not in output_data:
    output_data['full_name'] = 'Unknown'

if 'username' not in output_data:
    output_data['username'] = 'unknown'

if 'email' not in output_data:
    output_data['email'] = 'unknown@example.com' 