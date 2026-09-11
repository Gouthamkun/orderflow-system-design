import time

from app.payment_client import make_payment


# First: deliberately fail with order 8
print("\n=== FAILURE PHASE ===")

for i in range(1, 2):
    print(f"\nREQUEST {i}")

    try:
        make_payment(8, 499)
    except Exception as e:
        print("RESULT:", e)


# Wait for circuit recovery
print("\nWaiting 6 seconds for circuit recovery...")
time.sleep(6)


# Recovery probe: order 9 is healthy
print("\n=== RECOVERY PHASE ===")

try:
    make_payment(9, 499)
except Exception as e:
    print("RESULT:", e)


print("\n=== FINAL REQUEST ===")

try:
    make_payment(9, 499)
except Exception as e:
    print("RESULT:", e)