'''
Not used by the site. Can probably be deleted.
'''
def handle_uploaded_article(f):
    destination = open('some/file/name.txt', 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
