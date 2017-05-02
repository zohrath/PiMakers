'''
This is the main program of the system
'''

import datetime

if __name__ == '__main__':


    start = datetime.datetime.now()
    print("Hello")
    end = datetime.datetime.now()
    elapsed = end - start
    print(elapsed.seconds)

    while True:
        if ((end - start).seconds > 0):
            start = datetime.datetime.now()
            print("More than 1 second elapsed")
        end = datetime.datetime.now()