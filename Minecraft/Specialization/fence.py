from PIL import Image
import random
import modular_math

# Configurable image metadata
home = "C:\\Users\\mike_000\\Desktop\\"
img = Image.open(home + "planks_oak_2.png")
board_widths = [13, 13, 12, 13, 13]
edge_depth = 4
grout = 0
bordering = [0, 0, 0, 0]
horizontal = True

random.seed()

if not horizontal:
    img = img.transpose(Image.ROTATE_270)

resize_factor = img.size[0] / 16

fence_side = img.crop([0, 0, img.size[0], img.size[1]])
fence_top = img.crop([0, 0, img.size[0], img.size[1]])
gate_side = img.crop([0, 0, img.size[0], img.size[1]])

boards = []
boards_unadorned = []

top = 0
bottom = 0

for width in board_widths:
    top = bottom
    bottom += width
    board = img.crop([0, top, img.size[0], bottom])
    boards.append(board)
    boards_unadorned.append(board.crop([bordering[0], bordering[1], board.size[0] - bordering[2], board.size[1] - bordering[3]]))

    bottom += grout


def resize(img, size, edge=edge_depth):
    resized = Image.new('RGBA', size)

    # Split apart elements of plank
    center = img.crop([edge, edge, img.size[0] - edge, img.size[1] - edge])
    top_left = img.crop([0, 0, edge, edge])
    top_edge = img.crop([edge, 0, img.size[0] - edge, edge])
    top_right = img.crop([img.size[0] - edge, 0, img.size[0], edge])
    right_edge = img.crop([img.size[0] - edge, edge, img.size[0], img.size[1] - edge])
    bottom_right = img.crop([img.size[0] - edge, img.size[1] - edge, img.size[0], img.size[1]])
    bottom_edge = img.crop([edge, img.size[1] - edge, img.size[0] - edge, img.size[1]])
    bottom_left = img.crop([0, img.size[1] - edge, edge, img.size[1]])
    left_edge = img.crop([0, edge, edge, img.size[1] - edge])

    # Stretch horizontal grain
    top_edge = top_edge.resize([size[0] - (edge * 2), top_edge.size[1]])
    center = center.resize([size[0] - (edge * 2), center.size[1]])
    bottom_edge = bottom_edge.resize([size[0] - (edge * 2), bottom_edge.size[1]])

    # Repeat vertical grain
    temp_height = modular_math.ceil(size[1] - (edge * 2) / img.size[1] - (edge * 2))

    left_edge_large = Image.new('RGBA', (edge, temp_height))
    center_large = Image.new('RGBA', (center.size[0], temp_height))
    right_edge_large = Image.new('RGBA', (edge, temp_height))

    for repeat in range(temp_height):
        left_edge_large.paste(left_edge, (0, left_edge.size[1] * repeat, edge, left_edge.size[1] * (repeat + 1)))
        center_large.paste(center, (0, center.size[1] * repeat, center.size[0], center.size[1] * (repeat + 1)))
        right_edge_large.paste(right_edge, (0, right_edge.size[1] * repeat, edge, right_edge.size[1] * (repeat + 1)))

    left_edge = left_edge_large.crop([0, 0, left_edge.size[0], size[1] - (edge * 2)])
    center = center_large.crop([0, 0, center.size[0], size[1] - (edge * 2)])
    right_edge = right_edge_large.crop([0, 0, right_edge.size[0], size[1] - (edge * 2)])

    # Put pieces back together
    resized.paste(center, (edge, edge, resized.size[0] - edge, resized.size[1] - edge))
    resized.paste(top_left, (0, 0, edge, edge))
    resized.paste(top_edge, (edge, 0, resized.size[0] - edge, edge))
    resized.paste(top_right, (resized.size[0] - edge, 0, resized.size[0], edge))
    resized.paste(right_edge, (resized.size[0] - edge, edge, resized.size[0], resized.size[1] - edge))
    resized.paste(bottom_right, (resized.size[0] - edge, resized.size[1] - edge, resized.size[0], resized.size[1]))
    resized.paste(bottom_edge, (edge, resized.size[1] - edge, resized.size[0] - edge, resized.size[1]))
    resized.paste(bottom_left, (0, resized.size[1] - edge, edge, resized.size[1]))
    resized.paste(left_edge, (0, edge, edge, resized.size[1] - edge))

    return resized


def scale(coordinates):
    scaled = []
    for element in coordinates:
        scaled.append(int(element * resize_factor))
    return scaled


def rand():
    return random.randint(0, len(boards) - 1)

# FENCE SIDE
# Top Beam
top_beam = resize(boards[rand()], scale([16, 3]))
fence_side.paste(top_beam.crop(scale([10, 0, 16, 3])), scale([0, 1, 6, 4]))
fence_side.paste(top_beam.crop(scale([0, 0, 6, 3])), scale([10, 1, 16, 4]))

# Bottom Beam
bottom_beam = resize(boards[rand()], scale([16, 3]))
fence_side.paste(bottom_beam.crop(scale([10, 0, 16, 3])), scale([0, 7, 6, 10]))
fence_side.paste(bottom_beam.crop(scale([0, 0, 6, 3])), scale([10, 7, 16, 10]))

# Center post
center_post = resize(boards[rand()], scale([16, 4]))
center_post = center_post.transpose(Image.ROTATE_90)
center_post = center_post.transpose(Image.FLIP_LEFT_RIGHT)

fence_side.paste(center_post, scale([6, 0, 10, 16]))

# FENCE TOP
horizontal_post = resize(boards[rand()], scale([16, 2]))
fence_top.paste(horizontal_post.crop(scale([10, 0, 16, 2])), scale([0, 7, 6, 9]))
fence_top.paste(horizontal_post.crop(scale([0, 0, 6, 2])), scale([10, 7, 16, 9]))

vertical_post = resize(boards[rand()], scale([12, 2])).transpose(Image.ROTATE_270)
vertical_post = vertical_post.transpose(Image.FLIP_TOP_BOTTOM)
fence_top.paste(vertical_post.crop(scale([0, 6, 2, 12])), scale([7, 0, 9, 6]))
fence_top.paste(vertical_post.crop(scale([0, 0, 2, 6])), scale([7, 10, 9, 16]))


fence_top.paste(resize(boards_unadorned[rand()], scale([4, 4]), 1), scale([6, 6, 10, 10]))

# GATE SIDE
post = boards_unadorned[rand()].transpose(Image.ROTATE_270)
post = post.transpose(Image.FLIP_TOP_BOTTOM)
gate_side.paste(resize(post, scale([2, 11]), 1), scale([0, 0, 2, 11]))

post = boards_unadorned[rand()].transpose(Image.ROTATE_270)
post = post.transpose(Image.FLIP_TOP_BOTTOM)
gate_side.paste(resize(post, scale([2, 9]), 1), scale([6, 1, 8, 10]))

post = boards_unadorned[rand()].transpose(Image.ROTATE_270)
post = post.transpose(Image.FLIP_TOP_BOTTOM)
gate_side.paste(resize(post, scale([2, 9]), 1), scale([8, 1, 10, 10]))

post = boards_unadorned[rand()].transpose(Image.ROTATE_270)
post = post.transpose(Image.FLIP_TOP_BOTTOM)
gate_side.paste(resize(post, scale([2, 11]), 1), scale([14, 0, 16, 11]))

gate_side.paste(resize(boards_unadorned[rand()], scale([4, 3]), 1), scale([2, 1, 6, 4]))
gate_side.paste(resize(boards_unadorned[rand()], scale([4, 3]), 1), scale([10, 1, 14, 4]))
gate_side.paste(resize(boards_unadorned[rand()], scale([4, 3]), 1), scale([2, 7, 6, 10]))
gate_side.paste(resize(boards_unadorned[rand()], scale([4, 3]), 1), scale([10, 7, 14, 10]))

fence_side.save(home + "fence_side.png")
fence_top.save(home + "fence_top.png")
gate_side.save(home + "gate_side.png")

fence_side.show()
fence_top.show()
gate_side.show()
