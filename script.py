import time
import numpy as np
import pydirectinput
import pandas as pd

import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams     
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations, WindowFunctions


def main ():

    # Finding Ganglion board
    params = BrainFlowInputParams ()
    params.board_id = 1
    board_id = 1
    params.serial_port = 'COM5'
    sampling_rate = BoardShim.get_sampling_rate (board_id)

    # Defining values - min_val + vals_mean will change after
    time_thres =  10
    max_val = -100000000000
    vals_mean = 0
    num_samples = 5000
    samples = 0

    BoardShim.enable_dev_board_logger ()

    board = BoardShim (board_id, params)
    board.prepare_session ()

    # Connecting to the board
    if board_id == brainflow.board_shim.BoardIds.GANGLION_BOARD.value:
        board.config_board ('x1060000X')

    board.start_stream (45000)

    # Calibration
    print("Calibrating...")
    time.sleep(5)
    data = board.get_board_data()

    print("flex and relax your arm a couple of times")

    while(samples < num_samples):

        # Collecting the maximum and average values while calibrating
        data = board.get_board_data() 
        if(len(data[1]) > 0):
            DataFilter.perform_rolling_filter (data[1], 2, AggOperations.MEAN.value)
            vals_mean += sum([data[1,i]/num_samples for i in range(len(data[1]))]) 
            samples += len(data[1])
            if(np.amax(data[1]) > max_val):
                max_val = np.amax(data[1])
    # Subtract maximum from average values to get the threshold
    flex_thresh = 0.5*((max_val - vals_mean)**2) 


    print("threshold")
    print(flex_thresh)


    print("The Calibration is Complete! You can now start playing!")
    prev_time = int(round(time.time() * 1000))

    while True:
        # Getting data from the board
        data = board.get_board_data()

        if(len(data[1]) > 0):
            DataFilter.perform_rolling_filter (data[1], 2, AggOperations.MEAN.value) 
            if((int(round(time.time() * 1000)) - time_thres) > prev_time): 

                prev_time = int(round(time.time() * 1000)) # update time 
                # Check channel 1
                for element in data[1]:
                    # Check if the data surpasses the threshold
                    if(((element - vals_mean)**2) >= flex_thresh):
                        pydirectinput.press("up") # If it does then press the "up" key
                        break
                    else:
                        break
                # Check channel 2
                for element in data[3]:
                    # Check if the data surpasses the threshold
                    if(((element - vals_mean)**2) >= flex_thresh):
                        pydirectinput.press("down") # I fit does then press the "down" key
                        break
                    else:
                        break

    board.stop_stream ()                   
    board.release_session ()


if __name__ == "__main__":
    main ()
