from urllib.request import urlopen
from bs4 import BeautifulSoup
import json
import datetime
import pprint
import sys
pp= pprint.PrettyPrinter(indent=4)
def main():
    current_year = int(datetime.datetime.now().year)
    for year in range(1898, current_year + 1):
        sys.stdout = open( 'DataSets//IMDB_Top_50_' + str( year ) + '.json', 'w' )
        url = "http://www.imdb.com/search/title?release_date=" + str(year) + "," + str(year)+ "&title_type =feature"
        html = urlopen(url)
        soup = BeautifulSoup(html.read(), features = "html.parser")
        dataset_top50 = {}
        id =1
        movies_list = soup.findAll('div', attrs = {'class': 'lister-item-content'})
        for each in movies_list:
            movie_item = {
                'name': '',
                'certificate': '',
                'runtime': '',
                'genre': '',
                'description': '',
                'director': '',
                'stars': []
            }
            if each.find('h3', attrs= {'class': 'lister-item-header'}).find('a').text:
                name_value = each.find('h3', attrs= {'class': 'lister-item-header'}).find('a').text.strip()
                movie_item['name'] = name_value

            p_list = each.findAll('p')

            if p_list[0]:
                if p_list[0].find('span', attrs = {'class': 'certificate'}):
                    certificate_value = p_list[0].find('span', attrs = {'class': 'certificate'}).text.strip()
                    movie_item['certificate'] = certificate_value
                if p_list[0].find('span', attrs = {'class': 'runtime'}):
                    runtime_value = p_list[0].find('span', attrs = {'class': 'runtime'}).text.strip()
                    movie_item['runttime'] = runtime_value
                if p_list[0].find('span', attrs = {'class': 'genre'}):
                    genre_value = p_list[0].find('span', attrs = {'class': 'genre'}).text.strip()
                    movie_item['genre'] = genre_value
            if p_list[1]:
                description_value = p_list[1].text.strip()
                movie_item['description'] = description_value

            dataset_top50[id] = movie_item
            id +=1

        pp.pprint(dataset_top50)
        print(json.dumps(dataset_top50, indent=4))
main()




