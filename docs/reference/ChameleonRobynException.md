## ChameleonRobynException


Base exception for all chameleon-robyn errors (bad configuration, invalid return types, etc.).


Usage

``` python
ChameleonRobynException()
```


## Examples

``` python
try:
    chameleon_robyn.render('home/index.pt', title='Home')
except chameleon_robyn.ChameleonRobynException as e:
    log.error('template setup problem: %s', e)
```
