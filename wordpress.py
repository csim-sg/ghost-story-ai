import os
from typing import List
from pydantic import Field, BaseModel
import requests

wordpressAuthURL = 'https://public-api.wordpress.com/oauth2/token'

clientID = os.environ['WP_CLIENT_ID']
clientSecret = os.environ['WP_CLIENT_SECRET']

wordpressAPIURL = 'https://public-api.wordpress.com/rest/v1.1/sites/relak.la{}'

class Article(BaseModel):
  title: str = Field(title="Title")
  content: str = Field(title="Content")
  tags: List[str] = Field(title="Tags")
  categories: List[str] = Field(title="categories")

class Wordpress():

  def getWordpressToken(self):
    response = requests.post(
      wordpressAuthURL,
      data = {
        'client_id': clientID,
        'client_secret': clientSecret,
        'grant_type': 'password',
        'username': 'csimzw',
        'password': '5LH-XKnXa7_xMn+',
      }
    )
    return response.json()

  def NewArticle(self, article: Article):
    token = self.getWordpressToken()
    response = requests.post(
      wordpressAPIURL.format("/posts/new"),
      headers={
        "Authorization": "BEARER {}".format(token['access_token'])
      },
      data = {
        'title': article.title,
        'content': article.content,
        'author': 'csimzwalvin',
        'tags': ",".join(article.tags)
      }
    )
    return response



