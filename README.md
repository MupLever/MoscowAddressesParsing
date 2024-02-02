## MosOpen Parser

Этот скрипт на Python 3 позволяет вам подключаться к [`Электронная Москва`](http://mosopen.ru/streets)
и собирать информацию обо всех районах, улицах и домах.

### Dependencies
* scrapy

### Usage

```
scrapy crawl legal_addresses -O addresses.jl
```

### Linter
```
black
pylint
```
