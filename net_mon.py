import time
import psutil
import argparse


def main():
    # setup the argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--record", help="record the the monitored traffic usage")
    parser.add_argument("-p", "--path", help="record the the monitored traffic usage")
    parser.add_argument("-s", "--silent", help="no continuous output to the console")
    parser.parse_args()

    interval = 1  # time between readings in seconds
    last_down = 0
    last_up = 0
    while True:
        # set current byte counters
        current_down = psutil.net_io_counters().bytes_recv
        current_up = psutil.net_io_counters().bytes_sent

        # only work with the counters once the have been cleared
        if last_down or last_up:
            counted_bytes = (current_down - last_down, current_up - last_up)
            push_bytes(counted_bytes, interval)

        # set current readings to be the latest
        last_down = current_down
        last_up = current_up

        # wait until the next reading interval
        time.sleep(interval)


def push_bytes(counted, interval):
    """
        print current network usage
    :param counted: bytes counted since the last interval
    :param interval: interval length in seconds
    :return:
    """
    traffic = (counted[0] / interval, counted[1] / interval)
    print("down: {:.1f}kb/s\tup: {:.1f}kb/s".format(traffic[0] / 1024.0, traffic[1] / 1024.0))


if __name__ == '__main__':
    main()
