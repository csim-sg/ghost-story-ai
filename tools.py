from crewai_tools import tool
from datetime import datetime, timedelta
from wordpress import Wordpress


@tool("IsTermWritenBefore")
def IsTermWrittenBefore(topic: str, days: int=10) -> bool:
    """
    Return true or false whether the topic was being published in relak.la in the recent articles. 
    Base on the topic to search and days as number is the number of days from today to filter.
    By default, this tool will search for the recent articles for the past 10 days.
    """
    # Function logic here
    wp = Wordpress()
    subDays = timedelta(days=days)
    afterDate = datetime.now() - subDays
    articles = wp.getArticles(searchTerm=topic, afterDate=afterDate)
    return len(articles)>0