from loan.batchrunner import run_batch

if __name__ == "__main__":
    df = run_batch(use_mp=False)
    print(df)
