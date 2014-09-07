

class OldRouter(object):
    def db_for_read(self, model, **hints):
        if 'instance' in hints:
            db = hints['instance']._state.db
            if db:
                return db
        if model.__name__ == 'News':
            return 'old'

    def db_for_write(self, model, **hints):
        if 'instance' in hints:
            db = hints['instance']._state.db
            if db:
                return db
        if model.__name__ == 'News':
            return 'old'

