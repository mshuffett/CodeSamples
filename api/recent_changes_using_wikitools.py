from wikitools import wiki
from wikitools import api
from wikitools import page
# site = wiki.Wiki("http://en.wikipedia.org/w/api.php")
site = wiki.Wiki("http://es.wikipedia.org/w/api.php")
# define the params for the query
params = {
    'action': 'query',
    'list': 'recentchanges',
    'rcstart': '2012-08-25T04:41:39Z',  # has to be later then rcend
    'rcend': '2012-08-25T03:40:39Z',
    # 'generator': 'search',
    # 'gsrsearch': 'hadron'
    # 'gsrlimit': 50
    # 'srlimit': '50'
    'rclimit': 'max'
}
#  API
request = api.APIRequest(site, params)
# query the API
result = request.query(querycontinue=False)
print(page.Page(site, pageid=result['query']['recentchanges'][0]['pageid']).getWikiText())
