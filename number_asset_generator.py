from PIL import Image, ImageDraw, ImageFont

def create_image(number, save_location, bg_color="#F7D879", num_color="#000000"):
    img_size=100
    if abs(number - 7) == 1:
        num_color = '#A30000'
    # Create a new image with alpha channel
    image = Image.new('RGBA', (img_size, img_size), (0, 0, 0, 0))

    # Draw a circle
    draw = ImageDraw.Draw(image)
    draw.ellipse([(0, 0), image.size], fill=bg_color)

    # Check if Minion Pro font is available
    try:
        font = ImageFont.truetype("MinionPro-Medium", img_size/2) # Adjust size as needed
    except IOError:
        print("Minion Pro font is not available. Switching to default font.")
        font = ImageFont.load_default()

    # Add the number
    draw.text((img_size/2, img_size/2), str(number), fill=num_color, anchor="mm", font=font)

    # Draw small circles
    radius = int(img_size/25*1.5/2)  # Adjust as needed
    circle_pos_y = int( img_size * (25-7.6) / 25 )
    distance_between_circles = int(2*radius/2)
    num_circles = 6 - abs(number-7)
    left_circle_loc = int( img_size/2 - (num_circles - 1) * (radius + distance_between_circles / 2) )

    # for now, let's assume num_circles is 1
    for ii in range(num_circles):
        circle_pos_x = left_circle_loc + ii * (2 * radius + distance_between_circles)
        left_up_point = [circle_pos_x - radius, circle_pos_y - radius]
        right_down_point = [circle_pos_x + radius, circle_pos_y + radius]
        draw.ellipse(left_up_point + right_down_point, fill=num_color)



    # Save the image
    image.save(save_location, "PNG")

# Generate images for numbers 2 to 12
for i in range(2, 13):
    if i != 7:
        create_image(i, f"./assets/images/{i}.png")

