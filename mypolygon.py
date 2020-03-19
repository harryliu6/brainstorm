import turtle
import math

bob = turtle.Turtle()
print(bob)
# turtle.mainloop()
turtle.color("black")
turtle.pendown()
for i in range(4):
    bob.fd(100)
    bob.lt(90)
turtle.penup()


# Above is for 4.1 and 4.2#

# 4.3 1
def square(t):
    for i in range(4):
        t.fd(150)
        t.lt(90)


square(bob)


# # 4.3 2
def square(t, length):
    for i in range(4):
        t.fd(length)
        t.lt(90)


square(bob, 40)


# 4.3 3
def polygon(t, n, length):
    degree = 180 * (n - 2) / n
    for i in range(n):
        t.fd(length)
        t.lt(180 - degree)


polygon(bob, n=7, length=70)


# # 4.3 4

def circle(t, r):
    circumference = 2 * math.pi * r
    n = int(circumference / 3) + 3
    length = circumference / n
    polygon(t, n, length)


circle(bob, 5)

# 4.12 (4.3)

turtle.pendown()


def iso(t, n, length):
    peak_angle = 360 / n  # get degree of the iso
    angle = peak_angle / 2
    y = length * math.sin(angle * math.pi / 180)
    for i in range(n):
        t.fd(length)
        t.lt(90 + angle)
        t.fd(2 * y)
        t.lt(90 + angle)
        t.fd(length)
        t.rt(180)


iso(bob, 12, 100)

turtle.penup()
