## clear()


Reset the template engine to its uninitialized state.


Usage

``` python
clear()
```


After calling this, global_init() must be called again before rendering. Mostly useful in tests to isolate template configuration between cases.
