from typing import List
from pydantic import Field, BaseModel
import requests
import os



wordpressAuthURL = 'https://public-api.wordpress.com/oauth2/token'

clientID = os.environ['WP_CLIENT_ID']
clientSecret = os.environ['WP_CLIENT_SECRET']
username = os.environ['WP_USERNAME']
password = os.environ['WP_PASSWORD']
blogDomain = os.environ['WP_DOMAIN']

wordpressAPIURL = f'https://public-api.wordpress.com/rest/v1.1/{blogDomain}/'

class Article(BaseModel):
  title: str = Field(title="Title")
  content: str = Field(title="Content", description="string in HTML format")
  tags: List[str] = Field(title="Tags")
  categories: List[str] = Field(title="categories")
  featureImageURL: str = Field(title="image_url")
  featureImageTitle: str = Field(title="featureImageTitle")
  featureImageDescription: str = Field(title="image_description")

class Wordpress():

  def getWordpressToken(self):
    response = requests.post(
      wordpressAuthURL,
      data = {
        'client_id': clientID,
        'client_secret': clientSecret,
        'grant_type': 'password',
        'username': username,
        'password': password,
      }
    )
    return response.json()

  def UploadImage(self, article: Article, token: str):    
    response = requests.post(
      f'{wordpressAPIURL}/media/new',
      headers={
        "Authorization": "BEARER {}".format(token)
      },
      data = {
        'media_urls[]': article.featureImageURL,
        'attrs[0][title]': article.featureImageTitle,
        'attrs[0][alt]': article.featureImageTitle,
        'attrs[0][caption]': article.featureImageTitle,
        'attrs[0][description]': article.featureImageDescription
      }
    )
    return response.json()

  def NewArticle(self, article: Article):
    token = self.getWordpressToken()
    imageRes = self.UploadImage(article=article, token=token['access_token'])    
    response = requests.post(
      f'{wordpressAPIURL}/posts/new',
      headers={
        "Authorization": "BEARER {}".format(token['access_token'])
      },
      data = {
        'title': article.title,
        'content': article.content,
        'author': 'csimzwalvin',
        'tags': ",".join(article.tags),
        'categories': ",".join(article.categories),
        'featured_image': imageRes['media'][0]['ID']
      }
    )
    return response



