import tree
import os
import _io
import sys


class HuffmanTools:
    """
    Class containing functions for comrpessing, decompressing and formatting Huffman Compressed files
    Inherited by another class to make more userfrieldly and allows for more flexability if ever want to use
    this algorithm to compress files other than text.
    """
    def __init__(self):
        self.compression_codes = {}
        # Information regarding bit length of each part of the header - if 0 then length is undefined
        self.header_info = {'text_length': 32, 'tree_leaves': 16, 'postorder_tree': 0}

    def generate_frequency_table(self, text: str) -> dict:
        """
        Generates a dictionary of the frequencies of each character in the provided string
        :param text: String to gather frequencies
        :return frequency: Dictionary of frequency of each character in string
        """
        frequency = {}
        for char in text:
            if not char in frequency:
                frequency[char] = 0
            frequency[char] += 1
        return frequency

    def plant_forest(self, frequency_table: dict) -> list:
        """
        Generates a list of Tree objects in increasing order of frequency from frequency
        dictionary returned from the generate_frequency_table method
        :param frequency_table: Dictionary returned from generate_frequency_table method
        :return forest: List of Tree objects in ascending order of frequency
        """        
        forest = [tree.Tree(key, value) for key, value in sorted(frequency_table.items(), key=lambda item: item[1])]
        return forest

    def merge_trees(self, forest: list) -> tree.Tree:
        """
        Merges all trees in a forest until there is only 1 root tree with pointers
        to all sub roots in the forest - This is the formation of the huffman compression
        tree
        :param forest: list of tree.Tree objects returned from plant_forest method
        :return new_tree: tree.Tree objects as the huffman compression tree
        """
        if len(forest) == 1:
            # Only 1 tree in the forest
            new_tree = tree.Tree(None, forest[0].frequency, forest[0])

        # Multiple trees to merge in the forest
        while len(forest) > 1:
            new_tree = tree.Tree(None, forest[0].frequency + forest[1].frequency, forest[0], forest[1])
            del forest[:2]

            for index, tree_node in enumerate(forest):
                if new_tree.frequency < tree_node.frequency:
                    forest = forest[:index] + [new_tree] + forest[index:]
                    break

                elif index == len(forest) - 1:
                    forest.append(new_tree)
                    break
            
        return new_tree

    def get_binary_code(self, binary_list: list) -> str:
        """
        Takes in a list of binary - i.e. ['0', '1', '0'] and returns them
        in a nice string for ease of handling when processing and
        inputting into file
        :param binary_list: list of individual binary as strings i.e ['0', '1', '0']
        :return bits: Converts the provided binary_list into a more readable and useful string
        """
        bits = ""
        for bit in binary_list:
            if bit is not None:
                bits += str(bit)
        return bits 

    def generate_compression_codes(self, tree: tree.Tree, code=[], top=0) -> dict:
        """
        Traverses tree and generates comrpession codes for each leaf in
        the huffman tree
        :param tree: The tree that will be traversed
        :param code: Input list of None values of length of tree.depth -1. Use param - [None] * self.huffman_tree.depth after
                     calculating tree depth - 1.
        :param top: Leave blank - for method computation only
        :return self.compression_codes: Dictionary of key character and item of code
            i.e {'a': '010'}, used for getting the compression codes of each character
            without the need for the huffman compression tree
        """
        if tree.left:
            code[top] = 0
            self.generate_compression_codes(tree.left, code, top+1)
        if tree.right:
            code[top] = 1
            self.generate_compression_codes(tree.right, code, top+1)

        if not tree.left and not tree.right:
            self.compression_codes[tree.symbol] = self.get_binary_code(code)
        code[top-1] = None

        if all(bit is None for bit in code):
            return self.compression_codes

    def format_postorder_tree_for_header(self, postorder):
        """
        """
        bitstream = ''
        i = 0
        while i < len(postorder):
            if postorder[i] == '0':
                bitstream += '0'
            elif postorder[i] == '1':
                bitstream += '1'
                bitstream += "{0:07b}".format(ord(postorder[i+1]))
                i += 1
            i += 1
        # To indicate the end of the tree
        bitstream += '0'
        return bitstream

    def generate_file_header(self, text, huffman_tree):
        """
        """
        header = ""
        # integer sating the length of the text
        try:
            bit_format = "{0:0" + str(self.header_info['text_length']) + "b}"
            header += bit_format.format(len(text))
        except:
            raise UnicodeEncodeError("Text is too long to be represent in file header - need to increase header size")
        # Get postorder sequence
        postorder = tree.get_tree_postorder(huffman_tree)
        # integer stating the number of nodes in the postorder sequence
        if len(postorder) > 0:
            bit_format = "{0:0" + str(self.header_info["tree_leaves"]) + "b}"
            header += bit_format.format(len(postorder) + 1)   # +1 as that has been added to indicate the end of the sequence
        else:
            sys.exit("Compression Failed: Please generate compression codes before running this function, by running - \n generate_frequency_table(), plant_forest(), merge_trees(), generate_compression_codes()")
        # Add the actual postorder tree
        header += self.format_postorder_tree_for_header(postorder)
        # Binary postorder string with padding so that len() % 8 == 0
        header = self.pad_bitstream(header)
        header = self.get_byte_array(header)
        return header

    def generate_file_bytestream(self, text: str) -> bytes:
        """
        Converts text that is being compressed into bytestream for adding to the binary compression file
        :param text: String of text that is being compressed
        :return bytestream: String converted into bytes - a form that will work when inserting into binary file
        """
        bitstream = ''
        # Encodes each character in the text
        for char in text:
            bitstream += str(self.compression_codes[char])
        bitstream = self.pad_bitstream(bitstream)
        # Converts string into byte array
        bytestream = self.get_byte_array(bitstream)
        return bytes(bytestream)

    def pad_bitstream(self, bitstream: str) -> str:
        """
        Applies padding to the end of a bitstream so that it can fit in in a byte array - so that
        len() % 8 == 0
        :param bitstream: string of 0's and 1's to be padded
        :return bitstream: inputted bitstream but with padding at the end
        """
        padding = 8 - len(bitstream) % 8
        for i in range(padding):
            bitstream += '0'
        return bitstream

    def get_byte_array(self, bitstream: str) -> bytearray:
        """

        """
        byte_array = bytearray()
        for i in range(0, len(bitstream), 8):
            try:
                byte = bitstream[i: i+8]
            except:
                sys.exit("Compression Failed: Make sure to pad the bitstream before trying to convert to bytearray by running the pad_bitstream() function")
            byte_array.append(int(byte, 2))
        return byte_array

    def extract_file_bitstream(self, file_object: _io.BufferedReader) -> str:
        """
        Converts a file object into a string of 0's and 1's for easy processing down the road
        :param file_object:
        :return bitstream:
        """
        bitstream = ""
        while (byte := file_object.read(1)):
            bitstream += "{0:08b}".format(int.from_bytes(byte, byteorder='big'))
        return bitstream

    def extract_header_from_bitstream(self, bitstream: str) -> (int, list):
        """
        Extract the header information from a file bitstream - length of text and postorder huffman tree
        :param bitstream: String of binary extracted from binary file - full file
        :return file_length: Integer: number of characters in the body of the file
        :return postorder_huffman_tree: list of nodes of huffman decompression tree in postorder format
        """
        file_length = int(bitstream[:self.header_info['text_length']], base=2)
        tree_size = int(bitstream[self.header_info['text_length']: self.header_info['text_length'] + self.header_info['tree_leaves']], base=2)

        # Extract the tree from header
        postorder_huffman_tree = []
        bitstream_index = 0
        current_tree_index = 0
        while current_tree_index < tree_size:
            current_tree = bitstream[self.header_info['text_length'] + self.header_info['tree_leaves'] + bitstream_index]
            if current_tree == '0':
                postorder_huffman_tree.append(None)
            elif current_tree == '1':
                current_tree = bitstream[self.header_info['text_length'] + self.header_info['tree_leaves'] + bitstream_index + 1: 
                                         self.header_info['text_length'] + self.header_info['tree_leaves'] + bitstream_index + 8]
                character = chr(int(self.get_binary_code(current_tree), base=2))
                postorder_huffman_tree.append(character)
                bitstream_index += 7
                current_tree_index += 1

            bitstream_index += 1
            current_tree_index += 1

        return file_length, postorder_huffman_tree

    def calculate_binary_tree_header_length(self, postorder_tree_list: list) -> int:
        """
        Calculates the bit length of the binary tree stored in the file header from a given postorder list
        :param postorder_tree_list: List of tree in postorder
        :return length: Bit length of the binary tree stored in the file header
        """
        length = 0
        for node in postorder_tree_list:
            if node == None:
                length += 1
            else:
                length += 8
        # Count the padding as well
        padding = 8 - length % 8
        for i in range(padding):
            length += 1
        return length

    def get_file_body(self, bitstream: str, binary_tree_length: int) -> str:
        """
        Returns the body of a file given sizes of header information
        :param bitstream: Binary stream of entire compressed file to extract the body from
        :param binary_tree_length: length of the binary tree stored in the file header - get by running
                                   calculate_binary_tree_header_length()
        :return bitstream_body: Returns the body of a given bitstream
        """
        return bitstream[self.header_info['text_length'] + self.header_info['tree_leaves'] + binary_tree_length:]

    def decompress_bitstream(self, decomression_tree: tree.Tree, text_length: int, bitstream: str) -> str:
        """
        Function for converting compressed file body back into human readable text
        :param decompression_tree: Tree object to travers to get the codes
        :param text_length: integer - number of characters in the body of the file
        :param bitstream: string of binary to decompress using the given decompression_tree
        :return text: decompressed text
        """
        text = ""
        current_char = current_bit = 0
        current_node = decomression_tree
        while current_char < text_length:
            current_node = current_node.left if bitstream[current_bit] == '0' else current_node.right
            if current_node.symbol != None:
                # Reached a leaf on the tree
                text += current_node.symbol
                current_node = decomression_tree
                current_char += 1

            current_bit += 1
        return text
