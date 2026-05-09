replace = [
        #[a, b] replaces a to b (RGB values)
        ['4dcc8e', 'cc4d4d'],
        ['38705e', '703838'],
        ['f60e97', '9345f8'],
        ['a9d88e', 'd88e8e'],
        ['635b84', '845b5b'],
        ]

def shader(image, width, height): #changes the image if image doesnt have palette
    offset_step = (len(image) - width * height * 8) // height
    result = ""
    for i in range(height):
        for j in range(i * width * 8 + i * offset_step, (i + 1) * width * 8 + i * offset_step, 8):
            result += image[j:j+2]
            not_found = True
            for k in replace:
                if image[j+2:j+8] == k[0]:
                    result += k[1]
                    not_found = False
                    break
            if not_found:
                result += image[j+2:j+8]
        result += image[(i + 1) * width * 8 + i * offset_step: (i + 1) * width * 8 + i * offset_step + 2]
    return result

def convert_palette(palette): #changes palette when image has it
    result = ''
    for i in range(0, len(palette), 6):
        not_found = True
        for k in replace:
            if palette[i:i + 6] == k[0]:
                result += k[1]
                not_found = False
                break
        if not_found:
            result += palette[i:i + 6]
    return result





from zlib import compress, decompress
from binascii import unhexlify, crc32

def int_to_binary(num): #converts into 32-bit binary data
    a = hex(num)[2:]
    a = '0' * (8 - len(a)) + a
    return unhexlify(a)

def modify(filename):
    #getting file's data (lengths, data, crc)
    lengths = {}
    data = {}
    crc = {}
    file = open(filename, "rb")
    header = file.read(8)
    end = b''
    length = file.read(4)
    field = file.read(4)
    lengths[field] = length
    length = int(length.hex(), 16)
    while field != b'IEND':
        data[field] = file.read(length)
        crc[field] = file.read(4)
        length = file.read(4)
        field = file.read(4)
        lengths[field] = length
        length = int(length.hex(), 16)
    end = file.read()
    file.close()
    output = ''
    output_type = b'IDAT'
    #editing data with shader() function or by changing palette
    if data.get(b'PLTE') == None:
        output = compress( unhexlify( shader(  decompress(data[b'IDAT']).hex(), int(data[b'IHDR'][:4].hex(), 16), int(data[b'IHDR'][4:8].hex(), 16)  ) ) )
    else:
        output_type = b'PLTE'
        output = unhexlify( convert_palette(data[b'PLTE'].hex()) )
    file = open(filename, "wb")
    file.write(header)
    for i in data:
        if i == output_type:
            file.write(int_to_binary(len(output)))
            file.write(i)
            file.write(output)
            file.write(int_to_binary(crc32(output, crc32(output_type))))
        else:
            file.write(lengths[i])
            file.write(i)
            file.write(data[i])
            file.write(crc[i])
    file.write(b'\x00\x00\x00\x00IEND' + end)
    file.close()

from os import listdir
for i in listdir():
    if len(i) > 4 and i[-4:] == '.png' and i != 'output.png':
        modify(i)
