import base64
from typing import List
from pydantic import Field, BaseModel
import requests
import os
import markdown

username = 'Alvin Sim' #os.environ['WP_USERNAME']
password = 'E27B emJA wkgQ U7Zm Oxy4 u9Fs' #os.environ['WP_PASSWORD']
blogDomain = 'relak.la'#os.environ['WP_DOMAIN']

wordpressAPIURL = f'https://{blogDomain}/wp-json/wp/v2'

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
    credentials = username + ':' + password
    token = base64.b64encode(credentials.encode())
    return token.decode('utf-8')

  def UploadImage(self, featuredImage: ArticleImage, token: str):
    print(f'{wordpressAPIURL}/media') 
    r = requests.get(featuredImage.featureImageURL, allow_redirects=True)
    savingFileName = '%s.png' % featuredImage.featureImageTitle.replace(" ", "-")
    open(savingFileName, 'wb').write(r.content)
    file = open(savingFileName, 'rb')
    response = requests.post(
      f'{wordpressAPIURL}/media',
      headers={
        "Authorization": "Basic {}".format(token),
        # "Accept": "application/json",
        # "cache-control": "no-cache",
        #'Content-Disposition': "attachment; filename=%s" % featuredImage.featureImageTitle,
      },
      files = {
        'title': featuredImage.featureImageTitle,
        'description': featuredImage.featureImageDescription,
        'caption': featuredImage.featureImageDescription,
        'file': file
      }
    )
    return response.json()

  def NewArticle(self, article: Article, featuredImage: ArticleImage):
    token = self.getWordpressToken()
    imageRes = self.UploadImage(featuredImage=featuredImage, token=token)
    hTMLContent = markdown.markdown(article.content)
    response = requests.post(
      f'{wordpressAPIURL}/posts',
      headers={
        "Authorization": "Basic {}".format(token)
      },
      data = {
        'title': article.title,
        'content': hTMLContent,
        'author': 'Alvin Sim',
        'tags': ",".join(article.tags),
        'categories': ",".join(article.categories),
        'featured_image': imageRes['id']
      }
    )
    return response
  
# wp = Wordpress()
# image = ArticleImage
# image.featureImageURL= 'https://miro.medium.com/v2/resize:fit:300/1*DHilTwLnzy84S1PJznQ4FQ.png'
# image.featureImageTitle = 'testing'
# image.featureImageDescription = "qwdqwdqwdq"
# wp.UploadImage(featuredImage=image, token=wp.getWordpressToken())