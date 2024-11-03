import multiprocessing
import time

def worker(number):
    """Function that simulates some work by sleeping."""
    start_time = time.time()
    print(f"Worker {number} starting. Time of start {start_time:.5f}")
    time.sleep(2)  # Simulate a delay
    print("Testing if it works")
    print(f"Worker {number} done")

if __name__ == "__main__":
    processes = []
    # Start timing
    start_time = time.time()
    # Create and start multiple processes
    for i in range(5):
        p = multiprocessing.Process(target=worker, args=(i,))
        processes.append(p)
        p.start()
    # calculate time to complete these processes
    # Wait for all processes to complete
    for p in processes:
        p.join()

    # Calculate time to complete these processes
    end_time = time.time()
    elapsed_time = end_time - start_time

    print("All workers are done.")
    print(f"Total time taken: {elapsed_time:.2f} seconds")
