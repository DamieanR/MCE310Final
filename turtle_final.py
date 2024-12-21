#!/usr/bin/env python
import rospy
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
import math

class TurtleController:
    def __init__(self):
        rospy.init_node('turtle_controller', anonymous=True)
        self.velocity_publisher = rospy.Publisher('/turtle1/cmd_vel', Twist, queue_size=10)
        self.pose_subscriber = rospy.Subscriber('/turtle1/pose', Pose, self.update_pose)
        self.pose = Pose()
        self.rate = rospy.Rate(10)

    def update_pose(self, data):
        self.pose = data

    def move_forward(self, distance):
        vel_msg = Twist()
        start_x = self.pose.x
        start_y = self.pose.y

        while True:
            vel_msg.linear.x = 1.0
            self.velocity_publisher.publish(vel_msg)

            current_distance = math.sqrt((self.pose.x - start_x)**2 + (self.pose.y - start_y)**2)
            if current_distance >= distance:
                break

            self.rate.sleep()

        vel_msg.linear.x = 0
        self.velocity_publisher.publish(vel_msg)

    def turn(self, angle):
        vel_msg = Twist()
        angular_speed = 1.0

        target_angle = self.pose.theta + angle

        target_angle = math.atan2(math.sin(target_angle), math.cos(target_angle))

        while True:
            angle_diff = math.atan2(math.sin(target_angle - self.pose.theta), math.cos(target_angle - self.pose.theta))

            if abs(angle_diff) < 0.01:
                break

            vel_msg.angular.z = angular_speed if angle_diff > 0 else -angular_speed
            self.velocity_publisher.publish(vel_msg)

            self.rate.sleep()

        vel_msg.angular.z = 0
        self.velocity_publisher.publish(vel_msg)


    def draw_square(self, side_length):
        for _ in range(4):
            self.move_forward(side_length)
            self.turn(math.radians(90))

    def draw_triangle(self, side_length):
        for _ in range(3):
            self.move_forward(side_length)
            self.turn(math.radians(120))

    def draw_circle(self, radius):
        vel_msg = Twist()
        vel_msg.linear.x = 1.0
        vel_msg.angular.z = 1.0 / radius

        circumference = 2 * math.pi * radius
        time_needed = circumference / vel_msg.linear.x

        t0 = rospy.Time.now().to_sec()
        while rospy.Time.now().to_sec() - t0 < time_needed:
            self.velocity_publisher.publish(vel_msg)
            self.rate.sleep()

        vel_msg.linear.x = 0
        vel_msg.angular.z = 0
        self.velocity_publisher.publish(vel_msg)

    def draw_rectangle(self, length, width):
        for _ in range(2):
            self.move_forward(length)
            self.turn(math.radians(90))
            self.move_forward(width)
            self.turn(math.radians(90))

if __name__ == "__main__":
    try:
        turtle1 = TurtleController()

        shape = input('What shape should I follow? (square, triangle, circle, rectangle): ').lower()

        if shape == "square":
            side_length = float(input("Enter the side length: "))
            turtle1.draw_square(side_length)
        elif shape == "triangle":
            side_length = float(input("Enter the side length: "))
            turtle1.draw_triangle(side_length)
        elif shape == "circle":
            radius = float(input("Enter the radius: "))
            turtle1.draw_circle(radius)
        elif shape == "rectangle":
            length = float(input("Enter the length: "))
            width = float(input("Enter the width: "))
            turtle1.draw_rectangle(length, width)
        else:
            print("Invalid shape selected!")

    except rospy.ROSInterruptException:
        pass
