import time
import grpc

import payment_pb2
import payment_pb2_grpc


channel = grpc.insecure_channel("localhost:50051")

payment_client = payment_pb2_grpc.PaymentServiceStub(channel)

failure_count = 0
CIRCUIT_THRESHOLD = 3

circuit_state = "CLOSED"

opened_at = None
RECOVERY_TIMEOUT = 5

def make_payment(order_id: int, amount: float):


    # Circuit breaker
    global failure_count, circuit_state, opened_at

    if circuit_state == "OPEN":
        if time.time() - opened_at >= RECOVERY_TIMEOUT:
            circuit_state = "HALF-OPEN"
            failure_count = 0
            print("CIRCUIT HALF-OPEN")
        else:
            raise Exception("CIRCUIT OPEN - Payment Service unavailable")

    for attempt in range(1, 4):

        try:
            print(f"PAYMENT ATTEMPT {attempt}")

            response = payment_client.Pay(
                payment_pb2.PaymentRequest(
                    order_id=order_id,
                    amount=amount
                ),
                timeout=3
            )

            # Success → reset failures
            # Success → reset failures and close circuit
            failure_count = 0
            circuit_state = "CLOSED"
            opened_at = None

            print("PAYMENT SUCCESS")

            return response

        except grpc.RpcError as error:

            if error.code() == grpc.StatusCode.DEADLINE_EXCEEDED:

                failure_count += 1

                print(
                    f"PAYMENT TIMEOUT on attempt {attempt} "
                    f"| failures = {failure_count}"
                )

                if failure_count >= CIRCUIT_THRESHOLD:
                    circuit_state = "OPEN"
                    opened_at = time.time()
                    print("CIRCUIT OPEN")

                    raise Exception(
                        "CIRCUIT OPEN - Payment Service unavailable"
                    )

                if attempt < 3:
                    time.sleep(1)
                    continue

            raise