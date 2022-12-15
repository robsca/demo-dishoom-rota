import tkinter as tk
import time

# create a window
window = tk.Tk()

# add a cartesian plane

width = 1200
height = 1200
size_sqaure = 25
canvas = tk.Canvas(window, width=width, height=height, bg="white")

# create a translator from tkinter_coordinates to cartesian_coordinates
def translate_to_cartesian(tk_x, tk_y):
    # center at bottom left
    return tk_x - width//2, height//2 - tk_y

# create a translator from cartesian_coordinates to tkinter_coordinates
def translate_to_tkinter(cart_x, cart_y):
    return cart_x +  width//2, height//2 - cart_y

# draw a line from (x1, y1) to (x2, y2)
def draw_line(x1, y1, x2, y2):
    canvas.create_line(
        *translate_to_tkinter(x1, y1),
        *translate_to_tkinter(x2, y2),
        fill="black",
        width=0.5,
    )

# create a cartesian grid   
for i in range(-width//2, height//2, size_sqaure):
    draw_line(i, -height//2, i, height//2)
    draw_line(-width//2, i, width//2, i)

# add numbers to the grid
for i in range(-width//2, height//2, 100):
    canvas.create_text(
        *translate_to_tkinter(i, 0),
        text=str(i),
        font=("Purisa", 8),
    )
    canvas.create_text(
        *translate_to_tkinter(0, i),
        text=str(i),
        font=("Purisa", 8),
    )
    
def draw_square(x, y, color = 'black', coords = True):
    canvas.create_rectangle(
        *translate_to_tkinter(x, y),
        *translate_to_tkinter(x + size_sqaure, y + size_sqaure),
        fill=color,
        outline='white',
        stipple="gray50"
    )
    # write the coordinates of the square
    if coords:
        canvas.create_text(
            *translate_to_tkinter(x + size_sqaure//2, y + size_sqaure//2),
            text=f"{y//size_sqaure}",
            font=("Purisa", 8),
            fill='white',
        )

# move orrigin to down left
canvas.create_line(
    *translate_to_tkinter(-width//2, 0),
    *translate_to_tkinter(width//2, 0),
    fill="black",
    width=2,
)
canvas.create_line(
    *translate_to_tkinter(0, -height//2),
    *translate_to_tkinter(0, height//2),
    fill="black",
    width=2,
)

# canvas with origin in lower left corner
canvas.grid(row=0, column=0, rowspan=20)
if __name__ ==  '__main__':
    # draw a square at (100, 100) with side length 50
    # create a list of input values
    array = [1,2,2,2,3,4,4,4,4,3,3,3,2,2,4,5,5,5,4,3,2]
    def plot(array):
        import matplotlib.pyplot as plt
        plt.plot(array)
        plt.show()

    button = tk.Button(window, text="Plot", command=lambda: plot(array))
    button.grid(row=8, column=1)

    for x, y in enumerate(array):
        draw_square(x*size_sqaure, y*size_sqaure, 'blue')

    # if the button is pressed, the window closes
    def total(array):
        for x, y in enumerate(array):
            for y_ in range(y):
                draw_square(x*size_sqaure, y_*size_sqaure, 'red', False)
            draw_square(x*size_sqaure, y*size_sqaure, 'blue')
            window.update()


    # add the button to the window
    button_total_hours = tk.Button(window, text="Total Hour", command=lambda: total(array))
    
    open_time = '8'
    min_hours = tk.Entry(window)
    # set text to 0
    min_hours.insert(0, "4")
    max_hours = tk.Entry(window)
    # set text to 0
    max_hours.insert(0, "9")
    colors = ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'brown', 'grey', 'black']


    def horizontal_count(array):
        # show the possible shifts using all the iterations
        lengths = [i for i in range(int(min_hours.get()), int(max_hours.get()) + 1)]
        bricks_shifts = [[e-50 for e in range(0, length)] for i,length in enumerate(lengths)]
        print(bricks_shifts)
        colors = ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'brown', 'grey', 'black']
        shifts_for_dragging = []

        for i, shift in enumerate(bricks_shifts):
            shift_for_dragging = []
            # add name of the shift
            canvas.create_text(
                *translate_to_tkinter(-100, -i*50 + 300 + size_sqaure),
                text=f"{i+int(min_hours.get())} hours",
                font=("Mono", 16),
                fill='black',
            )
            for j, brick in enumerate(shift):
                draw_square(-(j*size_sqaure)-200, -(i*50)+300, colors[i], False)
                shift_for_dragging.append((-(j*size_sqaure)-200, -(i*50)+300))
                window.update()
                time.sleep(0.1)

            shifts_for_dragging.append(shift_for_dragging)

            
        # scan the mouse position
        def select_y(event):
            #print(shifts_for_dragging)
            colors = ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'brown', 'grey', 'black']
            import random
            color = random.choice(colors)
            # round the mouse position to the nearest square
            x, y = translate_to_cartesian(event.x, event.y)
            x = x//size_sqaure*size_sqaure
            y = y//size_sqaure*size_sqaure
            print(y)      
            closest_index = 0      
            # now check if the mouse is in the range of the possible shifts
            for i, shift in enumerate(shifts_for_dragging):
                # get the closest shift
                if abs(y) < abs(shifts_for_dragging[closest_index][0][1]):
                    closest_index = i
            print(shifts_for_dragging[closest_index])
            def draw(event):
                x, y = translate_to_cartesian(event.x, event.y)
                x = x//size_sqaure*size_sqaure
                y = y//size_sqaure*size_sqaure
                for i, brick in enumerate(shifts_for_dragging[closest_index]):
                    draw_square(x+i*size_sqaure, y, color, False)
                    window.update()
                    time.sleep(0.1)
            canvas.bind('<ButtonRelease-1>', lambda event: draw(event))
        canvas.bind('<Button-1>', select_y)

    button = tk.Button(window, text="Horizontal Count", command=lambda: horizontal_count(array))
    
    #### UI

    button_total_hours.grid(row=0, column= 1)
    button.grid(row=1, column= 1)
    tk.Label(window, text="max Hours").grid(row=2, column=1)
    # add label to max hours
    tk.Label(window, text="min Hours").grid(row=4, column=1)
    # add open time to window

    max_hours.grid(row=3, column=1)
    min_hours.grid(row=5, column=1)

    '''Esteban'''
    def start(array, open_time, min_hours, max_hours):
        from Esteban import Esteban_
        esteban = Esteban_(array)
        rota, shifts = esteban.solving_(open_time, min_hours, max_hours)
        shifts = esteban.shifts
        print(rota)
        print('Esteban')
        print(len(shifts))
        # draw the rota
        big_container = []
        small_container = []
        for i in range(len(shifts)):
            this_shift = shifts[i]
            try:
                next_shift = shifts[i+1]
                # if start next shift is == end this shift
                if this_shift[1] == next_shift[0]:
                    small_container.append(this_shift)
                else:
                    small_container.append(this_shift)
                    big_container.append(small_container)
                    small_container = []
            except:
                small_container.append(this_shift)
                big_container.append(small_container)
        print('')
        print('')

        shifts_ = []
        for y,layer in enumerate(big_container):
            for shift in layer:
                shift_ = []
                print(shift)
                for x in range(shift[0], shift[1]):
                    shift_.append([x, y])
                shifts_.append(shift_)
            print('----')

        print('')
        print('')
        # draw the rota
        colors = ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'brown', 'grey', 'black', 'light blue', 'light green', 'light yellow', 'light orange', 'light purple', 'light pink', 'light brown', 'light grey', 'light black']
        for i, shift in enumerate(shifts_):
            for x, y in shift:
                draw_square(x*size_sqaure - (open_time*size_sqaure), y*size_sqaure- (open_time*size_sqaure), colors[i], False)
                window.update()
                
        print(len(shifts_))

    # solve the problem
    new_button = tk.Button(window, text="Algorithm", command=lambda: start(array, int(open_time), int(min_hours.get()), int(max_hours.get())))
    new_button.grid(row=6, column=1)

    # run the window
    window.mainloop()