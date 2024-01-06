class CantGetFeedFromURL(Exception):
    """Some error has occured while trying to get data from feed URL."""

    pass


class CantSubscribeToFeed(Exception):
    """Some error has occured while trying to subscribe to feed."""

    pass


class FeedAlreadyExists(Exception):
    """User is already subscribed to the feed."""

    pass


class CantGetFeedInfoFromURL(Exception):
    """Can't retrieve mandatory feed info from URL."""

    pass
