class MessageR:
    def __init__(self, name: str):
        self.name = name
        self.default_str = f'[{self.name}]: '

    def __write__(self, *messages, status: str):
        text = ''.join(messages)
        final_message = f'> {status.upper()} - ' + self.default_str + text
        print(final_message, flush=True)

    def warning(self, *messages):
        self.__write__(*messages, status='warning')

    def error(self, *messages):
        self.__write__(*messages, status='error')

    def info(self, *messages):
        self.__write__(*messages, status='info')

    def bad(self, *messages):
        self.__write__(*messages, status='bad')

    def good(self, *messages):
        self.__write__(*messages, status='good')



        