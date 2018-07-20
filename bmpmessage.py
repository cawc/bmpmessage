import sys, struct, argparse
from random import randint

headerfields = { #TODO: support more types
	'BM'
}

compressionmethods = {
	0: 'BI_RGB',
	1: 'BI_RLE8',
	2: 'BI_RLE4',
	3: 'BI_BITFIELDS',
	4: 'BI_JPEG',
	5: 'BI_PNG',
	6: 'BI_ALPHABITFIELDS',
	11:'BI_CMYK',
	12:'BI_CMYKRLE8',
	13:'BI_CMYKRLE'
}

noncompressed = {
	0,
	11
}

def process_bmp(filename, message, mode):
	with open(filename, 'rb+') as file:
		data = file.read()
		fileheader = data[:14]
		headerfield = fileheader[0:2].decode('ascii')

		if headerfield not in headerfields:
			raise(RuntimeError('BMP format not supported'))

		#filesize = struct.unpack('<i',fileheader[2:6])[0]

		pixelarray_offset = struct.unpack('<i',fileheader[10:14])[0]


		dibheader = data[14:54] #BITMAPINFOHEADER size -> 40 bytes

		width = struct.unpack('<i',dibheader[4:8])[0]
		height = struct.unpack('<i',dibheader[8:12])[0]
		bitsperpixel = struct.unpack('<h',dibheader[14:16])[0]

		compressionmethod = struct.unpack('<i', dibheader[16:20])[0]
		if compressionmethod not in noncompressed:
			raise(RuntimeError('BMP is compressed, not supported'))

		#numberofcolors = struct.unpack('<I',dibheader[32:36])[0]

		pixelarray_size = int(width*height*bitsperpixel/8)

		if len(message) > pixelarray_size:
			raise RuntimeError('Image too small for message')
		
		print('Generating key...')
		key = genkey(len(message), pixelarray_offset, pixelarray_offset+pixelarray_size)
		print('Writing message...')
		if mode == 'es':
			randomiseimage(pixelarray_offset, pixelarray_offset+pixelarray_size, file)
		writemessage(key, message, file)
		key = '#'.join(map(str,key))
		print(f'Message written. Key = {key}')

def genkey(messagelength, minoff, maxoff):
	key = []
	while len(key) < messagelength:
		off = randint(minoff, maxoff)
		if off not in key:
			key.append(off)
	return key

def writemessage(key, message, file):
	if len(key) != len(message):
		raise(RuntimeError('Key does not belong to message'))
	for i in range(len(key)):
			file.seek(key[i])
			file.write(message[i].encode('ascii'))

def randomiseimage(minoff, maxoff, file):
	for i in range(minoff, maxoff):
		file.seek(i)
		file.write(randint(0,255).to_bytes(1,'little'))

def readmessage(filename, key):
	with open(filename, 'rb') as file:
		result = ''
		for offset in key:
			file.seek(offset)
			result += file.read(1).decode('ascii')
		print(result)

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('mode', choices=['e','d','es'], help='(e)ncode (d)ecode (es)ecure (overwrites image)')
	parser.add_argument('filename', help='name of file/path to file')
	parser.add_argument('mk', nargs='+', help='message to encode or key to decode, depending on mode option')
	args = parser.parse_args()



	if args.mode == 'e' or args.mode == 'es':
		message = ' '.join(args.mk)
		process_bmp(args.filename, message, args.mode)
	elif args.mode == 'd':
		key = map(int,args.mk[0].split('#'))
		readmessage(args.filename, key)

if __name__ == '__main__':
	main()
