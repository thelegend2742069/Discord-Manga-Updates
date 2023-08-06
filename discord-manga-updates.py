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
    chapter = feedparser.parse(xml)
    if chapter.bozo:
        logs.write(f'\n{now}: BOZO ALERT\nunable to reach {xml}')
        requests.post(webhook, data={"content":f'BOZO ALERT:\nunable to reach {xml}'})
        return 0

    manga = chapter.feed.title
    title = chapter.entries[0].title
    
    with shelve.open('latest_chapters.db') as cache:
        if title not in cache.values():
            latest.update({manga:title})

            logs.write(f'\n{now}:\nNew {manga} Chapter found!')

            link = chapter.entries[0].link
            image = chapter.feed.image.href
            pubDate = chapter.entries[0].published[0:16]

            post(title, link, manga, image, pubDate)
            cache.update(latest)

        else:
            logs.write(f'\n{now}:\nno new {manga} chapters')


def post(title, link, manga, image, pubDate):
    try:
        requests.post(webhook, json=
            {
                'username': author,
                'avatar_url': avatar,
                #'content': '<@&[RoleI]}>',
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
        
        logs.write('\nSuccessfully pushed POST request to Discord Webhook')
        
        
    except:
        logs.write('\nFAILED: unable to push POST request to Discord Webhook')


while True:
    for xml, (author, avatar) in rss_feeds.items():
        
        now = datetime.datetime.today().strftime('%Y/%m/%d %H:%M:%S')

        with open('logs.txt', 'a') as logs:
            parse(xml)
    
    time.sleep(900)