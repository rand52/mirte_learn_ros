import rclpy

class SubscriberExampleNode(Node):
   def __init__(self):
      super().__init__("subscriber_node")
      self._subscription = self.create_subscription(
         Range,
         "/io/distance/left",
         self.receive_message_callback,
         1
      )

   def receive_message_callback(self, message):
      self.get_logger().info("I got range: " + str(message.range))

def main():
   rclpy.init()
   my_subscriber_node = SubscriberExampleNode()
   try:
      rclpy.spin(my_subscriber_node)
   except KeyboardInterrupt:
      return