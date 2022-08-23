# Mobile App Straway

## Introduction
Le projet porte sur le développement d'une application mobile et un protocole d'échange pour la société Straway.

Elle permettra à l'utilisateur de se connecter aux pots connectés de la marque, puis de le configurer ainsi qu'avoir accès à une boutique en ligne pour commander de nouveaux pots.
 
La seconde partie de ce projet est le développement d'un protocole qui sera utiliser pour communiquer avec le pot connecté via le téléphone de l'utilisateur à une carte programmable ESP32. Celui-ci permettra la configuration du pot et le recueil des données de la plante. 
## Langages utilisés

 - <b>React Native </b> : pour l'application mobile
 - <b>Python </b> : pour le serveur de transit des informations
 - <b>C++</b> : pour la programmation de la carte ESP32
## Fonctionnalités 
### Application mobile
 - [ ] CRUD compte utilisateur
 - [ ] Connexion / Déconnexion au pot
 - [ ] Choix de la plante
 - [ ] Réglages manuelle des options
 - [ ] Suivi de données au travers de graphiques
 - [ ] Accéder au magasin

### Protocole d'échange
- [ ] Connexion / Déconnexion au pot 
 - [ ] Envoie d'instruction par bluetooth
	 - [ ] Réglages en fonction de la plante
 - [ ] Partager l'accés au données de la plante avec un tiers
 - [ ] Réception des données collectées par le pot
	 - [ ] Taux d'humidité
	 - [ ] Niveau d'eau du réservoir
	 - [ ] Température 
	 - [ ] Humidité de l'air
	 - [ ] Taux d'ensoleillement de la plante

 - [ ] Envoie d'instructions par Wifi
	 - [ ] Réglages en fonction de la plante

### Serveur
- [ ] Connexion au Wifi
- [ ] Transmission des données

### ESP32 
- [ ] Envoi des données collectées par le pot
	 - [ ] Taux d'humidité
	 - [ ] Niveau d'eau du réservoir
	 - [ ] Température 
	 - [ ] Humidité de l'air
	 - [ ] Taux d'ensoleillement de la plante
 - [ ] Réception d'instructions par Wifi
	 - [ ] Réglages en fonction de la plante

## Carnet de bord
<i>Semaine du 22/08/2022 au 29/08/2022</i>
--
<b>Objectifs 'SMART' :</b>
- [ ] Choisir la technologie back-end : Python vanilla OU Django REST Framework 
- [X] Designer modélisation BDD et diagramme de classes 
- [X] Développer CRUD :
- [x] User : id, firstName, lastName, email, password, roles (JSON), pots (classe Pot), picture 
- [x] Pot : id, nom,date de sortie, taux d’humidité, types de plante (JSON), plante (classe Plante), température, humidité, niveau du réservoir, taux d’ensoleillement, isConnected (booléen), ip (UNIQUE), prix, image, collection (string) 
- [X] Plant : id, nom, type, température, humidité, niveau du réservoir, taux d’ensoleillement, pots (classe Pot), image
 
