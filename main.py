__author__ = 'Esther'
import urllib.request
import re
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk import pos_tag
import random
import tweepy
import config
import getHypernym

def login():
    # for info on the tweepy module, see http://tweepy.readthedocs.org/en/v3.1.0/
    # Authentication is taken from config.py
    consumer_key = config.consumer_key
    consumer_secret = config.consumer_secret
    access_token = config.access_token
    access_token_secret = config.access_token_secret

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)
    return api

def readLyricsFromLyricsfreak(page):
    """
    Read website at page and return the lyrics part of the page as a readable string.
    """
    lyrics = urllib.request.urlopen(page)
    lyrics = lyrics.read()
    lyrics = lyrics.decode()
    try:
        lyrics = lyrics.split("<!-- SONG LYRICS -->")[1].split("<!-- /SONG LYRICS -->")[0]
        htmltag = re.compile("<[^<>]*>")
        lyrics = re.sub(htmltag, " / ", lyrics)
        lyrics = re.sub("\s+", " ", lyrics)
        return sent_tokenize(lyrics)
    except IndexError:
        # unable to read the song page for some HTML reasons
        return []

def getTopSongPagesFromLyricsfreak():
    """
    Read list of most popular songs from http://www.lyricsfreak.com/top/ and return a list of URLs that lead to each
    song listed.
    """
    topsongs = []
    linkpattern = re.compile('<td><a href="([^\"]*)"')
    songlist =  urllib.request.urlopen("http://www.lyricsfreak.com/top/")
    songlist = songlist.read()
    songlist = songlist.decode()
    try:
        songlist = songlist.split('<tbody>')[1].split("</tbody>")[0]
        for topsong in re.findall(linkpattern, songlist):
            topsongs.append("http://www.lyricsfreak.com"+topsong)

        songlist_new =  urllib.request.urlopen("http://www.lyricsfreak.com/top_new/")
        songlist_new = songlist_new.read()
        songlist_new = songlist_new.decode()
        songlist_new = songlist_new.split('<tbody>')[1].split("</tbody>")[0]
        for topsong in re.findall(linkpattern, songlist_new):
            topsongs.append("http://www.lyricsfreak.com"+topsong)
        return topsongs
    except IndexError:
        # unable to read the song list page for HTML reasons
        return []

def readLyricsFromMetrolyrics(page):
    """
    Read website at page and return the lyrics part of the page as a readable string.
    """
    lyrics = urllib.request.urlopen(page)
    lyrics = lyrics.read()
    lyrics = lyrics.decode()
    try:
        lyrics = lyrics.split('<div id="lyrics-body-text">')[1].split("</div>")[0]
        htmltag = re.compile("<[^<>]*>")
        lyrics = re.sub(htmltag,  " / ", lyrics)
        lyrics = re.sub("\s+", " ", lyrics)
        return sent_tokenize(lyrics)
    except IndexError:
        # unable to read the song page for HTML reasons
        return []
def getTopSongPagesFromMetrolyrics():
    """
    Read list of most popular songs from http://www.metrolyrics.com/top100.html and return a list of URLs that lead to each
    song listed.
    """

    topsongs = []
    linkpattern = re.compile('((</span>)|("tmb tmb-xs">))\s*<a href="([^\"]*)"')
    songlist =  urllib.request.urlopen("http://www.metrolyrics.com/top100.html")
    songlist = songlist.read()
    songlist = songlist.decode()

    try:
        songlist = songlist.split('<ul class="top20 clearfix">')[1].split('<div class="grid_4">')[0]
        for topsong in re.findall(linkpattern, songlist):
            topsongs.append(topsong[-1])
        return topsongs
    except IndexError:
        # unable to read the song list page for HTML reasons
        return []

def tagLyricFragment(fragment):
    """
    Tag the song line fragment with the NLTK POS tagger.
    """
    tagged_fragment = pos_tag(fragment)
    return tagged_fragment


def tweetRandomSongLine():
    """
    Do the work. Open Top Song Page, select a song, select a line from the song,
    tokenize that line, replace some occurences of NN tokens with "something"
    and some others with their hypernyms ... and tweet the result
    """
    songlinksLyricsFreak = getTopSongPagesFromLyricsfreak()
    songlinksMetrolyrics = getTopSongPagesFromMetrolyrics()
    api = login()
    tweeted = False
    while not tweeted:
        # page choice: to introduce diversity
        pagechoice = random.randint(0,1)
        if pagechoice == 0:
            randomselection = songlinksLyricsFreak[random.randint(0, len(songlinksLyricsFreak)-1)]
            sents = readLyricsFromLyricsfreak(randomselection)
        else:
            randomselection = songlinksMetrolyrics[random.randint(0, len(songlinksMetrolyrics)-1)]
            sents = readLyricsFromMetrolyrics(randomselection)
        if sents != []:
            original_line = sents[random.randint(0, len(sents)-1)]
            # make sure no much-too-long lines are processed and then thrown away
            if len(original_line) < 200:
                outline = original_line
                tokens = tagLyricFragment(word_tokenize(original_line.replace("/", "")))
                for token in tokens:
                    word = token[0]
                    label = token[1]
                    decision = random.randint(0, 4)
                    # change two in three NN tokens
                    if label == "NN" and word.lower() not in ["thing", "way"]:
                        if decision == 0:
                            outline = outline.replace(" "+word+" ", " something ", 1)
                        elif decision > 0 and getHypernym.getHypernym(word) != "":
                            outline = outline.replace(" "+word+" ", " "+getHypernym.getHypernym(word)+" ", 1)
                    elif label == "RB":
                        # I wonder if this will be interesting: adverbs become "in some way" (adverbs are tricky)
                        if decision < 2:
                            outline = outline.replace(" "+word+" ", " in some way ", 1)
                    elif label == "PRP$":
                        # possessive pronouns become "somebody's"
                        if decision < 3:
                            outline = outline.replace(" "+word+" ", " somebody's ", 1)
                    elif label == "PRP":
                        # personal pronouns become "someone"
                        if decision < 2:
                            outline = outline.replace(" "+word+" ", " someone ", 1)
                if len(outline) < 141 and outline != original_line:
                    # tweet this!
                    outline = "\U0001F3B6 " + outline.strip(" /") + " \U0001F3B6"
                    api.update_status(status=outline)
                    tweeted = True

tweetRandomSongLine()
