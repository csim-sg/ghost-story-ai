from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, DallETool, ScrapeWebsiteTool
from langchain_openai import ChatOpenAI
from wordpress import Article, ArticleImage, Wordpress

search_tool = SerperDevTool()

# Define your agents with roles and goals
researcher = Agent(
  role='Senior Paranormal Researcher',
  goal='Research South East Asia paranormal activities & stories',
  backstory="""You work in a small self funded group for paranormal activities.
  Your expertise lies in spotting paranormal activities in South East Asia 
  You have deep knowledge and love to research on different ghost being South East Asia religion""",
  verbose=True,
  allow_delegation=False,
  # You can pass an optional llm attribute specifying what model you wanna use.
  llm=ChatOpenAI(model_name="gpt-3.5-turbo", temperature=1.5),
  tools=[search_tool],
  #max_iter=5
)
writer = Agent(
  role='SEO Trained Editor',
  goal='Crafting a very believable story based on the true facts.',
  backstory="""
  You are a creative writer for a online blog. 
  You work closely with Senior Paranormal Researcher, in getting more information in order to write your story.
  With the information given by co-worker, you will research for possible SEO keyword and incorporate into a believable story.
  In order for your story to be ranked well in Search Engine, you will add keywords, and follow google SEO guideline.
""",
  verbose=True,
  allow_delegation=False,
  llm=ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.5),
  tools=[search_tool],
)

designer = Agent(
  role='Paranormal Researcher Assistant',
  goal='Search images from the internet that fit the story',
  backstory="""
  Your job is to search for images from the internet that fit the story & location. 
  When using the image, go to the website found and look for relevent image link
  In order to not get sued, you make sure the images used are properly credited back to the main website. 
""",
  verbose=True,
  allow_delegation=False,
  llm=ChatOpenAI(model_name="gpt-3.5-turbo", temperature=1),
  tools=[search_tool, ScrapeWebsiteTool()],
)

AIDesigner = Agent(
  role='AI Art director',
  goal='Generate feature images for the story',
  backstory="""
  As a AI Art director, your job will be to generate best relevent prompt for Dall-E,
  The images must fit well to the story background, location, ghostly being.
  You like realistic image generation with an eerie feeling
""",
  verbose=True,
  allow_delegation=False,
  tools=[DallETool()],
)

seoExpert = Agent(
  role='Chief Editor',
  goal='Having the most SEO friendly title and story',
  backstory="""
  You are a Google SEO specialist
  Your job is to think of the title to use for the story that is engaging and SEO friendly
  Re-write the story slightly if needed according to SEO guidelines 
""",
  verbose=True,
  llm=ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7),
  allow_delegation=True,
  tools=[search_tool],
)

ghostBeingResearch = Task(
  description="""
  Search the internet on any ghostly being from Malay & Chinese culture
  The search can be based on the following.
  1. Popular ghost location, 
  2. Army ghost story
  3. Infamous ghost
  4. Ghost with long history and popular in the region
  Make sure the ghostly being are not being writen in https://relak.la recently. 
  """,
  expected_output="""
    The name of the ghostly being, that was not written in https://relak.la in the recent 10 posts.
  """,
  agent=researcher,
  
)


# Create tasks for your agents
ghostlyResearch = Task(
  description="""
  Full research on the ghostly being to write and provide the required output
  """,
  expected_output="""
  Their Name and alias, characteristics, religion information, their lore in the following format and in bullet points
  ## Name & Alias ##

  ## Characteristics ##


  ## Religion Information ##


  ## Lore ##

  """,
  agent=researcher,
  async_execution=True,
  context=[ghostBeingResearch]
)

detailResearch = Task(
  description="""
  From the information given, do a more detail search on the history of the ghostly being.
  """,
  expected_output="""
  Full output in the following with bullet points
  ## History of the ghostly being ##

  ## Rumor of where is being sighted ##

  """,
  agent=researcher,
  async_execution=True,
  context=[ghostBeingResearch]
  
)

detailLocationResearch = Task(
  description="""
  From the information given, do a more detail search on where the ghostly being was being sighted, and any back story or history for the location.
  """,
  expected_output="""
  Full output in the following with bullet points
  ## History of the location ##

  ## When it happen ##
  
  ## Any back story or rumor in the location where its being sighted ##

  """,
  agent=researcher,
  async_execution=True,
  context=[ghostBeingResearch]
)

blogWriting = Task(
  description="""
  Based on the information,
  Write an angaging punchy scary ghost story. Please alter between short and long sentences. Avoid jargon or cliches.
  Make it scary but not unrealistics. The tone of voice should be casual, story telling and slightly conversational.
  Use burstiness in the sentences. Combining both short and long sentences to create a more human like flow
  Use human writing like exclamation points and pause. The story can be based on someone else experiences. 
  The intro should include either an interesting facts, quotation, or something to hook the reader.
  Avoid did you know. 
  """,
  expected_output="""
  Full scary ghost story of at least 5 paragraphs and within 2000 words
  Output the format using the following format
  ## Title ##

  ## Story ##
  """,
  agent=writer,
  context=[ghostlyResearch, detailResearch, detailLocationResearch]
)

searchImages = Task(
  description="""
  Given the story, 
  Search a few relavent images that may fit the theme & the ghostly being in the story  
  Always find the exact link of the image to use, Scrape the website and extract the image URL.
  """,
  expected_output="""
    Output a few images with their original website and which paragraph that this image should be inserted.
  """,
  agent=designer,
  async_execution=True,
  context=[blogWriting]
)

generatingFeatureImage = Task(
  description="""
  With the given story, generate a feature image that can be used with the 
  The image need to fit the information of the ghost
  The background setting of the image need to align with the lore & location of where is happen.
  The image should be realistic but not too scary. 
  Don't add word in the image
  """,
  expected_output="Output the Image Link & Description",
  agent=AIDesigner,
  async_execution=True,
  output_pydantic=ArticleImage,
)

seoTask = Task(
  description="""
  Making sure the title of the story is SEO friendly & eye catching.
  Read through the story written have relevent SEO keyword
  The flow of the story make sense and not sound too much like AI generated
  Extend or rewrite if it is less than 5 paragraphs or 1500 words excluding title.
  Add the images from Paranormal Researcher Assistant into relevent paragraph
  Adding relevent hashtag at the end of the story.
  According to the story, add in relevent categories
  """,
  expected_output="""
    Output according to the pydantic model
    Story into content in HTML format
    Remove title and featured image in the content output.
    title into title
    category into category
    tags into tags
    image_url as featureImageURL & image_description as featureImageDescription from AIDesigner output
  """,
  agent=seoExpert,
  output_pydantic=Article,
  context=[blogWriting, searchImages]
)

# Instantiate your crew with a sequential process
crew = Crew(
  agents=[researcher, writer, designer, seoExpert, AIDesigner],
  tasks=[ghostBeingResearch, ghostlyResearch, detailResearch, detailLocationResearch, blogWriting, searchImages, generatingFeatureImage, seoTask],
  verbose=True,
  process = Process.sequential,
  planning = True,
  planning_llm = ChatOpenAI(model="gpt-4o")
)

# Get your crew to work!
result = crew.kickoff()
taskOut = generatingFeatureImage.output
print("######################")
print(result.pydantic)
print(taskOut)


print("######### Start posting to Wordpress #########")
wp = Wordpress()
print(wp.NewArticle(result.pydantic, taskOut.pydantic))
