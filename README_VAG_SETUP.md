Vagrant Setup README

Copyright (c) 2013 djorda9

We will be using Vagrant V1.3.5 to standardize our development environment for this 
project.  We will be using VirtualBox that comes with Vagrant for the virtual machine.
The operating system for the virtual machine will be Ubuntu 12.04 LTS 64-bit with the 
following applications installed on it.

Apache 2.2.22
Python 2.6.8
SQLite 3.5.9
Django 1.6

If you do not have Vagrant V1.3.5 installed on your computer, please download and 
install Vagrant V1.3.5 from http://downloads.vagrantup.com/tags/v1.3.5 before continuing.
Once you have Vagrant V1.3.5 installed on your computer, the following instruction can be
used to create the virtual machine for developing the Simulated Conversation web 
application.  

1. Vagrant shares the directory folder that it is launched from with the virtual machine.
In  order to use this setup, please copy the vag_setup.tar.gz to the folder that you wish
to share with the virtual machine.

2. Open your terminal window and navigate to the directory folder you placed the 
vag_setup.tar.gz file in.

2. Decompress vag.setup.tar.gz with tar (tar xzvf vag_setup.tar.gz) or other decompression
software that decompresses .tar.gz.

3. In the terminal window at the command prompt, enter "vagrant up" and the virtual
machine will be built.

4.  Once the virtual machine is done building, the command prompt will reappear.  Once
the command prompt has reappeared, you can enter "vagrant ssh" to get to the terminal window 
for the virtual machine.

Note - The virtual machine has been setup with a static IP address of 192.168.33.10.
