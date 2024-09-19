import base64
from typing import List
from pydantic import Field, BaseModel
import requests
import os
import markdown

username = os.environ['WP_USERNAME']
password = os.environ['WP_PASSWORD']
blogDomain = os.environ['WP_DOMAIN']

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
  
  def getTerm(self, termName, termType):
    response = requests.get(
      f'{wordpressAPIURL}/{termType}?search={termName}'
    )
    if(response.ok and len(response.json()) > 0):
      return [data for data in response.json() if data['name'].lower() == termName.lower()][0]
    else:
      response = requests.post(
        f'{wordpressAPIURL}/{termType}',
        headers={
          "Authorization": "Basic {}".format(self.getWordpressToken())
        },
        data={
          "name": termName
        }
      )
      return response.json()
    

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
    print(imageRes)
    hTMLContent = markdown.markdown(article.content)
    print(hTMLContent)

    catIDs = []
    tagIDs = []

    for category in article.categories: 
      catReturn = self.getTerm(category, "categories")
      if catReturn:
        catIDs.append(catReturn['id'])
    for tag in article.tags: 
      tagReturn = self.getTerm(tag, "tags")
      if tagReturn:
        tagIDs.append(tagReturn['id'])

    response = requests.post(
      f'{wordpressAPIURL}/posts',
      headers={
        "Authorization": "Basic {}".format(token)
      },
      data = {
        'title': article.title,
        'content': hTMLContent,
        'tags': tagIDs,
        'categories': catIDs,
        'featured_media': imageRes['id'],
        'status': 'publish'
      }
    )
    return response
  
# wp = Wordpress()
# wp.getTerm("")
# image = ArticleImage
# image.featureImageURL= 'https://miro.medium.com/v2/resize:fit:300/1*DHilTwLnzy84S1PJznQ4FQ.png'
# image.featureImageTitle = 'testing'
# image.featureImageDescription = "qwdqwdqwdq"
# wp.UploadImage(featuredImage=image, token=wp.getWordpressToken())