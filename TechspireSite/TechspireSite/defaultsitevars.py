# Default sitevars for testing purposes. Generate a different secret key for production/development
class SiteVars:
    DjangoKey = 'vdxiih@c53!x^baaj^9c%(u5a0@q&f0^9m3b=$#+(s(oz*$0$z'
    Debug = True
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.sqlite3',
        }
    }
    allowed_hosts = []
