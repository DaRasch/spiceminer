.. _documentation:

*************
Documentation
*************

.. _documentation-import-all:

Import \*
=========

By default the ``spiceminer`` package exports the following modules, classes
and functions:

+--------------------------------------------------+--------------------------+
| **Modules**                                                                 |
+--------------------------------------------------+--------------------------+
| :py:mod:`~spiceminer.kernel`                     | Access to the database   |
+--------------------------------------------------+--------------------------+
| **Classes**                                                                 |
+--------------------------------------------------+--------------------------+
| :py:class:`~spiceminer.time_.Time`               | Powerfull implementation |
|                                                  | of POSIX time            |
+--------------------------------------------------+--------------------------+
| :py:class:`~spiceminer._spicewrapper.SpiceError` | Errors raised by the     |
|                                                  | c-framework              |
+--------------------------------------------------+--------------------------+
| **Functions**                                                               |
+--------------------------------------------------+--------------------------+
| :py:func:`~spiceminer.extra.angle`               | Calculate angles between |
|                                                  | 2 vectors                |
+--------------------------------------------------+--------------------------+
| :py:func:`~spiceminer.extra.frange`              | ``xrange`` function for  |
|                                                  | ``float``                |
+--------------------------------------------------+--------------------------+
| :py:func:`~spiceminer.extra.dtrange`             | ``xrange`` function for  |
|                                                  | ``datetime``             |
+--------------------------------------------------+--------------------------+

The :py:class:`~spiceminer.bodies.Body` class is not explicitly exported, but
it is the data structure representing Ephimeris Objects.

.. _documentation-modules:

Modules in detail
=================

.. toctree::
   :maxdepth: 2

   kernel
   bodies
   time_
   extra

.. _documentation-bodies-frames:

Bodies and reference frames
===========================

.. _documentation-frames:

Reference frames
----------------

.. _reference frames: http://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/frames.html

Official, very technical documentation for reference frames is available
`here <reference frames>`_.

All bodies are bound to reference frames, which have a position and rotation
relative to other reference frames. In most cases the frames are handled
automatically, but there are some frames, which are not referenced by any body.

* **J2000** -- Position like the SOLAR SYSTEM BARYCENTER

  * x-axis -- Line of intersection between earth's ecliptic and equator.
  * y-axis -- Cross product of x-axis and z-axis.
  * z-axis -- Normal of the earth's **equator** in 'northern' direction.

* **ECLIPJ2000** -- Position like the SOLAR SYSTEM BARYCENTER

  * x-axis -- Line of intersection between earth's ecliptic and equator.
  * y-axis -- Cross product of x-axis and z-axis.
  * z-axis -- Normal of the earth's **ecliptic** in 'northern' direction.

These frames are non-rotating and non-accelerating, making them ideal global
reference frames. The only way to access them is their string.

.. _documentation-bodies:

Bodies
------

Some bodies are hardcoded into the framework, so some information about them is
already available without any kernels loaded. To get position/rotation data it
is always necessary to load kernels.

The table below gives some information about most of the hardcoded objects as
well as objects available through collections that can be downloaded via the
``getdata.py`` script. The *Packages* field shows, wich collections are needed
to get as much data as possible.


.. NOTE:: See the :ref:`tutorial <tutorial-getting-started>` for more info on
   what ``getdata.py`` can do.

.. _documentation-bodies-natural:

Barycenters and natural bodies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

=======================     ======= =========== =========== ========
Name                        ID code Position    Rotation    Packages
=======================     ======= =========== =========== ========
SOLAR SYSTEM BARYCENTER     0       True        False       base
MERCURY BARYCENTER          1       True        False       base
VENUS BARYCENTER            2       True        False       base
EARTH BARYCENTER            3       True        False       base
MARS BARYCENTER             4       True        False       base
JUPITER BARYCENTER          5       True        False       base
SATURN BARYCENTER           6       True        False       base
URANUS BARYCENTER           7       True        False       base
NEPTUNE BARYCENTER          8       True        False       base
PLUTO BARYCENTER            9       True        False       base
SUN                         10      True        True        base
MERCURY                     199     True        True        base
VENUS                       299     True        True        base
MOON                        301     True        True        base
EARTH                       399     True        True        base
PHOBOS                      401     True        True        base
DEIMOS                      402     True        True        base
MARS                        499     True        True        base
IO                          501     False       True        base
EUROPA                      502     False       True        base
GANYMEDE                    503     False       True        base
CALLISTO                    504     False       True        base
AMALTHEA                    505     False       True        base
HIMALIA                     506     False       True        base
ALERA                       507     False       True        base
PASIPHAE                    508     False       True        base
SINOPE                      509     False       True        base
LYSITHEA                    510     False       True        base
CARME                       511     False       True        base
ANANKE                      512     False       True        base
LEDA                        513     False       True        base
THEBE                       514     False       True        base
ADRASTEA                    515     False       True        base
METIS                       516     False       True        base
CALLIRRHOE                  517     False       True        base
THEMISTO                    518     False       True        base
MAGACLITE                   519     False       True        base
TAYGETE                     520     False       True        base
CHALDENE                    521     False       True        base
HARPALYKE                   522     False       True        base
KALYKE                      523     False       True        base
IOCASTE                     524     False       True        base
ERINOME                     525     False       True        base
ISONOE                      526     False       True        base
PRAXIDIKE                   527     False       True        base
AUTONOE                     528     False       True        base
THYONE                      529     False       True        base
HERMIPPE                    530     False       True        base
AITNE                       531     False       True        base
EURYDOME                    532     False       True        base
EUANTHE                     533     False       True        base
EUPORIE                     534     False       True        base
ORTHOSIE                    535     False       True        base
SPONDE                      536     False       True        base
KALE                        537     False       True        base
PASITHEE                    538     False       True        base
HEGEMONE                    539     False       True        base
MNEME                       540     False       True        base
AOEDE                       541     False       True        base
THELXINOE                   542     False       True        base
ARCHE                       543     False       True        base
KALLICHORE                  544     False       True        base
HELIKE                      545     False       True        base
CARPO                       546     False       True        base
EUKELADE                    547     False       True        base
CYLLENE                     548     False       True        base
KORE                        549     False       True        base
HERSE                       550     False       True        base
JUPITER                     599     False       True        base
MIMAS                       601     False       True        base
ENCELADUS                   602     False       True        base
TETHYS                      603     False       True        base
DIONE                       604     False       True        base
RHEA                        605     False       True        base
TITAN                       606     False       True        base
HYPERION                    607     False       True        base
IAPETUS                     608     False       True        base
PHOEBE                      609     False       True        base
JANUS                       610     False       True        base
EPIMETHEUS                  611     False       True        base
HELENE                      612     False       True        base
TELESTO                     613     False       True        base
CALYPSO                     614     False       True        base
ATLAS                       615     False       True        base
PROMETHEUS                  616     False       True        base
PANDORA                     617     False       True        base
PAN                         618     False       True        base
YMIR                        619     False       True        base
PAALIAQ                     620     False       True        base
TARVOS                      621     False       True        base
IJIRAQ                      622     False       True        base
SUTTUNGR                    623     False       True        base
KIVIUQ                      624     False       True        base
MUNDILFARI                  625     False       True        base
ALBIORIX                    626     False       True        base
SKATHI                      627     False       True        base
ERRIAPUS                    628     False       True        base
SIARNAQ                     629     False       True        base
THRYMR                      630     False       True        base
NARVI                       631     False       True        base
METHONE                     632     False       True        base
PALLENE                     633     False       True        base
POLYDEUCES                  634     False       True        base
DAPHNIS                     635     False       True        base
AEGIR                       636     False       True        base
BEBHIONN                    637     False       True        base
BERGELMIR                   638     False       True        base
BESTLA                      639     False       True        base
FARBAUTI                    640     False       True        base
FENRIR                      641     False       True        base
FORNJOT                     642     False       True        base
HATI                        643     False       True        base
HYROKKIN                    644     False       True        base
KARI                        645     False       True        base
LOGE                        646     False       True        base
SKOLL                       647     False       True        base
SURTUR                      648     False       True        base
ANTHE                       649     False       True        base
JARNSAXA                    650     False       True        base
GREIP                       651     False       True        base
TARQEQ                      652     False       True        base
AEGAEON                     653     False       True        base
SATURN                      699     False       True        base
ARIEL                       701     False       True        base
UMBRIEL                     702     False       True        base
TITANIA                     703     False       True        base
OBERON                      704     False       True        base
MIRANDA                     705     False       True        base
CORDELIA                    706     False       True        base
OPHELIA                     707     False       True        base
BIANCA                      708     False       True        base
CRESSIDA                    709     False       True        base
DESDEMONA                   710     False       True        base
JULIET                      711     False       True        base
PORTIA                      712     False       True        base
ROSALIND                    713     False       True        base
BELINDA                     714     False       True        base
PUCK                        715     False       True        base
CALIBAN                     716     False       True        base
SYCORAX                     717     False       True        base
PROSPERO                    718     False       True        base
SETEBOS                     719     False       True        base
STEPHANO                    720     False       True        base
TRINCULO                    721     False       True        base
FRANCISCO                   722     False       True        base
MARGARET                    723     False       True        base
FERDINAND                   724     False       True        base
PERDITA                     725     False       True        base
MAB                         726     False       True        base
CUPID                       727     False       True        base
URANUS                      799     False       True        base
TRITON                      801     False       True        base
NEREID                      802     False       True        base
NAIAD                       803     False       True        base
THALASSA                    804     False       True        base
DESPINA                     805     False       True        base
GALATEA                     806     False       True        base
LARISSA                     807     False       True        base
PROTEUS                     808     False       True        base
HALIMEDE                    809     False       True        base
PSAMATHE                    810     False       True        base
SAO                         811     False       True        base
LAOMEDEIA                   812     False       True        base
NESO                        813     False       True        base
NEPTUNE                     899     False       True        base
CHARON                      901     False       True        base
NIX                         902     False       True        base
HYDRA                       903     False       True        base
PLUTO                       999     False       True        base
=======================     ======= =========== =========== ========
