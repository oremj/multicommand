from distutils.core import setup

setup(name='multicommand',
      author="Jeremiah Orem",
      version='0.1a',
      packages=['multicommand'],
      requires=['paramiko'],
      scripts=['scripts/issue-multi-command'],
      )
