from setuptools import setup

setup(
    name='lispy',
    version='0.1',
    packages=['test', 'lispy', 'lispy.parser', 'lispy.builtins',
              'lispy.interpreter'],
    url='http://github.com/dwbullok/lispy',
    license='MIT License',
    author='Dan Bullok, Ben Lambeth',
    author_email='dan@codeviking.com, lambethben@gmail.com',
    description='Model lisp-ish interpreter',
    test_suite='nose.collector',
    tests_require=['nose']

)
