from django import template
from django.core.cache import cache
from icache import icache


register = template.Library()


@register.tag(name="icache")
def do_icache(parser, token):

    """
    This will cache the contents of a template fragment until the
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

    Example::

        In template:

            {% load icache}
            {% icache 'movies-personal-rating' 'movies' user.id %}
                ... list of ordered by personal rating movies ...
            {% endicache %}

        Here, for each user-unique request, a new cache entry with this template
        fragment is created.

        In models.py:
            from django_icache import icache

            def movie_cache_post_save(sender, **kwargs):
                icache.incr('movies')  # increments value, stored by 'movies' key

            post_save.connect(movie_cache_post_save, sender=Movie)

        After saving some 'Movie' object, all stored template fragments, containing
        token 'movie', is considered to be outdated.

    """

    bits = token.split_contents()[1:]
    tokens, vars = [], []
    for t in bits:
        if t[0] == t[-1] and t[0] in ('"', "'"):
            tokens.append(t[1:-1])
        else:
            vars.append(parser.compile_filter(t))

    nodelist = parser.parse(('endicache',))
    parser.delete_first_token()

    return IcacheNode(nodelist, tokens, vals)


class IcacheNode(template.Node):
    def __init__(self, nodelist, tokens, vars):
        self.nodelist = nodelist
        self.vars = vars
        self.tokens = tokens

    def render(self, context):
        tokens = self.tokens + map(lambda x: unicode(x.resolve(context, True)), self.vals)
        key = '#'.join(tokens)

        version = icache.get_sum(tokens)
        output = icache.get_versioned(key, version)  # returns None if invalidated

        if output is None:
            output = self.nodelist.render(context)
            icache.set_versioned(key, output, version)

        return output
