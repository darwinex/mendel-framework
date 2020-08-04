|PyVersion| |Status| |License| |Docs|

Dαrwinex Mendel Framework for DARWIN Portfolio Management
=========================================================

This is the **Dαrwinex Mendel Framework for DARWIN Portfolio Management in Python**. 

Precisely, this framework is called the ``Mendel`` framework because it is created to **manage quantitatively and dinamically portfolios of DARWINS** and applying quantitative **R&D** for generating investment decisions.

So, based on an asset universe of **DARWINs**, we will need to select those that meet certain criteria.

A worflow example would be:

**1)** Live/batch request of **DARWIN** universe data. For example, apply a filter to get **DARWINs** with certain returns threshold for the last 3 months.

**2)** This data will be passed to the **DModel** component. The **DModel** component will hold the allocation algorithm together with any other auxiliary computation methods.

**3)** The final calculations/allocations will then be passed to the **DStrategy** component to accomplish the trading, scheduling and etc.

The framework
=============

**DAssetUniverse**: it will get **DARWIN** quote data or just other **DARWIN** available data fields such as investment attributes. 

**DModel**: it will have the neccesary allocation algorithm so that you can input **DARWIN** data and calculate the final weights.

**DStrategy**: will be used to instantiate and launch other components and use the final allocations of the **DModel**, together with the neccesary constraints associated, to create a whole developed portfolio management strategy.

Explanations
============

**The best way** to understand how to use the framework is watching the `dedicated playlist in our Youtube Channel <https://www.youtube.com/channel/UC6aYa9XjWy-HmHhyp5uN_9g>`_ while looking at the source code in this repository.

Apart from that, we will give you essential steps to get it working right away.

Firstly, you will need to provide new tokens on the ``APICredentials.json`` file that is inside the ``/D-Strategy1`` folder. This is neccesary in order to start the ``D-Refresher`` component and get automatic requests of the ``access`` and ``refresh`` tokens.

Once done that, the back-end will handle getting new access tokens using the refresh token via the **DRefresher** component.

After the initial credentials set-up, you will need to provide the ``accountID`` in the initialization of the ``DStrategy`` class.

**BEAR IN MIND** that the code in this project will execute in the ``accountID`` that you provide in the instantiation of the 
``DStrategy`` class, so watch out very carefully which ``accountID`` do you use to avoid wrong executions.

There is an actual working implementation so that you can try it out; you will need to dig in a bit into the code to see which **DARWINs** are considered to trade and which is the model to use. **THERE IS NO GUARANTEE that the example strategy will yield profits**, but it covers many implementation details and it is worth trying it to see how it performs and get accustomed to the framework.

Regarding ``Docker``, as it is a complex framework and comprises many different functionalities, the best way to get going
is to look for some tutorials on the internet or directly visit: `Docker main website <https://docs.docker.com/get-started/>`_, apart from the tutorials that are in the `Darwinex Youtube Channel <https://www.youtube.com/channel/UC6aYa9XjWy-HmHhyp5uN_9g>`_ that walkthrough this specific implementation.

In this case, the ``Docker images`` for this project are hosted on the `Darwinex Alpha Team Public Docker Hub repository <https://hub.docker.com/repository/docker/dwxalphateam/mendelframework>`_ as examples. 

In case that you want to implement this for your own accounts, **the best way** would be to create a dedicated Docker Hub account with your ``DStrategy`` image hosted there (you have one private repository for free) and use the ``DBaseImage`` and the ``DRefresher`` from the Darwinex Alpha Team Public Docker Hub repository or just build your own.

The ``Mendel Framework`` has functionality built-in to send ``Telegram`` messages via a ``Telegram Bot``. For that matter, you will need to build your own bot and use its specific token. The tutorial for that is in the dedicated playlist of our **Youtube Channel** as detailed above. You can just comment the lines associated to it and re-create the images if you don't want to use it directly.

Tools installation walkthrough
==============================

Once that you have developed/modified all the neccesary scripts within the ``Mendel Framework``, this would be the steps to run the ``docker services`` on a Linux machine:

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

(Install git) and download git repo to the root home folder:

::

    sudo apt install git-all && git clone https://github.com/darwinex/mendel-framework.git

Ensure that the .sh scripts are executable. In **Linux**:

::

    chmod +x /root/mendel-framework/D-Strategy1/*.sh
    chmod +x /root/mendel-framework/D-Refresher/*.sh

Also, you will have to download the Docker ``images`` from the Docker Hub repository.

This will pull the ``images`` that are defined in the ``docker-compose`` of that specific directory:

::

    cd /root/mendel-framework/dockerComposes/ && docker-compose pull

Edit your ``crontab`` file (``crontab -e``) with something like the following contents. 

For this to work out, you will need to have the exact path on your server/computer and have downloaded the repository. 

::

    # Execute at 20:58 previous to 21:00 close:
    58 20 * * 1-5 /usr/local/bin/docker-compose -f "/root/mendel-framework/dockerComposes/docker-compose.yml" up -d dstrategy1

    # Execute at minute 30 on every day-of-week to refresh tokens:
    */30 * * * * /usr/local/bin/docker-compose -f "/root/mendel-framework/dockerComposes/docker-compose.yml" up -d drefresher

Documentation
=============

You can find the complete `DARWIN API documentation <https://api.darwinex.com/store/>`_ here. You will be able to understand the different exposed enpoints as well has play around with them to understand the returned ``JSON`` messages, whether they result in a succesfull request-response attempt or no.

Other helpful links:

    *  `Darwinex API FAQ and walkthrough <https://help.darwinex.com/api-walkthrough>`_
    *  `Darwinex Help Center <https://help.darwinex.com/>`_

Discussion
==========

The `Darwinex API Community Forum <https://https://community.darwinex.com/>`_ is one of the places to discuss
``Darwinex API`` and anything related to it like the ``Mendel Framework``.

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