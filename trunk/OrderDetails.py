class OrderDetails:
    """
    This is simply a holder class to easily pass all necessary order information between methods
    This could also be easily implemented as a type rather than a class
    """
    def __init__ (self,shares,symbol,orderType,duration,closeType,limitPrice = 0):
        self.shares = shares
        self.symbol = symbol
        self.orderType = orderType
        self.duration = duration
        self.closeType = closeType
        self.limitPrice = limitPrice