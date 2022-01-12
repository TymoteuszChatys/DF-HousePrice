import pandas as pd
import requests
from bs4 import BeautifulSoup


def get_post_code_data(df):
    pc_list = df['post_code'].to_list()

    unique_pcs = set()
    for x in pc_list:
        unique_pcs.add(x)

    unique_pcs = list(unique_pcs)
    print(f"{len(unique_pcs)} unique post codes")

    codes = []
    average_prices = []
    detached = []
    semi_detached = []
    terraced = []
    flat = []

    for post_code in unique_pcs:
        try:
            avg_link = f"https://www.zoopla.co.uk/house-prices/browse/{post_code}/?q={post_code}&search_source=house-prices"
            soup = BeautifulSoup(requests.get(avg_link).content, features="html.parser")

            all = soup.find("span", {"class":"market-panel-stat-element-value js-market-stats-average-price"})["data-value-all"]
            s = soup.find("span", {"class":"market-panel-stat-element-value js-market-stats-average-price"})["data-value-s"]
            t = soup.find("span", {"class":"market-panel-stat-element-value js-market-stats-average-price"})["data-value-t"]
            f = soup.find("span", {"class":"market-panel-stat-element-value js-market-stats-average-price"})["data-value-f"]
            d = soup.find("span", {"class":"market-panel-stat-element-value js-market-stats-average-price"})["data-value-d"]

            arrays = [all,s,t,f,d]

            prices_array = []


            for type in arrays:
                bb = []
                for s in type.split(','):
                    try:
                        number = int(s)
                    except:
                        number = 0
                    bb.append(number)

                #3m,6m,12m,5y,10y,20y  ---> 2 = last year
                prices_array.append(bb[2])

            #prices_array #all, semi, terraced, flat, detached
            average_prices.append(prices_array[0])
            detached.append(prices_array[4])
            semi_detached.append(prices_array[1])
            terraced.append(prices_array[2])
            flat.append(prices_array[3])
            codes.append(post_code)
        except:
            print(f"Error - {post_code}")

    average_list = pd.DataFrame(
        {'post_code': codes,
        'avg_sold_price_12months': average_prices,
        'detached_12months': detached,
        'semi_detached_12months': semi_detached,
        'terraced_12months': terraced,
        'flat_12months': flat,
        })


    #Drop the row if we can not convert to a numeric type. This normally means that the property is POA (avg_sold_price_12months on application)
    #average_list['avg_sold_price_12months'] = pd.to_numeric(average_list['avg_sold_price_12months'], errors='coerce')
    #average_list['detached_12months'] = pd.to_numeric(average_list['detached_12months'], errors='coerce')
    #average_list['semi_detached_12months'] = pd.to_numeric(average_list['semi_detached_12months'], errors='coerce')
    #average_list['terraced_12months'] = pd.to_numeric(average_list['terraced_12months'], errors='coerce')
    #average_list['flat_12months'] = pd.to_numeric(average_list['flat_12months'], errors='coerce')

    return average_list


def get_house_data(url):
    df = pd.DataFrame()
    pages = 1
    numbers = []

    soup = BeautifulSoup(requests.get(url + "&pn=1").content, features="html.parser")
    page_buttons = soup.findAll("a", {"class":"eaoxhri5 css-xtzp5a-ButtonLink-Button-StyledPaginationLink eaqu47p1"})
    for num in page_buttons:
        try:
            numbers.append(int(num.text))
        except:
            pass

    number_of_pages = max(numbers)

    error_count = 0
    for i in range(number_of_pages):
        try:
            soup = BeautifulSoup(requests.get(url + "&pn=" + str(i)).content, features="html.parser")
            items = soup.find("div", {"class":"css-1anhqz4-ListingsContainer earci3d2"})

            index = 1

            for listing in items.select('div[data-testid*="search-result_listing"]'):
                try:

                    title = listing.find("h2", {"data-testid":"listing-title"}).text
                    address = listing.find("p", {"data-testid":"listing-description"}).text
                    price = listing.find("p", {"size":"6"}).text
                    station = listing.find("p", {"class":"css-nwapgq-Text eczcs4p0", "data-testid":"text"}).text
                    
                    home_info = listing.findAll("p", {"class":"css-r8a2xt-Text eczcs4p0", "data-testid":"text"})
                    
                    #print(len(home_info))
                    
                    beds = 0
                    baths = 0
                    receptions = 0

                    if (len(home_info) == 3):
                        beds = home_info[0].text
                        baths = home_info[1].text
                        receptions = home_info[2].text
                    elif (len(home_info) == 2):
                        beds = home_info[0].text
                        baths = home_info[1].text
                    else:
                        beds = home_info[0].text

                    new_data = {'title':title, 'address':address, 'price':price, 'station':station, 'beds':beds, 'baths':baths, 'receptions':receptions}
                    df = df.append(new_data,ignore_index=True)

                except:
                    error_count += 1
         
                #print(index)
                #print(f"{index} - {title}")
                #print(f"Address: {address}")
                #print(f"Price: {price}")
                #print(f"Station: {station}")


                #print(listing.find("div", {"data-testid":"listing-transport"}).contents)
            
                index +=1
        except:
            error_count += 25
            print(f"Invalid page {i}")
    

    print(f"Error count: {error_count}")
    return df