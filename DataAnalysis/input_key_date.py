import datetime


class TakeInput:

    def __init__(self):
        pass

    def hashtag(self):
        return input("Enter hashtag: ")

    def from_date(self, req):
        if req == "Y" or req == "y":
            fromdate = input("Enter from date in YYYY-MM-DD format: ")
        else:
            fromdate = "1"
        return fromdate

    def to_date(self, req):
        if req == "Y" or req == "y":
            toDate = input("Enter to date in the same format: ")
            d1 = datetime.datetime(int(toDate.split("-")[0]),
                                   int(toDate.split("-")[1]), int(toDate.split("-")[2]), 23, 59, 59)
        else:
            d1 = datetime.datetime.now()
        return d1


if __name__ == '__main__':

    take_input = TakeInput()
    hashtag = take_input.hashtag()
    b = input("Do you want to enter date constraint? Y/N? ")
    from_date = take_input.from_date(b)
    to_date = take_input.to_date(b)
