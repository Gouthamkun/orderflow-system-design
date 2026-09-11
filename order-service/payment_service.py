from concurrent import futures

import grpc

import payment_pb2
import payment_pb2_grpc


class PaymentService(payment_pb2_grpc.PaymentServiceServicer):

    def Pay(self, request, context):
        import time
        if(request.order_id == 8):
            time.sleep(5)  # Simulate processing time
        print(
            f"PAYMENT REQUEST: order={request.order_id}, "
            f"amount={request.amount}"
        )

        return payment_pb2.PaymentResponse(
            success=True,
            message=f"Payment successful for order {request.order_id}"
        )


server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

payment_pb2_grpc.add_PaymentServiceServicer_to_server(
    PaymentService(),
    server
)

server.add_insecure_port("[::]:50051")

server.start()

print("Payment Service running on port 50051")

server.wait_for_termination()