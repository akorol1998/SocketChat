from __future__ import annotations
from typing import Any

from abc import ABC, abstractmethod


class AsyncObservable(ABC):

	@abstractmethod
	def attach(self, observer: AsyncObserver) -> None:
		pass

	@abstractmethod
	def detach(self, observer: AsyncObserver) -> None:
		pass

	@abstractmethod
	def notify(self, *args, **kawrgs) -> None:
		pass


class AsyncObserver(ABC):
	

	@abstractmethod
	def update(self, *args, **kwargs) -> None:
		pass

