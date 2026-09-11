import grpc

import payment_pb2
import payment_pb2_grpc


channel = grpc.insecure_channel("localhost:50051")

client = payment_pb2_grpc.PaymentServiceStub(channel)

response = client.Pay(
    payment_pb2.PaymentRequest(
        order_id=5,
        amount=499.0
    )
)

print("SUCCESS:", response.success)
print("MESSAGE:", response.message)