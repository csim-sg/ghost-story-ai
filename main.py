from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, DallETool, ScrapeWebsiteTool
from langchain_openai import ChatOpenAI
from tools import IsTermWrittenBefore
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
  tools=[search_tool, IsTermWrittenBefore],
  #max_iter=5
)

juniorResearcher = Agent(
  role='Junior Paranormal Researcher',
  goal='Help Senior Researcher expend his research with details.',
  backstory="""
    You report to the senior researcher in the company. 
    Your job is to assist senior researcher on his original research and search more details so writer and editor can use your work to finish their job.
    You don't search for irrelevent term beyond what senior researcher provide.
  """,
  verbose=True,
  allow_delegation=False,
  # You can pass an optional llm attribute specifying what model you wanna use.
  llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=1.5),
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
  llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=1.2),
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
  llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=1.2),
  tools=[imageSearchTool],
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
  tools=[imageSearchTool, DallETool(
    size="1024x1024",
  )],
)

seoExpert = Agent(
  role='Chief Editor',
  goal='Having the most SEO friendly title and story',
  backstory="""
  You are a Google SEO specialist & Chief Editor
  Your job is to make sure the title and story from writer not sound too much like AI generated
  The title should be eye-catching and SEO friendly
  You also will insert those images from Paranormal Researcher Assistant between relevent paragraph so the story flow can be more engaging
""",
  verbose=True,
  llm=ChatOpenAI(model_name="gpt-4o-mini", temperature=0.5),
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
  Once a topic is found, search the topic in relak.la to make sure its not similiar to any stories writen recently. 
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
  Only research based on the output from ghostBeingResearch tasks. Do not irrelevent topic
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
  agent=juniorResearcher,
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
  agent=juniorResearcher,
  async_execution=True,
  context=[ghostBeingResearch]
  
)

blogWriting = Task(
  description="""
  Based on the information, and subsitute it with ###Information### below
  Write an engaging and scary ###Information### story. Please alter between short and long sentences. Avoid jargon or cliches.
  Make it realistics with sudden ghostly appearence. The tone of voice should be casual, story telling and slightly conversational.
  The story must have some reference or facts from the ###Information###.
  Do not make up place name, ghost name or culture.
  Use burstiness in the sentences. Combining both short and long sentences to create a more human like flow
  Use human writing like exclamation points and pause. You can mix and match stories from previous task. 
  The story should always be from a third or first person point of view.
  The intro should include either an interesting facts, quotation, or something to hook the reader.
  Avoid did you know. 
  """,
  expected_output="""
  Full scary ###Information### story of at least 5 paragraphs and within 2000 words
  Some of the following elements should be included in the story but not limited
  - Introduction and lore of the ###Information###
  - Where it take place, and any backstory to that place
  - How the encounter happen, include scary scenes
  - How the main character get away or how the ###Information### is being defeated. 
  - Conclusion can be the ###Information### still around or no more.
  Output the format using the following format
  [Title]

  [/Title]

  [Story]

  [/Story]
  """,
  agent=writer,
  context=[ghostlyResearch, detailResearch]
)

searchImages = Task(
  description="""
  Given the story from blogWriting tasks
  Do a google image search that may fit the theme & the ghostly being in the story  
  Always find the exact link of the image to use, Scrape the website and extract the image URL.
  """,
  expected_output="""
    Output a few images with their original website and which paragraph that this image should be inserted.
    Each of them in the following format
    [image]
      [image url][/image url]
      [alt text][/alt text]
      [source website url][/source website url]
    [/image]
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
  expected_output="Output the Image Link & Description",
  agent=AIDesigner,
  async_execution=True,
  output_pydantic=ArticleImage,
)

seoTask = Task(
  description="""
  With the given title and story,
  Make sure the title and the story are SEO friendly & eye catching & within 25 words
  The title should be related to the story. 
  The story must be relevent to ghostlyResearch & detailResearch task.
  Below are dos and don'ts that need to follow strictly
  Don'ts
    - Dont rewrite of the story
    - Dont inject featured images from generatingFeatureImage task into the story.
  Dos
    - Minor adjustments to make the story more engaging.
    - Inject images from searchImages task between relevent paragraph
    - Make sure the story have at least 5 paragraph or within 2000 words.
    - The story should be in third or first person view.
    - Think of relevent tags & category based on the story
  """,
  expected_output="""
    Remove title and featured images from the story
    Full story with images injected should be in Markdown
    Output must always fit into Article Pydantic Model that make sense.
    Do not add extra value into the fields.
    Do not cut short the story.
  """,
  agent=seoExpert,
  output_pydantic=Article,
  context=[ghostlyResearch, detailResearch, blogWriting, searchImages, generatingFeatureImage]
)

# Instantiate your crew with a sequential process
crew = Crew(
  agents=[researcher, juniorResearcher, writer, designer, seoExpert, AIDesigner],
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
