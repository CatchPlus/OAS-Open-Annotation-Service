from string import ascii_letters, digits
from random import choice

generateApiKey = lambda : ''.join(choice(ascii_letters + digits) for i in xrange(16))
