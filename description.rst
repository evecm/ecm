===================================
Interfaces Homme-Machine : Projet
===================================

-------------------------
 ICE Security Management
-------------------------

.. |date| date::

:Auteurs: Vincent Dupont, Robin Jarry
:date: |date|


.. |ISM| replace:: *ICE Security Management*
.. |EVE| replace:: `EVE Online`_
.. _`EVE Online` : http://www.eve-online.com
.. include:: <isopub.txt>

.. contents:: Tables des Matières


Description de l'Application
============================

|ISM| est une application de gestion et d'aide à la prise de décision pour le jeu |EVE|.

EVE Online
----------

|EVE| est un MMORPG (*Massive Multiplayer Online Role Playing Game*) développé par *CCP* qui est en production depuis 2003. Sa particularité par rapport aux autres MMORPG est que **la partie qui a commencé en 2003 est toujours en cours**. De plus, tous les joueurs de |EVE| jouent dans la même partie (et donc sur le même serveur). Il y a en moyenne 40.000 joueurs connectés en *prime time* (20h-23h) européenne.

|EVE| est un space opera qui se déroule dans une galaxie : *New Eden* qui comporte un peu plus de 6.000 systèmes solaires visitables ; chacun avec son cortège de planètes et de ceintures d'astéroïdes. Les joueurs incarnent une caste de la population de *New Eden* : les *Capsulers*. Ce sont des pilotes de vaisseaux interstellaires qui font d'une quarantaines de mètres à plusieurs kilomètres de long. Ces pilotes peuvent s'associer en sociétés appelées *Corporations* afin de parvenir à leurs fins. 

Les possibilités dans |EVE| sont variées, chaque système solaire contient des ressources naturelles qui peuvent être exploitées (minerai dans les astéroïdes, carburant dans les glaces stellaires, etc.). De l'exploitation de ces ressources, les pilotes peuvent tirer des matières premières pour construire des vaisseaux, des modules et des armes pour ceux-ci. Les vaisseaux servent principalement à faire la guerre à d'autres corporations pour conquérir de nouveaux systèmes solaires mais il y a d'autres rôles comme le transport ou le minage (entre autres). Certains joueurs décident de jouer des espions et infiltrent des *Corporations* pour les voler ou les détruire (celà fait partie du jeu :-)).

Les *Corporations* sont comparables à des sociétés privées telles que nous les connaissons aujourd'hui. Elles possèdent des comptes en banque, des bureaux, des entrepôts et des *assets* tels que des vaisseaux, des matières premières, etc. Pour gérer les accès aux entrepôts et aux comptes, il y a un système de droits assez complexe que nous ne décrirons pas ici. Et il est nécessaire |ndash| dès que la corporation atteint une certaine taille (les plus grosses peuvent comporter jusqu'à 600 membres) |ndash| d'apporter une attention particulière à la gestion de ces droits d'accès, afin de limiter les risques d'infiltration et de vol. Malheureusement, l'interface du jeu est assez dépouillée et ne permet pas de gérer convenablement ces droits. Notamment lorsque des joueurs arrêtent de jouer ou que des nouvelles recrues arrivent.

Les concepteurs du jeu ont mis à disposition une `API web <http://wiki.eve-id.net/APIv2_Page_Index>`_ pour obtenir des informations sur le jeu sans y être connecté. Cette API permet notamment de récupérer le contenu de tous les hangars d'une corporation, la liste de ses membres ainsi que la liste de leurs droits.

Besoins / Spécifications
------------------------

Avant de développer |ISM|, nous avons établi le cahier des charges suivants :

- Il faut un suivi précis des arrivées et des départs de joueurs de la corporation.
- Il faut un historique des changements de droits d'accès pour chaque membre.
- Chaque droit d'accès doit être pondéré afin de pouvoir calculer le "niveau d'accès" potentiel d'un membre
- Il faut une vision globale du contenu des hangars de la Corporation. L'interface du jeu n'est pas satisfaisante.
- Il faut une historisation du contenu de ces hangars. Afin de pouvoir dater une disparition suspecte (à quelques heures près).

Implémentation Technique
------------------------

Cette application se destinant à plusieurs utilisateurs en meme temps, il est sensé d'en faire une application web accessible hors jeu. 

Pour les choix de technologies, il nous fallait un langage de programmation avancé et flexible (PHP était donc déjà hors course) mais il nous fallait également un langage léger et facile à implémenter (exit Java aussi). Il restait donc Python_ et son framework web Django_.

Les requêtes à l'API du jeu se font par protocole http et les réponses sont au format XML. Nous avons utilisé la bibliothèque eveapi_ développée en Python_ pour récupérer des données depuis celle-ci.

Pour la partie client, nous avons utilisé le framework javascript jQuery_ et notamment les plugins jsTree_ pour afficher le contenu des hangars et datatables_ pour gérer les tableaux.

.. _Django : http://www.djangoproject.com/
.. _eveapi : http://wiki.eve-id.net/Eveapi
.. _Python : http://www.python.org/
.. _jQuery : http://jquery.com/
.. _jsTree : http://www.jstree.com/
.. _datatables : http://www.datatables.net/



Evolutions Possibles
--------------------

Parmi les nouvelles fonctionnalités utiles à implémenter, en voici quelques unes :

- Gestion des comptes en banque de la corporation : historique des opérations, filtre selon le type d'opération ou l'auteur.
- Production de diagrammes et d'indicateurs depuis les informations des comptes en banque.
- production de diagrammes sur l'évolution du niveau d'accès des membres.


Choix Ergonomiques
==================

Conclusion
==========

Appendice : Comment installer ISM ?
=====================================

En standalone
-------------

Derrière un serveur Apache
--------------------------





