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

def process_bmp(filename, message):
	with open(filename, 'rb+') as file:
		data = file.read()
		fileheader = data[:14]
		headerfield = fileheader[0:2].decode('ascii')
		#print(f'Headerfield: {headerfield}')

		if headerfield not in headerfields:
			raise(RuntimeError('BMP format not supported'))

		#filesize = struct.unpack('<i',fileheader[2:6])[0]
		#print(f'Size: {filesize} bytes')

		pixelarray_offset = struct.unpack('<i',fileheader[10:14])[0]


		dibheader = data[14:54] #BITMAPINFOHEADER size -> 40 bytes

		width = struct.unpack('<i',dibheader[4:8])[0]
		height = struct.unpack('<i',dibheader[8:12])[0]
		bitsperpixel = struct.unpack('<h',dibheader[14:16])[0]

		#print(f'Width: {width} pixels')
		#print(f'Height: {height} pixels')
		#print(f'Color depth: {bitsperpixel} bits')

		compressionmethod = struct.unpack('<i', dibheader[16:20])[0]
		#print(f'Compression method: {compressionmethods[compressionmethod]}')
		if compressionmethod not in noncompressed:
			raise(RuntimeError('BMP is compressed, not supported'))

		#numberofcolors = struct.unpack('<I',dibheader[32:36])[0]

		#print(f'Pixelarray offset: {pixelarray_offset}')

		pixelarray_size = int(width*height*bitsperpixel/8)

		#print(f'Pixelarray size: {pixelarray_size} bytes')

		if len(message) > pixelarray_size:
			raise RuntimeError('Image too small for message')
		
		print('Generating key...')
		key = genkey(len(message), pixelarray_offset, pixelarray_offset+pixelarray_size)
		print('Writing message...')
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

def readmessage(filename, key):
	with open(filename, 'rb') as file:
		result = ''
		for offset in key:
			file.seek(offset)
			result += file.read(1).decode('ascii')
		print(result)

def main():
	if len(sys.argv) < 4 or sys.argv[1] not in ('e','d'):
		print('Usage: bmpmessage.py e(ncode) [filename] [message]\n       bmpmessage.py d(ecode) [filename] [key]')
		return
	mode = sys.argv[1]
	filename = sys.argv[2]

	if mode == 'e':
		message = ' '.join(sys.argv[3:])
		process_bmp(filename, message)
	else:
		key = map(int,sys.argv[3].split('#'))
		readmessage(filename,key)

if __name__ == '__main__':
	main()