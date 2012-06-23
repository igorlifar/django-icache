from django.core.cache import cache


class ICache(object):

    """
    This provides some useful functions for 'timeout-less' caching.

    Methods:
        incr(key): Increment value, stored by key. If there is no
        such cache entry, stores 0 by givven key.

        incr_many(keys): Does the same as 'incr', but for the list
        of keys.

        get_sum(keys): Returns sum of values, stored by givven keys.
        If some value does'n exist, it is considered to be 0.

        set_versioned(key, value, version): Saves value and version
        by given key.

        get_versioned(key, version): Returns value, stored by
        set_versioned, if the stored version is equal to the given one;
        else returns None and deletes cache entry.

    """

    timeout = 60 * 60 * 24 * 5

    def incr(self, key):
        if not cache.has_key(key):
            cache.set(key, 1, self.timeout)
        else:
            cache.incr(key)

    def incr_many(self, keys):
        values = cache.get_many(keys)
        for key in keys:
            if key in values:
                values[key] += 1
            else:
                values[key] = 0

        cache.set_many(values, self.timeout)

    def get_sum(self, keys):
        objects = cache.get_many(keys)
        s = 0
        for k, v in objects.iteritems():
            s = s + v

        return s

    def set_versioned(self, key, value, version):
        cache.set(key, {
            'value': value,
            'version': version
        }, self.timeout)

    def get_versioned(self, key, version):
        obj = cache.get(key)
        if obj != None:
            if obj['version'] == version:
                return obj['value']
            else:
                cache.delete(key)
        return None

icache = ICache()
