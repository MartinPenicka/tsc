

class MessageBuffer:

    def __init__(self):

        self.__delim_msg = "@"
        self.__delim_content = "#"

        self.__incomming_buffer = ""
        self.__parsed_messages = []

    def __parse(self):

        if self.__incomming_buffer == "":
            return

        self.__parsed_messages = self.__incomming_buffer.split(self.__delim_msg)
        if self.__incomming_buffer[-1] != self.__delim_msg:
            self.__incomming_buffer = str(self.__parsed_messages[-1])
            self.__parsed_messages.pop()
        else:
            self.__incomming_buffer = ""

        if len(self.__parsed_messages) > 0 and self.__parsed_messages[-1] == "":
            self.__parsed_messages.pop()

    def append(self, received_data):

        self.__incomming_buffer += str(received_data)

    def get_msg(self):

        self.__parse()

        tmp_buffer = self.__parsed_messages
        self.__parsed_messages = []
        return tmp_buffer
