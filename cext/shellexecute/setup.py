from distutils.core import setup, Extension

module1 = Extension('shellexecute',
                    libraries = ['Shell32'],
                    sources = ['shellexecute.c'])

setup (name = 'shellexecute',
       version = '1.0',
       description = 'This is a shellexecute package',
       ext_modules = [module1])