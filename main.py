from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, DallETool, ScrapeWebsiteTool
from langchain_openai import ChatOpenAI
from wordpress import Article, ArticleImage, Wordpress

search_tool = SerperDevTool()
imageSearchTool = SerperDevTool(search_url='https://google.serper.dev/images', n_results=20)

# Define your agents with roles and goals
researcher = Agent(
  role='Senior Paranormal Researcher',
  goal='Research Asia paranormal activities & stories',
  backstory="""You work in a small self funded group for paranormal activities.
  Your expertise lies in spotting paranormal activities in Asia 
  You have deep knowledge and love to research on different ghost being Asia religion""",
  verbose=True,
  allow_delegation=False,
  # You can pass an optional llm attribute specifying what model you wanna use.
  llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0.8),
  tools=[search_tool],
  #max_iter=5
)
writer = Agent(
  role='SEO Trained Ghost Story Writer',
  goal='Crafting a very believable story based on the true facts.',
  backstory="""
  You are a creative writer for a online blog. 
  You work closely with Senior Paranormal Researcher, in getting more information in order to write your story.
  With the information given by co-worker, you will research for possible SEO keyword and incorporate into a believable story.
  In order for your story to be ranked well in Search Engine, you will add keywords, and follow google SEO guideline.
""",
  verbose=True,
  allow_delegation=False,
  llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0.7),
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
  llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=1),
  tools=[imageSearchTool, ScrapeWebsiteTool()],
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
  tools=[imageSearchTool, DallETool()],
)

seoExpert = Agent(
  role='Chief Editor',
  goal='Having the most SEO friendly title and story',
  backstory="""
  You are a Google SEO specialist
  Your job is to think of the title to use for the story that is engaging and SEO friendly
  Sent back to writer for rewrite if the story does not pass the requirement
""",
  verbose=True,
  llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=1.8),
  allow_delegation=True,
  tools=[search_tool],
)

ghostBeingResearch = Task(
  description="""
  Search for any ghost story or ghostly lore in Malay or Chinese culture or Buddist or Taoist religion
  The story or lore should only limit within Japan, China, Taiwan, Singapore, Thailand, Malaysia & Indonesia
  Some search terms to use but not limited to
  - Popular ghost location, 
  - Army ghost story
  - Infamous ghost
  - Ghost with long history and popular in the region
  - MRT ghost sighting
  - Type of ghosts
  - Malay thursday night 
  - Indonesia Bohmo
  - Chinese 7th months
  - Thailand ghost story
  - Buddist afterlife culture & story
  - Taoist ghost culture & story
  Make sure its not similiar to any stories writen in https://relak.la recently. 
  """,
  expected_output="""
    Output either 1 ghost story, ghostly being or culture for other tasks to based on
    Select the output from the web research done.
    The ghost story, ghostly being or culture must not be similiar to any of the recent 10 posts in https://relak.la.
  """,
  agent=researcher,
  
)


# Create tasks for your agents
ghostlyResearch = Task(
  description="""
  Detail research on the given information to write and provide the required output
  """,
  expected_output="""
  Detail output of the following in bullet points
  ## Name & Alias ##

  ## Characteristics ##

  ## History of the ghostly being ##

  ## Rumor of where is being sighted ##
  
  ## Religion & Culture Information ##

  ## Lore ##


  """,
  agent=researcher,
  async_execution=True,
  context=[ghostBeingResearch]
)

detailResearch = Task(
  description="""
  From the information given, search for related stories. 
  Summarised the story and determine any punchy line to use.
  Do not search for video or audio sites.
  Only use English or Mandrain sites
  Stories found must be related to the information. Do not expand to others
  """,
  expected_output="""
  Find 3 similiar stories online and provide the following information.
  ## URL of the story ##

  ## Summarised information ##

  ## Punch line or keyword to use ##

  """,
  agent=researcher,
  async_execution=True,
  context=[ghostBeingResearch]
  
)

blogWriting = Task(
  description="""
  Based on the information,
  Write an engaging and scary ghost story. Please alter between short and long sentences. Avoid jargon or cliches.
  Make it realistics with sudden ghostly appearence. The tone of voice should be casual, story telling and slightly conversational.
  Use burstiness in the sentences. Combining both short and long sentences to create a more human like flow
  Use human writing like exclamation points and pause. You can mix and match stories from previous task. 
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
  context=[ghostlyResearch, detailResearch]
)

searchImages = Task(
  description="""
  Given the story, 
  Do a google image search that may fit the theme & the ghostly being in the story  
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
  The image need to fit the information of the ghost, you can search the intenet for find how the ghost looks like
  The background setting of the image need to align with the lore & location of where is happen.
  The image should be realistic but not too scary. 
  Don't add word in the image
  """,
  expected_output="Output the Image Link & Description, the size of the image set as width 1024px, height 800px",
  agent=AIDesigner,
  async_execution=True,
  output_pydantic=ArticleImage,
)

seoTask = Task(
  description="""
  Make sure the title and the story are SEO friendly & eye catching. 
  The title should be related to the story. No over use of keywords.
  The flow of the story make sense and not sound too much like AI generated
  Inject the images and their website's ref found between paragraphs in the storys that make sense

  """,
  expected_output="""
    Split the title, story and featured image.
    Full story with images injected should be in Markdown
    Output must always fit into Article Pydantic Model that make sense.
    Do not add extra value into the fields.
    Do not cut short the story.
  """,
  agent=seoExpert,
  output_pydantic=Article,
  context=[blogWriting, searchImages, generatingFeatureImage]
)

# Instantiate your crew with a sequential process
crew = Crew(
  agents=[researcher, writer, designer, seoExpert, AIDesigner],
  tasks=[ghostBeingResearch, ghostlyResearch, detailResearch, blogWriting, searchImages, generatingFeatureImage, seoTask],
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
