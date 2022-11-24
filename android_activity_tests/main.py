from tests import lock_unlock, suspend_resume

if __name__ == "__main__":
    suspend_resume(app="",
                   activity="",
                   iteration_of_test=1000,
                   time_sleep=0.7)
