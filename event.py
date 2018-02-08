class Event:

    def __init__(self, uid="", dateStart="", dateEnd="", summary="", location="",
                 description="", lastModified=""):
        self.uid = uid
        self.dateStart = dateStart
        self.dateEnd = dateEnd
        self.summary = summary
        self.location = location
        self.description = description
        self.lastModified = lastModified

