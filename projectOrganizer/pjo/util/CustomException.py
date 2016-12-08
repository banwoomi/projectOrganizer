



import logging

errLogger = logging.getLogger("errLog")

class CustomException():
    
    def exceptionHandler(self, exception):
     
        print "$$$$$$$$$$$$$$$$$$$1"
        print exception
        print exception.args[0]
        print exception.args[1]
        print "$$$$$$$$$$$$$$$$$$$2"

    
    




# #your_view.py
# raise CustomApiException(333, "My custom message")
# 
# #json response
# {
#   "status_code": 333,
#   "message": "My custom message"
# }


