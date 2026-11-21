from itertools import islice


class BatchIterator:
    """Iterate over rows in fixed-size batches."""

    def __init__(self, rows, batch_size: int = 1000) -> None:
        self._rows = iter(rows)
        self.batch_size = batch_size

    def __iter__(self):
        return self

    def __next__(self):
        batch = list(islice(self._rows, self.batch_size))
        if not batch:
            raise StopIteration
        return batch

if __name__ == "__main__":
    for batch in BatchIterator(range(10), batch_size=3):
        print(len(batch), batch)
    