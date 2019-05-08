import multiprocessing
from servicelayer import env

INGESTOR_THREADS = min(8, multiprocessing.cpu_count())
INGESTOR_THREADS = env.to_int('INGESTOR_THREADS', INGESTOR_THREADS)
