import os
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool


search_tool = SerperDevTool()

# Define your agents with roles and goals
researcher = Agent(
  role='Senior Paranormal Researcher',
  goal='Research Singapore & Malaysia paranormal activities & stories',
  backstory="""You work in a small self funded group for paranormal activities.
  Your expertise lies in spotting paranormal activities in Singapore & Malaysia  
  You have deep knowledge and love to research on different ghost being Singapore & Malaysia religion""",
  verbose=True,
  allow_delegation=False,
  # You can pass an optional llm attribute specifying what model you wanna use.
  # llm=ChatOpenAI(model_name="gpt-3.5", temperature=0.7),
  tools=[search_tool],
  #max_iter=5
)
writer = Agent(
  role='Imaginary writer intern',
  goal='Crafting a very believable story.',
  backstory="""
  You are a creative & imaginary writer for a online blog. 
  Though the article written in the online blog are all friction, 
  but you still love to combine current happening in Singapore & Malaysia with additional research from your co-worker.
  You always try to make the article as believable as possible
""",
  verbose=True,
  allow_delegation=True,
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
  allow_delegation=True,
  tools=[search_tool],
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
  allow_delegation=True
)


# Create tasks for your agents
task1 = Task(
  description="""
  Conduct finding on any ghostly being from Singapore's Chinese & Malay culture
  then find a detail description of the ghostly being
  be more creative in the search term so it will not always return the same results
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

task2 = Task(
  description="""Using the information provided, write a scary story about the ghostly being.
  The story can be unrealistic but not too much to unbelievable. 
  Be creative with the location that the story happen, you can search for places in Singapore where this ghostly being appear
  State the region on Singapore this incident happen
  Avoid complex words or too formal so it doesn't sound like AI.
  Make it sound like it's being submitted from the public
  """,
  expected_output="Full ghost story of at least 4 paragraphs or 500 words",
  agent=writer
)

task3 = Task(
  description="""With the new story written
  Always try to find the image of the location and the ghostly being in the story. 
  Only use the image link instead of website and attached between the paragraphs
  Images found and used must be royalty free or add credit back to the image source below the image
  """,
  expected_output="Full story with the images link between the paragraph.",
  agent=designer
)

task4 = Task(
  description="""
  Think of a title that's relevent to the story. 
  Make sure the story follow SEO guideline and rewrite for SEO. 
  Make sure those images have proper title and alt text
  Adding relevent hashtag at the end of the story.
  """,
  expected_output="Full story with enhanced SEO editing",
  agent=seoExpert
)

# Instantiate your crew with a sequential process
crew = Crew(
  agents=[researcher, writer, designer, seoExpert],
  tasks=[task1, task2, task3, task4],
  verbose=True,
  process = Process.sequential
)

# Get your crew to work!
result = crew.kickoff()

print("######################")
print(result)