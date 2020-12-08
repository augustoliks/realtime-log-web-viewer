redis-rsyslog-vuejs
###################

Redis
-----

.. code-block:: shell

    docker exec -it redis bash
    redis-cli
    SUBSCRIBE fakelog

.. code-block:: shell

    logger "carlos neto" -T -n 127.0.0.1 -P 9090 
