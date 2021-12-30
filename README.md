# YouTubeTranscriptDownloader for Python
This can be used to download transcripts of YouTube videos from YouTube for videos which has transcripts uploaded by the channel as well as the ones auto-generated by YouTube.
Download as srt file.

# Requirements
 json,
 re,
 time,
 pandas,
 requests,
 webdriver_manager,
 selenium,
 
 # Usage
 ```
  import ytTranscript
  
  # https://www.youtube.com/watch?v=EDul4jJQA2I
  # see tlang options
  
  ytTranscript.Download('EDul4jJQA2I', tlang=TLangs.English)
 
 ```

