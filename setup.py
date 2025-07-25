from setuptools import setup, find_packages

setup(
    name='ansible_callback_notify_ntfy',
    version='0.1.0',
    packages=find_packages(),
    package_data={
        'ansible_callback_notify_ntfy': ['ansible_callback_notify_ntfy/*.py'],
    },
    author='Michael Neese',
    description='Ansible callback plugin for sending playbook recaps to NTFY server',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Framework :: Ansible',
    ],
)
