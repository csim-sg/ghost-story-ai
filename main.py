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
  role='Imaginary Editor',
  goal='Crafting a very believable story based on some true facts.',
  backstory="""
  You are a creative & imaginary writer for a online blog. 
  With the information given by co-worker, you always try to write a believable story.
  In order for your story to be ranked well in Search Engine, you will add keywords, and follow google SEO guideline.
""",
  verbose=True,
  allow_delegation=True,
  llm=ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.5)
)

designer = Agent(
  role='Paranormal Researcher Assistant',
  goal='Find images from the internet that fit the story',
  backstory="""
  Your job is to find images from the internet that fit the story & location. 
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
  You like realistic image generation with a eerie feeling
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
  llm=ChatOpenAI(model_name="gpt-3.5-turbo", temperature=1),
  allow_delegation=True
)


# Create tasks for your agents
ghostlyResearch = Task(
  description="""
  Search the internet on any ghostly being from South East Asia culture
  then find a detail description of the ghostly being
  be more creative in the search term so it will not always return the same results
  Mainly focus on countries and Islands around Singapore & Malaysia
  """,
  expected_output="""
  Their Name and alias, characteristics, religion information, their lore in the following format and in bullet points
  ## Name & Alias ##

  ## Characteristics ##


  ## Religion Information ##


  ## Lore ##

  """,
  agent=researcher,
  async_execution=True
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
  context=[ghostlyResearch]
  
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
  context=[ghostlyResearch]
)

blogWriting = Task(
  description="""
  Using the all the tasks output provided, craft a horror story.
  The story can be unrealistic but not too much to unbelievable. 
  Adding some backstory and history to make it more realistic
  Follow SEO guideline and keyword so it be can be rank better.
  Avoid complex words or too formal so it doesn't sound like AI.
  Make it sound like it's being submitted from the public
  """,
  expected_output="Full ghost story of at least 5 paragraphs and within 1500 words",
  agent=writer,
  context=[ghostlyResearch, detailResearch, detailLocationResearch]
)

searchImages = Task(
  description="""
  With the story written
  Search for relavent images for the story's paragraph
  Scrape the website and extract the image URL.
  Add the image URL below the paragraph 
  Below the image, add in citation of where is this image being found and credit link back.
  """,
  expected_output="Full story with the images link between the paragraph with credit.",
  agent=designer,
  context=[blogWriting]
)

generatingFeatureImage = Task(
  description="""
  With the given information, generate a feature image that can be used with the 
  The image need to fit the ghostly being and the lore
  The background setting of the image need to align with the lore & location of where is happen.
  The image should be realistic & but still adding eerie feeling
  Don't add word in the image
  """,
  expected_output="Output the Image Link & Description",
  agent=AIDesigner,
  output_pydantic=ArticleImage,
  context=[ghostlyResearch, detailResearch, detailLocationResearch, blogWriting],
)

seoTask = Task(
  description="""
  Think of a SEO friendly title that's relevent to the story.
  Make sure the story written have relevent SEO keyword
  The flow of the story must be correct and not sound too much like AI generated
  Keep all images from Art Director
  Adding relevent hashtag at the end of the story.
  According to the story, add in relevent categories  
  """,
  expected_output="""
    Output according to the pydantic model
    story into content in HTML format
    title into title
    category into category
    tags into tags
    image_url as featureImageURL & image_description as featureImageDescription from AIDesigner output
  """,
  agent=seoExpert,
  output_pydantic=Article,
  context=[searchImages, generatingFeatureImage, blogWriting]
)

# Instantiate your crew with a sequential process
crew = Crew(
  agents=[researcher, writer, designer, seoExpert, AIDesigner],
  tasks=[ghostlyResearch, detailResearch, detailLocationResearch, blogWriting, searchImages, generatingFeatureImage, seoTask],
  verbose=True,
  process = Process.sequential,
  planning = True,
  planning_llm = ChatOpenAI(model="gpt-3.5-turbo")
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
