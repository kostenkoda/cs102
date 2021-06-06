import scraputils
import db

news = scraputils.get_news('https://news.ycombinator.com/newest', n_pages = 20)

s = db.session()
for new in news:
    if len(new.keys()) == 5:
        _new = db.News(
        title = new['title'],
        author=new['author'],
        url=new['url'],
        comments=new['comments'],
        points=new['points']
        )
        s.add(_new)
s.commit()
