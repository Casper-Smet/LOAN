from loan.batchrunner import run_batch

df = run_batch(use_mp=False)
print(df)
