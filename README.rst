WARNING!!! this is not workable yet, hopfully soon.


Architect
=========

Goal: Monitor a Time Series DB (RRD, OpenTSDB, etc) to
auto scal anything supported by Contractor.



Docker Setup
============

(very  preliminary)

first need a TSD, for an easy Graphite install::

  docker pull hopsoft/graphite-statsd
  docker run -p 80:80 -d --name graphite hopsoft/graphite-statsd
  docker inspect graphite

Get the ip address from the inspect and edit the settings.py file
and set the GRAPHOTE_HOST to that ip address::

  docker build . -t architect
  docker run -p 8880:8880 -d --name architect architect


