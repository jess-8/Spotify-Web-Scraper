import requests
from bs4 import BeautifulSoup
from tabulate import tabulate
import pandas as pd
import matplotlib.pyplot as plt

# Create lists
song_titles = []  # create a list of only the song titles.
artist_names = [[]]   # create a list of only artist names
url_links = [[]]      # create a list of url links for the artist pages.
count = []   # create a list of number of plays for each song in the top 20.
top_5_all_elements = []  # create a list of rank, song title, and number of plays for each artist's top 5.
top_5_only_names = [[]]  # create a list of only the song titles for each artist's top 5.
rank_list = list(range(1, 21))      # Create a rank list to be used as table indexes.

# Get HTML from Top 50 Spotify Playlist
soup = BeautifulSoup(requests.get("https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M").content, "html.parser")

# Find main container of all info that will be parsed.
results = soup.find(id="main")

# Find tag associated with all the songs and sings containing the string "draggable=False"
top_20_songs = results.find_all("a", string=lambda text: "draggable=False")[3:52]

for top_20 in top_20_songs:                # append correlating information to each list
    if top_20.get("class") != None:
        song_titles.append(top_20.text)
        artist_names.append([])   # group with nested lists based on song
        url_links.append([])  # group with nested lists based on song
    else:
        artist_names[-1].append(top_20.text)
        url_links[-1].append("https://open.spotify.com" + top_20.get("href"))

artist_names = artist_names[1:]
url_links = url_links[1:]

for i in range(len(url_links)):
    if len(url_links[i]) > 1:
        url_links[i] = url_links[i][0]   # only include the link of the first artist in songs with more than 1 artist
    else:
        url_links[i] = url_links[i]

def loop_through_artist_page():
    for url_index in range(len(url_links)):
        try:                                                     
            soupy = BeautifulSoup(requests.get("".join(url_links[url_index])).content, "html.parser")
        except requests.exceptions.RequestException:
            print("Connection Error")
            break
        else:
            find_song_elements(soupy, url_index)
    
def find_song_elements(html, each_list_index):
    """" Parse through each artist's page for only rank, song title, and number of streams for corresponding top 5 songs."""
    results1 = html.find(id="main")   
    artist_songs = results1.find_all("div", class_="JUa6JJNj7R_Y3i4P8YUX")                      
    for song in artist_songs:
        song_element = song.find_all("span", string=lambda text: song_titles[each_list_index])       
        for element in song_element:                                                           
            get_top_5(element, each_list_index)
            get_count(element, song_element, each_list_index) 

def get_top_5(x, artist_index):                 
    """" Append only song titles and artist names from each artist's top 5 to top_5_all_elements list."""                            
    try:
        str(x.text) != "" and int(x.text.replace(",", ""))
    except ValueError:
        element = [artist_names[artist_index]] + [x.text]
        top_5_all_elements.append(element)

def get_count(y, song_elements, song_title_index):                 
    """" Append the number of plays for each song included in Top 20 playst to count list.""" 
    element_name = y.text
    if song_titles[song_title_index] == element_name:
        count.append(song_elements[song_elements.index(y)+1].text)

def only_top_5_titles():
    """" Create list with only each artist's top 5 song titles. """
    for only_name in range(len(top_5_all_elements)):                           
        if top_5_all_elements[only_name][0] != top_5_all_elements[only_name-1][0]:
            top_5_only_names.append([top_5_all_elements[only_name][1]])
        else:
            top_5_only_names[-1].append(top_5_all_elements[only_name][1])

def make_excel_table():
    """" Create a pandas dataframe with ranking, song title, artist, number of streams, and top 5 songs and export to excel. """
    df = pd.DataFrame()
    df["Ranking"] = rank_list
    df["Song Title"] = song_titles
    df["Artist"] = artist_names 
    df["Number of Streams"] = count 
    df["Artist's Top 5 Most Popular Songs"] = top_5_only_names[1:]   

    file_name = "Spotify_Top_20.xlsx"        # File name
    df.to_excel(file_name, index=False)      # Export to Excel

def make_bar_graph():
    """" Create a horizontal bar graph with top 20 song title and number of streams per each song."""
    for comma in range(len(count)):
        count[comma] = int(count[comma].replace(",", ""))    # Convert all streams to integers

    y = list(song_titles)
    x = list(count)
    my_plot = plt.barh(y, x)                          # Title of table
    plt.title("Number of Streams Per Top 20 Song")
    plt.xlabel("Number of Streams (in Billions)")     # x-axis labels
    plt.ylabel("Song Title")                          # y-axis labels
    plt.xticks(rotation=45)
    plt.yticks(fontsize=5)
    plt.bar_label(my_plot, x)                         # Include bar labels of corresponding streams
    plt.show()

while True:
    try:
        loop_through_artist_page()
        only_top_5_titles()
    except ValueError: 
        print("Issue with lists.")                    
        break
    except requests.exceptions.RequestException:
        print("Issue with connecting to links.")
        break
    else:
        make_excel_table()
        make_bar_graph()
        break
