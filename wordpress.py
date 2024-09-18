from typing import List
from pydantic import Field, BaseModel
import requests
import os
import markdown



wordpressAuthURL = 'https://public-api.wordpress.com/oauth2/token'

clientID = os.environ['WP_CLIENT_ID']
clientSecret = os.environ['WP_CLIENT_SECRET']
username = os.environ['WP_USERNAME']
password = os.environ['WP_PASSWORD']
blogDomain = os.environ['WP_DOMAIN']

wordpressAPIURL = f'https://public-api.wordpress.com/rest/v1.1/sites/{blogDomain}'

class Article(BaseModel):
  title: str = Field(title="Title")
  content: str = Field(title="Story", description="story in markdown format. Including images between the paragaph")
  tags: List[str] = Field(title="Tags")
  categories: List[str] = Field(title="categories")
  featureImageURL: str = Field(title="image_url")
  featureImageTitle: str = Field(title="featureImageTitle")
  featureImageDescription: str = Field(title="image_description")

class ArticleImage(BaseModel):
  featureImageURL: str = Field(description="Link of the Image")
  featureImageTitle: str = Field(description="Title of the image")
  featureImageDescription: str = Field(description="Description used to generate the image")

class Wordpress():

  def getArticles(self, searchTerm, afterDate):
    response = requests.get(
      f'{wordpressAPIURL}/posts?search={searchTerm}&after={afterDate}'
    )
    return response.json()

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

  def UploadImage(self, featuredImage: ArticleImage, token: str):
    print(f'{wordpressAPIURL}/media/new') 
    response = requests.post(
      f'{wordpressAPIURL}/media/new',
      headers={
        "Authorization": "BEARER {}".format(token)
      },
      data = {
        'media_urls[]': featuredImage.featureImageURL,
        'attrs[0][title]': featuredImage.featureImageTitle,
        'attrs[0][alt]': featuredImage.featureImageTitle,
        'attrs[0][caption]': featuredImage.featureImageTitle,
        'attrs[0][description]': featuredImage.featureImageDescription
      }
    )    
    return response.json()

  def NewArticle(self, article: Article, featuredImage: ArticleImage):
    token = self.getWordpressToken()
    imageRes = self.UploadImage(featuredImage=featuredImage, token=token['access_token'])
    hTMLContent = markdown.markdown(article.content)
    response = requests.post(
      f'{wordpressAPIURL}/posts/new',
      headers={
        "Authorization": "BEARER {}".format(token['access_token'])
      },
      data = {
        'title': article.title,
        'content': hTMLContent,
        'author': 'csimzwalvin',
        'tags': ",".join(article.tags),
        'categories': ",".join(article.categories),
        'featured_image': imageRes['media'][0]['ID']
      }
    )
    return response