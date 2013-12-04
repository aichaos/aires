"""RiveScript Brain for Aires."""

from aires.brains import Brain
import rivescript

class RiveScript(Brain):
    def init(self, params):
        self.rs = rivescript.RiveScript()
        self.rs.load_directory(params['replies'])
        self.rs.sort_replies()

    def reply(self, username, message):
        return self.rs.reply(username, message)
