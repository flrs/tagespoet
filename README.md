![tagespoet.de logo](static/resources/img/logo.png)

tagespoet.de
============
*A Flask application generating poems from daily news*

This application displays a website that showcases a poem. The poem is generated automatically on the basis of daily
news. The website also comprises an archive and an explanation of how the poem is generated. The language of the created
website is German. The website is live under [tagespoet.de](http://www.tagespoet.de). 

This application uses a wide range of web technologies, such as Python, Flask, MongoDB, jQuery, Ajax, HTML, Bootstrap,
JavaScript and CSS.

The application is meant to run on [OpenShift](http://www.openshift.com). It is configured to serve from a North American server time to
 the German time zone (North American time lagging six hours behind German time).
 
Deployment on OpenShift
-----------------------
This section describes how the script can be deployed on [OpenShift](http://www.openshift.com).

1. Create an OpenShift gear for the application.

2. Enable gear support for Python 2.7, MongoDB and Cron.

3. Clone this GitHub repository into the OpenShift gear.

4. The file `flaskapp_dummy.cfg` needs to be modified.
    1. Rename the file `flaskapp_dummy.cfg` to `flaskapp.cfg`. 
    2. The newly created `flaskapp.cfg` contains some remarks stating `#YOUR CODE HERE#`. Replace these remarks with 
    the relevant data.
    
All requirements are listed in requirements.txt and thus automatically installed by OpenShift. You should be good to go! 

Status of Development
---------------------
The script is experimental and not actively maintained. Many improvements can be made, some ideas are outlined by the 
comments marked with `# TODO` in the code.

Acknowledgements
----------------
The initial codebase for the poem generator originates from the [PoemGenerator repository](https://github.com/flrs/poemGenerator).
That code has been improved.
The template for the OpenShift flask application was taken from [Ryan Jarvinen's Flask Base Template](https://github.com/openshift-quickstart/flask-base).

License
-------
The code in this repository is distributed under a [Simplified BSD License](LICENSE.md).

