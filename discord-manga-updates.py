import feedparser, requests, datetime, time, shelve

webhook = '[Discord WebHook Link HERE]'

rss_feeds = {
    #add rss feeds in this format:
    #'[RSS/XML URL HERE]': ('[Author name HERE]', '[Discord Avatar HERE]'),

    #Bozo Test
    #'BozoTest': (None, None)
}

latest = {}


def parse(xml):
    chapter = feedparser.parse(xml)                                                         #parse xml file

    if chapter.bozo:                                                                        #check for bozo
        logs.write(f'\n{now}: BOZO ALERT\nunable to reach {xml}')                               #write bozo alert to logs
        requests.post(webhook, data={"content":f'BOZO ALERT:\nunable to reach {xml}'})          #send bozo alert to discord
        
        return 0

    manga = chapter.feed.title
    title = chapter.entries[0].title
    
    with shelve.open('latest_chapters.db') as cache:                                        #open cache(stores latest chapter name)
        if title not in cache.values():                                                         #check if chapter is new
            latest.update({manga:title})

            logs.write(f'\n{now}:\nNew {manga} Chapter found!')                                     #write latest chapter to log

            link = chapter.entries[0].link
            image = chapter.feed.image.href
            pubDate = chapter.entries[0].published[0:16]

            post(title, link, manga, image, pubDate)                                                #send post request
            cache.update(latest)                                                                    #update cache(latest chapter name)

        else:                                                                                   #write to log if no new chapters
            logs.write(f'\n{now}:\nno new {manga} chapters')


def post(title, link, manga, image, pubDate):
    try:                                                                                        #attempt post request
        requests.post(webhook, json=
            {
                'username': author,
                'avatar_url': avatar,
                #'content': '<@&[RoleID]}>',
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
        
        logs.write('\nSuccessfully pushed POST request to Discord Webhook')                     #write to logs if successful
        
        
    except:
        logs.write('\nFAILED: unable to push POST request to Discord Webhook')                  #write to logs if failed


while True:
    for xml, (author, avatar) in rss_feeds.items():
        
        now = datetime.datetime.today().strftime('%Y/%m/%d %H:%M:%S')                           #current time

        with open('logs.txt', 'a') as logs:                                                     #open logs.txt
            parse(xml)
    
    time.sleep(900)                                                                             #sleep for 15 minutes(900 secs)