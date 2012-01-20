class LogError(BaseException):
    
    info = None
    header = ""
    
    def __init__ (self, info, header=""):
        self.info = info
        self.header = header
        print "error: " + header
        try:
            print "error: " + info.to_s()
        except:
            print "cannot extract error details"