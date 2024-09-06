from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, DallETool, ScrapeWebsiteTool
from langchain_openai import ChatOpenAI
from wordpress import Article, Wordpress

import os

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
  role='Imaginary writer intern',
  goal='Crafting a very believable story.',
  backstory="""
  You are a creative & imaginary writer for a online blog. 
  Though the article written in the online blog are all friction, 
  but you still love to combine current happening in South East Asia with additional research from your co-worker.
  You always try to make the article as believable as possible
""",
  verbose=True,
  allow_delegation=False,
  llm=ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.5),
  tools=[search_tool],
)

designer = Agent(
  role='Art director',
  goal='Find images from the internet that fit the story',
  backstory="""
  You are an young creative Art director for the company. 
  You job is to search the internet and find images of the ghostly being or the location from the story written
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
  allow_delegation=False
)

webDeveloper = Agent(
  role='Web Developer',
  goal='Make sure the final output images or video are tag correctly',
  backstory="""
  Web developer helping the company to make no broken images or wrongly tag video.
""",
  verbose=True,
  llm=ChatOpenAI(model_name="gpt-3.5-turbo", temperature=1),
  allow_delegation=False
)


# Create tasks for your agents
ghostlyResearch = Task(
  description="""
  Conduct finding on any ghostly being from South East Asia culture
  then find a detail description of the ghostly being
  be more creative in the search term so it will not always return the same results
  Mainly focus on countries and Islands around Singapore & Malaysia
  """,
  expected_output="""
  Their Name and alias, characteristics, religion information, their lore in the following format and in bullet points
  ## Name & Alias ##
    1. Zhiang Shi

  ## Characteristics ##
    1. Translucent
    2. White figure

  ## Religion Information ##
    1. Zhiang Shi
    2. Chinese Taoist religion

  ## Lore ##
    1. Zhiang Shi
    2. Chinese Taoist religion
  """,
  agent=researcher
)

blogWriting = Task(
  description="""Using the information provided, write a scary story about the ghostly being.
  The story can be unrealistic but not too much to unbelievable. 
  Be creative with the location that the story happen, you can search for places where this ghostly being has being sighted
  Avoid complex words or too formal so it doesn't sound like AI.
  Make it sound like it's being submitted from the public
  """,
  expected_output="Full ghost story of at least 4 paragraphs and within 1500 words",
  agent=writer
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
  agent=designer
)

generatingFeatureImage = Task(
  description="""
  Generate a Dall-E prompt to create a feature image fitting the story. 
  The image should not be too scary.
  """,
  expected_output="Output the Image Link & Description as Featured Image into the pydantic model",
  agent=AIDesigner,
  async_execution=True
)

seoTask = Task(
  description="""
  Think of a SEO friendly title that's relevent to the story.   
  Keep all images from Art Director
  Adding relevent hashtag at the end of the story.
  According to the story, add in relevent categories  
  """,
  expected_output="""
    Output according to the pydantic model
    story into content in HTML format
    image_url as featureImageURL & image_description as featureImageDescription from AIDesigner output
  """,
  agent=seoExpert,
  output_pydantic=Article,
  context=[searchImages, generatingFeatureImage]
)

# Instantiate your crew with a sequential process
crew = Crew(
  agents=[researcher, writer, designer, seoExpert, AIDesigner],
  tasks=[ghostlyResearch, blogWriting, searchImages, generatingFeatureImage, seoTask],
  verbose=True,
  process = Process.sequential,
  planning = True,
  planning_llm = ChatOpenAI(model="gpt-4o-mini")
)

# Get your crew to work!
result = crew.kickoff()

print("######################")
print(result.pydantic)


print("######### Start posting to Wordpress #########")
wp = Wordpress()
print(wp.NewArticle(result.pydantic))