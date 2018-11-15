# pygantt

A simple matplotlib-based gantt chart maker.

## Example

Write a simple sectioned CSV file:

```csv
*Phase 1
0, 3, This is the first task and will take forever
3, 6, This is a banana

*Phase 2
2, 9, This is the second task and will take forever
1, 7, This is not a banana

*Phase 3
5, 7, This is the second task and will take forever
3, 7, This is a pinable

```

Call pygantt on it:

```bash
python pygant.py test.csv
```

The output is saved to `gantt.png` by default (change it with the `--output` option):

![example output](example_gantt.png)
