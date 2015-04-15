__author__ = 'Esther'
import urllib.request
import re
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk import pos_tag
import random
import tweepy
import config

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
    lyrics = lyrics.split("<!-- SONG LYRICS -->")[1].split("<!-- /SONG LYRICS -->")[0]
    htmltag = re.compile("<[^<>]*>")
    lyrics = re.sub(htmltag, " / ", lyrics)
    lyrics = re.sub("\s+", " ", lyrics)
    return sent_tokenize(lyrics)

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
    songlist = songlist.split('<tbody>')[1].split("</tbody>")[0]
    for topsong in re.findall(linkpattern, songlist):
        topsongs.append("http://www.lyricsfreak.com"+topsong)
    return topsongs

def readLyricsFromMetrolyrics(page):
    """
    Read website at page and return the lyrics part of the page as a readable string.
    """
    lyrics = urllib.request.urlopen(page)
    lyrics = lyrics.read()
    lyrics = lyrics.decode()
    lyrics = lyrics.split('<div id="lyrics-body-text">')[1].split("</div>")[0]
    htmltag = re.compile("<[^<>]*>")
    lyrics = re.sub(htmltag,  " / ", lyrics)
    lyrics = re.sub("\s+", " ", lyrics)
    return sent_tokenize(lyrics)

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

    songlist = songlist.split('<ul class="top20 clearfix">')[1].split('<div class="grid_4">')[0]
    for topsong in re.findall(linkpattern, songlist):
        topsongs.append(topsong[-1])
    return topsongs

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
    (Should become more interesting in the next update!) ... and tweet the result
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
        original_line = sents[random.randint(0, len(sents)-1)]
        outline = original_line
        tokens = tagLyricFragment(word_tokenize(original_line.replace("/", "")))
        #print(tokens)
        for token in tokens:
            word = token[0]
            label = token[1]
            decision = random.randint(0, 2)
            # change one in three NN tokens
            if label == "NN" and decision == 0:
                outline = outline.replace(word, "something")
        if len(outline) < 141 and outline != original_line:
            # tweet this!
            outline = "\U0001F3B6 " + outline.strip(" /") + " \U0001F3B6"
            api.update_status(status=outline)
            tweeted = True


tweetRandomSongLine()
