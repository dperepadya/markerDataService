class MessageProcessor:
    def __init__(self, queue_manager):
        self.queue_manager = queue_manager

    async def process_message(self, message, sender):
        raise NotImplementedError("Subclasses must implement")

    async def publish_message(self, data, channel, sender):
        raise NotImplementedError("Subclasses must implement")



