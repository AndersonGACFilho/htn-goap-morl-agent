from typing import Callable, Generic, TypeVar

T = TypeVar("T", bound=Callable)


class MulticastDelegate(Generic[T]):
    """
    Multicast delegate that allows multiple functions to be called
    when an event occurs.

    You can add and remove handlers to the delegate.
    Using the invoke_handlers method, all handlers will be called.

    Usage:
        on_state_change: MulticastDelegate[Callable[[WorldState], None]]
    """

    _event_handlers: list[T]

    def __init__(self):
        """
        The constructor for the MulticastDelegate class.
        """
        self._event_handlers = list()

    def add_handler(self, handler: T) -> None:
        """
        Adds a handler to the multicast delegate.
        Args:
            handler: The handler to add
        Returns:
            None
        """
        self._event_handlers.append(handler)

    def remove_handler(self, handler: T) -> None:
        """
        Removes a handler from the multicast delegate.
        Args:
            handler: The handler to remove
        Returns:
            None
        """
        try:
            self._event_handlers.remove(handler)
        except ValueError:
            pass

    def invoke_handlers(self, *args, **kwargs) -> None:
        """
        The method that is called when the event occurs.
        Args:
            args: The arguments passed to the event
            kwargs: The keyword arguments passed to the event
        Returns:
            None
        """
        for handler in self._event_handlers:
            handler(*args, **kwargs)

    def clear(self) -> None:
        """
        Clears the multicast delegate.
        Returns:
            None
        """
        self._event_handlers = list()

    def __contains__(self, event: T) -> bool:
        """
        Checks if the event is in the multicast delegate.
        Args:
            event: The event to check
        Returns:
            True if the event is in the multicast delegate
        """
        return event in self._event_handlers

    def __len__(self) -> int:
        """
        Gets the number of events in the multicast delegate.
        Returns:
            Number of events in the multicast delegate
        """
        return len(self._event_handlers)
