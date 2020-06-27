import huffman_compression_tools
import tree
import os, _io


class HuffmanFile(huffman_compression_tools.HuffmanTools):
    """
    Inherits the huffman_compression_tools.HuffmanTools class, to use the functions in a more useable way
    """

    HUFFMAN_FILE_MODES = ["rb", "wb"]

    def __init__(self, file_path: str, mode='rb', diagnostics=False):
        """
        :param file_path: string, path to compressed binary file
        :param mode: rb - read or wb - write to select the mode you wish to open the file in
        :param diagnostics: If True displays information to the command line as tasks are executed
        """
        super().__init__()

        self.compressed_file = file_path
        self.mode = mode
        self.diagnostics = diagnostics

        # Attributes for reducing time for multiple compressions
        self.huffman_tree: tree.Tree = None
        self.file_bytestream: bytes = None

        # Attributes for reducing time required for multiple decompressions
        self.decompressed_text: str = None


    @property
    def compressed_file(self) -> str:
        """
        Private file path attribute
        """
        return self.__compressed_file

    @compressed_file.setter
    def compressed_file(self, path: str) -> None:
        """
        Setter function for private file path attribute
        Invoked by calling self.compressed_file = New file path
        """
        if os.path.splitext(path)[1] == ".bin":
            self.__compressed_file = path
        else:
            raise ValueError("Please give the file path to a binary file (.bin)")

    @property
    def mode(self) -> str:
        return self.__mode

    @mode.setter
    def mode(self, new_mode: str) -> None:
        """
        Setter function for mode attribute - will only set mode initiatlly, cannot change file mode
        :param new_mode: New mode
        """
        if not hasattr(self, '__mode'):
            if new_mode in self.HUFFMAN_FILE_MODES:
                self.__mode = new_mode
            else:
                raise ValueError("Invalid file mode. Please select either \'rb\' or \'wb\'")
        else:
            raise _io.UnsupportedOperation("unable to change file mode")

    def wb(func):
        """
        Function decorator for write only functions
        """
        def function_wrapper(*args, **kwargs):
            if args[0].mode == 'wb':
                return_value = func(*args, **kwargs)
                return return_value
            else:
                raise _io.UnsupportedOperation("file not writable")
        return function_wrapper

    def rb(func):
        """
        Function decorator for read only funtions
        """
        def function_wrapper(*args, **kwargs):
            if args[0].mode == 'rb':
                text = func(*args, **kwargs)
                return text
            else:
                raise _io.UnsupportedOperation("file not readable")
        return function_wrapper

    def __enter__(self) -> object:
        """
        Function 1 or 2 to allow the object to work as a with statment
        Handles opening of file
        """
        try:
            self.file = open(self.__compressed_file, self.mode)
            if self.diagnostics:
                print("File ready to read!")
        except FileNotFoundError:
            if self.diagnostics:
                print("File not found - creating new file...")
            self.file = open(self.__compressed_file, "wb")
            self.mode = "wb"
            if self.diagnostics:
                print("New file created - ready to write to!")
        return self

    def __exit__(self, type, value, traceback) -> None:
        """
        Function 2 or 2 to allow the object to work as a with statment
        Handles closing of files
        """
        self.file.close()

    def __str__(self):
        return "<%s name=\'%s\' mode=\'%s\'>" % ("HuffmanFile", self.compressed_file, self.mode)

    @wb
    def compress(self, text: str) -> bytes:
        """
        Method for compressing a string of text, returning a stream of bytes - a form selected
        for writing to a binary file
        :param text: String of text that is to be compressed
        :return bytestream: stream of bytes, ready to be written to a binary (.bin) file
        """
        if self.huffman_tree is None:
            frequency = self.generate_frequency_table(text)
            huffman_forest = self.plant_forest(frequency)
            self.huffman_tree = self.merge_trees(huffman_forest)

            self.huffman_tree.depth = tree.tree_depth(self.huffman_tree) - 1

        if not self.compression_codes :
            compression_codes = self.generate_compression_codes(self.huffman_tree, [None]*self.huffman_tree.depth)

        header = self.generate_file_header(text, self.huffman_tree)
        bytestream = self.generate_file_bytestream(text)
        self.file_bytestream = header + bytestream
        return header + bytestream

    @rb
    def decompress(self) -> str:
        """
        Function for decompressing text of the objects compressed file
        :return decompressed_text: Decompressed text in a string
        """
        if self.decompressed_text is None:
            file_bitstream = self.extract_file_bitstream(self.file)

            text_length, postorder_tree_list = self.extract_header_from_bitstream(file_bitstream)

            if self.huffman_tree is None:
                self.huffman_tree = tree.construct_tree_from_postorder(postorder_tree_list)

            binary_text = self.get_file_body(file_bitstream, self.calculate_binary_tree_header_length(postorder_tree_list))
            self.decompressed_text = self.decompress_bitstream(self.huffman_tree, text_length, binary_text)

        return self.decompressed_text

    @wb
    def write_from_file(self, file: str) -> None:
        """
        Compress text from a text file to the object's binary file
        :param file: File path to a text file (.txt) that will be compressed and written to binary file
        """
        filename, file_extension = os.path.splitext(file.name)
        if file_extension == '.txt':
            file_bytestream = self.compress(file.read())
            if self.diagnostics:
                print("File Compressed Successfully!")
            self.file.write(file_bytestream)
            if self.diagnostics:
                print("File written to " + file.name + " successfully!")
            
        else:
            raise ValueError("Please give the path to a text file, not a " + file_extension + " file")
        
    @wb
    def write_from_string(self, text: str) -> None:
        """
        Compress text from a string to the object's binary file
        :param text: String of text to be compressed and then written to binary file
        """
        file_bytestream = self.compress(text)
        if self.diagnostics:
            print("Text Compressed Successfully!")
        self.file.write(file_bytestream)
        if self.diagnostics:
            print("File written to " + file.name + " successfully!")

    @rb
    def read_to_file(self, file: _io.TextIOWrapper) -> str:
        """
        Decompress the object file and write to text file and return the text
        :param file: Open text file object for writing decompressed text to
        :return text: Returns the decompressed text as a string
        """
        text = self.decompress()
        file.write(text)
        return text

    @rb
    def read(self) -> str:
        """
        Decompress the object file and return the string of decompressed text
        :return text: Decompressed text 
        """
        text = self.decompress()
        return text
