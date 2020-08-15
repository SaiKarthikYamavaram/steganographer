from PIL import Image
import filecmp
from getopt import getopt
from sys import argv


def __change_last_2_bits__(image_pixel_values, data_bits):
    return image_pixel_values >> 2 << 2 | data_bits


def hide_data_to_image(data_to_hide):
    """
    This function hides the data_to_hide inside the image located at input_file_path,
    and saves this modified image to output_file_path.

    DOESN'T WORK WITH JPEG IMAGES, PNG ARE FULLY SUPPORTED

    ## In future, it will also support Encryption of the data_to_hide by default

    Parameters
        ----------
        input_file_path : str
            The path to the image file in which data is to be hidden
        data_to_hide : bytes
            The data to be hidden in input image file
        output_file_path : str
            The path to the modified image file with the hidden data

    """
    input_file_path = "D:\\mini-project\\flask\\steganographer\\static\\images\\encrypt\\download.png"
    output_file_path = "D:\\mini-project\\flask\\steganographer\\encrypted_output\\" + \
        "_with_hidden_file" + "." + input_file_path.split(".")[-1]
    image = Image.open(input_file_path).convert('RGB')
    pixels = image.load()

    # End data_to_hide with 4 '\0' characters
    data_to_hide += b"\0\0\0\0"

    print(f"* INFO : Size of data to be hidden : {len(data_to_hide)} bytes")
    print(
        f"* INFO : Max Size of data that can be hidden : {(image.size[0]*image.size[1]*6)//8} bytes")

    if len(data_to_hide) > (image.size[0]*image.size[1]*6) // 8:
        print("* ERROR : Cannot hide file inside Image")
        print("* ERROR : Size of file to be hidden exceeds max file size")
        print("* TIP \t: Choose a bigger resolution image, 4K or 8K")
        return

    # We will break the data into chunks of 2 bits and save it to this stack in
    # reversed order ( So that we can pop elements )
    data_stack = list()

    for data in data_to_hide:
        data = bytes([data])
        # Get integer value of byte
        data = int.from_bytes(data, byteorder="big")
        chunk_stack = list()

        # Extracting 2 bits 4 times, 8 bits or 1 byte
        for i in range(4):
            last_two_bits = data & 0b11                 # Extract last two bits
            # Push these bits to stack in reversed order
            chunk_stack.append(last_two_bits)
            data = data >> 2                            # Remove those last two bits

        chunk_stack.reverse()                           # Correct the order of chunk_stack
        # Push items in correct order
        data_stack.extend(chunk_stack)

    while len(data_stack) % 3 != 0:
        # Make the length of stack divisible by 3 so that we can hide data properly in a Pixel
        # Because in one pixel we can hide 3 times 2 bits ( one element of this list )
        data_stack.append(0)

    # Reverse the data_stack to that we can pop elements
    data_stack.reverse()

    image_x_index, image_y_index = 0, 0

    while data_stack:
        # Pixel at index x and y
        pixel_val = pixels[image_x_index, image_y_index]

        # Hiding data in all 3 channels of each Pixel
        pixel_val = (__change_last_2_bits__(pixel_val[0], data_stack.pop()),
                     __change_last_2_bits__(pixel_val[1], data_stack.pop()),
                     __change_last_2_bits__(pixel_val[2], data_stack.pop()))

        # Save pixel changes to Image
        pixels[image_x_index, image_y_index] = pixel_val

        # If reached the end of X Axis
        if image_x_index == image.size[0] - 1:
            # Increment on Y Axis and reset X Axis
            image_x_index = 0
            image_y_index += 1
        else:
            # Increment on X Axis
            image_x_index += 1

    print(f"* INFO : Saving image to {output_file_path}")
    image.save(output_file_path)


def extract_message_from_image(input_file_path):

    image = Image.open(input_file_path).convert('RGB')
    pixels = image.load()

    # List where we will store the extracted bits
    data_stack = list()
    end_of_msg = False

    for image_y_index in range(image.size[1]):
        for image_x_index in range(image.size[0]):
            # Read pixel values traversing from [0, 0] to the end
            pixel = pixels[image_x_index, image_y_index]

            # Extract hidden message in chunk of 2 bits from each Channel
            data_stack.append(pixel[0] & 0b11)
            data_stack.append(pixel[1] & 0b11)
            data_stack.append(pixel[2] & 0b11)

            if len(data_stack) >= 16 and set(data_stack[-16:]) == set(b"\x00"):
                # We encountered 4 '\0' characters, that means our hidden message ends here
                end_of_msg = True
                break

        if end_of_msg:
            break

    if not end_of_msg:
        # That means we didn't encountered any '\0' character
        print("WARNING : Incomplete Hidden Message")
        print("WARNING : Image may be corrupted or no Message was hidden in this Image")

    data = bytes()

    for i in range(0, len(data_stack) - 4, 4):
        # Extract 2 bits 4 times i.e 8 bits ( We will get one UTF-8 Character)
        chunk = data_stack[i:i + 4]

        # The integer value of byte we will extract from the image
        recovered_int = 0

        # Extracting 8th and 7th bit respectively
        recovered_int |= chunk[0] << 6
        # Extracting 6th and 5th bit respectively
        recovered_int |= chunk[1] << 4
        # Extracting 4th and 3rd bit respectively
        recovered_int |= chunk[2] << 2
        # Extracting 2nd and 1st bit respectively
        recovered_int |= chunk[3]

        if len(data) >= 3 and recovered_int == 0 and set(data[-3:]) == set(b"\x00"):
            # 4 '\0' characters found, end of hidden file
            data += bytes([recovered_int])
            break
        else:
            # Putting extracted byte (8 bits) to the right place
            data += bytes([recovered_int])

    if end_of_msg:                                      # If the hidden file is complete
        # Remove last 4 '\0' characters
        data = data[:-4]

    # print(f"* INFO : Saving hidden file to {output_file_path}")
    print(f"* INFO : Size of hidden file recovered : {len(data)} bytes")
    return data
