|PyVersion| |Status| |License| |Docs|

Dαrwinex Mendel Framework for DARWIN Portfolio Management
=========================================================

This is the **Dαrwinex Mendel Framework for DARWIN Portfolio Management in Python**. 

Precisely, this framework is called the ``Mendel`` framework because it is created to **manage quantitatively and dinamically portfolios of DARWINS** and applying quantitative **R&D** for generating investment decisions.

So, based on an asset universe of **DARWINs**, we will need to select those that meet certain criteria.

A worflow example would be:

**1)** Live/batch request of **DARWIN** universe data > for example, apply a filter to not get all the **DARWINs** data (or maybe yes).

**2)** This data will be passed as a pickled object to the **DModel** component. There we will add some features or make calculations.

**3)** The final calculations/allocations will then be passed to the **DStrategy** component to accomplish the trading, scheduling and etc.

The framework
=============

**DGateway**: price and volume data, if available.

**DModel**: will be used related with the **DStrategy** to make predictions and forecasts.

**DStrategy**: will be used to launch the final implementation of the **DModel**, together with the neccesary constraints associated.

Explanations and code
=====================

Firstly, you will need to provide new tokens on each ``APICredentials.json`` file for each component to work. 

Once done that, the back-end will handle getting new access tokens using the refresh token when the one used is no longer active
via the **DRefresher** component.

**BEAR IN MIND** that the code in this project will execute in the ``accountID`` that you provide in the instantiation of the 
``DStrategy`` class, so watch our very carefully which ``accountID`` do you use to avoid wrong executions.

As ``Docker`` is a complex framework and comprises many different functionalities, the best way to get going
is to look for some tutorials on the internet or directly visit: `Docker main website <https://docs.docker.com/get-started/>`_ apart from the tutorials that are in the `Darwinex Youtube Channel <https://www.youtube.com/channel/UC6aYa9XjWy-HmHhyp5uN_9g>`_ that walkthrough the implementation.

In this case, the ``Docker images`` for this project are hosted on the `Darwinex Alpha Team Public Docker Hub repository <https://hub.docker.com/repository/docker/dwxalphateam/mendelframework>`_ as examples. 

In case that you want to implement this for your own accounts, the best way would be to create a dedicated Docker Hub account with your ``DStrategy`` image hosted there (you have one private repository for free) and use the ``DBaseImage`` and the ``DRefresher`` from the `Darwinex Alpha Team Public Docker Hub repository <https://hub.docker.com/repository/docker/dwxalphateam/mendelframework>`_ or just build your own.

Install Docker on a Linux machine:

::

    sudo apt-get update && sudo apt-get remove docker docker-engine docker.io

    sudo apt install docker.io

    sudo systemctl start docker && sudo systemctl enable docker 

Run the following line in a terminal to check the installation:

::

    sudo docker run hello-world

Install docker-compose on a Linux machine:

::

    sudo curl -L "https://github.com/docker/compose/releases/download/1.25.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

    sudo chmod +x /usr/local/bin/docker-compose

Run the following line in a terminal to check the installation:

::

    docker-compose --version

Edit your ``crontab`` file with something like the following contents. For this to work out, you will need to have the exact path
on your server/computer and have downloaded the repository. 

Make sure that the files are **EXECUTABLE**. In **Linux** ``chmod +x``:

::

    # Execute at 20:58 previous to 21:00 close:
    58 20 * * 1-5 /root/mendel-framework/dockerComposes/start-strategy.sh

    # Execute at minute 30 on every day-of-week to refresh tokens:
    */30 * * * * /root/mendel-framework/dockerComposes/start-refresher.sh

Documentation
=============

You can find the complete `API documentation <https://api.darwinex.com/store/>`_ here. You will be able to understand the different exposed enpoints as well has play around with them to understand the returned ``JSON`` messages, whether they result in a succesfull request-response attempt or no.

Other helpful links:

    *  `Darwinex API FAQ and walkthrough <https://help.darwinex.com/api-walkthrough>`_
    *  `Darwinex Help Center <https://help.darwinex.com/>`_

Discussion
==========

The `Darwinex API Community Forum <https://https://community.darwinex.com/>`_ is one of the places to discuss
``Darwinex API`` and anything related to it.

Furthermore, you can join the `Darwinex Collective Slack <https://join.slack.com/t/darwinex-collective/shared_invite/enQtNjg4MjA0ODUzODkyLWFiZWZlMDZjNGVmOGE2ZDBiZGI4ZWUxNjM5YTU0MjZkMTQ2NGZjNGIyN2QxZDY4NjUyZmVlNmU3N2E2NGE1Mjk>`_ for Q&A, debug and more.

Disclaimer
==========

The software is provided on the conditions of the **BSD** license that you can find inside the package.

**The αlpha's time has begun!**

:Author: Darwinex Alpha Team <content@darwinex.com>

.. |PyVersion| image:: https://img.shields.io/badge/python-3.7+-blue.svg
   :alt:

.. |Status| image:: https://img.shields.io/badge/status-beta-green.svg
   :alt:

.. |License| image:: https://img.shields.io/badge/license-BSD-blue.svg
   :alt:

.. |Docs| image:: https://img.shields.io/badge/Documentation-green.svg
   :alt: Documentation
   :target: https://api.darwinex.com/store/