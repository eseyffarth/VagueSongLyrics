# VagueSongLyrics
Tweeting vague song lyrics. They're a little more vague than the original lines.

# Sample Output
See [@VagueLyrics](https://www.twitter.com/VagueLyrics) for sample output.

# How this works
The code reads a list of popular songs from either http://www.metrolyrics.com/top100.html or http://www.lyricsfreak.com/top/ and picks a random song. It then opens the song lyrics page of that song and picks a random sentence from the song to tweet. Before the sentence is tweeted, it is vagueified in several ways. Nouns, adverbs, possessive pronouns and personal pronouns have a chance to be replaced by either a vague placeholder ("something", "in some way", "somebody's", "someone") or a hypernym/related noun.
