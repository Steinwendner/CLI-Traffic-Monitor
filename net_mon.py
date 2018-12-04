import time
import psutil
import argparse
import os


def main():
    # setup the argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--record", help="record the the monitored traffic usage", action="store_true")
    parser.add_argument("-s", "--silent", help="no continuous output to the console", action="store_true")
    arguments = parser.parse_args()

    path_to_recordings = None
    path_to_current_log = None

    record_queue = None

    # setup recording dir if -r is given
    if arguments.record:
        path_to_recordings = os.path.expanduser("~/.network_traffic")
        try:
            os.mkdir(path_to_recordings)
        except FileExistsError:
            # directory already exists
            pass

        # get a list of all files in the folder
        # file count starts with 0
        # first file: tm_0.log, second file: tm_1.log
        only_tm_files = list()
        for f in os.listdir(path_to_recordings):
            if os.path.isfile(os.path.join(path_to_recordings, f)) and f.startswith("tm_"):
                only_tm_files.append(f)
        path_to_current_log = os.path.join(path_to_recordings, "tm_{}.log".format(len(only_tm_files)))
        record_queue = list()
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
            if not arguments.silent:
                print_traffic(counted_bytes, interval)
            if arguments.record:
                record_queue.append("{} {} {}\n".format(int(time.time()), counted_bytes[0], counted_bytes[1]))
                if len(record_queue) >= 30:
                    with open(path_to_current_log, "a+", encoding="utf-8") as f:
                        for r in record_queue:
                            f.write(r)
                    record_queue.clear()

        # set current readings to be the latest
        last_down = current_down
        last_up = current_up

        # wait until the next reading interval
        time.sleep(interval)


def print_traffic(counted, interval):
    """
    Prints the current network usage to the console.

    :param counted: bytes counted since the last interval
    :param interval: interval length in seconds
    :return:
    """
    traffic = (counted[0] / interval, counted[1] / interval)
    print("down: {:4.1f}kb/s\tup: {:4.1f}kb/s".format(traffic[0] / 1024.0, traffic[1] / 1024.0))


if __name__ == '__main__':
    main()
