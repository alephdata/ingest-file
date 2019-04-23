import multiprocessing
from servicelayer import env

INGESTOR_THREADS = env.to_int(
    'INGESTOR_THREADS', min(8, multiprocessing.cpu_count())
)

BALKHASH_BACKEND_ENV = env('BALKHASH_BACKEND_ENV', 'LEVELDB')
