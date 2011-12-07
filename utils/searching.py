def get_terms(query):
    """Return a list of search terms from a query."""

    # Encode as UTF-8 for Solr.
    query = unicode(query).encode('utf-8')

    # Split into (non-empty) words.
    terms = filter(None, [term.strip() for term in query.split()])

    # TODO: Handle quotes, etc.

    return terms
