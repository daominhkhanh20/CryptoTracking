

class BaseAnalysis:
    def analysis(self, **kwargs):
        raise NotImplementedError()

    def send_message(self, **kwargs):
        raise NotImplementedError()
