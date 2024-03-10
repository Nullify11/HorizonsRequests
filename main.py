import payload_Gen as pg
import JPL_multithread as jpl
import threading

lock = threading.Lock()

print(pg.pay_gen_lock('output_file_100', lock))
