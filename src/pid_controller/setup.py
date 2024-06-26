from setuptools import find_packages, setup

package_name = 'pid_controller'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='sjm',
    maintainer_email='sjm@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': ['pid_controller=pid_controller.pid_controller:main',
                            'joystick=pid_controller.pid_controller_joystick:main',
                            'pid_joystick=pid_controller.pid_controller_joystick_pid:main'
                            
        ],
    },
)
