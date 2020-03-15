# Installation

```
pip install pygram
```

# Basic Usage

Using Pygram is incredibly simple:

```python
from pygram import Pygram


session = Pygram('myusername', 'password')

with session:
    pygram.follow_user_followers('iguser', amount=100)

```
