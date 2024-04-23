from multiprocessing import cpu_count, Process
import MINEPROCESS

def worker(num):
    """worker function"""
    print("Worker", num)
    MINEPROCESS.main()
    return

if __name__ == '__main__':
    num_processes = cpu_count()
    processes = []
    for i in range(num_processes):
        p = Process(target=worker, args=(i,))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    print("end program")