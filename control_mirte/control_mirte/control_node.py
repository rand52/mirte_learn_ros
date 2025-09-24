import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Range
from mirte_msgs.srv import SetMotorSpeed

class OurNode(Node):
    def __init__(self):
        super().__init__("subscriber_node")
        self.sub_left = self.create_subscription(
            Range,
            "/io/distance/left",
            self.receive_message_callback_left,
            1
        )
        self.sub_right = self.create_subscription(
            Range,
            "/io/distance/right",
            self.receive_message_callback_right,
            1
        )

        self.client_left = self.create_client(
            SetMotorSpeed,
            "/io/motor/right/set_speed")

        while not self.client_left.wait_for_service(timeout_sec=10.0):
            self.get_logger().info("Service left not available")

        self.get_logger().info("Initialized client left")
    
        self.client_right = self.create_client(
            SetMotorSpeed,
            "/io/motor/left/set_speed")

        while not self.client_right.wait_for_service(timeout_sec=10.0):
            self.get_logger().info("Service right not available")

        self.get_logger().info("Initialized client right")

        timer_period = 0.1  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def receive_message_callback_left(self, message):
        if message.range < 0:
            message.range = float('inf')
        self.left_dist = message.range

    def receive_message_callback_right(self, message):
        if message.range < 0:
            message.range = float('inf')
        self.right_dist = message.range

    def send_request(self, left, right):
        request = SetMotorSpeed.Request()
        request.speed = left
        future1 = self.client_left.call_async(request)
        self.get_logger().info("First done")
        request2 = SetMotorSpeed.Request()
        request2.speed = right
        future2 = self.client_right.call_async(request2)
        self.get_logger().info("Second done")
        return future1.result(), future2.result()

    def timer_callback(self):
        self.get_logger().info(f"Left {self.left_dist}; Right {self.right_dist}")
            # if sensordata < 30, turn
            # if sensordata >= 30, drive forward
        if self.left_dist < 0.3 and self.right_dist < 0.3:
            self.get_logger().info("Stop")
            self.send_request(0, 0)
        elif self.left_dist < 0.3:
            self.get_logger().info("Left")
            self.send_request(50, -50)
        elif self.right_dist < 0.3:
            self.get_logger().info("Right")
            self.send_request(-50, 50)
        else:
            self.get_logger().info("Forward")
            self.send_request(50, 50)


def main():
    rclpy.init()
    my_subscriber_node = OurNode()
    try:
        rclpy.spin(my_subscriber_node)
    except KeyboardInterrupt:
        return
