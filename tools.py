from crewai_tools import tool
import os
from datetime import datetime, timedelta

from wordpress import Wordpress


@tool("IsTermWritenBefore")
def IsTermWrittenBefore(storyTerm: str, days: int=10) -> bool:
    """
    Return true or false whether the term was being published in relak.la in the recent articles. 
    Base on the storyTerm to search and days as number is the number of days from today to filter.
    By default, this tool will search for the recent articles for the past 10 days.
    """
    # Function logic here
    wp = Wordpress()
    subDays = timedelta(days=days)
    afterDate = datetime.datetime.now() - subDays
    articles = wp.getArticles(searchTerm=storyTerm, afterDate=afterDate)
    return len(articles)>0