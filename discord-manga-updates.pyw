import feedparser, requests, datetime, time, shelve

WEBHOOK = '[Discord WebHook Link HERE]'
SLEEP_TIME_SECONDS = 900    #sleep time in seconds

rss_feeds = {
    #add rss feeds in this format:
    #'[RSS/XML URL HERE]': ('[Author name HERE]', '[Discord Avatar HERE]'),

    #Bozo Test, uncomment to test for unreachable links
    #'BozoTest': (None, None)
}

#will store names of latest chapter of each manga
latest = {}


def parse(xml):
    #parse xml file
    chapter = feedparser.parse(xml)

    if chapter.bozo:
        #if xml link is unreachable, write to logs and send discord message
        logs.write(f'\n{now}: BOZO ALERT\nunable to reach {xml}')
        requests.post(WEBHOOK, data={"content":f'BOZO ALERT:\nunable to reach {xml}'})
        
        return 0

    manga = chapter.feed.title
    title = chapter.entries[0].title
    
    with shelve.open('latest_chapters.db') as cache:
    #open cache(stores latest chapter names)
    
        if title not in cache.values():
            #if chapter is new update dictionary and cache
            latest.update({manga:title})
            cache.update(latest)
            
            #write to logs
            logs.write(f'\n{now}:\nNew {manga} Chapter found!')

            link = chapter.entries[0].link
            image = chapter.feed.image.href
            pubDate = chapter.entries[0].published[0:16]

            #send post request
            post(manga, title, image, link, pubDate)
            
        else:
            #write to log if no new chapters
            logs.write(f'\n{now}:\nno new {manga} chapters')


def post(manga, title, image, link, pubDate):
    try:
        #attempt post request
        requests.post(WEBHOOK, json=
            {
                'username': author,
                'avatar_url': avatar,
                #'content': '<@&[RoleID]}>',
                #uncomment and paste Role ID to tag a role
                #you can also tag users by <@[UserID]>
                'embeds':
                [
                    {
                        'title': title,
                        'url': link, 
                        'description': f'New {manga} Chapter just dropped!\n{pubDate}',
                        'image':{'url': image}
                    }
                ]
            })
        
        #write to logs if successful
        logs.write('\nSuccessfully pushed POST request to Discord Webhook')
        
        
    except:
        #write to logs if failed
        logs.write('\nFAILED: unable to push POST request to Discord Webhook')


while True:
    for xml, (author, avatar) in rss_feeds.items():
        #current time
        now = datetime.datetime.today().strftime('%Y/%m/%d %H:%M:%S')

        #open log file
        with open('logs.txt', 'a') as logs:
            parse(xml)
    
    time.sleep(SLEEP_TIME_SECONDS)