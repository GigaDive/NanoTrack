from processing_py import *
app = App(600,600) # create window: width, heightglobal x,y,z

def setup():
    global x,y,z
    x = 600/2
    y = 600/2
    z = 0

def draw():
    global x,y,z
    app.translate(x,y,z)
    app.rectMode(CENTER)
    app.rect(0,0,100,100)

    z += 1 # The rectangle moves forward as z increments.



# app = App(600,400) # create window: width, heightglobal x,y,z
# app.background(0,0,0) # set background:  red, green, blue
# app.fill(255,255,0) # set color for objects: red, green, blue
# app.rect(100,100,200,100) # draw a rectangle: x0, y0, size_x, size_y
# app.fill(0,0,255) # set color for objects: red, green, blue
# app.ellipse(100,200,50,50) # draw a circle: center_x, center_y, size_x, size_y
# app.ellipse(100,200,20,50) # draw a circle: center_x, center_y, size_x, size_y
# app.translate(width/2, height/2, 0)
# app.stroke(255)
# app.rotateX(PI/2)
# app.rotateZ(-PI/6)
# app.noFill()

# app.beginShape()
# app.vertex(-100, -100, -100)
# app.vertex( 100, -100, -100)
# app.vertex(   0,    0,  100)

# app.vertex( 100, -100, -100)
# app.vertex( 100,  100, -100)
# app.vertex(   0,    0,  100)

# app.vertex( 100, 100, -100)
# app.vertex(-100, 100, -100)
# app.vertex(   0,   0,  100)

# app.vertex(-100,  100, -100)
# app.vertex(-100, -100, -100)
# app.vertex(   0,    0,  100)

# app.endShape()

# app.redraw() # refresh the window
