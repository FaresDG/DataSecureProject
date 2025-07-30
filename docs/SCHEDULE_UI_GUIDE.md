# Emploi du temps - Design Guide

Ce document décrit les principes d'interface pour la nouvelle page d'emploi du temps, valide pour les rôles Étudiant, Parent, Professeur et Administrateur.

## 1. Vue Calendrier Responsive
- Basée sur **FullCalendar** avec habillage Tailwind / Bootstrap.
- Code couleur par matière ou type de session (cours, TP, réunion).
- Ligne "maintenant" visible pour situer l'heure actuelle.

## 2. Options de Vue
- Semaine (par défaut), Jour, Mois accessibles depuis la barre du calendrier.
- Filtres :
  - **Admin** : par classe ou enseignant.
  - **Professeur** : par groupe ou classe.
  - **Parent** : sélection d'un enfant.
  - **Étudiant** : uniquement son propre emploi du temps.

## 3. Micro‑interactions
- Tooltip au survol affichant salle, enseignant et description.
- Glisser‑déposer ou clic pour créer/modifier un créneau (admin et prof).
- Bouton "Exporter" pour iCal/CSV et version imprimable épurée.

## 4. Accessibilité
- Contrastes respectant les recommandations WCAG AA.
- Navigation clavier complète (tabulation sur les événements, raccourcis pour changer de vue).
- Labels ARIA sur les boutons et la zone calendrier.

## 5. Maquettes ASCII

### Étudiant / Parent – Vue Semaine (Desktop)
```
+-----------------------------------------------------------+
| < Septembre 2024 >  [Jour] [Semaine] [Mois]               |
+------+-----+-----+-----+-----+-----+-----+
| Heure| Lun | Mar | Mer | Jeu | Ven | Sam |
+------+-----+-----+-----+-----+-----+-----+
| 8h   |Maths|     |Phys.|     |     |     |
| 9h   | ...                                     |
+------+-----+-----+-----+-----+-----+-----+
```

### Professeur / Admin – Vue Jour (Mobile)
```
+-------------------------------+
| Aujourd'hui      [Filtres]    |
+-------------------------------+
|08h30  [Cours Maths 1ère A]    |
|10h30  [TP Physique]           |
|...                            |
+-------------------------------+
```

## 6. Composants Principaux
- **CalendarHeader** : boutons de navigation et sélecteurs.
- **EventItem** : affiche matière, salle et info rapide.
- **FilterPanel** : liste déroulante selon le rôle connecté.

## 7. Exemple de composant React
Un exemple complet est disponible dans [`docs/snippets/schedule_component.jsx`](snippets/schedule_component.jsx).
