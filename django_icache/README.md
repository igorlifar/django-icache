# Django-icache

## About

This is Django app for "timeout-less" caching. It uses Django cache
frame work in the background, so cache backend configuration is absolutely
the same, as it has been. You can use Django cache framework for additional
caching as well.

This app consists of two main parts: ICache object and icache template tag.

## ICache object
This is used by icache template tag. Using this, you can provide some real-time
data invalidation. Examples are in the bottom of the page.

Methods:
* `incr(key)`: Increment value, stored by key. If there is no
such cache entry, stores 0 by givven key.

* `incr_many(keys)`: Does the same as 'incr', but for the list
of keys.

* `get_sum(keys)`: Returns sum of values, stored by givven keys.
If some value does'n exist, it is considered to be 0.

* `set_versioned(key, value, version)`: Saves value and version
by given key.

* `get_versioned(key, version)`: Returns value, stored by
set_versioned, if the stored version is equal to the given one;
else returns None and deletes cache entry.

## Template tag

Template tag will cache the contents of a template fragment until the
data, used in this fragment, is outdated.

Usage::

    {% load icache %}
    {% icache [token_1] [token_2] [token_3] ... [token_n] %}
        .. some expensive processing ..
    {% endicache %}

Each unique set of arguments will result in a unique cache entry.

"Version" of the template fragment - is the sum of values, stored
in cache by keys, equal to arguments, passed to tag (is some cache
entry doesn't exist, its value is considered to be 0). Rendered
template fragment is stored with it's version.

Stored template fragment is considered to be outdated if its
current "version" is not equal to the stred one.

## Examples

In template:

    {% load icache}
    {% icache 'movies-personal-rating' 'movies' user.id %}
        ... list of ordered by personal rating movies ...
    {% endicache %}

Here, for each user-unique request, a new cache entry with this template
fragment is created.

In models.py:

    from django_icache import icache
   
    ... some code ...

    def movie_cache_post_save(sender, **kwargs):
        icache.incr('movies')  # increments value, stored by 'movies' key

    post_save.connect(movie_cache_post_save, sender=Movie)

After saving some `Movie` object, all stored template fragments, containing
token `'movie'`, is considered to be outdated.
