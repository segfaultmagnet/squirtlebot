class Player(object):
    '''Players are part of the league'''
    def __init__(self, data):
        self.player_id = data['userProfileId']
        self.first_name = data['firstName'].strip()
        self.last_name = data['lastName'].strip()
        self.user_name = data['userName']
        self.is_creater = data['isLeagueCreator']
        self.is_manager = data['isLeagueManager']

    def __repr__(self):
        return 'Player(%s: %s)' % (self.name())

    def name(self):
        return '%s %s' % (self.first_name, self.last_name)
