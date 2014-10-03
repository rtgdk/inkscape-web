

class OldRouter(object):
    def db_for_read(self, model, **hints):
        if model.__name__ == 'News':
            return 'old'
        if 'instance' in hints:
            db = hints['instance']._state.db
            if db:
                return db

    def db_for_write(self, model, **hints):
        if model.__name__ == 'News':
            return 'old'
        if 'instance' in hints:
            db = hints['instance']._state.db
            if db:
                return db

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'auth' or \
           obj2._meta.app_label == 'auth':
           return True
        return None

