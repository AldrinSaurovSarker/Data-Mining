# Importing necessary libraries
import requests  # To fetch HTML contents
import pandas as pd  # To work with CSV files
import time  # To show total number of times to collect data
from bs4 import BeautifulSoup  # To format HTML contents in HTML format


# Remove redundant whitespaces and unnecessary punctuation marks
# Params: A string
# Return: A string without "-" marks
def preprocess(text):
    return " ".join(" ".join(text.split('-')).split())


# Fetch the html contents from a page of given url link
# Params: An url (e.g., https://www.example.com), a session variable.
# Return: The html code of the page of the given url
def fetchSoup(url, session):
    return BeautifulSoup(session.get(url).content, 'html.parser')


# Create a new csv file and save the df (dataframe) data to the csv file
# Params: A data list, filename of the csv file
def appendToCSV(data, filename, columns):
    # Convert a python list to dataframe. The given column names are the header that should be in the CSV file
    df = pd.DataFrame(data, columns=columns)
    df.to_csv(filename)


# Given a link, fetch all the necessary contents
# Param: baseUrl (The url of the home page), ses (A session variable)
def dataEntry(baseUrl, ses):
    data = []
    authorList = []
    soup = fetchSoup(baseUrl + '/famouspoets/', ses)  # Fetch html content from the 'famous poet' section
    anchors = soup.find_all(class_='famous-footer')  # The 'famous-footer' class contains the links for each poet

    # For each poet, fetching all poems Anchors contains all links for all poets. As I'm taking data for only
    # "সুকান্ত ভট্টাচার্য" to "ঈশ্বরচন্দ্র গুপ্ত", I've taken anchors[5:]. To collect other data, a different range
    # should be given.
    for links in anchors[5:]:
        link = links

        # Flag variable is assigned to False if there is no pagination in the html page, otherwise it remains True
        flag = True

        while flag:
            linkText = baseUrl + link.get('href')  # Link page of a specific poet
            poetSoup = fetchSoup(linkText, ses)  # Html content of a specific poet page

            # Collecting information of the author
            authorInformation = poetSoup.find(class_='table table-striped table-responsive').find_all('tr')
            author = poetSoup.find('h1').text

            birthDate = ''
            birthPlace = ''
            deathDate = ''

            for authInfo in authorInformation:
                if "জন্ম তারিখ" in authInfo.find('th').text:
                    birthDate = authInfo.find('td').text
                if "জন্মস্থান" in authInfo.find('th').text:
                    birthPlace = authInfo.find('td').text
                if "মৃত্যু" in authInfo.find('th').text:
                    deathDate = authInfo.find('td').text

            if [author, birthDate, birthPlace, deathDate] not in authorList:
                authorList.append([author, birthDate, birthPlace, deathDate])

            poemLinks = poetSoup.find(class_='post-list').find_all('a')  # From the list of poems, selecting all links

            # For all poem link
            for poemUrl in poemLinks:
                usefulLink = baseUrl + poemUrl.get('href')  # Link of the poems
                postSoup = fetchSoup(usefulLink, ses)  # The page where the content of the poem is

                try:  # If all information is available
                    title = preprocess(postSoup.find('h1').get_text())
                    author = preprocess(postSoup.find('div', class_='author-name').get_text())
                    post = preprocess(postSoup.find('div', class_='post-content').get_text())

                    data.append([title, author, post])  # Storing all data in a list
                    print(len(data))  # Just a statement to identify how many data have been read already
                except AttributeError:
                    pass

            try:
                link = poetSoup.find(class_='PagedList-skipToNext').find('a')  # If pagination is available
            except AttributeError:  # If pagination is not available
                flag = False

    # Save the information in the 'author' list to a CSV file
    appendToCSV(authorList, 'AuthorInformation.csv', ['Name', 'Birth date', 'Birth place', 'Death date'])

    # Save the information in the 'data' list to a CSV file
    appendToCSV(data, 'BanglaKobita.csv', ['Title', 'Author', 'Poem'])


# The main function
if __name__ == '__main__':
    s = requests.Session()  # Creating a session to fastening the data collection process
    baseurl = 'https://www.bangla-kobita.com'  # The home url

    startTime = time.time()  # Time before starting the data collection
    dataEntry(baseurl, s)  # Data entry
    endTime = time.time()  # Time after completing the data collection

    print('Time taken : ', endTime - startTime)  # Display time to collect data
