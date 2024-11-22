import pandas as pd
import urllib.parse, urllib.request
from urllib import parse
from youtube_transcript_api import YouTubeTranscriptApi
import json


class Script_Exctractor:
    #NUM_OF_WORDS is depend on options
    def __init__(self,vid,setTime,NUM_OF_WORDS = 5):
        self.vid = vid
        self.scriptData:list = []
        self.setTime = setTime
        self.wikiUserKey = "dgvbwjfonhpzjpdjjkzpgefbiifvfz"
        self.NUM_OF_WORDS = NUM_OF_WORDS

    # youtube script extraction
    def Extract(self):
        # Preprocessing URL to obtain YouTube video ID
        parsed_url = parse.urlparse(self.vid)
        vid = parse.parse_qs(parsed_url.query)['v'][0]

        # Fetching the transcript
        transcript = YouTubeTranscriptApi.get_transcript(vid, ['en', 'en-US'])

        # Splitting transcript into time intervals
        sentences = []
        sentence = ''
        next_time_boundary = self.setTime
        for segment in transcript:
            if segment['start'] >= next_time_boundary:
                sentences.append(sentence.strip())
                sentence = ''
                next_time_boundary += self.setTime
            sentence += segment['text'] + ' '
        sentences.append(sentence.strip())

        # Processing the transcript
        self.scriptData = [s.replace(u'\xa0', u' ').replace(u'\n', u' ').replace(u'  ', u' ') for s in sentences]

        for i in range(len(self.scriptData)):
            text = self.scriptData[i].replace(u'\xa0', u' ').replace(u'\n',u' ').replace(u'  ',u' ')
            self.scriptData[i] = text

    def CallWikifier(self, text, lang="en", threshold=0.8, numberOfKCs=10):
        # Prepare the URL.
        data = urllib.parse.urlencode([
                ("text", text), ("lang", lang),
                ("userKey", self.wikiUserKey),
                ("pageRankSqThreshold", "%g" % threshold),
                ("applyPageRankSqThreshold", "true"),
                ("nTopDfValuesToIgnore", "200"),
                ("nWordsToIgnoreFromList", "200"),
                ("wikiDataClasses", "false"),
                ("wikiDataClassIds", "false"),
                ("support", "false"),
                ("ranges", "false"),
                ("minLinkFrequency", "3"),
                ("includeCosines", "false"),
                ("maxMentionEntropy", "2")
                ])
        url = "http://www.wikifier.org/annotate-article"
        # Call the Wikifier and read the response.
        req = urllib.request.Request(url, data=data.encode("utf8"), method="POST")
        with urllib.request.urlopen(req, timeout = 60) as f:
            response = f.read()
            response = json.loads(response.decode("utf8"))

        sorted_data = sorted(response['annotations'], key=lambda x: x['pageRank'], reverse=True)
        # Output the annotations.
        num = 0
        result = []
        for annotation in sorted_data:
            if num < numberOfKCs:
                result.append({"title":annotation["title"],"url":annotation["url"],"pageRank":annotation["pageRank"]})

            num += 1

        res = result
        result = []
        return res

    def UrltoWiki(self):
        self.Extract()

        number = 1
        results = []
        for text in self.scriptData:
            print(f"{number} segemnt")
            results.append(self.CallWikifier(text=text, numberOfKCs=self.NUM_OF_WORDS))
            number += 1

        wiki_data = pd.DataFrame()
        seg_no = 1

        for seg_item in results:
            seg_df = pd.DataFrame(seg_item)
            seg_df['seg_no'] = seg_no
            seg_df['understand']=0
            wiki_data = pd.concat([wiki_data,seg_df])
            seg_no = seg_no + 1
        wiki_data.index = range(len(wiki_data))
        return wiki_data

if __name__ == "__main__":

    print("main")
