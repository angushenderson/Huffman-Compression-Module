# Huffman-Compression-Module
Python module for compressing 7bit ascii text using the Huffman Compression Algorithm. The code compresses the text and writes it to a binary file (.bin), with header information so it can be decompressed.

## Using the module
To compress a text file and write to new file:
```
from HuffmanCoding import HuffmanFile
  
with open('text.txt', 'r') as input_file, HuffmanFile('compressed_text.bin', 'wb') as compressed_file:
    compressed_file.write_from_file(input_file)
```

To read a compressed file:
```
with HuffmanFile('compressed_text.bin', 'rb') as compressed_file, open('decompressed_text.txt', 'w') as output_file:
    compressed_file.read_to_file(output_file)
```
There are 2 modes that a Huffman binary file can be opened in:
1. 'rb' - read
2. 'wb' - write
These cannot be changed in the with statement

There are 4 main methods for using a HuffmanFile instance:
- For compressing the file:
  - `write_from_file(text_file)` - compressed and writes text from the text file to the binary compressed file
  - `write_from_string(text)` - compresses and writes text from the string to the binary compressed file
- For decompressing the file:
  - `read_to_file(file)` - decomrpesses and writes text to the passed text file
  - `read()` - decompresses and returns string of decompressed text
  
## Other object features
To print diagnostics while running the compression and decompression of files set `diagnostics=True`
The module only compresses 7bit ascii at the moment but in the future I would like to expand this to support the use of other text encoding such as utf-8 or use this algorithm to compress other media formats such as images or audio.
