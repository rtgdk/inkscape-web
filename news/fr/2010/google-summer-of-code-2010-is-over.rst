Title: Le Google Summer of Code 2010 est terminé
Author: prokoudine
Category: Events
Date: 2010-09-09

Le Google Summer of Code s'est achevé sur des résultats mitigés. Malheureusement,
nous avons perdu deux étudiants lors des évaluations intermédiaires en juillet,
et une autre lors des évaluations finales en août. D'un autre côté, deux projets
ont été couronnés de succès.

Le premier projet, réalisé par Krzysztof Kosiński, été dédié au portage du
rendu d'Inkscape vers Cairo, ce qui s'est avéré particulièrement efficace du
point de vue des performances. Krzysztof a également implémenté le support pour
plusieurs cœurs ou microprocesseurs pour le rendu des filtres SVG, et il
prévoit d'implémenter ces filtres en OpenCL de façon à ce que leur rendu soit
réalisé par les cartes graphiques lorsque c'est possible.
Le second projet, mené par Abhishek Sharma, concernait la C++ification du code
SPLayer et la privatisation des nœuds XML, ce qui devrait également apporter
un plus dans l'implémentation de calculs parallèles.

L'autre bonne nouvelle est qu'un des projet échoués, l'effet de chemin
PowerStroke, a été repris par le mentor de l'étudiant, Johan Engelen. Une
implémentation initiale est disponible dans la version de développement, mais
elle est désactivée par défaut. Il est bien possible que cet effet, ainsi que
les deux autres projets réussis, soient disponibles dans la version 0.49.
