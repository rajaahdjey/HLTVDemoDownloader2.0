# HLTVDemoDownloader2.0

This is an updated version of HLTVDemoDownloader created by ReagentX. https://github.com/ReagentX/HLTVDemoDownloader

This would not have been possible for me to do without the original version so huge thanks to him for that! 

A few changes from the Reagent's version (henceforth referred to as the original) :  

1. The original one is created for python 2.7 - so there is no urllib2. The core changes involve making the code logic work for this new 'results' page instead of 'events' page and also to make the downloader function in python 3. This was a fun learning experience for me overall! 
2. This version does not focus on `Event ID` rather focuses on the newly available filters in the HLTV results page.
3. In my case, I use it to filter the time period, quality of matches (matches with higher ranked teams are denoted as having higher stars) and map name. I find that a lot of analysis is time bound / map bound so this would help with that. 
4. For my convenience, I also have some code to extract the rar files - as part of the code itself.
5. There are still a few things that I have which the user needs to edit the code directly for - may be someday I will do some housekeeping on the code! It serves the purpose right now though. (Date filters , extracted folder name, stars etc.,) 

Few more things to do : 
1. Avoid hardcoding inputs - right now only map name is having a separate variable
2. Move the extraction to a separate function and call only when needed may be?
3. Downloading is not mulitthreaded - with HLTV recently partnering with bitskins and providing much faster downloads, hopefully this can be implemented.
