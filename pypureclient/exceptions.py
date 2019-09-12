class PureError(Exception):
    """
    Exception type raised by Pure Storage code.
    """

    def __init__(self, reason=None):
        self.reason = reason
        super(PureError, self).__init__()

    def __str__(self):
        return 'PureError: {}'.format(self.reason)
