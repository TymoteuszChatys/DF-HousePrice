import pandas as pd

def clean_type(zoopla_df):
    zoopla_clean = zoopla_df.copy()
    #Remove words and all numbers from the title so we get only the property type 
    zoopla_clean['title'] = zoopla_clean['title'].str.replace('for sale','')
    zoopla_clean['title'] = zoopla_clean['title'].str.replace('bed','')
    zoopla_clean['title'] = zoopla_clean['title'].str.replace('house','')
    zoopla_clean['title'] = zoopla_clean['title'].str.replace('\d+','', regex=True)
    #Remove trailing spaces etc...
    zoopla_clean['title'] = zoopla_clean['title'].str.strip()
    #Everything lower case
    zoopla_clean['title'] = zoopla_clean['title'].apply(lambda x: x.lower())

    #Define the properties to keep for analysis
    property_types_to_keep = ["flat","terraced","semi-detached","detached","end terrace"]
    zoopla_clean = zoopla_clean[zoopla_clean['title'].isin(property_types_to_keep)]

    #Change name of column
    zoopla_clean = zoopla_clean.rename({'title': 'type'}, axis='columns')

    return zoopla_clean

def clean_price(zoopla_df):
    zoopla_clean = zoopla_df.copy()
    #Clean the price column and change it to a numeric type
    zoopla_clean['price'] = zoopla_clean['price'].str.replace('£','')
    zoopla_clean['price'] = zoopla_clean['price'].str.replace(',','')
    #Drop the row if we can not convert to a numeric type. This normally means that the property is POA (Price on application)
    zoopla_clean['price'] = pd.to_numeric(zoopla_clean['price'], errors='coerce')
    zoopla_clean = zoopla_clean.dropna()

    return zoopla_clean

def get_dist_to_station(zoopla_df):
    zoopla_clean = zoopla_df.copy()
    #Remove all alphabetic entries from the station column -> to extract only the distance to the station from the property
    zoopla_clean['station'] = zoopla_clean['station'].str.replace('[a-zA-z]+','',regex=True)
    zoopla_clean['station'] = pd.to_numeric(zoopla_clean['station'], errors='coerce')

    return zoopla_clean

def clean_address(zoopla_df):
    zoopla_clean = zoopla_df.copy()

    zoopla_clean['address'] = zoopla_clean['address'].str.rsplit(',').str[-1]
    zoopla_clean['post_code']=zoopla_clean['address'].apply(lambda x: x.split(" ")[-1])
    zoopla_clean['location']=zoopla_clean['address'].apply(lambda x: ''.join(x.split(' ')[:-1]))
    zoopla_clean['location'] = zoopla_clean['location'].str.replace('[^A-Za-z0-9]+','',regex=True)
    zoopla_clean['location'] = zoopla_clean['location'].str.replace('Greater','',regex=True)
    zoopla_clean['location'] = zoopla_clean['location'].apply(lambda x: x.lower())
    zoopla_clean = zoopla_clean.drop(columns="address")
    
    loc_counts = zoopla_clean['location'].value_counts()
    pc_counts = zoopla_clean['post_code'].value_counts()

    zoopla_clean = zoopla_clean[~zoopla_clean['location'].isin(loc_counts[loc_counts < 25].index)]
    zoopla_clean = zoopla_clean[~zoopla_clean['post_code'].isin(pc_counts[pc_counts < 5].index)]


    return zoopla_clean

def remove_outliers(zoopla_df):
    zoopla_clean = zoopla_df.copy()

    zoopla_clean['beds'] = pd.to_numeric(zoopla_clean['beds'], errors='coerce')
    zoopla_clean['baths'] = pd.to_numeric(zoopla_clean['baths'], errors='coerce')
    zoopla_clean['receptions'] = pd.to_numeric(zoopla_clean['receptions'], errors='coerce')

    zoopla_clean = zoopla_clean.drop(zoopla_clean[zoopla_clean['beds'] > 5].index)
    zoopla_clean = zoopla_clean.drop(zoopla_clean[zoopla_clean['baths'] > 5].index)
    zoopla_clean = zoopla_clean.drop(zoopla_clean[zoopla_clean['receptions'] > 5].index)
    zoopla_clean = zoopla_clean.drop(zoopla_clean[zoopla_clean['price'] < 100000].index)

    return zoopla_clean


def drop_duplicates(zoopla_df):
    zoopla_clean = zoopla_df.copy()

    zoopla_clean.drop_duplicates(ignore_index=True)

    return zoopla_clean