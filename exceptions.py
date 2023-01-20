

class SpotiFileException(Exception):
    pass


class SpotifyClientException(SpotiFileException):
    pass


class SpotifyTrackException(SpotiFileException):
    pass


class SpotifyArtistException(SpotiFileException):
    pass
