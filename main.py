import payload_gen as pg
import multithread_controller as ctrl

start_time, end_time = ctrl.controller(166666, 5, 10, "output_file_TWO", 166667)

elapsed_time = end_time - start_time
print(f'Total elapsed Time: {round(elapsed_time/60,5)} minutes or {round(elapsed_time/(60*60),5)} hours.')
