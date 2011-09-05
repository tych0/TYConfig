"""
  This module is a wrapper around SafeConfigParser that makes it more pythonic
  (IMHO, naturally), by allowing users to access things as attributes, rather
  than using .getboolean(), etc. Config files like the following:

  [example]
  foo = bar
  one = 1

  can be accessed as:

  conf = TYConfig("file")
  assert conf.example.foo == 'bar'
  assert conf.example.one == 1

  tyconfig also tries to guess the type of your values. there is support for
  bool, int, and float hoisting, mirroring the getbool, getint and getfloat
  methods. The one difference is that ConfigParser's getbool() will return
  False on a config value of '0' (so tests such as False is False will pass),
  but TYConfig will return 0 (0 is False fails). Test such as if 0: still
  evaluate to false, so as long as you're not doing pointer comparsions on
  false values (probably poor form anyway), these two are semantically
  equivalent.

  ----------------------------------------------------------------------------
  "THE BEER-WARE LICENSE" (Revision 42):
  <tycho@tycho.ws> wrote this file. As long as you retain this notice you
  can do whatever you want with this stuff. If we meet some day, and you think
  this stuff is worth it, you can buy me a beer in return. Tycho Andersen
  (Shamelessly stolen from: http://people.freebsd.org/~phk/)
  ----------------------------------------------------------------------------

"""

from ConfigParser import SafeConfigParser

def guess_type(thing):
  for v in ['true', 'yes', 'on']:
    if thing.lower() == v.lower():
      return True

  for v in ['false', 'no', 'off']:
    if thing.lower() == v.lower():
      return False
  try:
    return int(thing)
  except ValueError:
    pass

  try:
    return float(thing)
  except ValueError:
    pass

  return thing

class _Section(object):
  def __init__(self, name, conf):
    # bypass our __setattr__ since we really want to put everythin in the
    # object's __dict__ since they are not sections
    object.__setattr__(self, "_name", name)
    object.__setattr__(self, "_conf", conf)

    for (k, v) in conf.items(self._name):
      object.__setattr__(self, k, guess_type(v))
  
  def __setattr__(self, k, v):
    self._conf.set(self._name, k, v)
    object.__setattr__(self, k, v)

class TYConfig(SafeConfigParser):
  def __init__(self, *args, **kwargs):
    SafeConfigParser.__init__(self, *args, **kwargs)
  
  def __getattr__(self, name):
    if not self.has_section(name):
      raise AttributeError("No section: " + name)
    s = _Section(name, self)
    setattr(self, name, s)
    return s

if __name__ == '__main__':
  from cStringIO import StringIO
  testfile = """
[misc]
one = 1
onepointfive = 1.5
false = 0
true = true
gtf_separator = tests passed!
"""
  conf = TYConfig()
  conf.readfp(StringIO(testfile))

  assert conf.misc.one == 1
  assert conf.misc.onepointfive == 1.5
  assert not conf.misc.false 
  assert conf.misc.true

  print conf.misc.gtf_separator
