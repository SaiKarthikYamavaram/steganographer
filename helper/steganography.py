from PIL import Image


def __change_last_2_bits__(image_pixel_values, data_bits):
    return image_pixel_values >> 2 << 2 | data_bits


def hide_data_to_image(data_to_hide):
    input_file_path = ".\\static\\images\\encrypt\\download.png"
    output_file_path = ".\\encrypted_output\\" + \
        "_with_hidden_file" + "." + input_file_path.split(".")[-1]
    image = Image.open(input_file_path).convert('RGB')
    pixels = image.load()

    data_to_hide += b"\0\0\0\0"

    data_stack = list()

    for data in data_to_hide:
        data = bytes([data])

        data = int.from_bytes(data, byteorder="big")
        chunk_stack = list()
        for i in range(4):
            last_two_bits = data & 0b11
            chunk_stack.append(last_two_bits)
            data = data >> 2

        chunk_stack.reverse()
        data_stack.extend(chunk_stack)

    while len(data_stack) % 3 != 0:
        data_stack.append(0)

    data_stack.reverse()

    image_x_index, image_y_index = 0, 0

    while data_stack:
        pixel_val = pixels[image_x_index, image_y_index]

        pixel_val = (__change_last_2_bits__(pixel_val[0], data_stack.pop()),
                     __change_last_2_bits__(pixel_val[1], data_stack.pop()),
                     __change_last_2_bits__(pixel_val[2], data_stack.pop()))

        pixels[image_x_index, image_y_index] = pixel_val

        if image_x_index == image.size[0] - 1:
            image_x_index = 0
            image_y_index += 1
        else:
            image_x_index += 1

    image.save(output_file_path)


def extract_message_from_image(input_file_path):

    image = Image.open(input_file_path).convert('RGB')
    pixels = image.load()
    data_stack = list()
    end_of_msg = False

    for image_y_index in range(image.size[1]):
        for image_x_index in range(image.size[0]):

            pixel = pixels[image_x_index, image_y_index]

            data_stack.append(pixel[0] & 0b11)
            data_stack.append(pixel[1] & 0b11)
            data_stack.append(pixel[2] & 0b11)

            if len(data_stack) >= 16 and set(data_stack[-16:]) == set(b"\x00"):
                end_of_msg = True
                break

        if end_of_msg:
            # print(data_stack)
            break

    if not end_of_msg:
        return False
    # print("data stack",data_stack)
    data = bytes()

    for i in range(0, len(data_stack) - 4, 4):
        chunk = data_stack[i:i + 4]
        recovered_int = 0
        recovered_int |= chunk[0] << 6
        recovered_int |= chunk[1] << 4
        recovered_int |= chunk[2] << 2
        recovered_int |= chunk[3]

        if len(data) >= 3 and recovered_int == 0 and set(data[-3:]) == set(b"\x00"):
            data += bytes([recovered_int])
            break
        else:
            data += bytes([recovered_int])

    if end_of_msg:
        data = data[:-4]
    print(data)
    return data
